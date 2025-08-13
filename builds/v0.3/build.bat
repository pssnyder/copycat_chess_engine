@echo off
REM Build script for Copycat Chess Engine v0.3 Enhanced AI
REM This script creates a standalone executable for Arena chess GUI compatibility

echo ========================================
echo Building Copycat Chess Engine v0.3 Enhanced AI
echo ========================================

REM Set build configuration
set VERSION=v0.3
set ENGINE_NAME=CopycatChessEngine_v0.3_Enhanced
set UCI_MAIN=copycat_uci.py
set OUTPUT_DIR=release

REM Check if PyInstaller is available
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ERROR: PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Create output directory
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist %ENGINE_NAME%.spec del %ENGINE_NAME%.spec

echo Building executable...

REM Build the executable with PyInstaller
pyinstaller --onefile ^
    --name %ENGINE_NAME% ^
    --distpath %OUTPUT_DIR% ^
    --workpath build ^
    --specpath . ^
    --console ^
    --add-data "v7p3r_chess_ai_model.pth;." ^
    --add-data "move_vocab.pkl;." ^
    --add-data "config.yaml;." ^
    --hidden-import torch ^
    --hidden-import chess ^
    --hidden-import numpy ^
    %UCI_MAIN%

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

REM Clean temporary files
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__

REM Verify the executable was created
if exist "%OUTPUT_DIR%\%ENGINE_NAME%.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo Executable created: %OUTPUT_DIR%\%ENGINE_NAME%.exe
    echo Ready for Arena chess GUI testing
    echo.
    echo To test with Arena:
    echo 1. Copy the .exe to your Arena engines folder
    echo 2. Add engine in Arena with UCI protocol
    echo 3. Select the .exe file as the engine path
    echo ========================================
) else (
    echo ERROR: Executable not found after build
    pause
    exit /b 1
)

pause
