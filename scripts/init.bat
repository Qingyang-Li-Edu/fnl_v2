@echo off
REM 初始化Python虚拟环境和依赖

echo ===================================
echo  项目初始化
echo ===================================
echo.

REM 检查uv是否安装
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未找到 uv
    echo 请先安装 uv: pip install uv
    pause
    exit /b 1
)

REM 创建虚拟环境
echo 创建虚拟环境...
uv venv .venv

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
uv pip install -r requirements.txt

echo.
echo 初始化完成！
echo 请运行 'scripts\run.bat' 启动应用
pause
