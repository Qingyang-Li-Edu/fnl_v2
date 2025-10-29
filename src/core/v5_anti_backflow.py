"""
V5 Anti-Backflow Control Algorithm
基于 STUKF 的光伏防逆流控制算法
"""

import numpy as np
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass
from .stukf import STUKF


@dataclass
class ControlParams:
    """控制参数"""
    buffer: float = 5.0  # 安全余量 (kW)
    use_buffer: bool = True  # 是否启用Buffer（插件）
    use_safety_ceiling: bool = True  # 是否使用安全上界（False时仅用性能上界）
    adaptive_safety: bool = True  # 是否使用自适应安全上界策略
    R_up: float = 10.0  # 上行斜率限制 (kW/s)
    R_down: float = 50.0  # 下行斜率限制 (kW/s)
    alpha: float = 1e-3  # 置信度参数
    S_down_max: Optional[float] = None  # 负载最大下行速率 (kW/s)
    P_max: float = 100.0  # 逆变器最大功率 (kW)
    tau_meas: float = 0.1  # 测量延迟 (s)
    tau_com: float = 0.1  # 通信延迟 (s)
    tau_exec: float = 0.2  # 执行延迟 (s)
    stukf_memory_decay: float = 0.99  # STUKF记忆衰减因子（0.9-0.999）

    # 动态安全策略参数
    enable_dynamic_safety: bool = True  # 启用动态安全策略
    trend_adaptive: bool = True  # 启用趋势自适应
    up_risk_factor: float = 0.5  # 上升时风险系数（越小越激进）
    down_risk_factor: float = 2.0  # 下降时风险系数（越大越保守）
    local_uncertainty_weight: float = 0.7  # 局部不确定性权重（0-1）
    local_window_size: int = 50  # 局部窗口大小（数据点数）


