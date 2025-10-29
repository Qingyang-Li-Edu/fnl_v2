"""
指标卡片组件
"""


def create_metric_card(label: str, value: str, delta: str = None, delta_color: str = "neutral",
                       icon: str = "analytics", icon_color: str = "blue") -> str:
    """创建 Material Design 指标卡片"""
    delta_html = ""
    if delta:
        delta_html = f'<div class="metric-delta {delta_color}">{delta}</div>'

    card_html = f"""
    <div class="metric-card material-fade-in">
        <div class="metric-icon {icon_color}">
            <span class="material-icons">{icon}</span>
        </div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    return card_html
