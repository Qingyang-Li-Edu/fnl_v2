"""
###  防逆流控制系统 - Streamlit Web 界面
基于 STUKF 算法的光伏防逆流控制可视化平台
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import StringIO
import time

from v5_anti_backflow import V5AntiBackflowController, ControlParams
from material_styles import MATERIAL_STYLE_CSS, get_material_colors, create_material_icon
from visualization import (
    create_time_series_plot,
    create_ramp_rate_distribution,
    create_curtailment_analysis,
    create_control_effectiveness_plot
)

# ===== 页面配置 =====
st.set_page_config(
    page_title=" 防逆流控制系统",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 应用 Material Design 样式 =====
st.markdown(MATERIAL_STYLE_CSS, unsafe_allow_html=True)

# 获取 Material Design 调色板
colors = get_material_colors()


# ===== 工具函数 =====
def load_data(uploaded_file) -> pd.DataFrame:
    """加载负载数据，支持多种列名格式，并进行数据清洗和平滑处理"""
    try:
        # 读取文件
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("不支持的文件格式。请上传 CSV 或 Excel 文件。")
            return None

        # 显示原始列名供调试
        st.info(f"检测到的列: {', '.join(df.columns.tolist())}")

        # 智能识别时间列
        time_col = None
        possible_time_cols = ['UTC时间', 'UTC', 'time', '时间', '时间戳', 'timestamp', 'datetime', 'Time', 'DateTime']
        for col in possible_time_cols:
            if col in df.columns:
                time_col = col
                break

        if time_col is None:
            st.error(f"未找到时间列。请确保文件包含以下列之一: {', '.join(possible_time_cols)}")
            return None

        # 智能识别负载列
        load_col = None
        possible_load_cols = ['负载数据', 'load', '负载', 'power', 'Load', 'Power', '功率', 'kW']
        for col in possible_load_cols:
            if col in df.columns:
                load_col = col
                break

        if load_col is None:
            st.error(f"未找到负载列。请确保文件包含以下列之一: {', '.join(possible_load_cols)}")
            return None

        # 创建标准化的数据框
        result_df = pd.DataFrame()

        # 处理时间列
        try:
            # 尝试解析时间字符串
            if df[time_col].dtype == 'object':
                result_df['time_raw'] = pd.to_datetime(df[time_col], errors='coerce')
            else:
                result_df['time_raw'] = df[time_col]

            # 移除时间为空的行
            if result_df['time_raw'].isna().any():
                na_count = result_df['time_raw'].isna().sum()
                st.warning(f"⚠️ 时间列中有 {na_count} 个无效值，已移除")
                result_df = result_df.dropna(subset=['time_raw'])

            # 转换为秒数（从第一个时间点开始）
            first_time = result_df['time_raw'].iloc[0]
            result_df['time'] = (result_df['time_raw'] - first_time).dt.total_seconds()

        except Exception as e:
            st.error(f"时间列解析失败: {str(e)}")
            # 如果解析失败，使用行索引作为时间
            st.warning("使用行索引作为时间序列")
            result_df['time'] = np.arange(len(df))

        # 处理负载列 - 数据清洗
        try:
            result_df['load_raw'] = pd.to_numeric(df[load_col], errors='coerce')

            # 统计原始数据问题
            original_count = len(result_df)
            na_count = result_df['load_raw'].isna().sum()
            negative_count = (result_df['load_raw'] < 0).sum()

            # 检测异常大的值（大于10000）
            abnormal_large = (result_df['load_raw'] > 10000).sum()

            # 显示数据质量报告
            if na_count > 0 or negative_count > 0 or abnormal_large > 0:
                st.warning("📊 数据质量报告：")
                if na_count > 0:
                    st.warning(f"  • 缺失值: {na_count} 个 ({na_count/original_count*100:.1f}%)")
                if negative_count > 0:
                    st.warning(f"  • 负值: {negative_count} 个 ({negative_count/original_count*100:.1f}%)")
                if abnormal_large > 0:
                    st.warning(f"  • 异常大值(>10000): {abnormal_large} 个 ({abnormal_large/original_count*100:.1f}%)")

            # 数据清洗步骤
            st.info("🔧 正在进行数据清洗和平滑处理...")

            # 1. 处理异常大的值 (> 10000) - 标记为 NaN
            result_df.loc[result_df['load_raw'] > 10000, 'load_raw'] = np.nan

            # 2. 处理负值 - 标记为 NaN
            result_df.loc[result_df['load_raw'] < 0, 'load_raw'] = np.nan

            # 3. 前向填充处理缺失值（使用上一个有效值）
            result_df['load'] = result_df['load_raw'].fillna(method='ffill')

            # 4. 如果开头有缺失值，使用后向填充
            result_df['load'] = result_df['load'].fillna(method='bfill')

            # 5. 如果仍有缺失值（整列都是NaN的情况），用0填充
            if result_df['load'].isna().any():
                st.warning("部分数据无法填充，使用0替代")
                result_df['load'] = result_df['load'].fillna(0)

            # 6. 应用移动平均平滑（可选，窗口大小为3）
            window_size = 3
            result_df['load_smoothed'] = result_df['load'].rolling(
                window=window_size,
                min_periods=1,
                center=True
            ).mean()

            # 使用平滑后的数据
            result_df['load'] = result_df['load_smoothed']

            # 7. 最终检查：确保负载值在合理范围内
            result_df['load'] = result_df['load'].clip(lower=0, upper=10000)

            # 显示清洗结果
            cleaned_count = len(result_df)
            if original_count != cleaned_count:
                st.success(f"✓ 数据清洗完成: {original_count} → {cleaned_count} 条数据")
            else:
                st.success(f"✓ 数据清洗完成: 保留 {cleaned_count} 条数据")

        except Exception as e:
            st.error(f"负载列解析失败: {str(e)}")
            import traceback
            st.error(f"详细错误: {traceback.format_exc()}")
            return None

        # 显示数据统计信息
        st.success(f"✅ 成功加载并处理 {len(result_df)} 条数据")

        # 数据统计
        col1, col2 = st.columns(2)
        with col1:
            st.metric("时间范围", f"{result_df['time'].max()/3600:.2f} 小时")
            st.metric("数据点数", f"{len(result_df):,}")
        with col2:
            st.metric("负载均值", f"{result_df['load'].mean():.2f} kW")
            st.metric("负载范围", f"{result_df['load'].min():.1f} ~ {result_df['load'].max():.1f} kW")

        # 显示处理前后对比（前10条数据）
        with st.expander("查看数据处理详情", expanded=False):
            comparison_df = pd.DataFrame({
                '时间(s)': result_df['time'].head(10),
                '原始负载': result_df['load_raw'].head(10),
                '处理后负载': result_df['load'].head(10)
            })
            st.dataframe(comparison_df, use_container_width=True)

            # 显示数据质量指标
            st.markdown("**数据质量指标:**")
            quality_metrics = pd.DataFrame({
                '指标': ['最小值', '最大值', '平均值', '标准差', '中位数'],
                '原始数据': [
                    f"{result_df['load_raw'].min():.2f}",
                    f"{result_df['load_raw'].max():.2f}",
                    f"{result_df['load_raw'].mean():.2f}",
                    f"{result_df['load_raw'].std():.2f}",
                    f"{result_df['load_raw'].median():.2f}"
                ],
                '处理后': [
                    f"{result_df['load'].min():.2f}",
                    f"{result_df['load'].max():.2f}",
                    f"{result_df['load'].mean():.2f}",
                    f"{result_df['load'].std():.2f}",
                    f"{result_df['load'].median():.2f}"
                ]
            })
            st.dataframe(quality_metrics, use_container_width=True)

        return result_df[['time', 'load']]

    except Exception as e:
        st.error(f"加载数据时出错: {str(e)}")
        import traceback
        st.error(f"详细错误: {traceback.format_exc()}")
        return None


def generate_sample_data(duration_hours: float = 10, interval_sec: float = 1.0) -> pd.DataFrame:
    """
    生成工厂负载数据（8:00-18:00，10小时）

    特征：
    - 宏观：双峰结构（上午10:00和下午14:30高峰）+ 午休低谷（12:00-12:30）
    - 微观：秒级设备启停冲击（+7~16kW，持续3-7秒）
    """
    num_points = int(duration_hours * 3600 / interval_sec)
    time_array = np.arange(num_points) * interval_sec

    # === 宏观日规律（基准负载曲线） ===
    # 将时间映射到 0-1 范围（0=8:00, 1=18:00）
    t_normalized = time_array / (duration_hours * 3600)

    base_load = np.zeros(num_points)
    for i, t in enumerate(t_normalized):
        hour = 8 + t * 10  # 映射到实际小时 8-18

        if hour < 8.5:  # 8:00-8:30 开工爬升
            base_load[i] = 15 + (45 - 15) * (hour - 8) / 0.5
        elif hour < 10:  # 8:30-10:00 快速爬升至高峰
            base_load[i] = 45 + (96 - 45) * (hour - 8.5) / 1.5
        elif hour < 11.5:  # 10:00-11:30 高位运行
            base_load[i] = 96 - 8 * (hour - 10) / 1.5
        elif hour < 12.5:  # 11:30-12:30 午休低谷
            base_load[i] = 88 - 60 * (hour - 11.5) if hour < 12 else 28
        elif hour < 13.5:  # 12:30-13:30 复工爬升
            base_load[i] = 28 + (85 - 28) * (hour - 12.5)
        elif hour < 15:  # 13:30-15:00 下午高峰
            base_load[i] = 85 + (96 - 85) * (hour - 13.5) / 1.5
        elif hour < 16.5:  # 15:00-16:30 缓慢下降
            base_load[i] = 96 - 30 * (hour - 15) / 1.5
        elif hour < 17.5:  # 16:30-17:30 快速关停
            base_load[i] = 66 - 47 * (hour - 16.5)
        else:  # 17:30-18:00 值班负载
            base_load[i] = 19 - 11 * (hour - 17.5) / 0.5

    # === 微观秒波动（设备启停冲击） ===
    equipment_impulses = np.zeros(num_points)

    # 设备启停参数
    impulse_types = [
        {'power': 7.5, 'duration': 4, 'freq': 0.015},   # 小型焊接机
        {'power': 12.0, 'duration': 5, 'freq': 0.012},  # 中型冲压机
        {'power': 15.5, 'duration': 6, 'freq': 0.008},  # 大型传送带
        {'power': 9.0, 'duration': 3, 'freq': 0.010},   # 压缩机
    ]

    for impulse_type in impulse_types:
        i = 0
        while i < num_points:
            # 随机判断是否发生启动事件
            if np.random.random() < impulse_type['freq']:
                # 生成冲击
                duration = int(impulse_type['duration'] * (1 + np.random.uniform(-0.3, 0.3)))
                power = impulse_type['power'] * (1 + np.random.uniform(-0.2, 0.2))

                # 冲击包络：快速上升 → 平台 → 缓慢下降
                for j in range(duration):
                    if i + j >= num_points:
                        break
                    if j == 0:
                        equipment_impulses[i + j] += power * 0.6  # 启动瞬间
                    elif j == 1:
                        equipment_impulses[i + j] += power * 1.0  # 峰值
                    elif j < duration - 1:
                        equipment_impulses[i + j] += power * 0.9  # 平台
                    else:
                        equipment_impulses[i + j] += power * 0.5  # 下降

                i += duration + np.random.randint(3, 10)  # 间隔3-10秒
            else:
                i += 1

    # === 小幅随机噪声（测量误差、小设备） ===
    small_noise = np.random.normal(0, 1.5, num_points)

    # === 合成最终负载 ===
    load_array = base_load + equipment_impulses + small_noise
    load_array = np.maximum(load_array, 5)  # 确保非负

    df = pd.DataFrame({
        'time': time_array,
        'load': load_array
    })

    return df


def run_simulation(df: pd.DataFrame, params: ControlParams) -> V5AntiBackflowController:
    """运行控制仿真"""
    controller = V5AntiBackflowController(
        params=params,
        initial_load=df['load'].iloc[0],
        process_noise=0.1,
        measurement_noise=1.0
    )

    # 添加进度条
    progress_bar = st.progress(0)
    status_text = st.empty()

    total_steps = len(df)
    for idx, row in df.iterrows():
        controller.compute_control(row['load'], row['time'])

        # 更新进度
        if idx % max(1, total_steps // 100) == 0:
            progress = int((idx + 1) / total_steps * 100)
            progress_bar.progress(progress)
            status_text.text(f"仿真进度: {progress}%")

    progress_bar.empty()
    status_text.empty()

    return controller


def compute_metrics(df: pd.DataFrame, history: dict) -> dict:
    """计算关键性能指标"""
    P_cmd = history['P_cmd']
    load = history['load']
    time = history['time']

    # 计算弃光量
    # 假设光伏最大功率为 P_max
    P_max = max(P_cmd) if len(P_cmd) > 0 else 0
    curtailed_power = P_max - P_cmd

    # 总弃光量 (kWh)
    dt = np.diff(time, prepend=time[0])
    total_curtailment = np.sum(curtailed_power * dt) / 3600  # 转换为 kWh

    # 最大弃光功率
    max_curtailment = np.max(curtailed_power)

    # 安全旁路触发次数
    safety_bypass_count = np.sum(history['safety_bypass'])

    # 计算变化率
    dP_cmd = np.diff(P_cmd, prepend=P_cmd[0])
    dt_nonzero = dt.copy()
    dt_nonzero[dt_nonzero == 0] = 1.0  # 避免除零
    ramp_rates = dP_cmd / dt_nonzero

    # 上调和下调速率
    up_rates = ramp_rates[ramp_rates > 0]
    down_rates = np.abs(ramp_rates[ramp_rates < 0])

    avg_up_rate = np.mean(up_rates) if len(up_rates) > 0 else 0
    max_up_rate = np.max(up_rates) if len(up_rates) > 0 else 0
    avg_down_rate = np.mean(down_rates) if len(down_rates) > 0 else 0
    max_down_rate = np.max(down_rates) if len(down_rates) > 0 else 0

    # 计算弃光率
    curtailment_rate = (total_curtailment / (P_max * (time[-1] - time[0]) / 3600)) * 100 if P_max > 0 else 0

    return {
        'total_curtailment_kwh': total_curtailment,
        'curtailment_rate': curtailment_rate,
        'max_curtailment_kw': max_curtailment,
        'safety_bypass_count': int(safety_bypass_count),
        'avg_up_rate': avg_up_rate,
        'max_up_rate': max_up_rate,
        'avg_down_rate': avg_down_rate,
        'max_down_rate': max_down_rate
    }


def create_metric_card(label: str, value: str, delta: str = None, delta_color: str = "neutral", icon: str = "analytics", icon_color: str = "blue"):
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


# ===== 主界面 =====
def main():
    # 标题
    st.markdown('<h1 style="margin-bottom: 0.5rem;"><span class="material-icons" style="font-size: 2.5rem; vertical-align: middle; margin-right: 12px; color: #1A73E8;">flash_on</span> 防逆流控制系统</h1>', unsafe_allow_html=True)
    st.markdown('<p style="margin-top: 0; margin-bottom: 1rem; color: #5f6368;">基于 STUKF 算法的光伏防逆流控制可视化平台</p>', unsafe_allow_html=True)
    st.markdown("---")

    # ===== 侧边栏 - 参数设置 =====
    with st.sidebar:
        st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">settings</span>参数设置</h2>', unsafe_allow_html=True)

        # 数据上传
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

        # 如果会话中有数据，使用它
        if 'df' in st.session_state:
            df = st.session_state['df']

        st.markdown("---")

        # 控制参数
        st.markdown('<h3><span class="material-icons" style="font-size: 1.25rem; vertical-align: middle; margin-right: 8px;">tune</span>控制参数</h3>', unsafe_allow_html=True)

        # Buffer插件（可选）
        use_buffer = st.checkbox(
            "启用安全余量 Buffer",
            value=True,
            help="开启后会在置信下界基础上再减去Buffer"
        )

        buffer = 5.0
        if use_buffer:
            buffer = st.number_input(
                "安全余量 Buffer (kW)",
                min_value=0.0,
                max_value=50.0,
                value=5.0,
                step=0.5,
                help="防止逆流的安全裕量"
            )

        # 置信度参数（连续滑动条）
        confidence_percent = st.slider(
            "置信度",
            min_value=80.0,
            max_value=99.99,
            value=99.0,
            step=0.1,
            format="%.2f%%",
            help="预测置信度。99%=较激进，95%=平衡，90%=保守"
        )
        alpha = 1 - (confidence_percent / 100.0)  # 转换为α参数

        st.caption(f"α = {alpha:.4f}")

        R_up = st.number_input(
            "上行斜率限制 R↑ (kW/s)",
            min_value=0.1,
            max_value=100.0,
            value=10.0,
            step=1.0,
            help="限制 PV 指令上升速度"
        )

        R_down = st.number_input(
            "下行斜率限制 R↓ (kW/s)",
            min_value=0.1,
            max_value=200.0,
            value=50.0,
            step=5.0,
            help="限制 PV 指令下降速度"
        )

        P_max = st.number_input(
            "逆变器最大功率 P_max (kW)",
            min_value=10.0,
            max_value=5000.0,
            value=500.0,
            step=10.0,
            help="PV装机容量（大装机场景）"
        )

        # 可选参数
        with st.expander("高级参数"):
            # === 动态安全策略 ===
            st.markdown("### 动态安全策略")
            enable_dynamic_safety = st.checkbox(
                "启用动态安全策略",
                value=True,
                help="启用后，U_A会根据负载趋势和近期波动动态调整"
            )

            if enable_dynamic_safety:
                # 策略1：趋势自适应
                st.markdown("**策略 I：趋势自适应置信度**")
                trend_adaptive = st.checkbox("启用趋势自适应", value=True)

                up_risk_factor = 0.5
                down_risk_factor = 2.0
                if trend_adaptive:
                    col_risk1, col_risk2 = st.columns(2)
                    with col_risk1:
                        up_risk_factor = st.slider(
                            "ρ↑ (上升风险系数)",
                            0.1, 1.0, 0.5, 0.05,
                            help="越小越激进（放松限制）"
                        )
                    with col_risk2:
                        down_risk_factor = st.slider(
                            "ρ↓ (下降风险系数)",
                            1.0, 5.0, 2.0, 0.1,
                            help="越大越保守（收紧限制）"
                        )

                # 策略2：局部不确定性
                st.markdown("**策略 II：局部不确定性混合**")
                col_local1, col_local2 = st.columns(2)
                with col_local1:
                    local_uncertainty_weight = st.slider(
                        "ω (局部权重)",
                        0.0, 1.0, 0.7, 0.05,
                        help="1.0=完全使用近期波动，0.0=完全使用全局估计"
                    )
                with col_local2:
                    local_window_size = st.number_input(
                        "N (窗口大小)",
                        10, 500, 50, 10,
                        help="用于计算局部不确定性的历史数据点数"
                    )
            else:
                trend_adaptive = False
                up_risk_factor = 1.0
                down_risk_factor = 1.0
                local_uncertainty_weight = 0.0
                local_window_size = 50

            st.markdown("---")

            # === STUKF记忆长度控制 ===
            st.markdown("### STUKF记忆长度控制")
            memory_decay = st.slider(
                "λ (记忆衰减因子)",
                min_value=0.90,
                max_value=0.999,
                value=0.99,
                step=0.001,
                format="%.3f",
                help="越小越关注近期数据。0.90=短记忆，0.999=长记忆"
            )
            st.caption(f"等效记忆时长: ≈ {1/(1-memory_decay):.0f} 时间步")

            st.markdown("---")

            # === 其他参数 ===
            st.markdown("### 其他参数")
            use_S_down_max = st.checkbox("启用负载最大下行速率")
            S_down_max = None
            if use_S_down_max:
                S_down_max = st.number_input(
                    "S_down_max (kW/s)",
                    min_value=0.1,
                    max_value=100.0,
                    value=20.0,
                    step=1.0
                )

            tau_meas = st.number_input("τ_meas 测量延迟 (s)", 0.01, 1.0, 0.1, 0.01)
            tau_com = st.number_input("τ_com 通信延迟 (s)", 0.01, 1.0, 0.1, 0.01)
            tau_exec = st.number_input("τ_exec 执行延迟 (s)", 0.01, 1.0, 0.2, 0.01)

        # 创建控制参数对象
        params = ControlParams(
            buffer=buffer,
            use_buffer=use_buffer,
            R_up=R_up,
            R_down=R_down,
            alpha=alpha,
            S_down_max=S_down_max,
            P_max=P_max,
            tau_meas=tau_meas,
            tau_com=tau_com,
            tau_exec=tau_exec,
            stukf_memory_decay=memory_decay,
            # 动态安全策略参数
            enable_dynamic_safety=enable_dynamic_safety,
            trend_adaptive=trend_adaptive,
            up_risk_factor=up_risk_factor,
            down_risk_factor=down_risk_factor,
            local_uncertainty_weight=local_uncertainty_weight,
            local_window_size=local_window_size
        )

        st.markdown("---")

        # 运行按钮
        run_button = st.button("运行仿真", use_container_width=True, type="primary")

    # ===== 主区域 =====
    if df is not None and run_button:
        st.markdown("## 📊 仿真结果")

        # 运行仿真
        with st.spinner("正在运行仿真..."):
            controller = run_simulation(df, params)
            history = controller.get_history()

        st.success("✓ 仿真完成！")

        # 计算指标
        metrics = compute_metrics(df, history)

        # 保存到会话状态
        st.session_state['controller'] = controller
        st.session_state['history'] = history
        st.session_state['metrics'] = metrics
        st.session_state['params_used'] = params

    # 显示结果（如果存在）
    if 'history' in st.session_state and 'metrics' in st.session_state:
        history = st.session_state['history']
        metrics = st.session_state['metrics']

        # ===== 关键指标展示 =====
        st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">assessment</span>关键性能指标</h2>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                create_metric_card(
                    "总弃光量",
                    f"{metrics['total_curtailment_kwh']:.2f} kWh",
                    f"{metrics['curtailment_rate']:.2f}%",
                    "neutral",
                    "wb_sunny",
                    "orange"
                ),
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                create_metric_card(
                    "最大弃光功率",
                    f"{metrics['max_curtailment_kw']:.2f} kW",
                    None,
                    "neutral",
                    "bolt",
                    "red"
                ),
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                create_metric_card(
                    "安全旁路次数",
                    f"{metrics['safety_bypass_count']}",
                    "安全触发",
                    "negative" if metrics['safety_bypass_count'] > 0 else "positive",
                    "security",
                    "red" if metrics['safety_bypass_count'] > 0 else "green"
                ),
                unsafe_allow_html=True
            )

        with col4:
            st.markdown(
                create_metric_card(
                    "平均上调速率",
                    f"{metrics['avg_up_rate']:.2f} kW/s",
                    f"最大: {metrics['max_up_rate']:.2f}",
                    "neutral",
                    "trending_up",
                    "blue"
                ),
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # 第二行指标
        col5, col6, col7, col8 = st.columns(4)

        with col5:
            st.markdown(
                create_metric_card(
                    "平均下调速率",
                    f"{metrics['avg_down_rate']:.2f} kW/s",
                    f"最大: {metrics['max_down_rate']:.2f}",
                    "neutral",
                    "trending_down",
                    "green"
                ),
                unsafe_allow_html=True
            )

        # 继续下一部分 - 可视化图表
        st.markdown("---")
        st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">show_chart</span>时间序列对比图</h2>', unsafe_allow_html=True)

        # 图表显示选项
        with st.expander("图表显示选项", expanded=False):
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                show_stukf = st.checkbox("显示 STUKF 预测", value=False)
                show_bounds = st.checkbox("显示安全/性能上界", value=True)
            with col_opt2:
                chart_height = st.slider("图表高度", 400, 800, 600, 50)
                show_debug = st.checkbox("显示调试信息", value=False)

        # 如果启用调试，显示关键计算步骤
        if show_debug:
            st.markdown("### 🔍 算法计算详情（随机采样10个时间点）")

            # 随机采样10个点显示
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

            debug_df = pd.DataFrame(debug_data)
            st.dataframe(debug_df, use_container_width=True)

            # 显示关键公式
            st.markdown("""
            **计算公式**:
            - `安全上界 U_A = 置信下界 - Buffer`
            - `性能上界 U_B = 预测均值 - Buffer`
            - `PV指令 P_cmd ≤ min(U_A, P_max)`

            **如果 PV指令 = P_max**:
            - 说明 `U_A ≥ P_max`
            - 即 `负载 - Buffer ≥ P_max`
            - 建议检查：负载数据是否过大 或 P_max 设置是否正确
            """)

        # 创建时间序列图
        fig_timeseries = create_time_series_plot(
            history,
            show_stukf=show_stukf,
            show_bounds=show_bounds,
            height=chart_height
        )
        st.plotly_chart(fig_timeseries, use_container_width=True)

        # ===== 控制效果分析 =====
        st.markdown("---")
        st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">insights</span>控制效果分析</h2>', unsafe_allow_html=True)

        fig_effectiveness = create_control_effectiveness_plot(history, height=500)
        st.plotly_chart(fig_effectiveness, use_container_width=True)

        # ===== 弃光分析 =====
        st.markdown("---")
        st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">wb_sunny</span>弃光分析</h2>', unsafe_allow_html=True)

        # 从会话状态获取 P_max
        params_used = st.session_state.get('params_used', None)
        P_max_val = params_used.P_max if params_used else 100.0

        fig_curtailment = create_curtailment_analysis(history, P_max_val, height=400)
        st.plotly_chart(fig_curtailment, use_container_width=True)

        # ===== 变化率分布 =====
        st.markdown("---")
        st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">bar_chart</span>变化率分布统计</h2>', unsafe_allow_html=True)

        fig_ramp = create_ramp_rate_distribution(history, height=400)
        st.plotly_chart(fig_ramp, use_container_width=True)

        # ===== 数据下载 =====
        st.markdown("---")
        st.markdown('<h2><span class="material-icons" style="vertical-align: middle; margin-right: 8px;">download</span>导出数据</h2>', unsafe_allow_html=True)

        col_d1, col_d2 = st.columns(2)

        with col_d1:
            # 导出仿真结果
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
            st.download_button(
                label="下载仿真结果 (CSV)",
                data=csv,
                file_name="v5_simulation_results.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )

        with col_d2:
            # 导出性能指标
            metrics_df = pd.DataFrame([metrics])
            metrics_csv = metrics_df.to_csv(index=False)

            st.download_button(
                label="下载性能指标 (CSV)",
                data=metrics_csv,
                file_name="v5_performance_metrics.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )

    else:
        # 欢迎界面
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

        上传的数据文件支持以下格式：

        **方式 1: 标准格式（推荐）**
        ```
        时间戳, UTC时间, 设备地址, 设备类型, 负载数据
        1, 2024-01-01 00:00:00, 001, PV, 45.2
        2, 2024-01-01 00:00:01, 001, PV, 46.1
        ...
        ```

        **方式 2: 简化格式**
        ```
        UTC时间, 负载数据
        2024-01-01 00:00:00, 45.2
        2024-01-01 00:00:01, 46.1
        ...
        ```

        **支持的列名**（自动识别）:
        - **时间列**: UTC时间, UTC, time, 时间, 时间戳, timestamp, datetime
        - **负载列**: 负载数据, load, 负载, power, 功率, kW

        **文件格式**: CSV, Excel (.xlsx, .xls)

        ### 💡 提示

        - 系统会自动识别列名，无需严格匹配
        - UTC时间会自动转换为相对时间（秒）
        - 负载数据单位：千瓦（kW）
        - 如有无效数据，系统会自动清洗并提示
        """)

        # 显示示例数据预览
        with st.expander("查看示例数据格式", expanded=False):
            sample_data = pd.DataFrame({
                '时间戳': [1, 2, 3, 4, 5],
                'UTC时间': [
                    '2024-01-01 00:00:00',
                    '2024-01-01 00:00:01',
                    '2024-01-01 00:00:02',
                    '2024-01-01 00:00:03',
                    '2024-01-01 00:00:04'
                ],
                '设备地址': ['001', '001', '001', '001', '001'],
                '设备类型': ['PV', 'PV', 'PV', 'PV', 'PV'],
                '负载数据': [45.2, 46.1, 44.8, 47.3, 45.9]
            })
            st.dataframe(sample_data, use_container_width=True)


if __name__ == "__main__":
    main()
