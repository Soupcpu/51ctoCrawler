@echo off
REM Windows 安装脚本

echo ==========================================
echo 51CTO Backend - Windows 安装
echo ==========================================
echo.

REM 1. 检查 Python
echo 1. 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python 未安装
    echo 请先安装 Python 3.11+: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

REM 2. 安装 Python 依赖
echo 2. 安装 Python 依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo X 依赖安装失败
    pause
    exit /b 1
)
echo √ Python 依赖安装成功
echo.

REM 3. 安装 Playwright 浏览器
echo 3. 安装 Playwright 浏览器...
echo    这可能需要几分钟...
playwright install chromium
if errorlevel 1 (
    echo X Playwright 浏览器安装失败
    echo 尝试使用: python -m playwright install chromium
    pause
    exit /b 1
)
echo √ Playwright 浏览器安装成功
echo.

echo ==========================================
echo √ 安装完成！
echo ==========================================
echo.
echo 现在可以运行：
echo   start-windows.bat
echo.
pause
