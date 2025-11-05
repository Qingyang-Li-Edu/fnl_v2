"""
STUKF (Smooth Trend Unscented Kalman Filter) Implementation
用于负载预测的平滑趋势无迹卡尔曼滤波器
"""

import numpy as np
from scipy.stats import norm
from typing import Tuple, Optional


class STUKF:
    """
    Smooth Trend Unscented Kalman Filter for load prediction

    状态向量: [L, dL/dt, d²L/dt²]
    - L: 当前负载
    - dL/dt: 负载变化率（趋势）
    - d²L/dt²: 负载加速度
    """

    def __init__(
        self,
        initial_load: float,
        process_noise: float = 0.1,
        measurement_noise: float = 1.0,
        alpha_ukf: float = 1e-3,
        beta_ukf: float = 2.0,
        kappa_ukf: float = 0.0,
        memory_decay: float = 0.99
    ):
        """
        初始化 STUKF

        参数:
            initial_load: 初始负载值
            process_noise: 过程噪声强度
            measurement_noise: 测量噪声强度
            alpha_ukf: UKF 参数 alpha (扩散参数)
            beta_ukf: UKF 参数 beta (高斯分布参数)
            kappa_ukf: UKF 参数 kappa (缩放参数)
            memory_decay: 记忆衰减因子 (0.9-0.999，越小越关注近期)
        """
        # 状态维度
        self.n = 3

        # 状态向量 [L, dL/dt, d²L/dt²]
        self.x = np.array([initial_load, 0.0, 0.0])

        # 状态协方差矩阵
        self.P = np.eye(3) * 100.0

        # 过程噪声协方差矩阵
        self.Q = np.eye(3) * process_noise

        # 测量噪声协方差
        self.R = measurement_noise

        # UKF 参数
        self.alpha = alpha_ukf
        self.beta = beta_ukf
        self.kappa = kappa_ukf

        # 记忆衰减因子
        self.memory_decay = memory_decay

        # 计算 lambda 参数
        self.lambda_ = self.alpha**2 * (self.n + self.kappa) - self.n

        # 计算权重
        self._compute_weights()

        # 历史数据
        self.load_history = [initial_load]
        self.time_history = [0.0]

    def _compute_weights(self):
        """计算 UKF sigma 点权重"""
        self.Wm = np.zeros(2 * self.n + 1)
        self.Wc = np.zeros(2 * self.n + 1)

        self.Wm[0] = self.lambda_ / (self.n + self.lambda_)
        self.Wc[0] = self.lambda_ / (self.n + self.lambda_) + (1 - self.alpha**2 + self.beta)

        for i in range(1, 2 * self.n + 1):
            self.Wm[i] = 1 / (2 * (self.n + self.lambda_))
            self.Wc[i] = 1 / (2 * (self.n + self.lambda_))

    def _generate_sigma_points(self) -> np.ndarray:
        """生成 sigma 点"""
        sigma_points = np.zeros((2 * self.n + 1, self.n))
        sigma_points[0] = self.x

        # 矩阵平方根
        try:
            U = np.linalg.cholesky((self.n + self.lambda_) * self.P)
        except np.linalg.LinAlgError:
            # 如果协方差矩阵不正定，使用 SVD
            U, S, _ = np.linalg.svd(self.P)
            U = U @ np.diag(np.sqrt(S * (self.n + self.lambda_)))

        for i in range(self.n):
            sigma_points[i + 1] = self.x + U[:, i]
            sigma_points[self.n + i + 1] = self.x - U[:, i]

        return sigma_points

    def _state_transition(self, x: np.ndarray, dt: float) -> np.ndarray:
        """
        状态转移函数
        x_k+1 = F * x_k
        """
        F = np.array([
            [1, dt, 0.5 * dt**2],
            [0, 1, dt],
            [0, 0, 1]
        ])
        return F @ x

    def _measurement_function(self, x: np.ndarray) -> float:
        """测量函数：只测量负载值"""
        return x[0]

    def predict(self, dt: float) -> Tuple[float, float]:
        """
        预测步骤

        参数:
            dt: 时间步长

        返回:
            (predicted_mean, predicted_std): 预测均值和标准差
        """
        # 生成 sigma 点
        sigma_points = self._generate_sigma_points()

        # 传播 sigma 点
        sigma_points_pred = np.zeros_like(sigma_points)
        for i in range(2 * self.n + 1):
            sigma_points_pred[i] = self._state_transition(sigma_points[i], dt)

        # 预测状态均值
        x_pred = np.sum(self.Wm[:, np.newaxis] * sigma_points_pred, axis=0)

        # 预测协方差
        P_pred = self.Q.copy()
        for i in range(2 * self.n + 1):
            diff = sigma_points_pred[i] - x_pred
            P_pred += self.Wc[i] * np.outer(diff, diff)

        self.x = x_pred
        self.P = P_pred

        return self.x[0], np.sqrt(self.P[0, 0])

    def update(self, measurement: float, time: float):
        """
        更新步骤

        参数:
            measurement: 测量的负载值
            time: 当前时间戳
        """
        # 【第1轮优化】计算负载变化率（用于自适应）
        dt = time - self.time_history[-1] if len(self.time_history) > 0 else 1.0
        dt = max(0.01, dt)  # 避免除零

        if len(self.load_history) > 0:
            dL = measurement - self.load_history[-1]
            dL_dt = dL / dt  # 负载变化率 (kW/s)
        else:
            dL_dt = 0.0

        # 生成 sigma 点
        sigma_points = self._generate_sigma_points()

        # 传播到测量空间
        z_sigma = np.array([self._measurement_function(sp) for sp in sigma_points])

        # 预测测量均值
        z_pred = np.sum(self.Wm * z_sigma)

        # 创新协方差
        Pzz = self.R
        for i in range(2 * self.n + 1):
            diff = z_sigma[i] - z_pred
            Pzz += self.Wc[i] * diff * diff

        # 交叉协方差
        Pxz = np.zeros(self.n)
        for i in range(2 * self.n + 1):
            Pxz += self.Wc[i] * (sigma_points[i] - self.x) * (z_sigma[i] - z_pred)

        # 卡尔曼增益
        K = Pxz / Pzz

        # 更新状态
        innovation = measurement - z_pred
        self.x = self.x + K * innovation

        # 更新协方差
        self.P = self.P - K[:, np.newaxis] * Pzz * K[np.newaxis, :]

        # 【第1轮优化】自适应协方差调整（安全版本）
        # 检测负载突变，适度增加不确定性以提高响应速度
        abs_dL_dt = abs(dL_dt)

        if abs_dL_dt > 5.0:  # 负载变化率超过 5 kW/s（突变）
            # 适度增加位置不确定性（1.5倍，而非指数膨胀）
            inflation_factor = min(1.5, 1.0 + abs_dL_dt / 50.0)  # 动态膨胀系数
            self.P[0, 0] *= inflation_factor

        # 协方差上限保护（防止爆炸）
        max_variance = 1000.0  # 位置方差上限
        self.P[0, 0] = min(self.P[0, 0], max_variance)

        # 速度和加速度方差也设置上限
        self.P[1, 1] = min(self.P[1, 1], 100.0)   # 速度方差上限
        self.P[2, 2] = min(self.P[2, 2], 10.0)    # 加速度方差上限

        # 保存历史
        self.load_history.append(measurement)
        self.time_history.append(time)

    def predict_ahead(self, horizon: float, confidence: float = 0.999) -> Tuple[float, float]:
        """
        预测未来 horizon 时间的负载

        参数:
            horizon: 预测时间范围（秒）
            confidence: 置信度（例如 0.999 表示 99.9%）

        返回:
            (mean_prediction, lower_bound): 均值预测和置信下界
        """
        # 使用当前状态预测
        x_future = self._state_transition(self.x, horizon)

        # 计算预测协方差
        F = np.array([
            [1, horizon, 0.5 * horizon**2],
            [0, 1, horizon],
            [0, 0, 1]
        ])
        P_future = F @ self.P @ F.T + self.Q * horizon

        mean_pred = x_future[0]
        std_pred = np.sqrt(P_future[0, 0])

        # 计算置信下界
        z_score = norm.ppf(1 - confidence)  # 负数，因为是下界
        lower_bound = mean_pred + z_score * std_pred

        return mean_pred, lower_bound

    def get_state(self) -> np.ndarray:
        """获取当前状态"""
        return self.x.copy()

    def get_covariance(self) -> np.ndarray:
        """获取当前协方差矩阵"""
        return self.P.copy()
