@echo off
rem Copycat_UCI.bat - Launcher for Copycat Chess Engine for Arena Chess GUI
rem This batch file starts the UCI chess engine for use with Arena

rem Change to the directory containing the script
cd /d "%~dp0"

rem Run the Python UCI interface
python copycat_uci.py

rem If Python exits with an error, pause to show the error message
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Engine terminated with error code %ERRORLEVEL%
    pause
)
