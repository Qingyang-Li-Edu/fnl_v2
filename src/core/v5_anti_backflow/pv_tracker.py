"""
PV Power Tracker
光伏可用功率跟踪器
"""

from typing import Tuple
from .params import ControlParams


class PVPowerTracker:
    """
    光伏可用功率跟踪器

    跟踪光伏阵列的实际可用功率，区分光伏功率约束和负载约束
    """

    def __init__(self, params: ControlParams):
        """
        初始化光伏功率跟踪器

        参数:
            params: 控制参数
        """
        self.params = params
        self.P_pv_available = params.P_max  # 初始假设光伏充足

    def apply_constraint(self, U: float) -> Tuple[float, bool]:
        """
        应用光伏功率约束

        参数:
            U: 约束前的上界

        返回:
            (U_constrained, pv_constrained): 约束后的上界和是否被光伏功率约束的标志
        """
        U_before_constraint = U
        U_constrained = min(U, self.P_pv_available)
        pv_constrained = U_constrained < U_before_constraint

        return U_constrained, pv_constrained

    def update(self, P_cmd: float, pv_constrained: bool, safety_bypass: bool, dt: float):
        """
        更新光伏可用功率跟踪（只响应真实的光伏功率变化）

        参数:
            P_cmd: 当前控制指令
            pv_constrained: 是否被光伏功率约束
            safety_bypass: 是否触发安全旁路
            dt: 时间步长
        """
        if pv_constrained and safety_bypass:
            # 条件：同时满足 (1) 被光伏功率约束 且 (2) 触发安全旁路
            # 说明：光伏功率真的不足，导致了下调
            # 动作：更新光伏可用功率基准为当前P_cmd
            self.P_pv_available = P_cmd

        elif not pv_constrained:
            # 条件：没有被光伏功率约束
            # 说明：光伏功率充足，当前限制来自其他因素（如负载下降、安全上界等）
            # 动作：允许光伏可用功率逐步恢复（模拟云散开、遮挡解除等场景）
            max_pv_increase = self.params.pv_recovery_rate * dt
            self.P_pv_available = min(
                self.P_pv_available + max_pv_increase, self.params.P_max
            )

        # else: pv_constrained=True but safety_bypass=False
        #       说明被光伏功率约束但在正常上升，保持 P_pv_available 不变

    def reset(self):
        """重置光伏可用功率为最大值"""
        self.P_pv_available = self.params.P_max

    @property
    def available_power(self) -> float:
        """获取当前光伏可用功率"""
        return self.P_pv_available
