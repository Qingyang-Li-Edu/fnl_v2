"""
性能指标计算模块
"""

import numpy as np
import pandas as pd


def compute_metrics(df: pd.DataFrame, history: dict) -> dict:
    """计算关键性能指标"""
    P_cmd = history['P_cmd']
    load = history['load']
    time = history['time']

    # 计算弃光量
    P_max = max(P_cmd) if len(P_cmd) > 0 else 0
    curtailed_power = P_max - P_cmd

    # 总弃光量 (kWh)
    dt = np.diff(time, prepend=time[0])
    total_curtailment = np.sum(curtailed_power * dt) / 3600

    # 最大弃光功率
    max_curtailment = np.max(curtailed_power)

    # 安全旁路触发次数
    safety_bypass_count = np.sum(history['safety_bypass'])

    # 计算变化率
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

    # 计算弃光率
    curtailment_rate = (total_curtailment / (P_max * (time[-1] - time[0]) / 3600)) * 100 if P_max > 0 else 0

    return {
        'total_curtailment_kwh': total_curtailment,
        'curtailment_rate': curtailment_rate,
        'max_curtailment_kw': max_curtailment,
        'safety_bypass_count': int(safety_bypass_count),
        'avg_up_rate': avg_up_rate,
        'max_up_rate': max_up_rate,
        'avg_down_rate': avg_down_rate,
        'max_down_rate': max_down_rate
    }
