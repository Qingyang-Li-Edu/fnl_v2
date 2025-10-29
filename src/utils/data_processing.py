"""
数据处理模块 - 负载数据加载和生成
"""

import pandas as pd
import numpy as np
import streamlit as st


def load_data(uploaded_file) -> pd.DataFrame:
    """加载负载数据，支持多种列名格式，并进行数据清洗（保留真实数据，仅处理异常值和缺失值）"""
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
            st.info("🔧 正在进行数据清洗...")

            # 1. 处理异常大的值 (> 10000) - 标记为 NaN
            result_df.loc[result_df['load_raw'] > 10000, 'load_raw'] = np.nan

            # 2. 处理负值 - 标记为 NaN
            result_df.loc[result_df['load_raw'] < 0, 'load_raw'] = np.nan

            # 3. 前向填充处理缺失值
            result_df['load'] = result_df['load_raw'].fillna(method='ffill')

            # 4. 如果开头有缺失值，使用后向填充
            result_df['load'] = result_df['load'].fillna(method='bfill')

            # 5. 如果仍有缺失值，用0填充
            if result_df['load'].isna().any():
                st.warning("部分数据无法填充，使用0替代")
                result_df['load'] = result_df['load'].fillna(0)

            # 6. 最终检查：确保负载值在合理范围内
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

        # 显示处理前后对比
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

    impulse_types = [
        {'power': 7.5, 'duration': 4, 'freq': 0.015},
        {'power': 12.0, 'duration': 5, 'freq': 0.012},
        {'power': 15.5, 'duration': 6, 'freq': 0.008},
        {'power': 9.0, 'duration': 3, 'freq': 0.010},
    ]

    for impulse_type in impulse_types:
        i = 0
        while i < num_points:
            if np.random.random() < impulse_type['freq']:
                duration = int(impulse_type['duration'] * (1 + np.random.uniform(-0.3, 0.3)))
                power = impulse_type['power'] * (1 + np.random.uniform(-0.2, 0.2))

                for j in range(duration):
                    if i + j >= num_points:
                        break
                    if j == 0:
                        equipment_impulses[i + j] += power * 0.6
                    elif j == 1:
                        equipment_impulses[i + j] += power * 1.0
                    elif j < duration - 1:
                        equipment_impulses[i + j] += power * 0.9
                    else:
                        equipment_impulses[i + j] += power * 0.5

                i += duration + np.random.randint(3, 10)
            else:
                i += 1

    # === 小幅随机噪声 ===
    small_noise = np.random.normal(0, 1.5, num_points)

    # === 合成最终负载 ===
    load_array = base_load + equipment_impulses + small_noise
    load_array = np.maximum(load_array, 5)

    df = pd.DataFrame({
        'time': time_array,
        'load': load_array
    })

    return df
