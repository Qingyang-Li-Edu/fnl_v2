@echo off
REM 运行防逆流控制系统

echo ===================================
echo  防逆流控制系统
echo ===================================
echo.
echo 正在启动...
echo.

REM 运行应用
uv run streamlit run src/ui/app.py --server.port=8501

echo.
echo 应用已停止
pause
