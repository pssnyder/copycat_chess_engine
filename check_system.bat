@echo off
rem check_system.bat - Script to check dependencies for Copycat Chess Engine

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

echo Running system check for Copycat Chess Engine...
echo.

"%PYTHON_EXE%" check_dependencies.py

echo.
echo System check complete.
pause
