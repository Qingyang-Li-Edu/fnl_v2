"""
V5 Anti-Backflow Controller
V5 防逆流控制器 - 主控制器
"""

import numpy as np
from typing import Dict, List, Tuple
import logging

from .params import ControlParams, ControlOutput
from .safety_calculator import SafetyCalculator
from .pv_tracker import PVPowerTracker
from .buffer_utils import apply_buffer
from ..stukf import STUKF


class V5AntiBackflowController:
    """
    V5 防逆流控制器

    基于 STUKF 预测和非对称限速的光伏防逆流控制
    """

    def __init__(
        self,
        params: ControlParams,
        initial_load: float,
        process_noise: float = 0.1,
        measurement_noise: float = 1.0,
    ):
        """
        初始化控制器

        参数:
            params: 控制参数
            initial_load: 初始负载值
            process_noise: STUKF 过程噪声
            measurement_noise: STUKF 测量噪声
        """
        self.params = params

        # 初始化 STUKF 预测器
        self.stukf = STUKF(
            initial_load,
            process_noise,
            measurement_noise,
            memory_decay=params.stukf_memory_decay,
        )

        # 初始化模块
        self.safety_calc = SafetyCalculator(params, self.stukf)
        self.pv_tracker = PVPowerTracker(params)

        # 初始化日志记录器
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"控制器初始化完成: use_safety_ceiling={params.use_safety_ceiling}, "
                        f"use_buffer={params.use_buffer}, P_max={params.P_max}, "
                        f"initial_load={initial_load}")

        # 控制状态
        self.P_cmd_prev = 0.0  # 上一次的指令
        self.time_prev = 0.0  # 上一次的时间
        self.current_time = 0.0
        self.L_prev = initial_load  # 上一次的负载测量值（用于急降检测）

        # 记录历史
        self.history: Dict[str, List] = {
            "time": [],
            "load": [],
            "P_cmd": [],
            "U_A": [],
            "U_B": [],
            "L_med": [],
            "L_lb": [],
            "safety_bypass": [],
            "P_pv_available": [],  # 光伏可用功率历史
        }

    def compute_control(self, L_t: float, time: float) -> ControlOutput:
        """
        计算控制指令

        参数:
            L_t: 当前负载测量值 (kW)
            time: 当前时间戳 (s)

        返回:
            ControlOutput: 控制输出
        """
        # 异常处理：负载异常
        if L_t <= 0 or np.isnan(L_t):
            output = self._create_zero_output()
            self._record_history(time, L_t, output)
            return output

        # 计算时间步长
        dt = self._compute_timestep(time)

        # 更新 STUKF
        self.stukf.update(L_t, time)

        # 计算控制时域
        H = self._compute_horizon(dt)

        # 1. 计算安全上界和性能上界
        U_A1, U_A2, L_med, L_lb = self.safety_calc.compute_safety_ceiling(L_t, H)
        U_A = min(U_A1, U_A2) if U_A1 is not None else U_A2
        U_B = self.safety_calc.compute_performance_ceiling(L_med)

        # 2. 应用物理约束（根据 use_safety_ceiling 决定是否使用安全上界）
        if self.params.use_safety_ceiling:
            U = min(U_A, self.params.P_max)
        else:
            U = self.params.P_max

        # 3. 应用光伏可用功率约束
        U, pv_constrained = self.pv_tracker.apply_constraint(U)

        # 4. 检查上行意图并应用性能上界
        upward_intent = self._check_upward_intent(U, L_med)
        if upward_intent:
            U = min(U, U_B)

        # 5. 紧急安全机制：负载急降检测
        U, emergency_triggered = self._check_emergency_drop(L_t, dt, U)

        # 6. 应用控制律（限速或安全旁路）
        P_cmd, safety_bypass = self._apply_control_law(U, dt, emergency_triggered)

        # 调试日志：记录关键计算结果
        self.logger.debug(
            f"时间={time:.2f}s, 负载={L_t:.2f}kW | "
            f"U_A={U_A:.2f}, U_B={U_B:.2f}, U={U:.2f} | "
            f"pv_constrained={pv_constrained}, upward_intent={upward_intent}, "
            f"safety_bypass={safety_bypass} | "
            f"P_cmd={P_cmd:.2f}kW, P_pv_available={self.pv_tracker.available_power:.2f}kW"
        )

        # 7. 更新光伏功率跟踪器
        self.pv_tracker.update(P_cmd, pv_constrained, safety_bypass, dt)

        # 8. 更新状态
        self._update_state(P_cmd, time, L_t)

        # 创建输出
        output = ControlOutput(
            P_cmd=P_cmd,
            U_A=U_A,
            U_B=U_B,
            U=U,
            L_med=L_med,
            L_lb=L_lb,
            safety_bypass=safety_bypass,
            upward_intent=upward_intent,
        )

        # 记录历史
        self._record_history(time, L_t, output)

        return output

    def _compute_horizon(self, dt: float) -> float:
        """计算控制时域 H"""
        return dt + self.params.tau_meas + self.params.tau_com + self.params.tau_exec

    def _compute_timestep(self, time: float) -> float:
        """计算并限制时间步长"""
        dt = time - self.time_prev if self.time_prev > 0 else 1.0
        return max(0.1, min(dt, 10.0))  # 限制在合理范围

    def _check_upward_intent(self, U: float, L_med: float) -> bool:
        """检查是否存在上行意图"""
        return (U > self.P_cmd_prev) or (L_med > self.P_cmd_prev)

    def _check_emergency_drop(
        self, L_t: float, dt: float, U: float
    ) -> Tuple[float, bool]:
        """
        检查负载急降并应用紧急限制

        参数:
            L_t: 当前负载
            dt: 时间步长
            U: 当前上界

        返回:
            (U_adjusted, emergency_triggered): 调整后的上界和紧急触发标志
        """
        emergency_triggered = False

        if self.params.S_down_max is not None:
            # 计算负载变化率
            dL = L_t - self.L_prev
            dL_dt = dL / dt if dt > 0 else 0

            # 如果负载下降速度超过阈值，触发紧急限制
            if dL_dt < -self.params.S_down_max:
                U_emergency = apply_buffer(L_t, self.params.use_buffer, self.params.buffer)
                U = min(U, U_emergency)
                emergency_triggered = True

        return U, emergency_triggered

    def _apply_control_law(
        self, U: float, dt: float, emergency_triggered: bool
    ) -> Tuple[float, bool]:
        """
        应用控制律（限速或安全旁路）

        参数:
            U: 上界
            dt: 时间步长
            emergency_triggered: 是否触发紧急旁路

        返回:
            (P_cmd, safety_bypass): 控制指令和安全旁路标志
        """
        # 计算限速边界
        U_ramp = self.P_cmd_prev + self.params.R_up * dt
        L_ramp = self.P_cmd_prev - self.params.R_down * dt

        # 应用控制律
        safety_bypass = emergency_triggered  # 初始化为紧急旁路状态

        if U < self.P_cmd_prev:
            # 安全旁路：立即下调
            P_cmd = max(0, min(U, self.params.P_max))
            safety_bypass = True
        else:
            # 正常控制：应用限速
            P_cmd = max(max(0, L_ramp), min(U, U_ramp))

        # 确保非负
        P_cmd = max(0, P_cmd)

        return P_cmd, safety_bypass

    def _update_state(self, P_cmd: float, time: float, L_t: float):
        """更新控制器状态"""
        self.P_cmd_prev = P_cmd
        self.time_prev = time
        self.current_time = time
        self.L_prev = L_t

    def _create_zero_output(self) -> ControlOutput:
        """创建零值输出（用于异常情况）"""
        return ControlOutput(
            P_cmd=0.0,
            U_A=0.0,
            U_B=0.0,
            U=0.0,
            L_med=0.0,
            L_lb=0.0,
            safety_bypass=True,
            upward_intent=False,
        )

    def _record_history(self, time: float, load: float, output: ControlOutput):
        """记录历史数据"""
        self.history["time"].append(time)
        self.history["load"].append(load)
        self.history["P_cmd"].append(output.P_cmd)
        self.history["U_A"].append(output.U_A)
        self.history["U_B"].append(output.U_B)
        self.history["L_med"].append(output.L_med)
        self.history["L_lb"].append(output.L_lb)
        self.history["safety_bypass"].append(output.safety_bypass)
        self.history["P_pv_available"].append(self.pv_tracker.available_power)

    def get_history(self) -> Dict[str, np.ndarray]:
        """获取历史数据（转换为 numpy 数组）"""
        return {key: np.array(values) for key, values in self.history.items()}

    def reset(self, initial_load: float):
        """重置控制器"""
        self.stukf = STUKF(initial_load)
        self.safety_calc = SafetyCalculator(self.params, self.stukf)
        self.pv_tracker.reset()
        self.P_cmd_prev = 0.0
        self.time_prev = 0.0
        self.current_time = 0.0
        self.L_prev = initial_load
        self.history = {
            "time": [],
            "load": [],
            "P_cmd": [],
            "U_A": [],
            "U_B": [],
            "L_med": [],
            "L_lb": [],
            "safety_bypass": [],
            "P_pv_available": [],  # 光伏可用功率历史
        }
