# CopycatUCI.cmd - Command script for Arena to launch Copycat Chess Engine
@echo off
setlocal

rem Change to the directory containing the script
cd /d "%~dp0"

rem Get Python executable path
for /f "tokens=*" %%i in ('where python') do set PYTHON_EXE=%%i

rem If Python is not found, try python3
if not defined PYTHON_EXE (
    for /f "tokens=*" %%i in ('where python3') do set PYTHON_EXE=%%i
)

rem If still not found, use default path
if not defined PYTHON_EXE (
    set PYTHON_EXE=python
)

rem Check for required packages quietly
"%PYTHON_EXE%" -c "import torch, chess, numpy" > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Some required packages are missing.
    echo Please run: %PYTHON_EXE% -m pip install -r requirements.txt
    pause
)

rem Display information
echo Copycat Chess Engine v0.5.31
echo Running on: %PYTHON_EXE%
echo CUDA available: 
"%PYTHON_EXE%" -c "import torch; print(torch.cuda.is_available())"
echo.

rem Run the UCI interface
"%PYTHON_EXE%" copycat_uci.py

rem If the command fails, show error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Engine exited with error code: %ERRORLEVEL%
    echo.
    echo Common issues:
    echo - Python not installed or not in PATH
    echo - Required packages not installed (torch, numpy, python-chess)
    echo - Missing model files
    echo.
    echo To install required packages:
    echo %PYTHON_EXE% -m pip install torch numpy python-chess
    echo.
    pause
)

endlocal
