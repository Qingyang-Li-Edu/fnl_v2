"""
V5 Anti-Backflow Control Parameters and Output
控制参数和输出数据类定义
"""

from dataclasses import dataclass
from typing import Optional


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

    # 光伏功率跟踪参数
    pv_recovery_rate: float = 1.0  # 光伏可用功率恢复速率 (kW/s)

    # 光伏功率配置（预留接口）
    pv_power_profile: Optional[callable] = None  # 光伏功率曲线函数(time)->float，None表示恒定P_max
    show_curtailment_metrics: bool = False  # 是否显示弃光率指标（光伏可变时启用）


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
