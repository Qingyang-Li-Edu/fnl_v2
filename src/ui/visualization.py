"""
可视化模块 - Plotly 图表（优化版）
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from src.ui.styles import get_material_colors
from src.ui.visualization_base import apply_chart_theme, colors


def create_time_series_plot(history: dict, show_stukf: bool = False, show_bounds: bool = True, height: int = 600):
    """创建时间序列对比图"""
    time = history['time']
    load = history['load']
    P_cmd = history['P_cmd']

    fig = go.Figure()

    # 原始负载
    fig.add_trace(go.Scatter(
        x=time, y=load, mode='lines', name='原始负载 L(t)',
        line=dict(color=colors['gray'], width=1.5),
        hovertemplate='<b>负载</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
    ))

    # PV 限发指令
    fig.add_trace(go.Scatter(
        x=time, y=P_cmd, mode='lines', name='PV限发指令 P_cmd',
        line=dict(color=colors['blue'], width=3),
        hovertemplate='<b>PV指令</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
    ))

    # STUKF 预测
    if show_stukf and 'L_med' in history:
        fig.add_trace(go.Scatter(
            x=time, y=history['L_med'], mode='lines', name='STUKF预测均值 L_med',
            line=dict(color=colors['purple'], width=1.5, dash='dash'),
            hovertemplate='<b>预测均值</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=time, y=history['L_lb'], mode='lines', name='STUKF置信下界 L_lb',
            line=dict(color=colors['orange'], width=1.5, dash='dot'),
            hovertemplate='<b>置信下界</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
        ))

    # 安全/性能上界
    if show_bounds and 'U_A' in history:
        fig.add_trace(go.Scatter(
            x=time, y=history['U_A'], mode='lines', name='安全上界 U_A',
            line=dict(color=colors['red'], width=1.2, dash='dash'), opacity=0.6,
            hovertemplate='<b>安全上界</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=time, y=history['U_B'], mode='lines', name='性能上界 U_B',
            line=dict(color=colors['green'], width=1.2, dash='dot'), opacity=0.6,
            hovertemplate='<b>性能上界</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
        ))

    # 安全旁路触发点
    if 'safety_bypass' in history:
        safety_indices = np.where(history['safety_bypass'])[0]
        if len(safety_indices) > 100:
            step = len(safety_indices) // 100
            safety_indices = safety_indices[::step]

        if len(safety_indices) > 0:
            fig.add_trace(go.Scatter(
                x=time[safety_indices], y=P_cmd[safety_indices], mode='markers', name='安全旁路触发',
                marker=dict(color=colors['red'], size=4, symbol='circle', line=dict(width=1, color='white')),
                hovertemplate='<b>安全旁路</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
            ))

    # 应用主题
    fig.update_layout(
        xaxis_title="时间 (秒)",
        yaxis_title="功率 (kW)",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(255, 255, 255, 0.8)")
    )

    return apply_chart_theme(fig, height)


def create_ramp_rate_distribution(history: dict, height: int = 400):
    """创建变化率分布图"""
    P_cmd = history['P_cmd']
    time = history['time']

    dP = np.diff(P_cmd, prepend=P_cmd[0])
    dt = np.diff(time, prepend=time[0])
    dt[dt == 0] = 1.0
    ramp_rates = dP / dt

    up_rates = ramp_rates[ramp_rates > 0]
    down_rates = np.abs(ramp_rates[ramp_rates < 0])

    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.12)

    fig.add_trace(go.Histogram(x=up_rates, nbinsx=50, name='上调速率', marker_color=colors['blue'], opacity=0.7,
                              hovertemplate='速率: %{x:.2f} kW/s<br>频次: %{y}<extra></extra>'), row=1, col=1)

    fig.add_trace(go.Histogram(x=down_rates, nbinsx=50, name='下调速率', marker_color=colors['orange'], opacity=0.7,
                              hovertemplate='速率: %{x:.2f} kW/s<br>频次: %{y}<extra></extra>'), row=1, col=2)

    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text="上调速率 (kW/s)", row=1, col=1)
    fig.update_xaxes(title_text="下调速率 (kW/s)", row=1, col=2)
    fig.update_yaxes(title_text="频次", row=1, col=1)
    fig.update_yaxes(title_text="频次", row=1, col=2)

    return apply_chart_theme(fig, height)


def create_curtailment_analysis(history: dict, P_max: float, height: int = 400):
    """创建光伏容量利用分析图"""
    P_cmd = history['P_cmd']
    time = history['time']

    unused_capacity = np.maximum(P_max - P_cmd, 0)

    fig = make_subplots(rows=1, cols=2,
                       specs=[[{"type": "scatter"}, {"type": "histogram"}]], horizontal_spacing=0.12)

    fig.add_trace(go.Scatter(x=time, y=unused_capacity, mode='lines', name='未利用容量',
                            line=dict(color=colors['orange'], width=2), fill='tozeroy', fillcolor=f'rgba(255, 149, 0, 0.2)',
                            hovertemplate='时间: %{x:.1f}s<br>未利用: %{y:.2f} kW<extra></extra>'), row=1, col=1)

    fig.add_trace(go.Histogram(x=unused_capacity[unused_capacity > 0], nbinsx=50, name='容量分布',
                              marker_color=colors['orange'], opacity=0.7,
                              hovertemplate='未利用: %{x:.2f} kW<br>频次: %{y}<extra></extra>'), row=1, col=2)

    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text="时间 (秒)", row=1, col=1)
    fig.update_xaxes(title_text="未利用容量 (kW)", row=1, col=2)
    fig.update_yaxes(title_text="未利用容量 (kW)", row=1, col=1)
    fig.update_yaxes(title_text="频次", row=1, col=2)

    return apply_chart_theme(fig, height)


def create_control_effectiveness_plot(history: dict, height: int = 500):
    """创建控制效果对比图"""
    time = history['time']
    load = history['load']
    P_cmd = history['P_cmd']
    net_load = load - P_cmd

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=time, y=load, mode='lines', name='原始负载',
                            line=dict(color=colors['gray'], width=1.5),
                            hovertemplate='<b>原始负载</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'))

    fig.add_trace(go.Scatter(x=time, y=P_cmd, mode='lines', name='PV输出',
                            line=dict(color=colors['green'], width=2), fill='tozeroy', fillcolor=f'rgba(52, 199, 89, 0.2)',
                            hovertemplate='<b>PV输出</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'))

    fig.add_trace(go.Scatter(x=time, y=net_load, mode='lines', name='净负载',
                            line=dict(color=colors['blue'], width=2),
                            hovertemplate='<b>净负载</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'))

    fig.add_hline(y=0, line_dash="dash", line_color=colors['red'], annotation_text="逆流临界线", annotation_position="right")

    fig.update_layout(
        xaxis_title="时间 (秒)",
        yaxis_title="功率 (kW)",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(255, 255, 255, 0.8)")
    )

    return apply_chart_theme(fig, height)
