"""
仿真运行模块
"""

import streamlit as st
from src.core import V5AntiBackflowController, ControlParams
import pandas as pd


def run_simulation(df: pd.DataFrame, params: ControlParams) -> V5AntiBackflowController:
    """运行控制仿真"""
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

    return controller
