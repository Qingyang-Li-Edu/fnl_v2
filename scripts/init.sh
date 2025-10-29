#!/bin/bash
# 初始化Python虚拟环境和依赖

echo "==================================="
echo " 项目初始化"
echo "==================================="
echo ""

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到 uv"
    echo "请先安装 uv: pip install uv"
    exit 1
fi

# 创建虚拟环境
echo "创建虚拟环境..."
uv venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
echo "安装依赖..."
uv pip install -r requirements.txt

echo ""
echo "初始化完成！"
echo "请运行 './scripts/run.sh' 启动应用"
