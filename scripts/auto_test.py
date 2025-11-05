"""
自动测试脚本：评估三种策略模式的性能
用于迭代优化，自动比较激进/平衡/保守模式
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
from src.core import V5AntiBackflowController, ControlParams
from src.utils import generate_sample_data
from src.utils.logging_config import setup_logger
import json
from datetime import datetime


def run_mode_test(mode_name: str, params: ControlParams, df: pd.DataFrame) -> dict:
    """
    运行单个模式的测试

    参数:
        mode_name: 模式名称
        params: 控制参数
        df: 测试数据

    返回:
        性能指标字典
    """
    logger = setup_logger(f"test_{mode_name}")
    logger.info(f"开始测试 {mode_name} 模式")

    # 运行仿真
    controller = V5AntiBackflowController(
        params=params,
        initial_load=df['load'].iloc[0],
        process_noise=0.1,
        measurement_noise=1.0
    )

    for idx, row in df.iterrows():
        controller.compute_control(row['load'], row['time'])

    # 获取结果
    history = controller.get_history()

    # 计算指标
    P_cmd = history['P_cmd']
    load = history['load']
    time = history['time']

    # 计算时间间隔
    dt = np.diff(time, prepend=time[0])

    # 1. 负载跟踪率（主要指标）
    load_energy = np.sum(load * dt) / 3600  # kWh
    output_energy = np.sum(P_cmd * dt) / 3600  # kWh
    utilization_rate = (output_energy / load_energy * 100) if load_energy > 0 else 0

    # 3. 逆流次数（P_cmd > load）
    backflow_count = np.sum(P_cmd > load)
    backflow_ratio = (backflow_count / len(P_cmd) * 100) if len(P_cmd) > 0 else 0

    # 4. 最大逆流功率
    backflow_power = np.maximum(P_cmd - load, 0)
    max_backflow = np.max(backflow_power)

    # 5. 响应延迟（P_cmd 跟随 load 的平均延迟）
    # 简化计算：P_cmd 和 load 的相关系数
    correlation = np.corrcoef(P_cmd, load)[0, 1] if len(P_cmd) > 1 else 0

    # 6. Safety bypass 次数
    safety_bypass_count = np.sum(history['safety_bypass'])

    # 7. 平均变化率
    dP_cmd = np.diff(P_cmd)
    dt_diff = np.diff(time)
    dt_diff[dt_diff == 0] = 1.0  # 避免除零
    rates = dP_cmd / dt_diff
    avg_up_rate = np.mean(rates[rates > 0]) if np.any(rates > 0) else 0
    avg_down_rate = np.abs(np.mean(rates[rates < 0])) if np.any(rates < 0) else 0

    metrics = {
        "mode": mode_name,
        "utilization_rate": utilization_rate,
        "backflow_count": int(backflow_count),
        "backflow_ratio": backflow_ratio,
        "max_backflow_kw": max_backflow,
        "correlation": correlation,
        "safety_bypass_count": int(safety_bypass_count),
        "avg_up_rate": avg_up_rate,
        "avg_down_rate": avg_down_rate,
        "avg_P_cmd": np.mean(P_cmd),
        "std_P_cmd": np.std(P_cmd),
    }

    logger.info(f"{mode_name} 模式测试完成")
    logger.info(f"  负载跟踪率: {utilization_rate:.2f}%")
    logger.info(f"  逆流次数: {backflow_count} ({backflow_ratio:.2f}%)")
    logger.info(f"  最大逆流: {max_backflow:.2f} kW")

    return metrics


def create_aggressive_params() -> ControlParams:
    """激进模式参数 - 第6轮：保持最佳平衡点"""
    return ControlParams(
        buffer=4.0,  # 保持4.0
        use_buffer=True,
        use_safety_ceiling=False,  # 不使用安全上界
        R_up=1000.0,
        R_down=1000.0,
        alpha=0.01,  # 保持大alpha
        P_max=500.0,
        enable_dynamic_safety=False,  # 不启用动态安全
        adaptive_safety=False,
    )


def create_balanced_params() -> ControlParams:
    """平衡模式参数 - 第10轮：微调降低逆流到10%以下"""
    return ControlParams(
        buffer=3.5,  # 从3.0增加到3.5
        use_buffer=True,
        use_safety_ceiling=False,  # 保持关闭安全上界
        R_up=1000.0,
        R_down=1000.0,
        alpha=0.01,  # 保持0.01
        P_max=500.0,
        enable_dynamic_safety=False,  # 关闭动态安全
        adaptive_safety=False,
    )


def create_conservative_params() -> ControlParams:
    """保守模式参数 - 第10轮：微调进一步降低逆流"""
    return ControlParams(
        buffer=6.0,  # 从5.0增加到6.0
        use_buffer=True,
        use_safety_ceiling=False,  # 关闭安全上界
        R_up=1000.0,
        R_down=1000.0,
        alpha=0.01,  # 保持0.01
        P_max=500.0,
        enable_dynamic_safety=False,  # 关闭动态安全
        adaptive_safety=False,
    )


def main():
    """主测试函数"""
    print("=" * 80)
    print("自动测试：三种策略模式性能评估")
    print("=" * 80)

    # 生成测试数据
    print("\n[1/4] 生成测试数据...")
    df = generate_sample_data(duration_hours=10)
    print(f"  数据长度: {len(df)} 个时间步")
    print(f"  负载范围: {df['load'].min():.2f} - {df['load'].max():.2f} kW")

    # 定义三种模式
    modes = {
        "激进": create_aggressive_params(),
        "平衡": create_balanced_params(),
        "保守": create_conservative_params(),
    }

    # 运行测试
    results = {}
    for i, (mode_name, params) in enumerate(modes.items(), 2):
        print(f"\n[{i}/4] 测试 {mode_name} 模式...")
        metrics = run_mode_test(mode_name, params, df)
        results[mode_name] = metrics

    # 输出比较报告
    print("\n" + "=" * 80)
    print("性能对比报告")
    print("=" * 80)

    print(f"\n{'指标':<20} {'激进':<15} {'平衡':<15} {'保守':<15}")
    print("-" * 68)

    metrics_to_compare = [
        ("负载跟踪率 (%)", "utilization_rate"),
        ("逆流次数", "backflow_count"),
        ("逆流比例 (%)", "backflow_ratio"),
        ("最大逆流 (kW)", "max_backflow_kw"),
        ("相关系数", "correlation"),
        ("Safety Bypass", "safety_bypass_count"),
        ("平均上调率 (kW/s)", "avg_up_rate"),
        ("平均下调率 (kW/s)", "avg_down_rate"),
    ]

    for label, key in metrics_to_compare:
        values = [results[mode][key] for mode in ["激进", "平衡", "保守"]]
        print(f"{label:<20} {values[0]:<15.2f} {values[1]:<15.2f} {values[2]:<15.2f}")

    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results_{timestamp}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到: {output_file}")
    print("=" * 80)

    return results


if __name__ == "__main__":
    main()
