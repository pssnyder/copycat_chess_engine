@echo off
echo Copycat Chess Engine - UCI Manual Test
echo ===================================
echo.
echo This script will start the Copycat Chess Engine in UCI mode 
echo and send basic UCI commands to test its functionality.
echo.
echo Press any key to start the test...
pause > nul

echo.
echo Starting UCI engine and running test commands...
echo.

REM Create a temporary file with UCI commands
set "temp_commands=%TEMP%\uci_commands.txt"
echo uci > "%temp_commands%"
echo isready >> "%temp_commands%"
echo ucinewgame >> "%temp_commands%"
echo position startpos moves e2e4 e7e5 >> "%temp_commands%"
echo go depth 5 >> "%temp_commands%"
echo quit >> "%temp_commands%"

REM Get the directory of the batch file
SET script_dir=%~dp0

REM Run the engine with the commands
type "%temp_commands%" | python "%script_dir%copycat_uci.py"

REM Delete the temporary file
del "%temp_commands%"

echo.
echo UCI test completed.
echo.
pause
