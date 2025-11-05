"""
仿真运行模块
"""

import streamlit as st
from src.core import V5AntiBackflowController, ControlParams
from src.utils.logging_config import setup_logger
import pandas as pd


def run_simulation(df: pd.DataFrame, params: ControlParams) -> V5AntiBackflowController:
    """运行控制仿真"""
    # 初始化日志系统
    logger = setup_logger("v5_anti_backflow")
    logger.info("开始运行仿真")
    logger.info(f"数据长度: {len(df)} 个时间步")
    logger.info(f"控制参数: use_safety_ceiling={params.use_safety_ceiling}, "
               f"use_buffer={params.use_buffer}, alpha={params.alpha}")

    controller = V5AntiBackflowController(
        params=params,
        initial_load=df['load'].iloc[0],
        process_noise=0.1,
        measurement_noise=1.0
    )

    # 添加进度条
    progress_bar = st.progress(0)
    status_text = st.empty()

    total_steps = len(df)
    for idx, row in df.iterrows():
        controller.compute_control(row['load'], row['time'])

        # 更新进度
        if idx % max(1, total_steps // 100) == 0:
            progress = int((idx + 1) / total_steps * 100)
            progress_bar.progress(progress)
            status_text.text(f"仿真进度: {progress}%")

    progress_bar.empty()
    status_text.empty()

    # 记录仿真完成信息
    history = controller.get_history()
    logger.info("仿真完成")
    logger.info(f"平均PV限发指令: {history['P_cmd'].mean():.2f}kW")
    logger.info(f"最大PV限发指令: {history['P_cmd'].max():.2f}kW")
    logger.info(f"PV限发指令为0的次数: {(history['P_cmd'] == 0).sum()}/{len(history['P_cmd'])}")

    return controller
