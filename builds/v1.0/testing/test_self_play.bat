@echo off
echo Copycat Chess Engine - Simple Self-Play Test
echo =========================================
echo.
echo This script will run a simple self-play test where the engine plays against itself.
echo.
echo Press any key to start the test...
pause > nul

REM Get the directory of the batch file
SET script_dir=%~dp0

REM Create and run the self-play test
echo import sys, os, time, random, chess >> "%TEMP%\self_play.py"
echo sys.path.insert(0, r"%script_dir%") >> "%TEMP%\self_play.py"
echo sys.path.insert(0, r"%script_dir%src") >> "%TEMP%\self_play.py"
echo. >> "%TEMP%\self_play.py"
echo # Try different import paths >> "%TEMP%\self_play.py"
echo try: >> "%TEMP%\self_play.py"
echo     from src.core.engine import CopycatChessEngine >> "%TEMP%\self_play.py"
echo except ImportError: >> "%TEMP%\self_play.py"
echo     try: >> "%TEMP%\self_play.py"
echo         from core.engine import CopycatChessEngine >> "%TEMP%\self_play.py"
echo     except ImportError: >> "%TEMP%\self_play.py"
echo         sys.path.append(r"%script_dir%") >> "%TEMP%\self_play.py"
echo         from engine import CopycatChessEngine >> "%TEMP%\self_play.py"
echo. >> "%TEMP%\self_play.py"
echo # Set up the self-play test >> "%TEMP%\self_play.py"
echo def run_self_play_test(num_moves=20): >> "%TEMP%\self_play.py"
echo     print("Initializing engine for self-play...") >> "%TEMP%\self_play.py"
echo     engine = CopycatChessEngine() >> "%TEMP%\self_play.py"
echo     board = chess.Board() >> "%TEMP%\self_play.py"
echo. >> "%TEMP%\self_play.py"
echo     print("\\nStarting position:") >> "%TEMP%\self_play.py"
echo     print(board) >> "%TEMP%\self_play.py"
echo. >> "%TEMP%\self_play.py"
echo     for i in range(num_moves): >> "%TEMP%\self_play.py"
echo         if board.is_game_over(): >> "%TEMP%\self_play.py"
echo             break >> "%TEMP%\self_play.py"
echo. >> "%TEMP%\self_play.py"
echo         print(f"\\nMove {i+1}:") >> "%TEMP%\self_play.py"
echo         print(f"{'White' if board.turn == chess.WHITE else 'Black'} to move") >> "%TEMP%\self_play.py"
echo. >> "%TEMP%\self_play.py"
echo         start_time = time.time() >> "%TEMP%\self_play.py"
echo         move = engine.select_move(board) >> "%TEMP%\self_play.py"
echo         end_time = time.time() >> "%TEMP%\self_play.py"
echo. >> "%TEMP%\self_play.py"
echo         if move and move != chess.Move.null(): >> "%TEMP%\self_play.py"
echo             print(f"Selected move: {move.uci()}") >> "%TEMP%\self_play.py"
echo             print(f"Think time: {end_time - start_time:.2f} seconds") >> "%TEMP%\self_play.py"
echo             board.push(move) >> "%TEMP%\self_play.py"
echo             print(board) >> "%TEMP%\self_play.py"
echo         else: >> "%TEMP%\self_play.py"
echo             print("Engine failed to select a move, choosing randomly") >> "%TEMP%\self_play.py"
echo             legal_moves = list(board.legal_moves) >> "%TEMP%\self_play.py"
echo             if legal_moves: >> "%TEMP%\self_play.py"
echo                 random_move = random.choice(legal_moves) >> "%TEMP%\self_play.py"
echo                 board.push(random_move) >> "%TEMP%\self_play.py"
echo                 print(f"Random move: {random_move.uci()}") >> "%TEMP%\self_play.py"
echo                 print(board) >> "%TEMP%\self_play.py"
echo             else: >> "%TEMP%\self_play.py"
echo                 print("No legal moves available") >> "%TEMP%\self_play.py"
echo                 break >> "%TEMP%\self_play.py"
echo. >> "%TEMP%\self_play.py"
echo     # Print game result >> "%TEMP%\self_play.py"
echo     print("\\nGame result:") >> "%TEMP%\self_play.py"
echo     if board.is_checkmate(): >> "%TEMP%\self_play.py"
echo         print(f"Checkmate! {'Black' if board.turn == chess.WHITE else 'White'} wins.") >> "%TEMP%\self_play.py"
echo     elif board.is_stalemate(): >> "%TEMP%\self_play.py"
echo         print("Stalemate!") >> "%TEMP%\self_play.py"
echo     elif board.is_insufficient_material(): >> "%TEMP%\self_play.py"
echo         print("Draw due to insufficient material!") >> "%TEMP%\self_play.py"
echo     elif board.is_fifty_moves(): >> "%TEMP%\self_play.py"
echo         print("Draw due to fifty-move rule!") >> "%TEMP%\self_play.py"
echo     elif board.is_repetition(3): >> "%TEMP%\self_play.py"
echo         print("Draw due to threefold repetition!") >> "%TEMP%\self_play.py"
echo     else: >> "%TEMP%\self_play.py"
echo         print("Game in progress...") >> "%TEMP%\self_play.py"
echo. >> "%TEMP%\self_play.py"
echo     print("\\nFinal position FEN:") >> "%TEMP%\self_play.py"
echo     print(board.fen()) >> "%TEMP%\self_play.py"
echo. >> "%TEMP%\self_play.py"
echo # Run the test >> "%TEMP%\self_play.py"
echo if __name__ == "__main__": >> "%TEMP%\self_play.py"
echo     print("Copycat Chess Engine - Self-Play Test") >> "%TEMP%\self_play.py"
echo     print("===================================\\n") >> "%TEMP%\self_play.py"
echo     try: >> "%TEMP%\self_play.py"
echo         num_moves = 10  # Limit to 10 moves for a quick test >> "%TEMP%\self_play.py"
echo         run_self_play_test(num_moves) >> "%TEMP%\self_play.py"
echo         print("\\nSelf-play test completed successfully!") >> "%TEMP%\self_play.py"
echo     except Exception as e: >> "%TEMP%\self_play.py"
echo         print(f"Error during self-play test: {str(e)}") >> "%TEMP%\self_play.py"
echo         sys.exit(1) >> "%TEMP%\self_play.py"

REM Run the test
python "%TEMP%\self_play.py"

REM Delete the temporary script
del "%TEMP%\self_play.py"

echo.
echo Self-play test completed.
echo.
pause
