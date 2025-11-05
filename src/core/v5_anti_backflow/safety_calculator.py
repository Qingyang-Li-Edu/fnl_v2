"""
Safety Ceiling Calculator
安全上界计算器
"""

import numpy as np
from typing import Tuple
from scipy.stats import norm

from .params import ControlParams
from .buffer_utils import apply_buffer
from ..stukf import STUKF


class SafetyCalculator:
    """安全上界计算器"""

    def __init__(self, params: ControlParams, stukf: STUKF):
        """
        初始化安全上界计算器

        参数:
            params: 控制参数
            stukf: STUKF 预测器
        """
        self.params = params
        self.stukf = stukf

    def compute_safety_ceiling(
        self, L_t: float, H: float
    ) -> Tuple[float, float, float, float]:
        """
        计算安全上界（支持动态策略）

        参数:
            L_t: 当前负载测量值
            H: 控制时域

        返回:
            (U_A1, U_A2, L_med, L_lb): 确定性安全上界、概率性安全上界、预测均值、置信下界
        """
        # === 动态安全策略 ===
        if self.params.enable_dynamic_safety:
            L_med, L_lb = self._compute_dynamic_prediction(H)
        else:
            # 静态策略（原始实现）
            L_med, L_lb = self.stukf.predict_ahead(H, confidence=1 - self.params.alpha)

        # 【第1轮优化】突变紧急检测
        # 如果 STUKF 检测到负载快速下降，使用更保守的下界
        if len(self.stukf.load_history) > 1:
            recent_dL_dt = self.stukf.x[1]  # 当前估计的负载变化率
            if recent_dL_dt < -10.0:  # 快速下降（> 10 kW/s）
                # 紧急模式：假设负载继续下降
                emergency_drop = abs(recent_dL_dt) * H * 1.2  # 1.2 安全系数
                L_lb_emergency = L_t - emergency_drop
                L_lb = min(L_lb, L_lb_emergency)  # 取更保守的值

        # === 计算安全上界 ===
        # 自适应策略 vs 传统策略
        if self.params.adaptive_safety and self.params.use_buffer:
            U_A2 = self._compute_adaptive_safety_bound(L_lb)
        else:
            # 传统策略：根据use_buffer决定是否减去Buffer
            U_A2 = apply_buffer(L_lb, self.params.use_buffer, self.params.buffer)

        # 确定性安全上界（如果提供了 S_down_max）
        if self.params.S_down_max is not None:
            max_drop = self.params.S_down_max * H
            U_A1 = apply_buffer(
                L_t - max_drop, self.params.use_buffer, self.params.buffer
            )
            return U_A1, U_A2, L_med, L_lb
        else:
            return None, U_A2, L_med, L_lb

    def compute_performance_ceiling(self, L_med: float) -> float:
        """
        计算性能上界

        参数:
            L_med: 预测的负载均值

        返回:
            性能上界
        """
        return apply_buffer(L_med, self.params.use_buffer, self.params.buffer)

    def _compute_dynamic_prediction(self, H: float) -> Tuple[float, float]:
        """
        使用动态策略计算预测值和置信下界

        参数:
            H: 控制时域

        返回:
            (L_med, L_lb): 预测均值和置信下界
        """
        # 策略1：趋势自适应置信度
        dynamic_alpha = self._compute_dynamic_alpha()

        # 使用动态置信度预测
        L_med, L_lb_global = self.stukf.predict_ahead(H, confidence=1 - dynamic_alpha)

        # 策略2：局部不确定性混合
        if len(self.stukf.load_history) >= self.params.local_window_size:
            L_lb = self._compute_mixed_lower_bound(L_med, L_lb_global, dynamic_alpha)
        else:
            # 数据不足，使用全局预测
            L_lb = L_lb_global

        return L_med, L_lb

    def _compute_dynamic_alpha(self) -> float:
        """
        计算动态置信度参数

        返回:
            动态调整后的 alpha 值
        """
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

        return dynamic_alpha

    def _compute_mixed_lower_bound(
        self, L_med: float, L_lb_global: float, dynamic_alpha: float
    ) -> float:
        """
        计算混合局部和全局不确定性的置信下界

        参数:
            L_med: 预测均值
            L_lb_global: 全局预测的置信下界
            dynamic_alpha: 动态置信度参数

        返回:
            混合后的置信下界
        """
        # 计算局部标准差
        recent_data = self.stukf.load_history[-self.params.local_window_size :]
        local_std = np.std(recent_data)

        # 计算全局预测的隐含标准差
        k_alpha = norm.ppf(1 - dynamic_alpha / 2)
        global_std = (L_med - L_lb_global) / k_alpha if k_alpha > 0 else local_std

        # 混合：局部权重 × 局部std + (1-局部权重) × 全局std
        mixed_std = (
            self.params.local_uncertainty_weight * local_std
            + (1 - self.params.local_uncertainty_weight) * global_std
        )

        # 使用混合标准差计算新的下界
        L_lb = L_med - k_alpha * mixed_std
        return L_lb

    def _compute_adaptive_safety_bound(self, L_lb: float) -> float:
        """
        计算自适应安全上界

        参数:
            L_lb: 置信下界

        返回:
            自适应安全上界
        """
        # 自适应安全上界：低负载时使用相对buffer，高负载时使用绝对buffer
        buffer_threshold = 2 * self.params.buffer

        if L_lb < buffer_threshold:
            # 低负载场景：使用相对buffer（保留20%安全余量）
            return max(0, L_lb * 0.8)
        else:
            # 高负载场景：使用绝对buffer
            return max(0, L_lb - self.params.buffer)
