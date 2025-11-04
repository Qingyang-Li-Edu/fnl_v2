"""
Google Material Design styling for Streamlit
参考 Google Material Design 设计语言的 CSS 样式
"""

MATERIAL_STYLE_CSS = """
<style>
/* ===== Google Material Icons 导入 ===== */
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

:root {
    /* Google Material Design 调色板 */
    --md-blue-primary: #1A73E8;
    --md-blue-dark: #1557B0;
    --md-blue-light: #4285F4;
    --md-green: #0F9D58;
    --md-green-light: #34A853;
    --md-yellow: #F9AB00;
    --md-red: #EA4335;
    --md-purple: #9334E6;
    --md-teal: #00897B;
    --md-orange: #FA7B17;

    /* 灰度色阶 */
    --md-gray-50: #FAFAFA;
    --md-gray-100: #F5F5F5;
    --md-gray-200: #EEEEEE;
    --md-gray-300: #E0E0E0;
    --md-gray-400: #BDBDBD;
    --md-gray-500: #9E9E9E;
    --md-gray-600: #757575;
    --md-gray-700: #616161;
    --md-gray-800: #424242;
    --md-gray-900: #212121;

    /* 背景色 */
    --bg-primary: #FFFFFF;
    --bg-secondary: #F8F9FA;
    --bg-tertiary: #F1F3F4;

    /* 文字颜色 */
    --text-primary: rgba(0, 0, 0, 0.87);
    --text-secondary: rgba(0, 0, 0, 0.60);
    --text-disabled: rgba(0, 0, 0, 0.38);

    /* 边框 */
    --border-color: #DADCE0;
    --divider-color: #E8EAED;

    /* Material Design 阴影 */
    --shadow-1: 0 1px 2px 0 rgba(60,64,67,0.30), 0 1px 3px 1px rgba(60,64,67,0.15);
    --shadow-2: 0 1px 2px 0 rgba(60,64,67,0.30), 0 2px 6px 2px rgba(60,64,67,0.15);
    --shadow-3: 0 4px 8px 3px rgba(60,64,67,0.15), 0 1px 3px rgba(60,64,67,0.30);
    --shadow-4: 0 6px 10px 4px rgba(60,64,67,0.15), 0 2px 3px rgba(60,64,67,0.30);

    /* 圆角 */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;
}

/* ===== Material Icons 样式 ===== */
.material-icons {
    font-family: 'Material Icons';
    font-weight: normal;
    font-style: normal;
    font-size: 24px;
    display: inline-block;
    line-height: 1;
    text-transform: none;
    letter-spacing: normal;
    word-wrap: normal;
    white-space: nowrap;
    direction: ltr;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
    vertical-align: middle;
}

/* ===== 主容器样式 ===== */
.stApp {
    background: #FFFFFF;
    font-family: 'Roboto', -apple-system, sans-serif;
}

/* ===== 主内容区域 ===== */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1280px;
    background: #FFFFFF;
}

/* ===== 侧边栏样式 ===== */
[data-testid="stSidebar"] {
    background: var(--bg-primary);
    border-right: 1px solid var(--border-color);
    box-shadow: var(--shadow-1);
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1rem;
}

/* 侧边栏标题 */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--text-primary);
    font-weight: 500;
    margin-bottom: 1.5rem;  /* 增加标题下方间距 */
}

/* 侧边栏间距优化 */
[data-testid="stSidebar"] .stCheckbox,
[data-testid="stSidebar"] .stNumberInput,
[data-testid="stSidebar"] .stSlider,
[data-testid="stSidebar"] .stSelectbox {
    margin-bottom: 1.25rem;  /* 增加组件之间的间距 */
}

/* 侧边栏分组卡片 */
[data-testid="stSidebar"] .element-container {
    position: relative;
}

/* 为分隔线后的第一组元素添加背景卡片效果 */
[data-testid="stSidebar"] hr + div {
    background: rgba(26, 115, 232, 0.04);
    border-radius: var(--radius-md);
    padding: 16px;
    margin: 12px 0;
    border: 1px solid rgba(26, 115, 232, 0.1);
}

/* ===== 固定的侧边栏切换按钮 ===== */
.sidebar-toggle {
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 999999;
    background: var(--md-blue-primary);
    color: white;
    border: none;
    border-radius: 50%;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: var(--shadow-3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-toggle:hover {
    background: var(--md-blue-dark);
    box-shadow: var(--shadow-4);
    transform: scale(1.05);
}

.sidebar-toggle:active {
    transform: scale(0.95);
}

/* ===== 标题样式 ===== */
h1 {
    font-size: 2.5rem;  /* 40px - 主标题加大 */
    font-weight: 500;   /* 加粗 */
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    line-height: 1.2;
}

h2 {
    font-size: 1.75rem;  /* 28px - 区域标题 */
    font-weight: 500;
    color: var(--text-primary);
    margin-top: 2rem;
    margin-bottom: 1.25rem;
}

h3 {
    font-size: 1.5rem;  /* 24px - 子标题 */
    font-weight: 500;
    color: var(--text-primary);
    margin-top: 1.5rem;
    margin-bottom: 1rem;
}

/* ===== 文本样式 ===== */
p {
    font-size: 1rem;
    line-height: 1.6;
    color: var(--text-primary);
    margin-bottom: 1rem;
}

/* 应用副标题 */
.app-subtitle {
    margin-top: 0;
    margin-bottom: 1rem;
    color: var(--text-secondary);
    font-size: 1.125rem;
    line-height: 1.6;
}

/* 视图模式标签 */
.view-mode-label {
    padding: 10px;
    text-align: center;
    font-size: 14px;
    color: var(--text-secondary);
}

/* ===== 确保所有文本都有足够的对比度 ===== */
.stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
    color: var(--text-primary) !important;
    font-size: 1rem !important;
}

.stMarkdown h3 {
    font-size: 1.25rem !important;
    font-weight: 500 !important;
}

.stMarkdown strong, .stMarkdown b {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}

/* 列表文本 */
li {
    font-size: 1rem;
    line-height: 1.6;
    color: var(--text-primary) !important;
}

/* 代码块 */
code {
    font-size: 0.9rem;
    color: #202124 !important;
    background: #F1F3F4 !important;
    padding: 2px 6px;
    border-radius: 3px;
}

/* 预格式化文本块 */
pre {
    background: #F1F3F4 !important;
    color: #202124 !important;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #E8EAED;
}

pre code {
    background: transparent !important;
}

/* Caption文本 */
.stCaptionContainer, .stCaption {
    color: var(--text-secondary) !important;
    font-size: 0.875rem !important;
}

/* ===== Material Design 按钮样式 ===== */
/* Primary 按钮 - 主要操作 */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: var(--md-blue-primary);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    padding: 16px 32px;  /* 主按钮更大 */
    font-size: 1.125rem;  /* 18px - 主按钮文字更大 */
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.0892857143em;
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: var(--shadow-2);
    min-height: 56px;  /* 主按钮最高 */
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: var(--md-blue-dark);
    box-shadow: var(--shadow-4);
    transform: translateY(-2px);
}

/* Secondary 按钮 - 次要操作 */
.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"] {
    background: transparent;
    color: var(--md-blue-primary);
    border: 2px solid var(--md-blue-primary);
    border-radius: var(--radius-md);
    padding: 12px 24px;
    font-size: 1rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.0892857143em;
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: none;
    min-height: 48px;
}

.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover {
    background: rgba(26, 115, 232, 0.08);
    border-color: var(--md-blue-dark);
    color: var(--md-blue-dark);
}

/* Tertiary/Text 按钮 - 辅助操作 */
.stButton > button[kind="tertiary"],
.stButton > button:not([kind]) {
    background: transparent;
    color: var(--md-blue-primary);
    border: none;
    border-radius: var(--radius-md);
    padding: 10px 20px;
    font-size: 0.9375rem;  /* 15px */
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.0892857143em;
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: none;
    min-height: 40px;
}

.stButton > button[kind="tertiary"]:hover,
.stButton > button:not([kind]):hover {
    background: rgba(26, 115, 232, 0.08);
    transform: none;
}

/* 默认按钮（如果没有特殊指定） */
.stButton > button {
    background: var(--md-blue-primary);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    padding: 14px 28px;
    font-size: 1rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.0892857143em;
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: var(--shadow-2);
    min-height: 48px;
}

.stButton > button:hover {
    background: var(--md-blue-dark);
    box-shadow: var(--shadow-3);
    transform: translateY(-2px);
}

.stButton > button:active {
    box-shadow: var(--shadow-4);
    transform: translateY(0);
}

/* ===== 输入控件样式 ===== */
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stSelectbox > div > div > select {
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 12px 16px;
    font-size: 1.1rem;
    background: var(--bg-primary);
    color: var(--text-primary);
    transition: all 0.2s ease;
}

/* 输入框标签 */
.stNumberInput label, .stTextInput label, .stSelectbox label, .stSlider label {
    font-size: 1.125rem !important;  /* 18px - 增大标签字体 */
    font-weight: 500 !important;
    color: var(--text-primary) !important;
    margin-bottom: 0.5rem !important;
}

.stNumberInput > div > div > input:focus,
.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus {
    border-color: var(--md-blue-primary);
    outline: none;
    box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.2);
}

/* ===== 滑块样式 ===== */
.stSlider > div > div > div > div {
    background: var(--md-blue-primary);
}

.stSlider > div > div > div {
    background: var(--md-gray-300);
}

/* ===== 自定义 Material Design 指标卡片 ===== */
.metric-card {
    background: var(--bg-primary);
    border-radius: var(--radius-lg);  /* 增大圆角 */
    padding: 20px;  /* 增大内边距 */
    box-shadow: var(--shadow-2);  /* 加强阴影 */
    border: 1px solid var(--border-color);
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    display: flex;
    flex-direction: column;
}

.metric-card:hover {
    box-shadow: var(--shadow-4);  /* 悬停时更强的阴影 */
    transform: translateY(-4px);  /* 更明显的上移效果 */
}

/* 重点卡片 - 渐变背景 */
.metric-card-featured {
    background: linear-gradient(135deg, rgba(26, 115, 232, 0.05) 0%, rgba(66, 133, 244, 0.08) 100%);
    border-radius: var(--radius-lg);
    padding: 24px;  /* 更大的内边距 */
    box-shadow: var(--shadow-3);  /* 更强的初始阴影 */
    border: 2px solid rgba(26, 115, 232, 0.2);  /* 彩色边框 */
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
}

/* 重点卡片添加光效 */
.metric-card-featured::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.metric-card-featured:hover::before {
    opacity: 1;
}

.metric-card-featured:hover {
    box-shadow: 0 8px 24px rgba(26, 115, 232, 0.25);
    transform: translateY(-6px) scale(1.02);  /* 更明显的悬停效果 */
    border-color: rgba(26, 115, 232, 0.4);
}

.metric-icon {
    width: 48px;  /* 增大图标容器 */
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;  /* 增加下方间距 */
}

.metric-icon .material-icons {
    font-size: 28px;  /* 增大图标大小 */
}

.metric-icon.blue {
    background: rgba(26, 115, 232, 0.1);
    color: var(--md-blue-primary);
}

.metric-icon.green {
    background: rgba(15, 157, 88, 0.1);
    color: var(--md-green);
}

.metric-icon.red {
    background: rgba(234, 67, 53, 0.1);
    color: var(--md-red);
}

.metric-icon.orange {
    background: rgba(249, 171, 0, 0.1);
    color: var(--md-yellow);
}

.metric-label {
    font-size: 1rem;  /* 16px - 保持标签字体适中 */
    font-weight: 600;  /* 加粗 */
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 12px;  /* 增加下方间距 */
}

.metric-value {
    font-size: 2.75rem;  /* 44px - 显著增大数值字体！ */
    font-weight: 600;  /* 加粗数值 */
    color: var(--text-primary);
    margin-bottom: 8px;
    line-height: 1;
}

/* 数值滚动动画 */
@keyframes countUp {
    from {
        opacity: 0;
        transform: translateY(20px) scale(0.8);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.metric-value {
    animation: countUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

/* 重点卡片的数值更醒目 */
.metric-card-featured .metric-value {
    font-size: 3rem;  /* 48px - 重点卡片数值更大！ */
    color: var(--md-blue-primary);
    text-shadow: 0 2px 4px rgba(26, 115, 232, 0.1);
    animation: countUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.metric-delta {
    font-size: 1.125rem;  /* 18px - 略微增大 */
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 4px;
    color: var(--text-primary);
}

.metric-delta.positive {
    color: var(--md-green);
}

.metric-delta.negative {
    color: var(--md-red);
}

.metric-delta.neutral {
    color: var(--text-secondary);
}

/* ===== 文件上传器样式 ===== */
[data-testid="stFileUploader"] {
    background: var(--bg-primary);
    border: 2px dashed var(--border-color);
    border-radius: var(--radius-md);
    padding: 24px;
    transition: all 0.2s ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--md-blue-primary);
    background: rgba(26, 115, 232, 0.04);
}

/* ===== Expander 样式 ===== */
.streamlit-expanderHeader {
    background: #FFFFFF !important;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-color);
    font-weight: 500;
    color: #202124 !important;
    padding: 12px 16px;
    transition: all 0.2s ease;
}

.streamlit-expanderHeader:hover {
    background: #F8F9FA !important;
    border-color: var(--md-blue-primary);
}

.streamlit-expanderHeader svg {
    fill: #202124 !important;
}

/* Expander内容区域 */
.streamlit-expanderContent {
    background: #FFFFFF !important;
    border: 1px solid var(--border-color);
    border-top: none;
    padding: 16px;
}

/* ===== 复选框样式 ===== */
.stCheckbox {
    font-size: 1.125rem;  /* 18px - 增大字体 */
    color: var(--text-primary);
}

.stCheckbox label {
    font-size: 1.125rem !important;  /* 18px - 与其他标签一致 */
    font-weight: 500 !important;
    color: var(--text-primary) !important;
}

.stCheckbox > label > div {
    padding-top: 4px;  /* 增加垂直间距 */
    padding-bottom: 4px;
}

/* ===== 确保所有 Streamlit 组件的文本颜色 ===== */
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stSlider label, .stRadio label, .stCheckbox label,
.stFileUploader label, .stDateInput label, .stTimeInput label {
    color: var(--text-primary) !important;
    font-size: 1rem !important;
}

/* ===== 按钮文本 ===== */
.stButton > button {
    font-size: 1rem !important;
}

/* ===== Plotly 图表容器样式 ===== */
.js-plotly-plot {
    border-radius: var(--radius-md);
    overflow: hidden;
    background: var(--bg-primary);
    box-shadow: var(--shadow-1);
    border: 1px solid var(--border-color);
}

/* ===== 分隔线样式 ===== */
hr {
    border: none;
    border-top: 1px solid var(--divider-color);
    margin: 1.5rem 0;
}

/* ===== 列间距调整 ===== */
[data-testid="column"] {
    padding: 0 12px;  /* 增加列间距 */
}

/* 第一列左对齐，最后一列右对齐 */
[data-testid="column"]:first-child {
    padding-left: 0;
}

[data-testid="column"]:last-child {
    padding-right: 0;
}

/* ===== 加载动画 ===== */
.stSpinner > div {
    border-top-color: var(--md-blue-primary) !important;
}

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {
    h1 {
        font-size: 1.75rem;
    }

    h2 {
        font-size: 1.25rem;
    }

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    .metric-card {
        padding: 12px;
    }

    .metric-value {
        font-size: 1.5rem;
    }
}

/* ===== 隐藏默认元素 ===== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* ===== 确保侧边栏切换按钮始终可见 ===== */
[data-testid="collapsedControl"] {
    display: flex !important;
    position: fixed !important;
    top: 1rem !important;
    left: 1rem !important;
    z-index: 999999 !important;
    background: #FFFFFF !important;
    color: #000000 !important;
    border-radius: 50% !important;
    width: 48px !important;
    height: 48px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
    border: 2px solid #000000 !important;
}

[data-testid="collapsedControl"]:hover {
    background: #F8F9FA !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
}

[data-testid="collapsedControl"] svg {
    fill: #000000 !important;
    stroke: #000000 !important;
}

/* ===== Expander折叠按钮（高级参数等） ===== */
.streamlit-expanderHeader svg {
    fill: #000000 !important;
    stroke: #000000 !important;
}

.streamlit-expanderHeader button {
    color: #000000 !important;
}

.streamlit-expanderHeader button svg {
    fill: #000000 !important;
    stroke: #000000 !important;
}

/* 确保所有展开/折叠图标都是黑色 */
summary svg, details svg {
    fill: #000000 !important;
    stroke: #000000 !important;
}

[data-testid="stExpanderToggleIcon"] svg {
    fill: #000000 !important;
    stroke: #000000 !important;
}

/* ===== 自定义滚动条 ===== */
::-webkit-scrollbar {
    width: 12px;
    height: 12px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--md-gray-400);
    border-radius: 6px;
    border: 3px solid var(--bg-secondary);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--md-gray-500);
}

/* ===== Material Design 动画 ===== */
@keyframes materialFadeIn {
    from {
        opacity: 0;
        transform: translateY(8px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.material-fade-in {
    animation: materialFadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ===== 提示框样式 ===== */
.stAlert {
    border-radius: var(--radius-md);
    border-left: 4px solid var(--md-blue-primary);
    box-shadow: var(--shadow-1);
}
</style>
"""


def get_material_colors():
    """返回 Google Material Design 调色板用于图表"""
    return {
        'blue': '#1A73E8',
        'blue_light': '#4285F4',
        'green': '#34A853',
        'green_dark': '#0F9D58',
        'yellow': '#F9AB00',
        'red': '#EA4335',
        'purple': '#9334E6',
        'teal': '#00897B',
        'orange': '#FA7B17',
        'gray': '#9E9E9E',
        'gray_light': '#E0E0E0',
        'gray_dark': '#616161'
    }


def create_material_icon(icon_name: str, color: str = "blue") -> str:
    """创建 Material Design 图标 HTML"""
    return f'<span class="material-icons" style="color: var(--md-{color});">{icon_name}</span>'
