@echo off
REM Optimized build script for Copycat Chess Engine
REM Creates a lightweight executable by excluding unnecessary dependencies

echo ========================================
echo Building Optimized Copycat Chess Engine
echo ========================================

set ENGINE_NAME=CopycatChessEngine_Optimized
set UCI_MAIN=copycat_optimized_uci.py
set OUTPUT_DIR=release

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist %ENGINE_NAME%.spec del %ENGINE_NAME%.spec

echo Creating optimized build...

REM Build with minimal dependencies and exclusions
pyinstaller --onefile ^
    --name %ENGINE_NAME% ^
    --distpath %OUTPUT_DIR% ^
    --workpath build ^
    --specpath . ^
    --console ^
    --optimize 2 ^
    --exclude-module tensorflow ^
    --exclude-module tensorboard ^
    --exclude-module matplotlib ^
    --exclude-module pandas ^
    --exclude-module scipy ^
    --exclude-module sklearn ^
    --exclude-module PIL ^
    --exclude-module cv2 ^
    --exclude-module jupyter ^
    --exclude-module notebook ^
    --exclude-module ipython ^
    --exclude-module sympy ^
    --exclude-module h5py ^
    --exclude-module torchvision ^
    --exclude-module torchaudio ^
    --exclude-module pytest ^
    --exclude-module setuptools ^
    --exclude-module wheel ^
    --exclude-module pip ^
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

REM Check result
if exist "%OUTPUT_DIR%\%ENGINE_NAME%.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    for %%F in ("%OUTPUT_DIR%\%ENGINE_NAME%.exe") do (
        set size=%%~zF
        set /a sizeMB=!size!/1048576
        echo Executable: %OUTPUT_DIR%\%ENGINE_NAME%.exe
        echo Size: !sizeMB! MB
    )
    echo.
    echo Features included:
    echo - UCI protocol support
    echo - Neural network AI (if models available)
    echo - Evaluation engine fallback
    echo - Time management
    echo - Debug mode option
    echo.
    echo Arena Setup:
    echo 1. Copy .exe to Arena engines folder
    echo 2. Add engine with UCI protocol
    echo 3. Engine will auto-detect available models
    echo ========================================
) else (
    echo ERROR: Executable not found after build
    pause
    exit /b 1
)

pause
