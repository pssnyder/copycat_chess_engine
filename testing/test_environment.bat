@echo off
rem test_environment.bat - Runs tests to diagnose Python environment issues

echo Running Python environment tests...
echo Results will be saved to environment_test_results.txt
echo.

rem Try to use the VS Code selected Python interpreter if available
if defined PYTHONPATH (
    echo Using VS Code selected Python interpreter...
    "%PYTHONPATH%" test_imports.py > environment_test_results.txt 2>&1
) else (
    rem Get Python executable path
    for /f "tokens=*" %%i in ('where python') do set PYTHON_EXE=%%i
    echo Using Python found in PATH: %PYTHON_EXE%
    "%PYTHON_EXE%" test_imports.py > environment_test_results.txt 2>&1
)

echo Test completed. Opening results...
echo.

notepad environment_test_results.txt

echo.
echo VS Code Terminal Python Settings:
echo -------------------------------
echo If the terminal is using a different Python version than the editor:
echo.
echo 1. Open VS Code settings (Ctrl+,)
echo 2. Search for "terminal.integrated.defaultProfile.windows"
echo 3. Set it to "Command Prompt" or "PowerShell"
echo 4. Search for "python.terminal.activateEnvironment"
echo 5. Make sure it's checked (true)
echo 6. Open a new terminal (the old one won't be affected)
echo.
pause
