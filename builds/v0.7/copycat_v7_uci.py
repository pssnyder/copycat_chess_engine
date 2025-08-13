#!/usr/bin/env python3
"""
Copycat Chess Engine v0.7 - Simplified UCI Interface
Based on v0.2 evaluation AI with clean, lightweight implementation
Designed for tournament play with Arena chess GUI
"""

import sys
import os
import chess
import time
import numpy as np

# Import dependencies with graceful fallbacks
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("info string PyTorch not available, using evaluation-only mode")

try:
    from chess_core import CopycatEvaluationAI
    from evaluation_engine import EvaluationEngine
    AI_MODULES_AVAILABLE = True
except ImportError:
    AI_MODULES_AVAILABLE = False
    print("info string AI modules not available, using basic mode")

class CopycatEngine:
    def __init__(self):
        self.name = "Copycat Chess Engine v0.7"
        self.author = "Copycat Chess AI"
        self.board = chess.Board()
        
        # Engine state
        self.ai = None
        self.initialized = False
        self.debug = False
        
        # Time control
        self.movetime = None
        self.wtime = None
        self.btime = None
        self.winc = None
        self.binc = None
        self.movestogo = None
        
        # Device selection
        if TORCH_AVAILABLE:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = "cpu"

    def initialize(self):
        """Initialize the chess engine"""
        if not TORCH_AVAILABLE or not AI_MODULES_AVAILABLE:
            print("info string Running in evaluation-only mode")
            self.initialized = True
            return True
        
        try:
            # Look for model files in current directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(script_dir, "v7p3r_chess_ai_model.pth")
            vocab_path = os.path.join(script_dir, "move_vocab.pkl")
            
            if not os.path.exists(model_path):
                print(f"info string Model file not found: {model_path}")
                print("info string Running in evaluation-only mode")
                self.initialized = True
                return True
                
            if not os.path.exists(vocab_path):
                print(f"info string Vocabulary file not found: {vocab_path}")
                print("info string Running in evaluation-only mode")
                self.initialized = True
                return True
            
            # Initialize AI
            self.ai = CopycatEvaluationAI(
                model_path=model_path,
                vocab_path=vocab_path,
                device=self.device
            )
            
            print("info string AI successfully initialized")
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"info string Error initializing AI: {str(e)}")
            print("info string Falling back to evaluation-only mode")
            self.ai = None
            self.initialized = True
            return True

    def handle_uci(self):
        """Handle UCI command"""
        print(f"id name {self.name}")
        print(f"id author {self.author}")
        print("option name Debug type check default false")
        print("uciok")

    def handle_isready(self):
        """Handle isready command"""
        if not self.initialized:
            self.initialize()
        print("readyok")

    def handle_setoption(self, args):
        """Handle setoption command"""
        if len(args) >= 4 and args[0] == "name" and args[2] == "value":
            option_name = args[1].lower()
            option_value = args[3].lower()
            
            if option_name == "debug":
                self.debug = (option_value == "true")
                print(f"info string Debug mode: {self.debug}")

    def handle_position(self, args):
        """Handle position command"""
        if not args:
            return
        
        try:
            if args[0] == "startpos":
                self.board = chess.Board()
                move_idx = 1
            elif args[0] == "fen":
                # Parse FEN
                fen_parts = []
                i = 1
                while i < len(args) and args[i] != "moves":
                    fen_parts.append(args[i])
                    i += 1
                
                fen = " ".join(fen_parts)
                self.board = chess.Board(fen)
                move_idx = i
            else:
                return
            
            # Apply moves
            if move_idx < len(args) and args[move_idx] == "moves":
                for move_str in args[move_idx + 1:]:
                    try:
                        move = chess.Move.from_uci(move_str)
                        if move in self.board.legal_moves:
                            self.board.push(move)
                        else:
                            if self.debug:
                                print(f"info string Illegal move ignored: {move_str}")
                            break
                    except ValueError:
                        if self.debug:
                            print(f"info string Invalid move: {move_str}")
                        break
                        
        except Exception as e:
            if self.debug:
                print(f"info string Error in position: {str(e)}")
            self.board = chess.Board()  # Reset on error

    def handle_go(self, args):
        """Handle go command"""
        if not self.initialized:
            self.handle_isready()
        
        # Parse time controls
        self.parse_time_controls(args)
        
        # Calculate thinking time
        think_time = self.calculate_think_time()
        
        if self.debug:
            print(f"info string Thinking time: {think_time:.2f}s")
        
        # Find best move
        try:
            start_time = time.time()
            best_move = self.find_best_move(think_time)
            elapsed = time.time() - start_time
            
            if best_move:
                if self.debug:
                    print(f"info string Move selected in {elapsed:.2f}s")
                print(f"bestmove {best_move.uci()}")
            else:
                print("bestmove 0000")
                
        except Exception as e:
            if self.debug:
                print(f"info string Error finding move: {str(e)}")
            
            # Emergency fallback
            legal_moves = list(self.board.legal_moves)
            if legal_moves:
                emergency_move = legal_moves[0]
                print(f"bestmove {emergency_move.uci()}")
            else:
                print("bestmove 0000")

    def parse_time_controls(self, args):
        """Parse time control arguments"""
        self.movetime = None
        self.wtime = self.btime = None
        self.winc = self.binc = None
        self.movestogo = None
        
        i = 0
        while i < len(args) - 1:
            param = args[i]
            value = args[i + 1]
            
            try:
                if param == "movetime":
                    self.movetime = int(value)
                elif param == "wtime":
                    self.wtime = int(value)
                elif param == "btime":
                    self.btime = int(value)
                elif param == "winc":
                    self.winc = int(value)
                elif param == "binc":
                    self.binc = int(value)
                elif param == "movestogo":
                    self.movestogo = int(value)
            except ValueError:
                pass
            
            i += 2

    def calculate_think_time(self):
        """Calculate how long to think"""
        if self.movetime:
            return self.movetime / 1000.0
        
        # Get time for current player
        my_time = self.wtime if self.board.turn == chess.WHITE else self.btime
        my_inc = self.winc if self.board.turn == chess.WHITE else self.binc
        
        if my_time is None:
            return 1.0  # Default 1 second
        
        time_sec = my_time / 1000.0
        inc_sec = (my_inc or 0) / 1000.0
        
        # Simple time management
        moves_left = self.movestogo or 25
        base_time = (time_sec / moves_left) + (inc_sec * 0.8)
        
        # Safety limits
        min_time = 0.1
        max_time = min(time_sec * 0.1, 5.0)  # Max 10% of remaining time or 5s
        
        return max(min_time, min(base_time, max_time))

    def find_best_move(self, think_time):
        """Find the best move"""
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        
        if len(legal_moves) == 1:
            return legal_moves[0]  # Only one legal move
        
        try:
            # Use AI if available
            if self.ai:
                if self.debug:
                    print("info string Using AI + Evaluation")
                return self.ai.select_best_move(self.board, debug=self.debug)
            
            # Fallback to evaluation only
            if AI_MODULES_AVAILABLE:
                if self.debug:
                    print("info string Using evaluation only")
                return self.evaluate_moves(legal_moves, think_time)
            
            # Last resort: first legal move
            if self.debug:
                print("info string Using first legal move")
            return legal_moves[0]
            
        except Exception as e:
            if self.debug:
                print(f"info string Error in move selection: {str(e)}")
            return legal_moves[0]

    def evaluate_moves(self, legal_moves, think_time):
        """Evaluate moves using position evaluation"""
        try:
            evaluator = EvaluationEngine(self.board)
            best_move = legal_moves[0]
            best_score = float('-inf')
            
            start_time = time.time()
            
            for move in legal_moves:
                if time.time() - start_time > think_time * 0.8:
                    break  # Time limit
                
                score = evaluator.evaluate_move(move)
                
                # Adjust score for current player
                if self.board.turn == chess.BLACK:
                    score = -score
                
                if score > best_score:
                    best_score = score
                    best_move = move
            
            return best_move
            
        except Exception:
            return legal_moves[0]

    def handle_stop(self):
        """Handle stop command"""
        pass

    def handle_quit(self):
        """Handle quit command"""
        sys.exit(0)

    def handle_ucinewgame(self):
        """Handle ucinewgame command"""
        self.board = chess.Board()

    def run(self):
        """Main UCI loop"""
        while True:
            try:
                line = sys.stdin.readline().strip()
                if not line:
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                command = parts[0].lower()
                args = parts[1:]
                
                if command == "uci":
                    self.handle_uci()
                elif command == "isready":
                    self.handle_isready()
                elif command == "setoption":
                    self.handle_setoption(args)
                elif command == "position":
                    self.handle_position(args)
                elif command == "go":
                    self.handle_go(args)
                elif command == "stop":
                    self.handle_stop()
                elif command == "quit":
                    self.handle_quit()
                elif command == "ucinewgame":
                    self.handle_ucinewgame()
                # Ignore unknown commands
                    
            except Exception as e:
                if hasattr(self, 'debug') and self.debug:
                    print(f"info string Command error: {str(e)}")

if __name__ == "__main__":
    engine = CopycatEngine()
    engine.run()
