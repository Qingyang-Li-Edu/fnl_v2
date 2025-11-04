"""
指标卡片组件
"""


def create_metric_card(label: str, value: str, delta: str = None, delta_color: str = "neutral",
                       icon: str = "analytics", icon_color: str = "blue", featured: bool = False) -> str:
    """创建 Material Design 指标卡片

    Args:
        label: 标签文字
        value: 数值
        delta: 副文本（可选）
        delta_color: 副文本颜色（positive/negative/neutral）
        icon: Material Icons 图标名称
        icon_color: 图标颜色（blue/green/red/orange）
        featured: 是否为重点卡片（添加渐变背景）
    """
    delta_html = ""
    if delta:
        delta_html = f'<div class="metric-delta {delta_color}">{delta}</div>'

    # 为重点卡片添加特殊样式
    card_class = "metric-card-featured" if featured else "metric-card"

    card_html = f"""
    <div class="{card_class} material-fade-in">
        <div class="metric-icon {icon_color}">
            <span class="material-icons">{icon}</span>
        </div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    return card_html
