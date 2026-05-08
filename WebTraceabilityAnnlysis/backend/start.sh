#!/bin/bash

echo "========================================"
echo "海洋垃圾溯源分析后端服务启动脚本"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[1/3] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.8+"
    echo "下载地址: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python环境正常"
python3 --version
echo ""

echo "[2/3] 安装依赖包..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败，请检查requirements.txt"
    exit 1
fi

echo "✅ 依赖安装完成"
echo ""

echo "[3/3] 启动后端服务..."
echo ""
echo "========================================"
echo "🌊 海洋垃圾溯源分析API"
echo "========================================"
echo ""
echo "服务地址: http://localhost:8080/trace"
echo "健康检查: http://localhost:8080/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

python3 trace_api.py
