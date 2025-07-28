@echo off
rem fix_terminal_interpreter.bat - Helps configure VS Code to use the correct Python interpreter in terminals

echo VS Code Terminal Python Interpreter Fixer
echo ========================================
echo.
echo This script will help you ensure that VS Code terminals use the same Python interpreter
echo as the one selected for your editor.
echo.

rem Print the current Python in PATH
for /f "tokens=*" %%i in ('where python') do set PYTHON_PATH=%%i
echo Current Python in PATH: %PYTHON_PATH%
echo.

rem Check Python version
python --version
echo.

rem Create a settings file with the correct terminal settings
echo Creating VS Code settings to fix terminal interpreter...
echo.

if not exist .vscode (
    mkdir .vscode
    echo Created .vscode directory
)

rem Check if settings.json exists
set SETTINGS_FILE=.vscode\settings.json
if exist %SETTINGS_FILE% (
    echo Existing settings.json found, creating backup...
    copy %SETTINGS_FILE% %SETTINGS_FILE%.backup
    echo Created backup at %SETTINGS_FILE%.backup
)

rem Create or update settings file with terminal settings
echo {
echo     "python.terminal.activateEnvironment": true,
echo     "terminal.integrated.defaultProfile.windows": "Command Prompt",
echo     "python.analysis.diagnosticSeverityOverrides": {
echo         "reportMissingImports": "none",
echo         "reportOptionalMemberAccess": "none"
echo     }
echo } > %SETTINGS_FILE%

echo.
echo Settings updated. Please follow these steps:
echo 1. Close all VS Code terminal windows
echo 2. Reload VS Code window (Ctrl+Shift+P then "Developer: Reload Window")
echo 3. Open a new terminal and check the Python version again
echo.
echo If the issue persists, try these additional steps:
echo 1. Open VS Code Command Palette (Ctrl+Shift+P)
echo 2. Type "Python: Select Interpreter" and choose the correct Python version
echo 3. Type "Python: Create Terminal" to create a terminal with the selected interpreter
echo.
pause
