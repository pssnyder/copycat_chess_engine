#!/usr/bin/env python3
"""
Chess Game Module for Copycat Chess Engine
Provides game management and integration with the engine.
"""

import chess
import chess.pgn
import time
import os
import json
import io
from typing import Dict, List, Tuple, Optional, Any
import datetime

from core.engine import CopycatChessEngine
from core.chess_core import detect_game_phase, detect_opening_from_moves, move_to_algebraic

class ChessGame:
    """
    Class to manage a chess game and integrate with the engine.
    """
    
    def __init__(self, engine=None, time_control="classical"):
        """
        Initialize the chess game.
        
        Args:
            engine: The chess engine to use (optional)
            time_control: The time control for the game (classical, rapid, blitz)
        """
        self.board = chess.Board()
        self.move_history = []
        self.time_control = time_control
        self.game_phase = "opening"
        self.opening = None
        self.player_color = chess.WHITE  # Default to white
        self.game_started = time.time()
        self.move_times = []
        self.engine = engine if engine else CopycatChessEngine()
        
        # Game statistics
        self.stats = {
            "captures": 0,
            "checks": 0,
            "castling": False,
            "promotions": 0
        }
    
    def reset(self):
        """Reset the game to the starting position."""
        self.board = chess.Board()
        self.move_history = []
        self.game_phase = "opening"
        self.opening = None
        self.game_started = time.time()
        self.move_times = []
        
        # Reset game statistics
        self.stats = {
            "captures": 0,
            "checks": 0,
            "castling": False,
            "promotions": 0
        }
    
    def set_position_from_fen(self, fen: str):
        """
        Set the board position from a FEN string.
        
        Args:
            fen: The FEN string representing the position
        """
        try:
            self.board = chess.Board(fen)
            self.move_history = []  # Clear move history
            self.game_phase = detect_game_phase(self.board)
            self.opening = None  # Reset opening detection
            self.game_started = time.time()
            self.move_times = []
        except ValueError:
            raise ValueError(f"Invalid FEN string: {fen}")
    
    def set_position_from_pgn(self, pgn_str: str):
        """
        Set the board position from a PGN string.
        
        Args:
            pgn_str: The PGN string representing the game
        """
        try:
            # Parse the PGN
            pgn_io = io.StringIO(pgn_str)
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                raise ValueError("Failed to parse PGN string")
            
            # Reset the board
            self.board = game.board()
            
            # Play through the moves to get to the final position
            self.move_history = []
            for move in game.mainline_moves():
                self.move_history.append(move)
                self.board.push(move)
            
            # Update game state
            self.game_phase = detect_game_phase(self.board)
            self.opening = game.headers.get("Opening", None)
            self.game_started = time.time()
            self.move_times = []
            
            # Try to extract metadata from the PGN
            if "White" in game.headers:
                self.player_color = chess.WHITE
            elif "Black" in game.headers:
                self.player_color = chess.BLACK
        except Exception as e:
            raise ValueError(f"Error loading game from PGN: {str(e)}")
    
    def make_move(self, move, update_stats=True):
        """
        Make a move on the board.
        
        Args:
            move: The move to make (can be string in UCI format, or chess.Move)
            update_stats: Whether to update game statistics
            
        Returns:
            bool: Whether the move was legal and applied
        """
        # Convert move to chess.Move if it's a string
        if isinstance(move, str):
            try:
                move = chess.Move.from_uci(move)
            except ValueError:
                try:
                    move = self.board.parse_san(move)
                except ValueError:
                    return False
        
        # Check if the move is legal
        if move not in self.board.legal_moves:
            return False
        
        # Record time for this move
        move_time = time.time()
        
        # Update statistics before making the move
        if update_stats:
            # Check if it's a capture
            if self.board.is_capture(move):
                self.stats["captures"] += 1
            
            # Check if it's a check
            if self.board.gives_check(move):
                self.stats["checks"] += 1
            
            # Check if it's a castling move
            if self.board.is_castling(move):
                self.stats["castling"] = True
            
            # Check if it's a promotion
            if move.promotion is not None:
                self.stats["promotions"] += 1
        
        # Make the move
        self.board.push(move)
        self.move_history.append(move)
        
        # Calculate time taken for this move
        if self.move_times:
            time_taken = move_time - self.move_times[-1]
        else:
            time_taken = move_time - self.game_started
        self.move_times.append(move_time)
        
        # Update game phase
        self.game_phase = detect_game_phase(self.board)
        
        # Detect opening if we're still in the opening phase
        if self.game_phase == "opening" and not self.opening:
            # Convert move history to algebraic notation
            algebraic_moves = []
            temp_board = chess.Board()
            for m in self.move_history:
                algebraic_moves.append(move_to_algebraic(m, temp_board))
                temp_board.push(m)
            
            self.opening = detect_opening_from_moves(algebraic_moves)
        
        return True
    
    def get_engine_move(self, time_limit=None):
        """
        Get the best move from the engine.
        
        Args:
            time_limit: Optional time limit in seconds
            
        Returns:
            chess.Move: The engine's selected move
        """
        if not self.engine:
            raise ValueError("No engine available")
        
        # Get the best move from the engine
        return self.engine.select_move(self.board, time_limit)
    
    def play_engine_move(self, time_limit=None):
        """
        Make a move selected by the engine.
        
        Args:
            time_limit: Optional time limit in seconds
            
        Returns:
            chess.Move: The move played, or None if no legal moves
        """
        if not self.board.legal_moves:
            return None
        
        move = self.get_engine_move(time_limit)
        if move and move != chess.Move.null():
            self.make_move(move)
            return move
        
        # Fallback to a random legal move if engine fails
        fallback_move = list(self.board.legal_moves)[0]
        self.make_move(fallback_move)
        return fallback_move
    
    def get_game_result(self):
        """
        Get the result of the game.
        
        Returns:
            str: The game result ("1-0", "0-1", "1/2-1/2", or "*")
        """
        if self.board.is_checkmate():
            return "0-1" if self.board.turn == chess.WHITE else "1-0"
        elif self.board.is_stalemate() or self.board.is_insufficient_material() or self.board.is_fifty_moves() or self.board.is_repetition(3):
            return "1/2-1/2"
        else:
            return "*"  # Game in progress
    
    def get_pgn(self):
        """
        Get the PGN representation of the current game.
        
        Returns:
            str: The PGN string
        """
        game = chess.pgn.Game()
        
        # Set headers
        game.headers["Event"] = "Copycat Chess Game"
        game.headers["Site"] = "Copycat Engine"
        game.headers["Date"] = datetime.datetime.now().strftime("%Y.%m.%d")
        game.headers["Round"] = "1"
        game.headers["White"] = "Player" if self.player_color == chess.WHITE else "Copycat Engine"
        game.headers["Black"] = "Copycat Engine" if self.player_color == chess.WHITE else "Player"
        game.headers["Result"] = self.get_game_result()
        
        if self.opening:
            game.headers["Opening"] = self.opening
        
        # Add the moves
        node = game
        for move in self.move_history:
            node = node.add_variation(move)
        
        # Export to PGN
        exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=False)
        pgn_string = game.accept(exporter)
        
        return pgn_string
    
    def save_game(self, filename):
        """
        Save the game to a PGN file.
        
        Args:
            filename: The name of the file to save to
        """
        pgn_string = self.get_pgn()
        
        with open(filename, "w") as f:
            f.write(pgn_string)
    
    def save_stats(self, filename):
        """
        Save game statistics to a JSON file.
        
        Args:
            filename: The name of the file to save to
        """
        stats = {
            "game_info": {
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "time_control": self.time_control,
                "moves": len(self.move_history),
                "opening": self.opening if self.opening else "Unknown",
                "result": self.get_game_result()
            },
            "statistics": {
                "captures": self.stats["captures"],
                "checks": self.stats["checks"],
                "castling": self.stats["castling"],
                "promotions": self.stats["promotions"],
                "game_phase": self.game_phase
            }
        }
        
        with open(filename, "w") as f:
            json.dump(stats, f, indent=4)
    
    def __str__(self):
        """
        Get a string representation of the current position.
        
        Returns:
            str: The string representation of the board
        """
        return str(self.board)


def main():
    """Simple demonstration of the ChessGame class."""
    # Create a new game with the engine
    engine = CopycatChessEngine()
    game = ChessGame(engine)
    
    print("Copycat Chess Game")
    print("-----------------")
    print(game)
    
    # Make some moves
    moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6"]
    
    for move_uci in moves:
        print(f"\nMaking move: {move_uci}")
        game.make_move(move_uci)
        print(game)
    
    # Let the engine make a move
    print("\nEngine's turn...")
    engine_move = game.play_engine_move()
    print(f"Engine played: {engine_move.uci()}")
    print(game)
    
    # Print game information
    print(f"\nCurrent phase: {game.game_phase}")
    print(f"Detected opening: {game.opening}")
    print(f"Game result: {game.get_game_result()}")
    
    # Save the game
    game.save_game("demo_game.pgn")
    game.save_stats("demo_stats.json")
    print("\nGame saved to demo_game.pgn")
    print("Statistics saved to demo_stats.json")


if __name__ == "__main__":
    main()
