#!/bin/bash
# 启动 AI 逆转裁判 Web 版

echo "=================================="
echo "AI 逆转裁判 Web 版启动脚本"
echo "=================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "错误: 未找到 Python，请先安装 Python 3.7+"
    exit 1
fi

# 使用 python3 或 python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "使用 Python: $PYTHON_CMD"
echo ""

# 检查依赖
echo "检查依赖..."
$PYTHON_CMD -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Flask 未安装，正在安装依赖..."
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 依赖安装失败"
        exit 1
    fi
fi

echo "依赖检查完成"
echo ""

# 启动 Web 服务器
echo "启动 Web 服务器..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务器"
echo ""

$PYTHON_CMD web_app.py
