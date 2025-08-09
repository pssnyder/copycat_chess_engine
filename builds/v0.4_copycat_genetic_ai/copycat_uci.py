#!/usr/bin/env python
# copycat_uci.py - UCI launcher for Copycat Chess Engine v0.4
import sys
import os
import chess
import time

# Import torch with error handling
try:
    import torch
    torch_available = True
except ImportError:
    torch_available = False
    print("info string Warning: PyTorch not found. Chess engine requires PyTorch to function.")

from chess_core import CopycatEvaluationAI

class UCIEngine:
    def __init__(self):
        self.name = "Copycat Chess Engine v0.4 Genetic"
        self.author = "Copycat Chess AI"
        self.board = chess.Board()
        
        if torch_available:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = "cpu"
        
        self.ai = None
        self.initialized = False
        
        # Default time controls
        self.movetime = None
        self.wtime = None
        self.btime = None
        self.winc = None
        self.binc = None
        self.movestogo = None
        
    def initialize_engine(self):
        """Initialize the AI engine with the necessary models"""
        try:
            if not torch_available:
                print("info string PyTorch is not available. Please install it with: pip install torch")
                return False
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Try both RL models and traditional models
            rl_actor_path = os.path.join(script_dir, "rl_actor_model.pth")
            rl_critic_path = os.path.join(script_dir, "rl_critic_model.pth")
            
            if os.path.exists(rl_actor_path) and os.path.exists(rl_critic_path):
                # Use reinforcement learning models if available
                print("info string Using reinforcement learning models")
                # For now, we'll fall back to the evaluation AI
                # since the RL models might need special handling
                
            # Fall back to evaluation AI
            model_path = os.path.join(script_dir, "v7p3r_chess_ai_model.pth")
            vocab_path = os.path.join(script_dir, "move_vocab.pkl")
            
            # Check if we have the traditional models in the builds directory
            if not os.path.exists(model_path):
                # Look for models in parent directories
                parent_dirs = [
                    os.path.join(script_dir, "..", "v0.3_copycat_enhanced_ai"),
                    os.path.join(script_dir, "..", "v0.2_copycat_eval_ai"),
                    os.path.join(script_dir, "..", "v0.1_copycat_ai")
                ]
                
                for parent_dir in parent_dirs:
                    test_model = os.path.join(parent_dir, "v7p3r_chess_ai_model.pth")
                    test_vocab = os.path.join(parent_dir, "move_vocab.pkl")
                    if os.path.exists(test_model) and os.path.exists(test_vocab):
                        model_path = test_model
                        vocab_path = test_vocab
                        print(f"info string Using model from: {parent_dir}")
                        break
            
            if not os.path.exists(model_path):
                print(f"info string Model file not found: {model_path}")
                return False
                
            if not os.path.exists(vocab_path):
                print(f"info string Vocabulary file not found: {vocab_path}")
                return False
            
            self.ai = CopycatEvaluationAI(
                model_path=model_path,
                vocab_path=vocab_path,
                device=self.device
            )
            self.initialized = True
            print("info string Engine initialized successfully")
            return True
        except Exception as e:
            print(f"info string Error initializing engine: {str(e)}")
            return False

    def handle_uci(self):
        """Handle the uci command"""
        print(f"id name {self.name}")
        print(f"id author {self.author}")
        print("option name Hash type spin default 16 min 1 max 1024")
        print("option name Threads type spin default 1 min 1 max 64")
        print("uciok")

    def handle_isready(self):
        """Handle the isready command"""
        if not self.initialized:
            if not self.initialize_engine():
                print("info string Engine initialization failed")
                return
        print("readyok")

    def handle_position(self, args):
        """Handle the position command"""
        if not args:
            return
        
        if args[0] == "startpos":
            self.board = chess.Board()
            move_idx = 1
        elif args[0] == "fen":
            fen_end = 1
            while fen_end < len(args) and args[fen_end] != "moves":
                fen_end += 1
            
            fen = " ".join(args[1:fen_end])
            try:
                self.board = chess.Board(fen)
                move_idx = fen_end
            except ValueError:
                print(f"info string Invalid FEN: {fen}")
                return
        else:
            print("info string Invalid position command")
            return
        
        if move_idx < len(args) and args[move_idx] == "moves":
            for move_uci in args[move_idx+1:]:
                try:
                    move = chess.Move.from_uci(move_uci)
                    if move in self.board.legal_moves:
                        self.board.push(move)
                except ValueError:
                    print(f"info string Invalid move: {move_uci}")
                    break

    def handle_go(self, args):
        """Handle the go command"""
        if not self.initialized:
            if not self.initialize_engine():
                print("info string Engine not initialized")
                print("bestmove a1a1")
                return
        
        if self.ai is None:
            print("info string AI engine not properly initialized")
            print("bestmove a1a1")
            return

        try:
            if not list(self.board.legal_moves):
                print("info string Game over position - no legal moves")
                print("bestmove 0000")
                return
                
            best_move = self.ai.select_best_move(self.board)
            
            if best_move is None or best_move not in self.board.legal_moves:
                legal_moves = list(self.board.legal_moves)
                if legal_moves:
                    import random
                    best_move = random.choice(legal_moves)
                    print("info string Using fallback random move")
                else:
                    print("info string No legal moves available")
                    print("bestmove 0000")
                    return
            
            print(f"bestmove {best_move.uci()}")
            
        except Exception as e:
            print(f"info string Error finding best move: {str(e)}")
            try:
                legal_moves = list(self.board.legal_moves)
                if legal_moves:
                    import random
                    fallback_move = random.choice(legal_moves)
                    print(f"bestmove {fallback_move.uci()}")
                else:
                    print("bestmove 0000")
            except:
                print("bestmove 0000")

    def handle_stop(self):
        """Handle the stop command"""
        pass

    def handle_quit(self):
        """Handle the quit command"""
        sys.exit(0)

    def handle_ucinewgame(self):
        """Handle the ucinewgame command"""
        self.board = chess.Board()

    def run(self):
        """Main UCI command loop"""
        while True:
            try:
                command = sys.stdin.readline().strip()
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                args = parts[1:]
                
                if cmd == "uci":
                    self.handle_uci()
                elif cmd == "isready":
                    self.handle_isready()
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
                    
            except Exception as e:
                print(f"info string Error processing command: {str(e)}")

def main():
    """Launch the Copycat Chess Engine v0.4 in UCI mode"""
    try:
        engine = UCIEngine()
        engine.run()
    except Exception as e:
        sys.stderr.write(f"Fatal error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
