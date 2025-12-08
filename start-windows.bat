@echo off
REM Windows 启动脚本

echo ==========================================
echo 51CTO Backend - 启动服务
echo ==========================================
echo.

REM 检查是否已安装依赖
python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo X Playwright 未安装
    echo.
    echo 请先运行安装脚本：
    echo   setup-windows.bat
    echo.
    pause
    exit /b 1
)

echo 启动服务器...
echo.
echo 访问地址：
echo   - API 文档: http://localhost:8002/docs
echo   - 健康检查: http://localhost:8002/health
echo.
echo 按 Ctrl+C 停止服务器
echo.
echo ==========================================
echo.

python run.py

pause
