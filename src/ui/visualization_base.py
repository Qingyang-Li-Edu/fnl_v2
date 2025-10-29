"""
可视化基础配置模块
"""

from src.ui.styles import get_material_colors

colors = get_material_colors()


def apply_chart_theme(fig, height: int = 600):
    """应用统一的图表主题样式"""
    fig.update_layout(
        height=height,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, SF Pro Display, sans-serif",
            size=12,
            color="#1D1D1F"
        ),
        margin=dict(l=60, r=40, t=60, b=60)
    )

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
