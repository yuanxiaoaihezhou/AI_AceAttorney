@echo off
REM 启动 AI 逆转裁判 Web 版

echo ==================================
echo AI 逆转裁判 Web 版启动脚本
echo ==================================
echo.

REM 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

echo 使用 Python: python
echo.

REM 检查依赖
echo 检查依赖...
python -c "import flask" >nul 2>nul
if %errorlevel% neq 0 (
    echo Flask 未安装，正在安装依赖...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

echo 依赖检查完成
echo.

REM 启动 Web 服务器
echo 启动 Web 服务器...
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止服务器
echo.

python web_app.py
pause
