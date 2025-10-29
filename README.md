# 防逆流控制系统 V2.0

基于 STUKF 算法的光伏防逆流控制可视化平台（优化重构版）

## 🎯 项目概述

这是一个基于 **STUKF（平滑趋势无迹卡尔曼滤波器）** 的光伏防逆流控制算法可视化平台，用于实时预测负载并控制光伏发电，防止电力逆流到电网。

## ✨ V2.0 优化内容

### 代码质量提升
- ✅ **消除冗余代码** - 删除 200+ 行重复样式代码
- ✅ **模块化重构** - 将 935 行的单文件拆分为多个 <300 行的模块
- ✅ **清晰的目录结构** - src/docs/scripts 分离
- ✅ **统一的代码规范** - 所有文件符合 <300 行标准

### 架构改进
```
旧版 (1015+ 行混乱)  →  新版 (模块化、清晰)
app.py (935行)       →  多个功能模块
styles + material    →  统一样式系统
混乱的文档          →  docs/ 目录整理
```

## 📁 项目结构

```
fnl_v2/
├── src/                          # 源代码目录
│   ├── core/                     # 核心算法
│   │   ├── stukf.py             # STUKF 滤波器
│   │   └── v5_anti_backflow.py  # V5 防逆流控制器
│   ├── ui/                       # 用户界面
│   │   ├── app.py               # 主应用（精简版）
│   │   ├── visualization.py     # 可视化（优化版）
│   │   ├── visualization_base.py # 可视化基础配置
│   │   ├── components/          # UI组件
│   │   │   └── metric_card.py
│   │   └── styles/              # 样式系统
│   │       └── styles.py
│   └── utils/                    # 工具模块
│       ├── data_processing.py    # 数据处理
│       ├── metrics.py            # 性能指标计算
│       └── simulation.py         # 仿真运行
├── docs/                         # 文档目录
│   ├── README.md                 # 主文档
│   ├── QUICKSTART.md             # 快速开始
│   └── guides/                   # 指南文档
│       ├── 算法架构.txt
│       └── 需求.txt
├── scripts/                      # 启动脚本
│   ├── init.sh / init.bat       # 初始化脚本
│   └── run.sh / run.bat         # 运行脚本
├── debug/                        # 调试工具
│   └── debug_pcmd.py
├── logs/                         # 日志目录
├── main.py                       # 主入口
├── requirements.txt              # 依赖清单
└── CLAUDE.md                     # 开发规范
```

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.8+ 和 uv：

```bash
pip install uv
```

### 2. 初始化项目

**Windows:**
```bash
scripts\init.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/init.sh
./scripts/init.sh
```

### 3. 运行应用

**Windows:**
```bash
scripts\run.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

或直接运行：
```bash
python main.py
```

应用将在浏览器中自动打开：http://localhost:8501

## 📊 功能特点

### 核心功能
- ✅ **实时负载预测** - 基于 STUKF 算法的高精度预测
- ✅ **防逆流控制** - 智能 PV 限发指令生成
- ✅ **非对称限速保护** - 上行/下行速率独立控制
- ✅ **安全旁路机制** - 紧急情况自动触发
- ✅ **动态安全策略** - 趋势自适应 + 局部不确定性

### 可视化分析
- 📈 时间序列对比图
- 📊 变化率分布统计
- ☀️ 弃光分析
- 🎯 控制效果对比
- 📉 性能指标展示

### 交互式配置
- 🎛️ 控制参数实时调整
- 📁 数据文件上传（CSV/Excel）
- 🎲 示例数据生成
- 💾 结果导出下载

## 📄 数据格式

### 支持的文件格式
- CSV (.csv)
- Excel (.xlsx, .xls)

### 列名识别（自动）
- **时间列**: UTC时间, UTC, time, 时间, timestamp, datetime
- **负载列**: 负载数据, load, 负载, power, 功率, kW

### 示例数据格式
```csv
UTC时间,负载数据
2024-01-01 00:00:00,45.2
2024-01-01 00:00:01,46.1
2024-01-01 00:00:02,44.8
```

## 🔧 核心算法

### STUKF（平滑趋势无迹卡尔曼滤波器）
- 状态向量：[L, dL/dt, d²L/dt²]
- 无迹变换（Unscented Transform）
- 记忆衰减因子可调

### V5 防逆流控制
- 双上界策略：安全上界 U_A + 性能上界 U_B
- 动态安全策略：趋势自适应 + 局部不确定性
- 非对称限速：R_up ≠ R_down

## 📈 性能指标

系统自动计算以下关键指标：
- 总弃光量（kWh）
- 弃光率（%）
- 安全旁路触发次数
- 平均/最大上调速率
- 平均/最大下调速率

## 🏗️ 技术栈

- **前端**: Streamlit
- **可视化**: Plotly
- **算法**: NumPy, SciPy
- **数据处理**: Pandas
- **样式**: Google Material Design

## 📝 代码质量标准

遵循项目 CLAUDE.md 规范：
- ✅ Python 文件 ≤ 300 行
- ✅ 每个文件夹 ≤ 8 个文件
- ✅ 强类型数据结构
- ✅ 使用 uv 管理依赖
- ✅ 清晰的模块职责划分

## 🔍 调试工具

位于 `debug/` 目录：
- `debug_pcmd.py` - P_cmd 计算过程诊断工具

## 📚 文档

详细文档位于 `docs/` 目录：
- [README.md](docs/README.md) - 完整项目文档
- [QUICKSTART.md](docs/QUICKSTART.md) - 快速开始指南
- [guides/](docs/guides/) - 算法架构和需求文档

## 🎨 UI 截图

应用采用 Google Material Design 设计语言，提供：
- 🎨 现代化界面
- 📱 响应式布局
- 🎯 清晰的指标卡片
- 📊 交互式图表

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📮 联系方式

项目维护者：[Your Name]

---

**版本**: 2.0.0
**最后更新**: 2025-10-28
**优化完成**: 代码重构 + 模块化 + 文档整理
