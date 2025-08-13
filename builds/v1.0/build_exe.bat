@echo off
echo Copycat Chess Engine - Build Executable
echo =====================================
echo.

REM Check dependencies first
echo Checking dependencies...
python check_dependencies.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Error: Dependency check failed.
    echo Please install the required dependencies and try again.
    pause
    exit /b 1
)

REM Run tests
echo.
echo Running tests to ensure everything works...
python tests\test_engine.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Tests failed. Please fix any issues before building the executable.
    pause
    exit /b 1
)

REM Build the executable
echo.
echo Building the executable...
python build_exe.py --onefile --name CopycatChessEngine

if %ERRORLEVEL% neq 0 (
    echo.
    echo Failed to build executable. Check the error messages above.
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo The executable has been created in the 'dist' directory.
echo.
pause
