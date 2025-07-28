@echo off
rem CopycatUCI_VSCode.bat - Command script for Arena to launch Copycat Chess Engine
rem This version is designed to use the VS Code selected Python interpreter

setlocal

rem Change to the directory containing the script
cd /d "%~dp0"

rem Try to get the VS Code selected Python interpreter if available
set VSCODE_PYTHON=""

rem Look for the interpreter path in .vscode/settings.json
if exist .vscode\settings.json (
    for /f "tokens=*" %%i in ('findstr "python.defaultInterpreterPath" .vscode\settings.json') do (
        set INTERPRETER_LINE=%%i
        set INTERPRETER_LINE=!INTERPRETER_LINE:"python.defaultInterpreterPath": "=!
        set INTERPRETER_LINE=!INTERPRETER_LINE:"=!
        set INTERPRETER_LINE=!INTERPRETER_LINE:,=!
        set VSCODE_PYTHON=!INTERPRETER_LINE!
    )
)

rem If not found in settings, try the default locations
if %VSCODE_PYTHON%=="" (
    if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
        set VSCODE_PYTHON="%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python38\python.exe" (
        set VSCODE_PYTHON="%LOCALAPPDATA%\Programs\Python\Python38\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
        set VSCODE_PYTHON="%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set VSCODE_PYTHON="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set VSCODE_PYTHON="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    )
)

rem Get Python executable path if not found above
if %VSCODE_PYTHON%=="" (
    for /f "tokens=*" %%i in ('where python') do set VSCODE_PYTHON=%%i
)

rem Display information
echo Copycat Chess Engine v0.5.31
echo Running with Python: %VSCODE_PYTHON%
echo.

rem Check if packages are installed
"%VSCODE_PYTHON%" -c "import torch, chess, numpy" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Required packages are missing!
    echo Installing required packages...
    "%VSCODE_PYTHON%" -m pip install torch numpy python-chess
)

rem Run the UCI interface
"%VSCODE_PYTHON%" copycat_uci.py

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
    pause
)

endlocal
