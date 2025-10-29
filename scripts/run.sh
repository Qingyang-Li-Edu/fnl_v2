#!/bin/bash
# 运行防逆流控制系统

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到 uv"
    echo "请先安装 uv: pip install uv"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "错误: 虚拟环境未初始化"
    echo "请先运行: ./scripts/init.sh"
    exit 1
fi

echo "==================================="
echo " 防逆流控制系统"
echo "==================================="
echo ""
echo "正在启动..."
echo ""

# 设置PYTHONPATH并使用uv运行应用
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uv run streamlit run src/ui/app.py --server.port=8501

echo ""
echo "应用已停止"
