"""
性能指标计算模块
"""

import numpy as np
import pandas as pd


def compute_metrics(df: pd.DataFrame, history: dict, show_curtailment: bool = False) -> dict:
    """
    计算关键性能指标

    参数:
        df: 原始数据DataFrame
        history: 控制历史数据
        show_curtailment: 是否计算弃光率指标（光伏可变时启用）
    """
    P_cmd = history['P_cmd']
    load = history['load']
    time = history['time']

    # 计算时间间隔
    dt = np.diff(time, prepend=time[0])

    # 1. 负载跟踪率（主要指标）
    load_energy = np.sum(load * dt) / 3600  # kWh
    output_energy = np.sum(P_cmd * dt) / 3600  # kWh
    load_tracking_rate = (output_energy / load_energy * 100) if load_energy > 0 else 0

    # 2. 弃光率（可选，光伏可变时启用）
    if show_curtailment and 'P_pv_available' in history:
        P_pv_available = history['P_pv_available']
        pv_energy = np.sum(P_pv_available * dt) / 3600  # kWh
        curtailment_energy = pv_energy - output_energy
        curtailment_rate = (curtailment_energy / pv_energy * 100) if pv_energy > 0 else 0
        max_curtailment = np.max(P_pv_available - P_cmd)
    else:
        curtailment_rate = None
        curtailment_energy = None
        max_curtailment = None

    # 3. 逆流指标（P_cmd > load）
    backflow_count = np.sum(P_cmd > load)
    backflow_ratio = (backflow_count / len(P_cmd) * 100) if len(P_cmd) > 0 else 0

    # 最大逆流功率
    backflow_power = np.maximum(P_cmd - load, 0)
    max_backflow = np.max(backflow_power)

    # 4. 安全旁路触发次数
    safety_bypass_count = np.sum(history['safety_bypass'])

    # 5. 计算变化率
    dP_cmd = np.diff(P_cmd, prepend=P_cmd[0])
    dt_nonzero = dt.copy()
    dt_nonzero[dt_nonzero == 0] = 1.0
    ramp_rates = dP_cmd / dt_nonzero

    # 上调和下调速率
    up_rates = ramp_rates[ramp_rates > 0]
    down_rates = np.abs(ramp_rates[ramp_rates < 0])

    avg_up_rate = np.mean(up_rates) if len(up_rates) > 0 else 0
    max_up_rate = np.max(up_rates) if len(up_rates) > 0 else 0
    avg_down_rate = np.mean(down_rates) if len(down_rates) > 0 else 0
    max_down_rate = np.max(down_rates) if len(down_rates) > 0 else 0

    return {
        'load_tracking_rate': load_tracking_rate,  # 负载跟踪率（主要指标）
        'backflow_count': int(backflow_count),  # 逆流次数
        'backflow_ratio': backflow_ratio,  # 逆流比例 (%)
        'max_backflow_kw': max_backflow,  # 最大逆流功率 (kW)
        'curtailment_rate': curtailment_rate,  # 弃光率（可选）
        'total_curtailment_kwh': curtailment_energy,  # 总弃光量（可选）
        'max_curtailment_kw': max_curtailment,  # 最大弃光功率（可选）
        'safety_bypass_count': int(safety_bypass_count),
        'avg_up_rate': avg_up_rate,
        'max_up_rate': max_up_rate,
        'avg_down_rate': avg_down_rate,
        'max_down_rate': max_down_rate
    }
