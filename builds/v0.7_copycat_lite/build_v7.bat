@echo off
REM Simple build script for Copycat Chess Engine v0.7
REM Lightweight, tournament-ready executable

echo ========================================
echo Building Copycat Chess Engine v0.7
echo ========================================

set ENGINE_NAME=CopycatChessEngine_v0.7
set UCI_MAIN=copycat_v7_uci.py
set OUTPUT_DIR=release

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist %ENGINE_NAME%.spec del %ENGINE_NAME%.spec

echo Creating lightweight build...

REM Minimal build with only essential dependencies
pyinstaller --onefile ^
    --name %ENGINE_NAME% ^
    --distpath %OUTPUT_DIR% ^
    --console ^
    --optimize 2 ^
    --exclude-module tensorflow ^
    --exclude-module matplotlib ^
    --exclude-module pandas ^
    --exclude-module scipy ^
    --exclude-module PIL ^
    --exclude-module jupyter ^
    --exclude-module notebook ^
    --exclude-module sympy ^
    --exclude-module setuptools ^
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

REM Clean up
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__

REM Report results
if exist "%OUTPUT_DIR%\%ENGINE_NAME%.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    
    REM Get file size
    for %%F in ("%OUTPUT_DIR%\%ENGINE_NAME%.exe") do (
        set size=%%~zF
        set /a sizeMB=!size!/1048576
    )
    
    echo Engine: %OUTPUT_DIR%\%ENGINE_NAME%.exe
    echo Size: !sizeMB! MB
    echo.
    echo Features:
    echo - Neural network + evaluation hybrid
    echo - Fast tournament-ready performance
    echo - Arena chess GUI compatible
    echo - Graceful fallbacks for robustness
    echo.
    echo Ready for testing!
    echo ========================================
) else (
    echo ERROR: Build failed - executable not found
    pause
    exit /b 1
)

pause
