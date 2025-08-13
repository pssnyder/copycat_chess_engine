@echo off
REM Build script for Copycat Chess Engine v0.5 BETA
REM This script creates a standalone executable for Arena chess GUI compatibility

echo ========================================
echo Building Copycat Chess Engine v0.5 BETA
echo ========================================

REM Set build configuration
set VERSION=v0.5_BETA
set ENGINE_NAME=CopycatChessEngine_v0.5_BETA
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

REM Look for models in various locations and copy if needed
echo Searching for required model files...

REM Check for RL models first
if exist "rl_actor_model.pth" (
    echo Found RL models in current directory
    set MODEL_TYPE=RL
) else (
    echo RL models not found, looking for traditional models...
    
    REM Try to find models in parent directories
    if exist "..\v0.3_copycat_enhanced_ai\v7p3r_chess_ai_model.pth" (
        echo Using models from v0.3...
        copy "..\v0.3_copycat_enhanced_ai\v7p3r_chess_ai_model.pth" . >nul 2>&1
        copy "..\v0.3_copycat_enhanced_ai\move_vocab.pkl" . >nul 2>&1
        set MODEL_TYPE=TRADITIONAL
    ) else if exist "..\v0.2_copycat_eval_ai\v7p3r_chess_ai_model.pth" (
        echo Using models from v0.2...
        copy "..\v0.2_copycat_eval_ai\v7p3r_chess_ai_model.pth" . >nul 2>&1
        copy "..\v0.2_copycat_eval_ai\move_vocab.pkl" . >nul 2>&1
        set MODEL_TYPE=TRADITIONAL
    ) else if exist "..\v0.1_copycat_ai\v7p3r_chess_ai_model.pth" (
        echo Using models from v0.1...
        copy "..\v0.1_copycat_ai\v7p3r_chess_ai_model.pth" . >nul 2>&1
        copy "..\v0.1_copycat_ai\move_vocab.pkl" . >nul 2>&1
        set MODEL_TYPE=TRADITIONAL
    ) else if exist "..\..\rl_actor_model.pth" (
        echo Using RL models from main directory...
        copy "..\..\rl_actor_model.pth" . >nul 2>&1
        copy "..\..\rl_critic_model.pth" . >nul 2>&1
        copy "..\..\training_stats.json" . >nul 2>&1
        set MODEL_TYPE=RL
    ) else (
        echo ERROR: No model files found in any location!
        echo Please ensure model files exist in one of the parent version directories.
        pause
        exit /b 1
    )
)

REM Build the executable with appropriate data files
if "%MODEL_TYPE%"=="RL" (
    echo Building with RL models...
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
    echo Building with traditional models...
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
    echo Model type used: %MODEL_TYPE%
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
