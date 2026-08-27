@echo off
setlocal

cd /d "%~dp0"

echo ==========================================
echo       Payload Carrier
echo ==========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found.
    echo Please run install.bat first.
    pause
    exit /b 1
)

echo Starting Payload Carrier...
echo.

".venv\Scripts\python.exe" main.py

if errorlevel 1 (
    echo.
    echo ==========================================
    echo       Program exited with an error
    echo ==========================================
    pause
)

endlocal
