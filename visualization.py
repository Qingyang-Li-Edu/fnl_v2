"""
可视化模块 - Plotly 图表
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from material_styles import get_material_colors

colors = get_material_colors()


def create_time_series_plot(history: dict, show_stukf: bool = False, show_bounds: bool = True, height: int = 600):
    """
    创建时间序列对比图

    参数:
        history: 历史数据字典
        show_stukf: 是否显示 STUKF 预测
        show_bounds: 是否显示安全/性能上界
        height: 图表高度
    """
    time = history['time']
    load = history['load']
    P_cmd = history['P_cmd']

    # 创建图表
    fig = go.Figure()

    # 1. 原始负载（细线，灰色）
    fig.add_trace(go.Scatter(
        x=time,
        y=load,
        mode='lines',
        name='原始负载 L(t)',
        line=dict(color=colors['gray'], width=1.5),
        hovertemplate='<b>负载</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
    ))

    # 2. PV 限发指令（粗线，主色调）
    fig.add_trace(go.Scatter(
        x=time,
        y=P_cmd,
        mode='lines',
        name='PV限发指令 P_cmd',
        line=dict(color=colors['blue'], width=3),
        hovertemplate='<b>PV指令</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
    ))

    # 3. STUKF 预测（可选）
    if show_stukf and 'L_med' in history:
        # 预测均值
        fig.add_trace(go.Scatter(
            x=time,
            y=history['L_med'],
            mode='lines',
            name='STUKF预测均值 L_med',
            line=dict(color=colors['purple'], width=1.5, dash='dash'),
            hovertemplate='<b>预测均值</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
        ))

        # 预测下界
        fig.add_trace(go.Scatter(
            x=time,
            y=history['L_lb'],
            mode='lines',
            name='STUKF置信下界 L_lb',
            line=dict(color=colors['orange'], width=1.5, dash='dot'),
            hovertemplate='<b>置信下界</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
        ))

    # 4. 安全/性能上界（可选）
    if show_bounds and 'U_A' in history and 'U_B' in history:
        # 安全上界
        fig.add_trace(go.Scatter(
            x=time,
            y=history['U_A'],
            mode='lines',
            name='安全上界 U_A',
            line=dict(color=colors['red'], width=1.2, dash='dash'),
            opacity=0.6,
            hovertemplate='<b>安全上界</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
        ))

        # 性能上界
        fig.add_trace(go.Scatter(
            x=time,
            y=history['U_B'],
            mode='lines',
            name='性能上界 U_B',
            line=dict(color=colors['green'], width=1.2, dash='dot'),
            opacity=0.6,
            hovertemplate='<b>性能上界</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
        ))

    # 5. 标记安全旁路触发点
    if 'safety_bypass' in history:
        safety_indices = np.where(history['safety_bypass'])[0]
        if len(safety_indices) > 0:
            # 如果点太多，进行采样显示（最多显示100个点）
            if len(safety_indices) > 100:
                # 均匀采样
                step = len(safety_indices) // 100
                safety_indices = safety_indices[::step]

            fig.add_trace(go.Scatter(
                x=time[safety_indices],
                y=P_cmd[safety_indices],
                mode='markers',
                name='安全旁路触发',
                marker=dict(
                    color=colors['red'],
                    size=4,  # 减小点的大小
                    symbol='circle',  # 改用圆形
                    line=dict(width=1, color='white')  # 白色边框，增加对比
                ),
                hovertemplate='<b>安全旁路</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
            ))

    # 布局设置
    fig.update_layout(
        height=height,
        xaxis_title="时间 (秒)",
        yaxis_title="功率 (kW)",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255, 255, 255, 0.8)"
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, SF Pro Display, sans-serif",
            size=12,
            color="#1D1D1F"
        ),
        margin=dict(l=60, r=40, t=60, b=60)
    )

    # 网格样式
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='#E5E5E7',
        showline=True,
        linewidth=1,
        linecolor='#D2D2D7'
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='#E5E5E7',
        showline=True,
        linewidth=1,
        linecolor='#D2D2D7'
    )

    return fig


def create_ramp_rate_distribution(history: dict, height: int = 400):
    """
    创建变化率分布图

    参数:
        history: 历史数据字典
        height: 图表高度
    """
    P_cmd = history['P_cmd']
    time = history['time']

    # 计算变化率
    dP = np.diff(P_cmd, prepend=P_cmd[0])
    dt = np.diff(time, prepend=time[0])
    dt[dt == 0] = 1.0  # 避免除零
    ramp_rates = dP / dt

    # 分离上调和下调
    up_rates = ramp_rates[ramp_rates > 0]
    down_rates = np.abs(ramp_rates[ramp_rates < 0])

    # 创建子图
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('上调速率分布', '下调速率分布'),
        horizontal_spacing=0.12
    )

    # 上调速率直方图
    fig.add_trace(
        go.Histogram(
            x=up_rates,
            nbinsx=50,
            name='上调速率',
            marker_color=colors['blue'],
            opacity=0.7,
            hovertemplate='速率: %{x:.2f} kW/s<br>频次: %{y}<extra></extra>'
        ),
        row=1, col=1
    )

    # 下调速率直方图
    fig.add_trace(
        go.Histogram(
            x=down_rates,
            nbinsx=50,
            name='下调速率',
            marker_color=colors['orange'],
            opacity=0.7,
            hovertemplate='速率: %{x:.2f} kW/s<br>频次: %{y}<extra></extra>'
        ),
        row=1, col=2
    )

    # 布局
    fig.update_layout(
        height=height,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, SF Pro Display, sans-serif",
            size=12,
            color="#1D1D1F"
        ),
        margin=dict(l=60, r=40, t=60, b=60)
    )

    # 更新坐标轴
    fig.update_xaxes(title_text="速率 (kW/s)", row=1, col=1, showgrid=True, gridcolor='#E5E5E7')
    fig.update_xaxes(title_text="速率 (kW/s)", row=1, col=2, showgrid=True, gridcolor='#E5E5E7')
    fig.update_yaxes(title_text="频次", row=1, col=1, showgrid=True, gridcolor='#E5E5E7')
    fig.update_yaxes(title_text="频次", row=1, col=2, showgrid=True, gridcolor='#E5E5E7')

    return fig


def create_curtailment_analysis(history: dict, P_max: float, height: int = 400):
    """
    创建弃光分析图

    参数:
        history: 历史数据字典
        P_max: 最大功率
        height: 图表高度
    """
    P_cmd = history['P_cmd']
    time = history['time']

    # 计算弃光功率
    curtailment = P_max - P_cmd
    curtailment = np.maximum(curtailment, 0)  # 只考虑正值

    # 创建子图
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('弃光功率时间序列', '弃光功率分布'),
        specs=[[{"type": "scatter"}, {"type": "histogram"}]],
        horizontal_spacing=0.12
    )

    # 弃光功率时间序列
    fig.add_trace(
        go.Scatter(
            x=time,
            y=curtailment,
            mode='lines',
            name='弃光功率',
            line=dict(color=colors['red'], width=2),
            fill='tozeroy',
            fillcolor=f'rgba(255, 59, 48, 0.2)',
            hovertemplate='时间: %{x:.1f}s<br>弃光: %{y:.2f} kW<extra></extra>'
        ),
        row=1, col=1
    )

    # 弃光功率分布直方图
    fig.add_trace(
        go.Histogram(
            x=curtailment[curtailment > 0],  # 只显示非零弃光
            nbinsx=50,
            name='弃光分布',
            marker_color=colors['red'],
            opacity=0.7,
            hovertemplate='弃光: %{x:.2f} kW<br>频次: %{y}<extra></extra>'
        ),
        row=1, col=2
    )

    # 布局
    fig.update_layout(
        height=height,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, SF Pro Display, sans-serif",
            size=12,
            color="#1D1D1F"
        ),
        margin=dict(l=60, r=40, t=60, b=60)
    )

    # 更新坐标轴
    fig.update_xaxes(title_text="时间 (秒)", row=1, col=1, showgrid=True, gridcolor='#E5E5E7')
    fig.update_xaxes(title_text="弃光功率 (kW)", row=1, col=2, showgrid=True, gridcolor='#E5E5E7')
    fig.update_yaxes(title_text="弃光功率 (kW)", row=1, col=1, showgrid=True, gridcolor='#E5E5E7')
    fig.update_yaxes(title_text="频次", row=1, col=2, showgrid=True, gridcolor='#E5E5E7')

    return fig


def create_control_effectiveness_plot(history: dict, height: int = 500):
    """
    创建控制效果对比图（原始负载 vs PV指令 vs 净负载）

    参数:
        history: 历史数据字典
        height: 图表高度
    """
    time = history['time']
    load = history['load']
    P_cmd = history['P_cmd']

    # 计算净负载（负载 - PV输出）
    net_load = load - P_cmd

    fig = go.Figure()

    # 原始负载
    fig.add_trace(go.Scatter(
        x=time,
        y=load,
        mode='lines',
        name='原始负载',
        line=dict(color=colors['gray'], width=1.5),
        hovertemplate='<b>原始负载</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
    ))

    # PV 输出
    fig.add_trace(go.Scatter(
        x=time,
        y=P_cmd,
        mode='lines',
        name='PV输出',
        line=dict(color=colors['green'], width=2),
        fill='tozeroy',
        fillcolor=f'rgba(52, 199, 89, 0.2)',
        hovertemplate='<b>PV输出</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
    ))

    # 净负载
    fig.add_trace(go.Scatter(
        x=time,
        y=net_load,
        mode='lines',
        name='净负载',
        line=dict(color=colors['blue'], width=2),
        hovertemplate='<b>净负载</b><br>时间: %{x:.1f}s<br>功率: %{y:.2f} kW<extra></extra>'
    ))

    # 零线（参考）
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color=colors['red'],
        annotation_text="逆流临界线",
        annotation_position="right"
    )

    # 布局
    fig.update_layout(
        height=height,
        xaxis_title="时间 (秒)",
        yaxis_title="功率 (kW)",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255, 255, 255, 0.8)"
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, SF Pro Display, sans-serif",
            size=12,
            color="#1D1D1F"
        ),
        margin=dict(l=60, r=40, t=60, b=60)
    )

    # 网格样式
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E7')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E7')

    return fig
