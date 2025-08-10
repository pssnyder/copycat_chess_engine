@echo off
echo Copycat Chess Engine - Test Suite
echo ================================
echo.

REM Get the directory of the batch file
SET script_dir=%~dp0

cd /d "%script_dir%"

echo Running engine tests...
python tests\test_engine.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Some tests failed. Please fix the issues before building the executable.
    echo.
    pause
    exit /b 1
)

echo.
echo All tests passed! The engine is working properly.
echo.
pause
