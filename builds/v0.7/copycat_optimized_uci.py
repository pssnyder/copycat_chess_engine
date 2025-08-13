#!/usr/bin/env python3
"""
Copycat Chess Engine - Optimized UCI Interface
Combines neural network predictions with evaluation engine for optimal play
Designed for Arena chess GUI compatibility with minimal dependencies
"""

import sys
import os
import chess
import time
import numpy as np

# Minimal imports for reduced executable size
try:
    import torch
    torch_available = True
except ImportError:
    torch_available = False
    print("info string Warning: PyTorch not found. Engine will use fallback mode.")

try:
    from chess_core import CopycatEvaluationAI
    from evaluation_engine import EvaluationEngine
    AI_AVAILABLE = True
except ImportError:
    print("info string Warning: AI modules not found. Using basic evaluation.")
    AI_AVAILABLE = False

class OptimizedUCIEngine:
    def __init__(self):
        self.name = "Copycat Chess Engine - Optimized"
        self.author = "Copycat Chess AI"
        self.version = "v1.0"
        self.board = chess.Board()
        
        # Engine state
        self.ai = None
        self.evaluator = None
        self.initialized = False
        self.debug_mode = False
        
        # Time management
        self.movetime = None
        self.wtime = None
        self.btime = None
        self.winc = None
        self.binc = None
        self.movestogo = None
        
        # Device selection
        if torch_available:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = "cpu"
        
    def initialize_engine(self):
        """Initialize AI and evaluation components"""
        try:
            if not torch_available or not AI_AVAILABLE:
                print("info string Using evaluation-only mode")
                self.evaluator = None  # Will create per-move
                self.initialized = True
                return True
            
            # Look for model files in order of preference
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Traditional models (v7p3r) - these work with our ChessAI class
            traditional_models = [
                (os.path.join(script_dir, "builds", "v0.3_copycat_enhanced_ai", "v7p3r_chess_ai_model.pth"),
                 os.path.join(script_dir, "builds", "v0.3_copycat_enhanced_ai", "move_vocab.pkl")),
                (os.path.join(script_dir, "builds", "v0.2_copycat_eval_ai", "v7p3r_chess_ai_model.pth"),
                 os.path.join(script_dir, "builds", "v0.2_copycat_eval_ai", "move_vocab.pkl")),
                (os.path.join(script_dir, "builds", "v0.1_copycat_ai", "v7p3r_chess_ai_model.pth"),
                 os.path.join(script_dir, "builds", "v0.1_copycat_ai", "move_vocab.pkl"))
            ]
            
            # Try traditional models first (they have compatible architecture)
            for model_path, vocab_path in traditional_models:
                if os.path.exists(model_path) and os.path.exists(vocab_path):
                    try:
                        print(f"info string Trying traditional model: {os.path.basename(model_path)}")
                        self.ai = CopycatEvaluationAI(
                            model_path=model_path,
                            vocab_path=vocab_path,
                            device=self.device
                        )
                        print("info string Traditional AI engine initialized successfully")
                        self.initialized = True
                        return True
                    except Exception as e:
                        print(f"info string Failed to load {os.path.basename(model_path)}: {str(e)}")
                        continue
            
            # If no traditional models work, fall back to evaluation only
            print("info string No compatible AI models found, using evaluation-only mode")
            self.ai = None
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"info string Error during initialization: {str(e)}")
            print("info string Using evaluation-only fallback")
            self.ai = None
            self.initialized = True
            return True  # Always succeed with fallback

    def handle_uci(self):
        """Handle UCI identification"""
        print(f"id name {self.name}")
        print(f"id author {self.author}")
        print("option name Debug type check default false")
        print("option name Hash type spin default 16 min 1 max 128")
        print("option name Threads type spin default 1 min 1 max 4")
        print("uciok")

    def handle_isready(self):
        """Handle engine readiness check"""
        if not self.initialized:
            if not self.initialize_engine():
                print("info string Engine initialization failed, using fallback")
        print("readyok")

    def handle_setoption(self, args):
        """Handle UCI options"""
        if len(args) >= 4 and args[0] == "name":
            option_name = args[1].lower()
            if len(args) >= 4 and args[2] == "value":
                option_value = args[3].lower()
                
                if option_name == "debug":
                    self.debug_mode = (option_value == "true")
                    print(f"info string Debug mode: {self.debug_mode}")

    def handle_position(self, args):
        """Handle position setup"""
        if not args:
            return
        
        try:
            if args[0] == "startpos":
                self.board = chess.Board()
                move_idx = 1
            elif args[0] == "fen":
                # Find end of FEN string
                fen_end = 1
                while fen_end < len(args) and args[fen_end] != "moves":
                    fen_end += 1
                
                fen = " ".join(args[1:fen_end])
                self.board = chess.Board(fen)
                move_idx = fen_end
            else:
                print("info string Invalid position command")
                return
            
            # Apply moves if provided
            if move_idx < len(args) and args[move_idx] == "moves":
                for move_uci in args[move_idx+1:]:
                    try:
                        move = chess.Move.from_uci(move_uci)
                        if move in self.board.legal_moves:
                            self.board.push(move)
                        else:
                            print(f"info string Illegal move ignored: {move_uci}")
                            break
                    except ValueError:
                        print(f"info string Invalid move format: {move_uci}")
                        break
                        
        except Exception as e:
            print(f"info string Error setting position: {str(e)}")
            self.board = chess.Board()  # Reset to start position

    def handle_go(self, args):
        """Handle move search command"""
        if not self.initialized:
            self.handle_isready()
        
        # Parse time control
        self.parse_go_params(args)
        
        # Calculate thinking time
        think_time = self.calculate_think_time()
        
        if self.debug_mode:
            print(f"info string Thinking time: {think_time:.2f}s")
        
        try:
            # Get best move
            start_time = time.time()
            best_move = self.find_best_move(think_time)
            elapsed = time.time() - start_time
            
            if best_move:
                if self.debug_mode:
                    print(f"info string Move found in {elapsed:.2f}s")
                print(f"bestmove {best_move.uci()}")
            else:
                print("info string No legal moves found")
                print("bestmove 0000")
                
        except Exception as e:
            print(f"info string Error during search: {str(e)}")
            # Emergency fallback
            legal_moves = list(self.board.legal_moves)
            if legal_moves:
                import random
                emergency_move = random.choice(legal_moves)
                print(f"bestmove {emergency_move.uci()}")
            else:
                print("bestmove 0000")

    def parse_go_params(self, args):
        """Parse go command parameters"""
        self.movetime = None
        self.wtime = self.btime = None
        self.winc = self.binc = None
        self.movestogo = None
        
        i = 0
        while i < len(args):
            if args[i] == "movetime" and i + 1 < len(args):
                self.movetime = int(args[i + 1])
                i += 2
            elif args[i] == "wtime" and i + 1 < len(args):
                self.wtime = int(args[i + 1])
                i += 2
            elif args[i] == "btime" and i + 1 < len(args):
                self.btime = int(args[i + 1])
                i += 2
            elif args[i] == "winc" and i + 1 < len(args):
                self.winc = int(args[i + 1])
                i += 2
            elif args[i] == "binc" and i + 1 < len(args):
                self.binc = int(args[i + 1])
                i += 2
            elif args[i] == "movestogo" and i + 1 < len(args):
                self.movestogo = int(args[i + 1])
                i += 2
            else:
                i += 1

    def calculate_think_time(self):
        """Calculate optimal thinking time"""
        if self.movetime:
            return self.movetime / 1000.0
        
        # Determine time left for current player
        time_left = self.wtime if self.board.turn == chess.WHITE else self.btime
        increment = self.winc if self.board.turn == chess.WHITE else self.binc
        
        if time_left is None:
            return 1.0  # Default 1 second
        
        time_left_sec = time_left / 1000.0
        inc_sec = (increment or 0) / 1000.0
        
        # Conservative time management
        moves_remaining = self.movestogo or 30
        base_time = (time_left_sec / moves_remaining) + (inc_sec * 0.8)
        
        # Emergency time protection
        emergency_reserve = min(time_left_sec * 0.05, 2.0)
        max_time = max(time_left_sec - emergency_reserve, 0.1)
        
        return min(max(base_time, 0.1), max_time)

    def find_best_move(self, think_time):
        """Find the best move using available AI or evaluation"""
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        
        if len(legal_moves) == 1:
            return legal_moves[0]  # Forced move
        
        try:
            # Use AI if available
            if self.ai:
                if self.debug_mode:
                    print("info string Using AI + Evaluation engine")
                return self.ai.select_best_move(self.board, debug=self.debug_mode)
            
            # Fallback to pure evaluation
            if self.debug_mode:
                print("info string Using evaluation-only mode")
            return self.evaluate_moves(legal_moves, think_time)
            
        except Exception as e:
            print(f"info string Error in move selection: {str(e)}")
            # Last resort: return first legal move
            return legal_moves[0]

    def evaluate_moves(self, legal_moves, think_time):
        """Evaluate moves using position evaluation"""
        if not AI_AVAILABLE:
            # Ultra-simple fallback
            return legal_moves[0]
        
        try:
            evaluator = EvaluationEngine(self.board)
            best_move = None
            best_score = float('-inf')
            
            start_time = time.time()
            
            for move in legal_moves:
                if time.time() - start_time > think_time * 0.8:
                    break  # Time management
                
                score = evaluator.evaluate_move(move)
                if self.board.turn == chess.BLACK:
                    score = -score  # Flip for black
                
                if score > best_score:
                    best_score = score
                    best_move = move
            
            return best_move or legal_moves[0]
            
        except Exception:
            return legal_moves[0]

    def handle_stop(self):
        """Handle stop command"""
        pass  # Simple implementation doesn't need search cancellation

    def handle_quit(self):
        """Handle quit command"""
        sys.exit(0)

    def handle_ucinewgame(self):
        """Handle new game command"""
        self.board = chess.Board()

    def run(self):
        """Main UCI command loop"""
        while True:
            try:
                command = sys.stdin.readline().strip()
                if not command:
                    continue
                
                parts = command.split()
                if not parts:
                    continue
                
                cmd = parts[0].lower()
                args = parts[1:]
                
                if cmd == "uci":
                    self.handle_uci()
                elif cmd == "isready":
                    self.handle_isready()
                elif cmd == "setoption":
                    self.handle_setoption(args)
                elif cmd == "position":
                    self.handle_position(args)
                elif cmd == "go":
                    self.handle_go(args)
                elif cmd == "stop":
                    self.handle_stop()
                elif cmd == "quit":
                    self.handle_quit()
                elif cmd == "ucinewgame":
                    self.handle_ucinewgame()
                else:
                    # Ignore unknown commands
                    pass
                    
            except Exception as e:
                print(f"info string Command error: {str(e)}")

def main():
    """Entry point for the chess engine"""
    try:
        engine = OptimizedUCIEngine()
        engine.run()
    except Exception as e:
        sys.stderr.write(f"Fatal error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
