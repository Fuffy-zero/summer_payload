@echo off
setlocal

echo ==========================================
echo       Payload Carrier - Installer
echo ==========================================
echo.

REM Check Python 3.12
echo [1/6] Checking Python 3.12...
py -3.12 --version
if errorlevel 1 (
    echo.
    echo ERROR: Python 3.12 is not installed.
    echo Please install Python 3.12 first.
    pause
    exit /b 1
)

echo.
echo [2/6] Creating virtual environment...
if exist ".venv" (
    echo .venv already exists. Skipping...
) else (
    py -3.12 -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo.
echo [3/6] Activating virtual environment...
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo.
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip.
    pause
    exit /b 1
)

echo.
echo [5/6] Installing required libraries...
python -m pip install --only-binary=:all: ^
numpy==2.4.3 ^
psutil==7.2.2 ^
lxml==6.0.2 ^
fastcrc==0.3.5 ^
pymavlink==2.4.49 ^
opencv-python==4.13.0.92 ^
mediapipe==0.10.14 ^
keyboard

if errorlevel 1 (
    echo ERROR: Failed to install required libraries.
    pause
    exit /b 1
)

echo.
echo Installing PySide6...
python -m pip install PySide6==6.11.2

if errorlevel 1 (
    echo ERROR: Failed to install PySide6.
    pause
    exit /b 1
)

echo.
echo [6/6] Installing pyhula...
if not exist "pyhula-1.1.8-cp312-cp312-win_amd64.whl" (
    echo ERROR: pyhula wheel not found!
    echo.
    echo Required file:
    echo pyhula-1.1.8-cp312-cp312-win_amd64.whl
    echo.
    pause
    exit /b 1
)

python -m pip install --no-deps "pyhula-1.1.8-cp312-cp312-win_amd64.whl"

if errorlevel 1 (
    echo ERROR: Failed to install pyhula.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo       Installation completed!
echo ==========================================
echo.

echo Checking installed versions...
echo.
python --version
python -m pip show pyhula | findstr "Version:"
python -m pip show PySide6 | findstr "Version:"

echo.
echo Testing pyhula import...
python -c "import pyhula; print('pyhula import: OK')"

if errorlevel 1 (
    echo.
    echo WARNING: pyhula import failed.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo       Payload Carrier is ready!
echo ==========================================
echo.
echo To run the program:
echo     run.bat
echo.
pause