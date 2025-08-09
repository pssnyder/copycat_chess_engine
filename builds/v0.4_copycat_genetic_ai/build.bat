@echo off
REM Build script for Copycat Chess Engine v0.4 Genetic AI
REM This script creates a standalone executable for Arena chess GUI compatibility

echo ========================================
echo Building Copycat Chess Engine v0.4 Genetic AI
echo ========================================

REM Set build configuration
set VERSION=v0.4
set ENGINE_NAME=CopycatChessEngine_v0.4_Genetic
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
REM Include RL models if they exist, otherwise fallback to parent models
pyinstaller --onefile ^
    --name %ENGINE_NAME% ^
    --distpath %OUTPUT_DIR% ^
    --workpath build ^
    --specpath . ^
    --console ^
    --add-data "config.yaml;." ^
    --hidden-import torch ^
    --hidden-import chess ^
    --hidden-import numpy ^
    %UCI_MAIN%

REM Check if RL models exist and add them
if exist "rl_actor_model.pth" (
    echo Adding RL actor model...
    pyinstaller --onefile ^
        --name %ENGINE_NAME% ^
        --distpath %OUTPUT_DIR% ^
        --workpath build ^
        --specpath . ^
        --console ^
        --add-data "rl_actor_model.pth;." ^
        --add-data "rl_critic_model.pth;." ^
        --add-data "config.yaml;." ^
        --hidden-import torch ^
        --hidden-import chess ^
        --hidden-import numpy ^
        %UCI_MAIN%
) else (
    echo RL models not found, checking for traditional models...
    REM Try to find models in parent directories
    if exist "..\v0.3_copycat_enhanced_ai\v7p3r_chess_ai_model.pth" (
        echo Using models from v0.3...
        copy "..\v0.3_copycat_enhanced_ai\v7p3r_chess_ai_model.pth" .
        copy "..\v0.3_copycat_enhanced_ai\move_vocab.pkl" .
    ) else if exist "..\v0.2_copycat_eval_ai\v7p3r_chess_ai_model.pth" (
        echo Using models from v0.2...
        copy "..\v0.2_copycat_eval_ai\v7p3r_chess_ai_model.pth" .
        copy "..\v0.2_copycat_eval_ai\move_vocab.pkl" .
    ) else if exist "..\v0.1_copycat_ai\v7p3r_chess_ai_model.pth" (
        echo Using models from v0.1...
        copy "..\v0.1_copycat_ai\v7p3r_chess_ai_model.pth" .
        copy "..\v0.1_copycat_ai\move_vocab.pkl" .
    )
    
    REM Rebuild with found models
    if exist "v7p3r_chess_ai_model.pth" (
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
    )
)

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
