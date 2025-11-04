"""
防逆流控制系统 - Streamlit Web 界面
基于 STUKF 算法的光伏防逆流控制可视化平台
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
import numpy as np

from src.core import ControlParams
from src.ui.styles import MATERIAL_STYLE_CSS, get_material_colors
from src.ui.components import create_metric_card
from src.ui.theme import get_dark_theme_css, get_theme_toggle_button, get_theme_toggle_script
from src.utils import load_data, generate_sample_data, run_simulation, compute_metrics
from src.ui.visualization import (
    create_time_series_plot,
    create_ramp_rate_distribution,
    create_curtailment_analysis,
    create_control_effectiveness_plot
)
from src.ui.dashboard import create_dashboard_view

# 页面配置
st.set_page_config(
    page_title=" 防逆流控制系统",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用样式
st.markdown(MATERIAL_STYLE_CSS, unsafe_allow_html=True)
colors = get_material_colors()


def render_sidebar():
    """渲染侧边栏参数设置"""
    with st.sidebar:
        # 主题切换（放在最顶部，独立区域）
        st.markdown("---")
        dark_mode = st.checkbox(
            "🌙 深色模式",
            value=st.session_state.get('dark_mode', False),
            key='dark_mode_toggle',
            help="点击切换深色/浅色主题"
        )
        if dark_mode != st.session_state.get('dark_mode', False):
            st.session_state['dark_mode'] = dark_mode
            st.rerun()
        st.markdown("---")

        st.markdown('<h2 style="margin-bottom: 0;"><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">settings</span>参数设置</h2>', unsafe_allow_html=True)

        # 快速预设配置
        st.markdown('<div style="background: linear-gradient(135deg, rgba(26, 115, 232, 0.08) 0%, rgba(66, 133, 244, 0.12) 100%); border-radius: 8px; padding: 16px; margin-bottom: 20px; border: 2px solid rgba(26, 115, 232, 0.2);">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin-top: 0; font-size: 1.125rem;"><span class="material-icons" style="font-size: 1.25rem; vertical-align: middle; margin-right: 6px;">rocket_launch</span>快速预设</h3>', unsafe_allow_html=True)

        col_preset1, col_preset2, col_preset3 = st.columns(3)
        with col_preset1:
            aggressive_mode = st.button("🔥 激进", help="最大化光伏利用率，关闭安全上界", use_container_width=True)
        with col_preset2:
            balanced_mode = st.button("⚖️ 平衡", help="平衡性能与安全", use_container_width=True)
        with col_preset3:
            conservative_mode = st.button("🛡️ 保守", help="最大化安全性，启用所有保护", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # 应用预设
        if 'preset_applied' not in st.session_state:
            st.session_state['preset_applied'] = None

        if aggressive_mode:
            st.session_state['preset_applied'] = 'aggressive'
            st.session_state['use_safety_ceiling'] = False
            st.session_state['use_buffer'] = False
            st.session_state['confidence'] = 95.0
        elif balanced_mode:
            st.session_state['preset_applied'] = 'balanced'
            st.session_state['use_safety_ceiling'] = True
            st.session_state['use_buffer'] = True
            st.session_state['confidence'] = 99.0
        elif conservative_mode:
            st.session_state['preset_applied'] = 'conservative'
            st.session_state['use_safety_ceiling'] = True
            st.session_state['use_buffer'] = True
            st.session_state['confidence'] = 99.9

        # 数据输入
        st.markdown('<h3><span class="material-icons" style="font-size: 1.25rem; vertical-align: middle; margin-right: 8px;">folder_open</span>数据输入</h3>', unsafe_allow_html=True)
        use_sample_data = st.checkbox("使用示例数据", value=True)

        df = None
        if use_sample_data:
            duration = st.slider("示例数据时长 (小时)", 1, 24, 10)
            if st.button("生成示例数据"):
                with st.spinner("生成示例数据中..."):
                    df = generate_sample_data(duration_hours=duration)
                    st.session_state['df'] = df
                    st.success("✓ 示例数据已生成")
        else:
            uploaded_file = st.file_uploader(
                "上传负载数据文件",
                type=['csv', 'xlsx', 'xls'],
                help="文件需包含 'time' 和 'load' 列"
            )
            if uploaded_file:
                df = load_data(uploaded_file)
                if df is not None:
                    st.session_state['df'] = df
                    st.success("✓ 数据已加载")

        if 'df' in st.session_state:
            df = st.session_state['df']

        st.markdown("---")

        # 控制参数
        st.markdown('<h3><span class="material-icons" style="font-size: 1.25rem; vertical-align: middle; margin-right: 8px;">tune</span>控制参数</h3>', unsafe_allow_html=True)

        # 从 session_state 获取预设值，如果没有则使用默认值
        default_use_safety = st.session_state.get('use_safety_ceiling', False)
        default_use_buffer = st.session_state.get('use_buffer', True)
        default_confidence = st.session_state.get('confidence', 99.0)

        # 安全上界开关（核心参数）
        use_safety_ceiling = st.checkbox(
            "使用安全上界 U_A",
            value=default_use_safety,
            help="关闭后仅使用性能上界U_B，可大幅提高光伏利用率（90%以上）。开启后更保守但更安全。"
        )

        use_buffer = st.checkbox("启用安全余量 Buffer", value=default_use_buffer, help="开启后会在置信下界基础上再减去Buffer")
        buffer = st.number_input("安全余量 Buffer (kW)", min_value=0.0, max_value=50.0, value=5.0, step=0.5) if use_buffer else 5.0

        confidence_percent = st.slider("置信度", min_value=80.0, max_value=99.99, value=default_confidence, step=0.1, format="%.2f%%")
        alpha = 1 - (confidence_percent / 100.0)
        st.caption(f"α = {alpha:.4f}")

        P_max = st.number_input("逆变器最大功率 P_max (kW)", min_value=10.0, max_value=5000.0, value=500.0, step=10.0)

        # 高级参数
        params_dict = render_advanced_params(use_safety_ceiling)

        # 创建控制参数对象（R_up和R_down使用极大值，相当于无限制）
        params = ControlParams(
            buffer=buffer,
            use_buffer=use_buffer,
            use_safety_ceiling=use_safety_ceiling,
            R_up=1000.0,  # 极大值，相当于无限速约束
            R_down=1000.0,  # 极大值，相当于无限速约束
            alpha=alpha,
            P_max=P_max,
            **params_dict
        )

        st.markdown("---")
        run_button = st.button("运行仿真", use_container_width=True, type="primary")

        return df, params, run_button


def render_advanced_params(use_safety_ceiling):
    """渲染高级参数设置"""
    with st.expander("高级参数"):
        # 安全上界策略（仅在启用安全上界时显示）
        adaptive_safety = False
        if use_safety_ceiling:
            st.markdown("### 安全上界策略")
            adaptive_safety = st.checkbox(
                "自适应安全上界",
                value=True,
                help="低负载时使用相对buffer（更激进），高负载时使用绝对buffer（保守）"
            )
            st.markdown("---")

        st.markdown("### 动态安全策略")
        enable_dynamic_safety = st.checkbox("启用动态安全策略", value=True)

        if enable_dynamic_safety:
            st.markdown("**策略 I：趋势自适应置信度**")
            trend_adaptive = st.checkbox("启用趋势自适应", value=True)

            if trend_adaptive:
                col_risk1, col_risk2 = st.columns(2)
                with col_risk1:
                    up_risk_factor = st.slider("ρ↑ (上升风险系数)", 0.1, 1.0, 0.5, 0.05)
                with col_risk2:
                    down_risk_factor = st.slider("ρ↓ (下降风险系数)", 1.0, 5.0, 2.0, 0.1)
            else:
                up_risk_factor, down_risk_factor = 0.5, 2.0

            st.markdown("**策略 II：局部不确定性混合**")
            col_local1, col_local2 = st.columns(2)
            with col_local1:
                local_uncertainty_weight = st.slider("ω (局部权重)", 0.0, 1.0, 0.7, 0.05)
            with col_local2:
                local_window_size = st.number_input("N (窗口大小)", 10, 500, 50, 10)
        else:
            trend_adaptive = False
            up_risk_factor, down_risk_factor = 1.0, 1.0
            local_uncertainty_weight, local_window_size = 0.0, 50

        st.markdown("---")
        st.markdown("### STUKF记忆长度控制")
        memory_decay = st.slider("λ (记忆衰减因子)", min_value=0.90, max_value=0.999, value=0.99, step=0.001, format="%.3f")
        st.caption(f"等效记忆时长: ≈ {1/(1-memory_decay):.0f} 时间步")

        st.markdown("---")
        st.markdown("### 负载跟踪模式")
        st.caption("默认启用：PV输出直接跟踪负载曲线，不给出超过负载的功率指令")
        use_S_down_max = st.checkbox("启用负载急降保护", value=False,
                                     help="检测到负载急速下降时立即限制PV输出，防止逆流")
        S_down_max = st.number_input("急降阈值 (kW/s)", min_value=0.1, max_value=100.0, value=20.0, step=1.0,
                                     help="负载下降速率超过此值时触发保护") if use_S_down_max else None

        st.markdown("---")
        st.markdown("### 系统延迟参数")
        tau_meas = st.number_input("τ_meas 测量延迟 (s)", 0.01, 1.0, 0.1, 0.01)
        tau_com = st.number_input("τ_com 通信延迟 (s)", 0.01, 1.0, 0.1, 0.01)
        tau_exec = st.number_input("τ_exec 执行延迟 (s)", 0.01, 1.0, 0.2, 0.01)

    return {
        'tau_meas': tau_meas,
        'tau_com': tau_com,
        'tau_exec': tau_exec,
        'S_down_max': S_down_max,
        'stukf_memory_decay': memory_decay,
        'adaptive_safety': adaptive_safety,
        'enable_dynamic_safety': enable_dynamic_safety,
        'trend_adaptive': trend_adaptive,
        'up_risk_factor': up_risk_factor,
        'down_risk_factor': down_risk_factor,
        'local_uncertainty_weight': local_uncertainty_weight,
        'local_window_size': local_window_size
    }


def render_metrics(metrics):
    """渲染性能指标卡片"""
    st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">assessment</span>关键性能指标</h2>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    # 动态颜色警告系统
    curtailment_rate = metrics['curtailment_rate']
    if curtailment_rate >= 10.0:
        curtail_color = "red"
        curtail_delta_color = "negative"
        curtail_icon = "warning"
    elif curtailment_rate >= 5.0:
        curtail_color = "orange"
        curtail_delta_color = "negative"
        curtail_icon = "wb_sunny"
    else:
        curtail_color = "green"
        curtail_delta_color = "positive"
        curtail_icon = "wb_sunny"

    with col1:
        st.markdown(create_metric_card("弃光率", f"{metrics['curtailment_rate']:.2f}%",
                                      f"总量: {metrics['total_curtailment_kwh']:.1f} kWh",
                                      curtail_delta_color, curtail_icon, curtail_color, featured=True),
                   unsafe_allow_html=True)

    with col2:
        st.markdown(create_metric_card("最大弃光功率", f"{metrics['max_curtailment_kw']:.2f} kW",
                                      None, "neutral", "bolt", "orange"), unsafe_allow_html=True)

    with col3:
        bypass_color = "red" if metrics['safety_bypass_count'] > 0 else "green"
        bypass_delta_color = "negative" if metrics['safety_bypass_count'] > 0 else "positive"
        st.markdown(create_metric_card("安全旁路次数", f"{metrics['safety_bypass_count']}", "安全触发",
                                      bypass_delta_color, "security", bypass_color), unsafe_allow_html=True)

    with col4:
        st.markdown(create_metric_card("平均上调速率", f"{metrics['avg_up_rate']:.2f} kW/s",
                                      f"最大: {metrics['max_up_rate']:.2f}", "neutral", "trending_up", "blue"),
                   unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(create_metric_card("平均下调速率", f"{metrics['avg_down_rate']:.2f} kW/s",
                                      f"最大: {metrics['max_down_rate']:.2f}", "neutral", "trending_down", "green"),
                   unsafe_allow_html=True)


def render_results():
    """渲染仿真结果"""
    if 'history' not in st.session_state or 'metrics' not in st.session_state:
        render_welcome_screen()
        return

    history = st.session_state['history']
    metrics = st.session_state['metrics']
    params_used = st.session_state.get('params_used', None)

    # 视图模式切换
    st.markdown('<div style="background: linear-gradient(135deg, rgba(26, 115, 232, 0.05) 0%, rgba(66, 133, 244, 0.08) 100%); border-radius: 8px; padding: 16px; margin-bottom: 20px;">', unsafe_allow_html=True)
    col_mode1, col_mode2, col_mode3 = st.columns([1, 1, 2])
    with col_mode1:
        view_mode = st.selectbox(
            "📊 视图模式",
            ["标准视图", "仪表盘视图"],
            label_visibility="collapsed",
            key="view_mode"
        )
    with col_mode2:
        st.markdown(f'<div class="view-mode-label">当前: <b>{view_mode}</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 根据模式渲染不同视图
    if view_mode == "仪表盘视图":
        render_dashboard_mode(metrics)
    else:
        render_standard_mode(history, metrics, params_used)


def render_dashboard_mode(metrics: dict):
    """渲染仪表盘模式"""
    st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">speed</span>实时监控仪表盘</h2>', unsafe_allow_html=True)

    dashboards = create_dashboard_view(metrics)

    # 第一行：最重要的指标 - 弃光率（占据更大空间）
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(dashboards['curtailment_rate'], use_container_width=True)
    with col2:
        st.plotly_chart(dashboards['safety_bypass'], use_container_width=True)

    # 第二行：其他指标
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(dashboards['max_curtailment'], use_container_width=True)
    with col4:
        st.plotly_chart(dashboards['avg_up_rate'], use_container_width=True)

    # 详细数据表格
    st.markdown("---")
    st.markdown('<h3><span class="material-icons" style="font-size: 1.25rem; vertical-align: middle; margin-right: 8px;">table_chart</span>详细指标</h3>', unsafe_allow_html=True)

    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    with col_d1:
        st.metric("总弃光量", f"{metrics['total_curtailment_kwh']:.2f} kWh")
    with col_d2:
        st.metric("最大上调速率", f"{metrics['max_up_rate']:.2f} kW/s")
    with col_d3:
        st.metric("平均下调速率", f"{metrics['avg_down_rate']:.2f} kW/s")
    with col_d4:
        st.metric("最大下调速率", f"{metrics['max_down_rate']:.2f} kW/s")


def render_standard_mode(history: dict, metrics: dict, params_used):
    """渲染标准模式"""
    render_metrics(metrics)

    # 时间序列图
    st.markdown("---")
    st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">show_chart</span>时间序列对比图</h2>', unsafe_allow_html=True)

    with st.expander("图表显示选项", expanded=False):
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            show_stukf = st.checkbox("显示 STUKF 预测", value=False)
            show_bounds = st.checkbox("显示安全/性能上界", value=True)
        with col_opt2:
            chart_height = st.slider("图表高度", 400, 800, 600, 50)
            show_debug = st.checkbox("显示调试信息", value=False)

    if show_debug:
        render_debug_info(history)

    fig_timeseries = create_time_series_plot(history, show_stukf=show_stukf, show_bounds=show_bounds, height=chart_height)
    # 使用config参数启用全屏等功能
    st.plotly_chart(fig_timeseries, use_container_width=True, config=getattr(fig_timeseries, '_config', {}))

    # 其他图表
    st.markdown("---")
    st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">insights</span>控制效果分析</h2>', unsafe_allow_html=True)
    fig_effectiveness = create_control_effectiveness_plot(history, height=500)
    st.plotly_chart(fig_effectiveness, use_container_width=True, config=getattr(fig_effectiveness, '_config', {}))

    st.markdown("---")
    st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">wb_sunny</span>弃光分析</h2>', unsafe_allow_html=True)
    P_max_val = params_used.P_max if params_used else 100.0
    fig_curtailment = create_curtailment_analysis(history, P_max_val, height=400)
    st.plotly_chart(fig_curtailment, use_container_width=True, config=getattr(fig_curtailment, '_config', {}))

    st.markdown("---")
    st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">bar_chart</span>变化率分布统计</h2>', unsafe_allow_html=True)
    fig_ramp = create_ramp_rate_distribution(history, height=400)
    st.plotly_chart(fig_ramp, use_container_width=True, config=getattr(fig_ramp, '_config', {}))

    render_download_section(history, metrics)


def render_debug_info(history):
    """渲染调试信息"""
    st.markdown("### 🔍 算法计算详情（随机采样10个时间点）")

    sample_indices = np.random.choice(len(history['time']), min(10, len(history['time'])), replace=False)
    sample_indices = sorted(sample_indices)

    debug_data = []
    for idx in sample_indices:
        debug_data.append({
            '时间(s)': f"{history['time'][idx]:.1f}",
            '负载(kW)': f"{history['load'][idx]:.2f}",
            '预测均值': f"{history['L_med'][idx]:.2f}",
            '置信下界': f"{history['L_lb'][idx]:.2f}",
            '安全上界U_A': f"{history['U_A'][idx]:.2f}",
            '性能上界U_B': f"{history['U_B'][idx]:.2f}",
            'PV指令': f"{history['P_cmd'][idx]:.2f}",
            '安全旁路': '是' if history['safety_bypass'][idx] else '否'
        })

    st.dataframe(pd.DataFrame(debug_data), use_container_width=True)


def render_download_section(history, metrics):
    """渲染数据下载区域"""
    st.markdown("---")
    st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">download</span>导出数据</h2>', unsafe_allow_html=True)

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        result_df = pd.DataFrame({
            'time': history['time'],
            'load': history['load'],
            'P_cmd': history['P_cmd'],
            'U_A': history['U_A'],
            'U_B': history['U_B'],
            'L_med': history['L_med'],
            'L_lb': history['L_lb'],
            'safety_bypass': history['safety_bypass']
        })

        csv = result_df.to_csv(index=False)
        st.download_button("下载仿真结果 (CSV)", data=csv, file_name="v5_simulation_results.csv",
                          mime="text/csv", use_container_width=True, type="primary")

    with col_d2:
        metrics_df = pd.DataFrame([metrics])
        metrics_csv = metrics_df.to_csv(index=False)
        st.download_button("下载性能指标 (CSV)", data=metrics_csv, file_name="v5_performance_metrics.csv",
                          mime="text/csv", use_container_width=True, type="primary")


def render_welcome_screen():
    """渲染欢迎界面"""
    st.markdown("""
    ### 👋 欢迎使用  防逆流控制系统

    这是一个基于 **STUKF（平滑趋势无迹卡尔曼滤波器）** 的光伏防逆流控制算法可视化平台。

    ###  快速开始

    1. **左侧边栏** 选择"使用示例数据"或上传您的负载数据
    2. **调整控制参数** 以优化系统性能
    3. **点击"运行仿真"** 查看控制效果
    4. **分析结果** 通过关键指标和可视化图表

    ### 📋 功能特点

    - ✅ 实时负载预测与控制
    - ✅ 非对称限速保护
    - ✅ 安全旁路机制
    - ✅ 交互式可视化
    - ✅ 性能指标分析

    ### 📁 数据格式要求

    上传的数据文件支持 CSV、Excel (.xlsx, .xls) 格式。

    **支持的列名**（自动识别）:
    - **时间列**: UTC时间, UTC, time, 时间, timestamp
    - **负载列**: 负载数据, load, 负载, power, 功率
    """)


def main():
    """主函数"""
    # 初始化主题状态（必须在最前面）
    if 'dark_mode' not in st.session_state:
        st.session_state['dark_mode'] = False

    # 全局应用深色模式CSS（如果启用）
    if st.session_state.get('dark_mode', False):
        st.markdown(get_dark_theme_css(), unsafe_allow_html=True)

    st.markdown('<h1 style="margin-bottom: 0.5rem; font-size: 2.5rem; font-weight: 500;"><span class="material-icons" style="font-size: 3rem; vertical-align: middle; margin-right: 12px; color: #1A73E8;">flash_on</span>防逆流控制系统 V2.0</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">基于 STUKF 算法的光伏防逆流控制可视化平台</p>', unsafe_allow_html=True)
    st.markdown("---")

    # 侧边栏参数设置
    df, params, run_button = render_sidebar()

    # 运行仿真
    if df is not None and run_button:
        st.markdown("## 📊 仿真结果")

        with st.spinner("正在运行仿真..."):
            controller = run_simulation(df, params)
            history = controller.get_history()

        st.success("✓ 仿真完成！")

        metrics = compute_metrics(df, history)

        st.session_state['controller'] = controller
        st.session_state['history'] = history
        st.session_state['metrics'] = metrics
        st.session_state['params_used'] = params

    # 显示结果
    render_results()


if __name__ == "__main__":
    main()
