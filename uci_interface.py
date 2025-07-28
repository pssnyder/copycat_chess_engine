# uci_interface.py
# UCI (Universal Chess Interface) compatibility layer for Copycat Chess Engine

import sys
import chess
import time
import os

# Import torch with error handling
try:
    import torch
    torch_available = True
except ImportError:
    torch_available = False
    print("info string Warning: PyTorch not found. Chess engine requires PyTorch to function.")
    print("info string Please install with: pip install torch")

from chess_core import CopycatEvaluationAI

class UCIEngine:
    def __init__(self):
        self.name = "Copycat Chess Engine v0.5.31"
        self.author = "Copycat Chess AI"
        self.board = chess.Board()
        
        # Set device if torch is available
        if 'torch_available' in globals() and torch_available:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = "cpu"  # Fallback to CPU if torch isn't available
        
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
            # Check if torch is available
            if 'torch_available' not in globals() or not torch_available:
                print("info string PyTorch is not available. Please install it with: pip install torch")
                return False
            
            # Get the directory of this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Try to find model file
            model_paths = [
                # Try the main directory first
                os.path.join(script_dir, "rl_actor_model.pth"),
                # Then try enhanced AI build
                os.path.join(script_dir, "builds", "v0.5.31_copycat_enhanced_ai", "v7p3r_chess_ai_model.pth"),
                # Try genetic AI build
                os.path.join(script_dir, "builds", "v0.5.31_copycat_genetic_ai", "v7p3r_chess_ai_model.pth"),
                # Try eval AI build
                os.path.join(script_dir, "builds", "v0.5.30_copycat_eval_ai", "v7p3r_chess_ai_model.pth")
            ]
            
            # Try to find vocab file
            vocab_paths = [
                # Try enhanced AI build
                os.path.join(script_dir, "builds", "v0.5.31_copycat_enhanced_ai", "move_vocab.pkl"),
                # Try genetic AI build
                os.path.join(script_dir, "builds", "v0.5.31_copycat_genetic_ai", "move_vocab.pkl"),
                # Try eval AI build
                os.path.join(script_dir, "builds", "v0.5.30_copycat_eval_ai", "move_vocab.pkl")
            ]
            
            # Find first existing model path
            model_path = None
            for path in model_paths:
                if os.path.exists(path):
                    model_path = path
                    print(f"info string Found model at: {path}")
                    break
            
            if model_path is None:
                raise FileNotFoundError("Could not find model file")
            
            # Find first existing vocab path
            vocab_path = None
            for path in vocab_paths:
                if os.path.exists(path):
                    vocab_path = path
                    print(f"info string Found vocabulary at: {path}")
                    break
            
            if vocab_path is None:
                raise FileNotFoundError("Could not find vocabulary file")
            
            # Initialize the AI
            self.ai = CopycatEvaluationAI(
                model_path=model_path,
                vocab_path=vocab_path,
                device=self.device
            )
            self.initialized = True
            return True
        except Exception as e:
            print(f"info string Error initializing engine: {str(e)}")
            return False

    def handle_uci(self):
        """Handle the uci command"""
        print(f"id name {self.name}")
        print(f"id author {self.author}")
        # UCI options would go here
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
        
        # Parse the position command
        if args[0] == "startpos":
            self.board = chess.Board()
            move_idx = 1
        elif args[0] == "fen":
            # Find the end of the FEN string
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
        
        # Apply moves if provided
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
                print("bestmove a1a1")  # Send a dummy move in case of error
                return
        
        # Make sure self.ai is not None
        if self.ai is None:
            print("info string AI engine not properly initialized")
            print("bestmove a1a1")  # Send a dummy move in case of error
            return

        # Parse time control parameters
        self.wtime = None
        self.btime = None
        self.winc = None
        self.binc = None
        self.movestogo = None
        self.movetime = None
        depth = 5  # Default depth
        
        i = 0
        while i < len(args):
            if args[i] == "wtime":
                i += 1
                if i < len(args):
                    self.wtime = int(args[i])
            elif args[i] == "btime":
                i += 1
                if i < len(args):
                    self.btime = int(args[i])
            elif args[i] == "winc":
                i += 1
                if i < len(args):
                    self.winc = int(args[i])
            elif args[i] == "binc":
                i += 1
                if i < len(args):
                    self.binc = int(args[i])
            elif args[i] == "movestogo":
                i += 1
                if i < len(args):
                    self.movestogo = int(args[i])
            elif args[i] == "depth":
                i += 1
                if i < len(args):
                    depth = int(args[i])
            elif args[i] == "movetime":
                i += 1
                if i < len(args):
                    self.movetime = int(args[i])
            i += 1
        
        # Calculate thinking time
        think_time = self.calculate_think_time()
        
        # Find best move
        start_time = time.time()
        try:
            # Check if there are any legal moves
            if not list(self.board.legal_moves):
                print("info string Game over position - no legal moves")
                print("bestmove 0000")  # Null move
                return
                
            # Get best move from AI
            best_move = self.ai.select_best_move(self.board)
            
            # Double-check the result
            if best_move is None or best_move not in self.board.legal_moves:
                # Fall back to a random legal move if the AI fails
                legal_moves = list(self.board.legal_moves)
                if legal_moves:
                    import random
                    best_move = random.choice(legal_moves)
                    print("info string Using fallback random move")
                else:
                    print("info string No legal moves available")
                    print("bestmove 0000")  # Null move
                    return
            
            # Report best move
            print(f"bestmove {best_move.uci()}")
            
        except Exception as e:
            print(f"info string Error finding best move: {str(e)}")
            # Try to recover with a random legal move
            try:
                legal_moves = list(self.board.legal_moves)
                if legal_moves:
                    import random
                    fallback_move = random.choice(legal_moves)
                    print(f"info string Using fallback random move: {fallback_move.uci()}")
                    print(f"bestmove {fallback_move.uci()}")
                else:
                    print("bestmove 0000")  # Null move
            except:
                print("bestmove 0000")  # Null move in case of error

    def calculate_think_time(self):
        """Calculate how long to think based on time control and config settings"""
        if self.movetime is not None:
            return self.movetime / 1000.0  # Convert ms to seconds
        
        # If no time control specified, use default time
        if self.wtime is None and self.btime is None:
            return 1.0  # Default 1 second
        
        # Determine whose turn it is
        time_left = self.wtime if self.board.turn == chess.WHITE else self.btime
        inc = self.winc if self.board.turn == chess.WHITE else self.binc
        
        if time_left is None:
            return 1.0  # Default if no time specified
        
        # Convert from milliseconds to seconds
        time_left_sec = time_left / 1000.0
        inc_sec = 0 if inc is None else inc / 1000.0
        
        # Advanced time management based on game phase and position complexity
        moves_left = 30 if self.movestogo is None else self.movestogo
        
        # Base time calculation
        base_time = time_left_sec / moves_left + inc_sec * 0.8
        
        # Position complexity factors
        complexity_multiplier = 1.0
        
        # Adjust for game phase
        num_pieces = sum(1 for _ in chess.SQUARES if self.board.piece_at(_) is not None)
        if num_pieces <= 10:  # Endgame
            complexity_multiplier = 1.2  # Spend more time in endgame
        elif num_pieces >= 28:  # Opening
            complexity_multiplier = 0.8  # Spend less time in opening
            
        # Adjust for tactical positions
        if self.board.is_check():
            complexity_multiplier *= 1.3  # Spend more time when in check
            
        # Calculate final think time
        think_time = base_time * complexity_multiplier
        
        # Ensure we don't use too much time (safety limits)
        max_time = min(time_left_sec / 10.0, 30.0)  # Don't use more than 10% of total time, max 30 seconds
        emergency_time = 0.1  # Always reserve at least 100ms
        think_time = max(min(think_time, max_time), emergency_time)
        
        return think_time

    def handle_stop(self):
        """Handle the stop command"""
        # Not needed for our simple implementation
        # In a more advanced engine, this would stop any ongoing search
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
                if not sys.stdin.isatty():
                    # If not in interactive mode, wait for input
                    command = sys.stdin.readline().strip()
                else:
                    command = input().strip()
                
                if not command:
                    continue
                
                # Split the command into parts
                parts = command.split()
                cmd = parts[0].lower()
                args = parts[1:]
                
                # Process the command
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
                else:
                    # Ignore unknown commands
                    pass
            except Exception as e:
                print(f"info string Error processing command: {str(e)}")

if __name__ == "__main__":
    # Run the UCI engine
    engine = UCIEngine()
    engine.run()
