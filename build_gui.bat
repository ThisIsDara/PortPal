@echo off
REM PortPal GUI Server - Quick Build Script
REM This script builds the GUI server into a standalone executable

echo.
echo ========================================
echo  PortPal GUI Builder
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not available
    pause
    exit /b 1
)

echo Installing required packages...
echo.
pip install -r requirements-gui.txt
if errorlevel 1 (
    echo Error: Failed to install packages
    pause
    exit /b 1
)

echo.
echo Building executable...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist PortPal.spec del PortPal.spec

REM Build the executable
pyinstaller --onefile --windowed --name "PortPal" gui_server.py

if errorlevel 1 (
    echo Error: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build Complete!
echo ========================================
echo.
echo Your executable is ready at:
echo   dist/PortPal.exe
echo.
echo You can now:
echo 1. Run the executable directly
echo 2. Share it with others (no Python needed!)
echo 3. Create a shortcut for easy access
echo.
pause
