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
    if /i "%PIPELINE_BUILD_PAUSE%"=="1" pause
    exit /b 1
)

echo Step 1: Installing Python dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies from requirements.txt
    if /i "%PIPELINE_BUILD_PAUSE%"=="1" pause
    exit /b 1
)

echo Step 1.5: Checking Tkinter GUI support...
python -c "import tkinter as tk; root=tk.Tk(); root.destroy()" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python Tkinter/Tcl-Tk is not working, so the GUI executable cannot be built correctly.
    echo Repair or reinstall Python and include the Tcl/Tk and IDLE optional feature, then run build.bat again.
    if /i "%PIPELINE_BUILD_PAUSE%"=="1" pause
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
    --hidden-import=fitz ^
    --collect-all fitz ^
    --collect-all pdf2image ^
    --collect-all scenedetect ^
    --collect-all cv2 ^
    main.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    if /i "%PIPELINE_BUILD_PAUSE%"=="1" pause
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
if /i "%PIPELINE_BUILD_PAUSE%"=="1" pause
