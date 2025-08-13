@echo off
echo Copycat Chess Engine - Dependency Checker
echo ========================================
echo.

python check_dependencies.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Error: Dependency check failed.
    echo Please install the required dependencies and try again.
    pause
    exit /b 1
)

echo.
echo All dependencies are installed. Ready to run Copycat Chess Engine!
echo.
pause