@dataclass
class ControlOutput:
    """控制输出"""
    P_cmd: float  # 下发的PV限发指令
    U_A: float  # 安全上界
    U_B: float  # 性能上界
    U: float  # 最终使用的上界
    L_med: float  # STUKF预测的均值
    L_lb: float  # STUKF预测的置信下界
    safety_bypass: bool  # 是否触发安全旁路
    upward_intent: bool  # 是否存在上行意图


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
        measurement_noise: float = 1.0
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
        self.stukf = STUKF(
            initial_load,
            process_noise,
            measurement_noise,
            memory_decay=params.stukf_memory_decay
        )

        # 控制状态
        self.P_cmd_prev = 0.0  # 上一次的指令
        self.time_prev = 0.0  # 上一次的时间
        self.current_time = 0.0
        self.L_prev = initial_load  # 上一次的负载测量值（用于急降检测）

        # 记录历史
        self.history: Dict[str, List] = {
            'time': [],
            'load': [],
            'P_cmd': [],
            'U_A': [],
            'U_B': [],
            'L_med': [],
            'L_lb': [],
            'safety_bypass': []
        }

    def _compute_horizon(self, dt: float) -> float:
        """计算控制时域 H"""
        return dt + self.params.tau_meas + self.params.tau_com + self.params.tau_exec

    def _compute_safety_ceiling(self, L_t: float, H: float) -> Tuple[float, float]:
        """
        计算安全上界（支持动态策略）

        返回:
            (U_A1, U_A2, L_med, L_lb): 确定性安全上界、概率性安全上界、预测均值、置信下界
        """
        from scipy.stats import norm

        # === 动态安全策略 ===
        if self.params.enable_dynamic_safety:
            # 策略1：趋势自适应置信度
            dynamic_alpha = self.params.alpha

            if self.params.trend_adaptive:
                dL_dt = self.stukf.x[1]  # 负载变化率（一阶导数）

                if dL_dt > 1.0:  # 负载上升（阈值：1 kW/s）
                    # 上升时：放松限制
                    risk_factor = self.params.up_risk_factor
                elif dL_dt < -1.0:  # 负载下降
                    # 下降时：收紧限制
                    risk_factor = self.params.down_risk_factor
                else:  # 变化不明显
                    risk_factor = 1.0

                # 调整置信度：risk_factor越大，alpha越小（越保守）
                dynamic_alpha = self.params.alpha / risk_factor
                dynamic_alpha = np.clip(dynamic_alpha, 1e-6, 0.2)  # 限制范围

            # 使用动态置信度预测
            L_med, L_lb_global = self.stukf.predict_ahead(H, confidence=1 - dynamic_alpha)

            # 策略2：局部不确定性混合
            if len(self.stukf.load_history) >= self.params.local_window_size:
                # 计算局部标准差
                recent_data = self.stukf.load_history[-self.params.local_window_size:]
                local_std = np.std(recent_data)

                # 计算全局预测的隐含标准差
                k_alpha = norm.ppf(1 - dynamic_alpha / 2)
                global_std = (L_med - L_lb_global) / k_alpha if k_alpha > 0 else local_std

                # 混合：局部权重 × 局部std + (1-局部权重) × 全局std
                mixed_std = (
                    self.params.local_uncertainty_weight * local_std +
                    (1 - self.params.local_uncertainty_weight) * global_std
                )

                # 使用混合标准差计算新的下界
                L_lb = L_med - k_alpha * mixed_std
            else:
                # 数据不足，使用全局预测
                L_lb = L_lb_global

        else:
            # 静态策略（原始实现）
            L_med, L_lb = self.stukf.predict_ahead(H, confidence=1 - self.params.alpha)

        # === 计算安全上界 ===
        # 自适应策略 vs 传统策略
        if self.params.adaptive_safety and self.params.use_buffer:
            # 自适应安全上界：低负载时使用相对buffer，高负载时使用绝对buffer
            buffer_threshold = 2 * self.params.buffer

            if L_lb < buffer_threshold:
                # 低负载场景：使用相对buffer（保留20%安全余量）
                U_A2 = max(0, L_lb * 0.8)
            else:
                # 高负载场景：使用绝对buffer
                U_A2 = max(0, L_lb - self.params.buffer)
        else:
            # 传统策略：根据use_buffer决定是否减去Buffer
            if self.params.use_buffer:
                U_A2 = max(0, L_lb - self.params.buffer)
            else:
                U_A2 = max(0, L_lb)

        # 确定性安全上界（如果提供了 S_down_max）
        if self.params.S_down_max is not None:
            max_drop = self.params.S_down_max * H
            if self.params.use_buffer:
                U_A1 = max(0, L_t - max_drop - self.params.buffer)
            else:
                U_A1 = max(0, L_t - max_drop)
            return U_A1, U_A2, L_med, L_lb
        else:
            return None, U_A2, L_med, L_lb

    def _compute_performance_ceiling(self, L_med: float) -> float:
        """计算性能上界"""
        if self.params.use_buffer:
            return max(0, L_med - self.params.buffer)
        else:
            return max(0, L_med)

    def _check_upward_intent(self, U: float, L_med: float) -> bool:
        """检查是否存在上行意图"""
        return (U > self.P_cmd_prev) or (L_med > self.P_cmd_prev)

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
            output = ControlOutput(
                P_cmd=0.0,
                U_A=0.0,
                U_B=0.0,
                U=0.0,
                L_med=0.0,
                L_lb=0.0,
                safety_bypass=True,
                upward_intent=False
            )
            self._record_history(time, L_t, output)
            return output

        # 计算时间步长
        dt = time - self.time_prev if self.time_prev > 0 else 1.0
        dt = max(0.1, min(dt, 10.0))  # 限制在合理范围

        # 更新 STUKF
        self.stukf.update(L_t, time)

        # 计算控制时域
        H = self._compute_horizon(dt)

        # 1. 计算安全上界
        U_A1, U_A2, L_med, L_lb = self._compute_safety_ceiling(L_t, H)

        # 合成安全上界
        if U_A1 is not None:
            U_A = min(U_A1, U_A2)
        else:
            U_A = U_A2

        # 2. 计算性能上界
        U_B = self._compute_performance_ceiling(L_med)

        # 3. 应用物理约束（根据 use_safety_ceiling 决定是否使用安全上界）
        if self.params.use_safety_ceiling:
            # 使用安全上界
            U = min(U_A, self.params.P_max)
        else:
            # 不使用安全上界，仅受物理限制
            U = self.params.P_max

        # 4. 检查上行意图
        upward_intent = self._check_upward_intent(U, L_med)

        # 如果存在上行意图，应用性能上界
        if upward_intent:
            U = min(U, U_B)

        # === 紧急安全机制：负载急降检测（独立于安全上界开关） ===
        emergency_triggered = False
        if self.params.S_down_max is not None:
            # 计算负载变化率
            dL = L_t - self.L_prev
            dL_dt = dL / dt if dt > 0 else 0

            # 如果负载下降速度超过阈值，触发紧急限制
            if dL_dt < -self.params.S_down_max:
                # 紧急限制：PV输出不超过当前负载（减去buffer）
                if self.params.use_buffer:
                    U_emergency = max(0, L_t - self.params.buffer)
                else:
                    U_emergency = max(0, L_t)

                U = min(U, U_emergency)
                emergency_triggered = True  # 标记为触发了紧急旁路

        # 5. 计算限速边界
        U_ramp = self.P_cmd_prev + self.params.R_up * dt
        L_ramp = self.P_cmd_prev - self.params.R_down * dt

        # 6. 应用控制律
        safety_bypass = emergency_triggered  # 初始化为紧急旁路状态

        if U < self.P_cmd_prev:
            # 安全旁路：立即下调
            P_cmd = max(0, min(U, self.params.P_max))
            safety_bypass = True
        else:
            # 正常控制：应用限速
            P_cmd = max(
                max(0, L_ramp),
                min(U, U_ramp)
            )

        # 确保非负
        P_cmd = max(0, P_cmd)

        # 更新状态
        self.P_cmd_prev = P_cmd
        self.time_prev = time
        self.current_time = time
        self.L_prev = L_t  # 更新上一次负载值，用于下次急降检测

        # 创建输出
        output = ControlOutput(
            P_cmd=P_cmd,
            U_A=U_A,
            U_B=U_B,
            U=U,
            L_med=L_med,
            L_lb=L_lb,
            safety_bypass=safety_bypass,
            upward_intent=upward_intent
        )

        # 记录历史
        self._record_history(time, L_t, output)

        return output

    def _record_history(self, time: float, load: float, output: ControlOutput):
        """记录历史数据"""
        self.history['time'].append(time)
        self.history['load'].append(load)
        self.history['P_cmd'].append(output.P_cmd)
        self.history['U_A'].append(output.U_A)
        self.history['U_B'].append(output.U_B)
        self.history['L_med'].append(output.L_med)
        self.history['L_lb'].append(output.L_lb)
        self.history['safety_bypass'].append(output.safety_bypass)

    def get_history(self) -> Dict[str, np.ndarray]:
        """获取历史数据（转换为 numpy 数组）"""
        return {key: np.array(values) for key, values in self.history.items()}

    def reset(self, initial_load: float):
        """重置控制器"""
        self.stukf = STUKF(initial_load)
        self.P_cmd_prev = 0.0
        self.time_prev = 0.0
        self.current_time = 0.0
        self.history = {
            'time': [],
            'load': [],
            'P_cmd': [],
            'U_A': [],
            'U_B': [],
            'L_med': [],
            'L_lb': [],
            'safety_bypass': []
        }
