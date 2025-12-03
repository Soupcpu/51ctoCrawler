@echo off
chcp 65001 >nul
echo ========================================
echo 51CTO Backend API
echo ========================================
echo.

echo Checking dependencies...
python -c "import fastapi, uvicorn, selenium" 2>nul
if errorlevel 1 (
    echo Dependencies not installed!
    echo Installing...
    pip install -r requirements.txt
)

echo.
echo Starting server...
python run.py

pause
