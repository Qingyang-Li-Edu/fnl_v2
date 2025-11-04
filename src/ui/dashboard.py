"""
仪表盘模式 - 大号指标展示
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.ui.visualization_base import apply_chart_theme


def create_gauge_chart(value: float, title: str, max_value: float = 100,
                       color_ranges: list = None, unit: str = "%") -> go.Figure:
    """创建单个仪表盘图表

    Args:
        value: 当前值
        title: 标题
        max_value: 最大值
        color_ranges: 颜色范围 [(threshold, color), ...]
        unit: 单位
    """
    if color_ranges is None:
        # 默认颜色范围
        color_ranges = [
            (max_value * 0.5, "#34A853"),  # 绿色
            (max_value * 0.8, "#F9AB00"),  # 黄色
            (max_value, "#EA4335")         # 红色
        ]

    # 创建颜色步骤
    steps = []
    prev_threshold = 0
    for threshold, color in color_ranges:
        steps.append({
            'range': [prev_threshold, threshold],
            'color': color
        })
        prev_threshold = threshold

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': title,
            'font': {'size': 24, 'color': '#202124', 'family': 'Roboto'}
        },
        number={
            'font': {'size': 56, 'color': '#202124', 'family': 'Roboto'},
            'suffix': unit
        },
        gauge={
            'axis': {
                'range': [None, max_value],
                'tickwidth': 2,
                'tickcolor': "#DADCE0",
                'tickfont': {'size': 16, 'color': '#5F6368'}
            },
            'bar': {'color': "#1A73E8", 'thickness': 0.8},
            'bgcolor': "white",
            'borderwidth': 3,
            'bordercolor': "#DADCE0",
            'steps': steps,
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=80, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#202124", 'family': "Roboto"}
    )

    return fig


def create_dashboard_view(metrics: dict) -> dict:
    """创建仪表盘视图

    Args:
        metrics: 性能指标字典

    Returns:
        包含多个仪表盘图表的字典
    """
    dashboards = {}

    # 弃光率仪表盘（最重要）
    curtailment_rate = metrics['curtailment_rate']
    curtailment_color_ranges = [
        (5.0, "#34A853"),    # <5%: 绿色（优秀）
        (10.0, "#F9AB00"),   # 5-10%: 黄色（警告）
        (100.0, "#EA4335")   # >10%: 红色（严重）
    ]
    dashboards['curtailment_rate'] = create_gauge_chart(
        value=curtailment_rate,
        title="弃光率",
        max_value=20.0,
        color_ranges=curtailment_color_ranges,
        unit="%"
    )

    # 最大弃光功率仪表盘
    max_curtailment_kw = metrics['max_curtailment_kw']
    dashboards['max_curtailment'] = create_gauge_chart(
        value=max_curtailment_kw,
        title="最大弃光功率",
        max_value=100.0,
        unit=" kW"
    )

    # 安全旁路次数仪表盘
    safety_bypass_count = metrics['safety_bypass_count']
    bypass_color_ranges = [
        (0, "#34A853"),      # 0次: 绿色
        (10, "#F9AB00"),     # 1-10次: 黄色
        (100, "#EA4335")     # >10次: 红色
    ]
    dashboards['safety_bypass'] = create_gauge_chart(
        value=safety_bypass_count,
        title="安全旁路次数",
        max_value=max(safety_bypass_count * 2, 10),
        color_ranges=bypass_color_ranges,
        unit=" 次"
    )

    # 平均上调速率仪表盘
    avg_up_rate = metrics['avg_up_rate']
    dashboards['avg_up_rate'] = create_gauge_chart(
        value=avg_up_rate,
        title="平均上调速率",
        max_value=20.0,
        unit=" kW/s"
    )

    return dashboards


def create_compact_gauge(value: float, title: str, max_value: float,
                        color: str = "#1A73E8") -> str:
    """创建紧凑型HTML仪表盘（用于卡片内嵌）

    Args:
        value: 当前值
        title: 标题
        max_value: 最大值
        color: 颜色

    Returns:
        HTML字符串
    """
    percentage = min((value / max_value) * 100, 100)

    html = f"""
    <div style="text-align: center; padding: 20px;">
        <div style="font-size: 14px; color: #5F6368; margin-bottom: 10px; font-weight: 500;">
            {title}
        </div>
        <div style="position: relative; width: 120px; height: 120px; margin: 0 auto;">
            <svg width="120" height="120" style="transform: rotate(-90deg);">
                <circle cx="60" cy="60" r="50" fill="none"
                        stroke="#E8EAED" stroke-width="10"/>
                <circle cx="60" cy="60" r="50" fill="none"
                        stroke="{color}" stroke-width="10"
                        stroke-dasharray="{percentage * 3.14}, 314"
                        stroke-linecap="round"/>
            </svg>
            <div style="position: absolute; top: 50%; left: 50%;
                        transform: translate(-50%, -50%);
                        font-size: 24px; font-weight: 600; color: #202124;">
                {value:.1f}
            </div>
        </div>
        <div style="font-size: 12px; color: #5F6368; margin-top: 10px;">
            / {max_value}
        </div>
    </div>
    """
    return html
