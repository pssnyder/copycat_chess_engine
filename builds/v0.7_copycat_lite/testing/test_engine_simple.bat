@echo off
cd /d "S:\Maker Stuff\Programming\Chess Engines\Copycat Chess AI\copycat_chess_engine\release"
echo Testing CopycatChessEngine_v0.7.exe
echo.
echo Testing UCI interface...
echo uci | CopycatChessEngine_v0.7.exe
echo.
echo Testing basic functionality...
(echo uci & echo isready & echo ucinewgame & echo position startpos & echo go movetime 1000 & timeout /t 5 > nul & echo quit) | CopycatChessEngine_v0.7.exe
echo.
echo Test complete.
pause
