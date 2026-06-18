@echo off
REM Antigravity Pipeline - Build Script for PyInstaller
REM This script creates a standalone executable (pipeline.exe)

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ========================================
echo Antigravity Pipeline - Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo Step 1: Installing PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo Step 2: Building standalone executable...
echo This may take a few minutes...
echo.

REM Build with PyInstaller
pyinstaller --onefile ^
    --windowed ^
    --name pipeline ^
    --add-data "bin:bin" ^
    --add-data "config.py:." ^
    --hidden-import=tkinter ^
    --hidden-import=cv2 ^
    --hidden-import=PIL ^
    --collect-all pdf2image ^
    --collect-all scenedetect ^
    --collect-all cv2 ^
    main.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Successful!
echo ========================================
echo.
echo Executable created: dist\pipeline.exe
echo.
echo Next steps:
echo 1. Copy dist\pipeline.exe to your desired location
echo 2. Create folders: SOURCE, VIDEOS (alongside the .exe)
echo 3. Double-click pipeline.exe to launch
echo.
pause
