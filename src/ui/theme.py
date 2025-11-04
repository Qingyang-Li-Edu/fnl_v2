"""
主题管理模块 - 深色/浅色模式
"""


def get_dark_theme_css() -> str:
    """获取深色主题CSS"""
    return """
<style>
/* ===== 深色主题全局强制覆盖 ===== */
/* 最高优先级：覆盖所有inline style */
.stApp,
.stApp *,
.main,
.main *,
body,
body * {
    color: #E8EAED !important;
}

/* 主容器背景 */
.stApp,
.main,
body {
    background: #1E1E1E !important;
}

.main .block-container {
    background: #1E1E1E !important;
}

/* 侧边栏 */
[data-testid="stSidebar"],
[data-testid="stSidebar"] * {
    background-color: #2D2D2D !important;
    color: #E8EAED !important;
}

[data-testid="stSidebar"] {
    border-right-color: #3C3C3C !important;
}

/* 标题 - 强制白色 */
h1, h1 *,
h2, h2 *,
h3, h3 *,
h4, h4 *,
h5, h5 *,
h6, h6 * {
    color: #E8EAED !important;
}

/* 段落和文本 - 强制白色 */
p, p *,
span, span *,
div, div *,
label, label *,
a, a * {
    color: #E8EAED !important;
}

/* 卡片 */
.metric-card {
    background: #2D2D2D !important;
    border-color: #3C3C3C !important;
}

.metric-card * {
    color: #E8EAED !important;
}

.metric-card-featured {
    background: linear-gradient(135deg, rgba(26, 115, 232, 0.15) 0%, rgba(66, 133, 244, 0.2) 100%) !important;
    border-color: rgba(26, 115, 232, 0.3) !important;
}

.metric-card-featured * {
    color: #E8EAED !important;
}

.metric-label,
.metric-value {
    color: #E8EAED !important;
}

/* 输入框 */
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stSelectbox > div > div > select {
    background: #2D2D2D !important;
    color: #E8EAED !important;
    border-color: #3C3C3C !important;
}

/* 按钮 */
.stButton > button {
    background: #1A73E8 !important;
    color: white !important;
}

.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #8AB4F8 !important;
    border-color: #8AB4F8 !important;
}

/* 图表 */
.js-plotly-plot {
    background: #2D2D2D !important;
    border-color: #3C3C3C !important;
}

/* Streamlit Markdown - 强制白色 */
.stMarkdown,
.stMarkdown *,
.stMarkdown p,
.stMarkdown p *,
.stMarkdown span,
.stMarkdown span *,
.stMarkdown div,
.stMarkdown div * {
    color: #E8EAED !important;
}

/* Expander */
.streamlit-expanderHeader,
.streamlit-expanderHeader * {
    background: #2D2D2D !important;
    border-color: #3C3C3C !important;
    color: #E8EAED !important;
}

.streamlit-expanderContent,
.streamlit-expanderContent * {
    background: #2D2D2D !important;
    border-color: #3C3C3C !important;
    color: #E8EAED !important;
}

/* 文件上传器 */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] * {
    background: #2D2D2D !important;
    border-color: #3C3C3C !important;
    color: #E8EAED !important;
}

/* 滚动条 */
::-webkit-scrollbar-track {
    background: #2D2D2D !important;
}

::-webkit-scrollbar-thumb {
    background: #5F6368 !important;
}

/* 所有标签 */
label,
label *,
.stCheckbox label,
.stCheckbox label *,
.stRadio label,
.stRadio label *,
.stSlider label,
.stSlider label * {
    color: #E8EAED !important;
}

/* Caption */
.stCaptionContainer,
.stCaptionContainer *,
.stCaption,
.stCaption * {
    color: rgba(255, 255, 255, 0.60) !important;
}

/* 代码块 */
code,
code *,
pre,
pre * {
    background: #2D2D2D !important;
    color: #E8EAED !important;
    border-color: #3C3C3C !important;
}

/* 加载动画/进度条 */
.stSpinner > div {
    border-top-color: #8AB4F8 !important;
}

.stProgress > div > div {
    background-color: #8AB4F8 !important;
}

/* 应用副标题 - 深色模式 */
.app-subtitle,
.app-subtitle * {
    color: rgba(255, 255, 255, 0.70) !important;
}

/* 视图模式标签 - 深色模式 */
.view-mode-label,
.view-mode-label * {
    color: rgba(255, 255, 255, 0.70) !important;
}

/* Material Icons - 保持可见 */
.material-icons {
    color: #8AB4F8 !important;
}

/* 强制覆盖所有inline style的颜色 */
[style*="color"] {
    color: #E8EAED !important;
}

/* ===== 滑块样式 - 深色模式 ===== */
/* 滑块本身（活动部分） */
.stSlider > div > div > div > div {
    background: #8AB4F8 !important;
}

/* 滑块轨道（背景部分） */
.stSlider > div > div > div {
    background: #3C3C3C !important;
}

/* 滑块把手 */
.stSlider > div > div > div > div > div {
    background: #8AB4F8 !important;
    border-color: #8AB4F8 !important;
}

/* 滑块数值显示 */
.stSlider [data-baseweb="slider"] > div:last-child,
.stSlider [data-testid="stTickBar"],
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"] {
    color: #E8EAED !important;
}

/* ===== 快速预设外部框 - 深色模式 ===== */
/* 覆盖内联样式的渐变背景 */
[data-testid="stSidebar"] [style*="linear-gradient"],
[data-testid="stSidebar"] div[style*="linear-gradient"] {
    background: linear-gradient(135deg, rgba(26, 115, 232, 0.15) 0%, rgba(66, 133, 244, 0.20) 100%) !important;
    border-color: rgba(26, 115, 232, 0.3) !important;
}

/* 主内容区的渐变框 */
.main [style*="linear-gradient"] {
    background: linear-gradient(135deg, rgba(26, 115, 232, 0.12) 0%, rgba(66, 133, 244, 0.18) 100%) !important;
}

/* ===== 选择框 - 深色模式 ===== */
/* 选择框容器 */
.stSelectbox > div > div,
.stSelectbox > div > div > div,
[data-baseweb="select"] {
    background: #2D2D2D !important;
    color: #E8EAED !important;
    border-color: #3C3C3C !important;
}

/* 选择框输入框 */
.stSelectbox input {
    color: #E8EAED !important;
    background: #2D2D2D !important;
}

/* 选择框下拉箭头图标 */
.stSelectbox svg,
[data-baseweb="select"] svg {
    fill: #E8EAED !important;
    stroke: #E8EAED !important;
}

/* 选择框下拉菜单容器 */
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    background: #2D2D2D !important;
    border-color: #3C3C3C !important;
}

/* 选择框选项 */
[data-baseweb="menu"] li,
[role="option"],
ul[role="listbox"] li {
    background: #2D2D2D !important;
    color: #E8EAED !important;
}

/* 选择框选项 hover 状态 */
[data-baseweb="menu"] li:hover,
[role="option"]:hover,
ul[role="listbox"] li:hover {
    background: #3C3C3C !important;
    color: #E8EAED !important;
}

/* 选择框选中的选项 */
[aria-selected="true"],
[role="option"][aria-selected="true"] {
    background: rgba(26, 115, 232, 0.3) !important;
    color: #E8EAED !important;
}

/* 选择框焦点状态 */
.stSelectbox > div > div:focus-within {
    border-color: #8AB4F8 !important;
    box-shadow: 0 0 0 2px rgba(138, 180, 248, 0.2) !important;
}
</style>
"""


def get_theme_toggle_script() -> str:
    """获取主题切换JavaScript脚本"""
    return """
<script>
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    body.setAttribute('data-theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);

    // 保存到localStorage
    localStorage.setItem('theme', newTheme);

    // 更新按钮图标
    const icon = document.querySelector('.theme-toggle .material-icons');
    if (icon) {
        icon.textContent = newTheme === 'dark' ? 'light_mode' : 'dark_mode';
    }
}

// 页面加载时应用保存的主题
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);

    const icon = document.querySelector('.theme-toggle .material-icons');
    if (icon) {
        icon.textContent = savedTheme === 'dark' ? 'light_mode' : 'dark_mode';
    }
});

// Streamlit重新渲染时重新应用主题
const observer = new MutationObserver(function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (document.body.getAttribute('data-theme') !== savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
        document.documentElement.setAttribute('data-theme', savedTheme);
    }
});

observer.observe(document.body, {
    attributes: false,
    childList: true,
    subtree: false
});
</script>
"""


def get_theme_toggle_button() -> str:
    """获取主题切换按钮HTML"""
    return """
<button class="theme-toggle" onclick="toggleTheme()" title="切换主题">
    <span class="material-icons">dark_mode</span>
</button>
"""
