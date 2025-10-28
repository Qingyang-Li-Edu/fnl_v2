"""
Apple-inspired CSS styling for Streamlit
参考 Apple 设计语言的 CSS 样式
"""

APPLE_STYLE_CSS = """
<style>
/* ===== 全局样式 ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');

:root {
    /* Apple 调色板 */
    --apple-blue: #007AFF;
    --apple-blue-light: #5AC8FA;
    --apple-green: #34C759;
    --apple-orange: #FF9500;
    --apple-red: #FF3B30;
    --apple-purple: #AF52DE;
    --apple-teal: #5AC8FA;
    --apple-gray: #8E8E93;
    --apple-gray-light: #F2F2F7;
    --apple-gray-medium: #E5E5EA;
    --apple-gray-dark: #636366;

    /* 背景色 */
    --bg-primary: #FFFFFF;
    --bg-secondary: #F5F5F7;
    --bg-tertiary: #FAFAFA;

    /* 文字颜色 */
    --text-primary: #1D1D1F;
    --text-secondary: #86868B;
    --text-tertiary: #B0B0B5;

    /* 边框和分割线 */
    --border-color: #D2D2D7;
    --divider-color: #E5E5E7;

    /* 阴影 */
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
    --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);

    /* 圆角 */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
}

/* ===== 主容器样式 ===== */
.stApp {
    background: var(--bg-secondary);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
}

/* ===== 主内容区域 ===== */
.main .block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    max-width: 1200px;
    background: transparent;
}

/* ===== 侧边栏样式 ===== */
[data-testid="stSidebar"] {
    background: var(--bg-primary);
    border-right: 1px solid var(--border-color);
    box-shadow: var(--shadow-sm);
}

[data-testid="stSidebar"] > div:first-child {
    padding: 2rem 1.5rem;
}

/* 侧边栏标题 */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--text-primary);
    font-weight: 600;
    letter-spacing: -0.02em;
    margin-bottom: 1.5rem;
}

/* ===== 标题样式 ===== */
h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    margin-bottom: 0.5rem;
    line-height: 1.1;
}

h2 {
    font-size: 2rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

h3 {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}

/* ===== 文本样式 ===== */
p {
    font-size: 1rem;
    line-height: 1.6;
    color: var(--text-secondary);
    margin-bottom: 1rem;
}

/* ===== 按钮样式 ===== */
.stButton > button {
    background: var(--apple-blue);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    padding: 0.75rem 2rem;
    font-size: 1rem;
    font-weight: 500;
    transition: all 0.2s ease;
    box-shadow: var(--shadow-sm);
    letter-spacing: -0.01em;
}

.stButton > button:hover {
    background: #0051D5;
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}

.stButton > button:active {
    transform: translateY(0);
    box-shadow: var(--shadow-sm);
}

/* ===== 输入控件样式 ===== */
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stSelectbox > div > div > select {
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    font-size: 0.95rem;
    background: var(--bg-primary);
    color: var(--text-primary);
    transition: all 0.2s ease;
}

.stNumberInput > div > div > input:focus,
.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus {
    border-color: var(--apple-blue);
    outline: none;
    box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

/* ===== 滑块样式 ===== */
.stSlider > div > div > div > div {
    background: var(--apple-blue);
}

.stSlider > div > div > div {
    background: var(--apple-gray-medium);
}

/* ===== 指标卡片样式 ===== */
[data-testid="stMetricValue"] {
    font-size: 2rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}

[data-testid="stMetricLabel"] {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

[data-testid="stMetricDelta"] {
    font-size: 0.875rem;
    font-weight: 500;
}

/* ===== 自定义指标卡片 ===== */
.metric-card {
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
    transition: all 0.2s ease;
    height: 100%;
}

.metric-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.metric-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}

.metric-delta {
    font-size: 0.875rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.metric-delta.positive {
    color: var(--apple-green);
}

.metric-delta.negative {
    color: var(--apple-red);
}

.metric-delta.neutral {
    color: var(--text-secondary);
}

/* ===== 文件上传器样式 ===== */
[data-testid="stFileUploader"] {
    background: var(--bg-primary);
    border: 2px dashed var(--border-color);
    border-radius: var(--radius-lg);
    padding: 2rem;
    transition: all 0.2s ease;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--apple-blue);
    background: var(--bg-tertiary);
}

/* ===== Expander 样式 ===== */
.streamlit-expanderHeader {
    background: var(--bg-primary);
    border-radius: var(--radius-md);
    border: 1px solid var(--border-color);
    font-weight: 500;
    color: var(--text-primary);
    padding: 0.75rem 1rem;
}

.streamlit-expanderHeader:hover {
    border-color: var(--apple-blue);
    background: var(--bg-tertiary);
}

/* ===== 复选框样式 ===== */
.stCheckbox {
    font-size: 0.95rem;
    color: var(--text-primary);
}

/* ===== 数据框样式 ===== */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

/* ===== Plotly 图表容器样式 ===== */
.js-plotly-plot {
    border-radius: var(--radius-lg);
    overflow: hidden;
    background: var(--bg-primary);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
}

/* ===== 分隔线样式 ===== */
hr {
    border: none;
    border-top: 1px solid var(--divider-color);
    margin: 2rem 0;
}

/* ===== 列间距调整 ===== */
[data-testid="column"] {
    padding: 0 0.75rem;
}

/* ===== 加载动画 ===== */
.stSpinner > div {
    border-top-color: var(--apple-blue) !important;
}

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {
    h1 {
        font-size: 2rem;
    }

    h2 {
        font-size: 1.5rem;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .metric-card {
        padding: 1rem;
    }

    .metric-value {
        font-size: 1.5rem;
    }
}

/* ===== 隐藏默认元素 ===== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ===== 自定义滚动条 ===== */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--apple-gray);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--apple-gray-dark);
}

/* ===== 动画 ===== */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in {
    animation: fadeIn 0.4s ease-out;
}
</style>
"""


def get_apple_colors():
    """返回 Apple 调色板用于图表"""
    return {
        'blue': '#007AFF',
        'blue_light': '#5AC8FA',
        'green': '#34C759',
        'orange': '#FF9500',
        'red': '#FF3B30',
        'purple': '#AF52DE',
        'teal': '#5AC8FA',
        'gray': '#8E8E93',
        'gray_light': '#F2F2F7',
        'gray_dark': '#636366'
    }
