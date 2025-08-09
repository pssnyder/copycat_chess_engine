@echo off
echo Generating Enhanced Chess Analytics and Decision Logic...
cd /d "%~dp0"

echo Step 1: Running Enhanced Metadata Analysis...
python "analysis\enhanced_metadata_analyzer.py"
echo.

echo Step 2: Creating Decision Flow Diagram...
python "analysis\generate_decision_diagram.py"
echo.

echo Step 3: Generating Updated Dashboard...
python "analysis\generate_dashboard_final.py"
echo.

echo Analysis complete! Results saved to the results directory.
echo Opening decision flow diagram...
start "" "results\engine_decision_flow.png"

echo.
echo Press any key to open the enhanced dashboard in your browser...
pause > nul
start "" "results\chess_dashboard.html"
