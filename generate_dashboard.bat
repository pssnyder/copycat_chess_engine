@echo off
echo Generating Chess Analytics Dashboard with fixed timing and openings charts...
cd /d "%~dp0"
python "analysis\generate_dashboard_final.py"
echo.
echo Dashboard generation complete! The dashboard has been saved to results\chess_dashboard.html
echo Press any key to open the dashboard in your default browser...
pause > nul
start "" "results\chess_dashboard.html"
