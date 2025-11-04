"""
可视化基础配置模块
"""

from src.ui.styles import get_material_colors

colors = get_material_colors()


def apply_chart_theme(fig, height: int = 600, enable_fullscreen: bool = True):
    """应用统一的图表主题样式

    Args:
        fig: Plotly图表对象
        height: 图表高度
        enable_fullscreen: 是否启用全屏按钮
    """
    # 配置modebar按钮
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToAdd': ['toImage'] if enable_fullscreen else [],
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'chart',
            'height': 1080,
            'width': 1920,
            'scale': 2
        }
    }

    fig.update_layout(
        height=height,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Roboto, -apple-system, BlinkMacSystemFont, sans-serif",
            size=13,
            color="#202124"
        ),
        margin=dict(l=70, r=50, t=70, b=70),
        title_font=dict(size=18, color="#202124", family="Roboto"),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Roboto",
            bordercolor="#DADCE0"
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='#E8EAED',
        showline=True,
        linewidth=1.5,
        linecolor='#DADCE0',
        zeroline=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='#E8EAED',
        showline=True,
        linewidth=1.5,
        linecolor='#DADCE0',
        zeroline=False
    )

    # 为fig添加config属性（用于Streamlit）
    fig._config = config

    return fig
