#!/usr/bin/import chess
import numpy as np
import random
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any, Set
import time
from search import SearchManager, MoveCandidate
"""
Copycat Chess Engine - Data Analytics Edition
This engine uses data analytics from player games to select moves that
mimic a player's style and preferences rather than using traditional
evaluation or neural networks.
"""

import os
import json
import chess
import chess.pgn
import numpy as np
import random
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any, Set
import time

class CopycatChessEngine:
    """
    A chess engine that uses data analytics to mimic a player's style.
    Prioritizes moves based on pattern matching with historical game data.
    """
    
    def __init__(self, results_dir="results"):
        """Initialize the engine with paths to analysis results."""
        self.results_dir = results_dir
        
        # Load analysis data
        self.analysis_data = self.load_analysis_data()
        self.player_stats = self.load_player_stats()
        self.enhanced_analysis = self.load_enhanced_analysis()
        
        # Game state tracking
        self.current_phase = "opening"
        self.move_count = 0
        self.player_color = None
        self.opening_detected = None
        self.time_control = "classical"  # Default
        
        # Move selection parameters
        self.decisiveness_weight = 0.3  # How much to weight decisive outcomes
        self.style_consistency_weight = 0.4  # How much to weight player's style
        self.position_similarity_weight = 0.3  # How much to weight position similarity
        
        # Find enhanced analysis file path
        enhanced_analysis_path = None
        possible_paths = [
            os.path.join(self.results_dir, 'enhanced_analysis_results.json'),
            os.path.join(self.results_dir, 'enhanced_analysis.json'),
            os.path.join(self.results_dir, 'analysis_results.json')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                enhanced_analysis_path = path
                break
        
        # Create search manager with analysis data
        self.search_manager = SearchManager(enhanced_analysis_path)
        
        print(f"Copycat Chess Engine initialized with data analytics from {enhanced_analysis_path if enhanced_analysis_path else 'default profile'}")
    
    def load_analysis_data(self) -> Dict:
        """Load the analysis data from the results directory."""
        try:
            with open(os.path.join(self.results_dir, 'analysis_summary.json'), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: analysis_summary.json not found in {self.results_dir}")
            return {}
    
    def load_player_stats(self) -> Dict:
        """Load the player statistics from the results directory."""
        try:
            with open(os.path.join(self.results_dir, 'player_stats.json'), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: player_stats.json not found in {self.results_dir}")
            
            # Try enhanced player stats
            try:
                with open(os.path.join(self.results_dir, 'enhanced_player_stats.json'), 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                print(f"Warning: enhanced_player_stats.json not found in {self.results_dir}")
                return {}
    
    def load_enhanced_analysis(self) -> Dict:
        """Load the enhanced analysis data from the results directory."""
        try:
            with open(os.path.join(self.results_dir, 'enhanced_analysis.json'), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: enhanced_analysis.json not found in {self.results_dir}")
            return {}
    
    def detect_game_phase(self, board) -> str:
        """
        Detect the current phase of the game based on the position.
        
        Args:
            board: A chess.Board object representing the current position
            
        Returns:
            str: "opening", "middlegame", or "endgame"
        """
        # Count pieces on the board
        piece_count = 0
        queen_count = 0
        
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            piece_count += len(board.pieces(piece_type, chess.WHITE))
            piece_count += len(board.pieces(piece_type, chess.BLACK))
            
            if piece_type == chess.QUEEN:
                queen_count += len(board.pieces(piece_type, chess.WHITE))
                queen_count += len(board.pieces(piece_type, chess.BLACK))
        
        # Check castling rights
        castling_rights = any([
            board.has_kingside_castling_rights(chess.WHITE),
            board.has_queenside_castling_rights(chess.WHITE),
            board.has_kingside_castling_rights(chess.BLACK),
            board.has_queenside_castling_rights(chess.BLACK)
        ])
        
        # Opening: >= 14 pieces, castling rights available, less than 15 full moves
        if piece_count >= 14 and castling_rights and board.fullmove_number <= 15:
            return "opening"
        
        # Endgame: <= 10 pieces or no queens
        elif piece_count <= 10 or queen_count == 0:
            return "endgame"
        
        # Otherwise it's middlegame
        else:
            return "middlegame"
    
    def detect_opening(self, board) -> str:
        """
        Try to detect the opening being played based on the position.
        
        Args:
            board: A chess.Board object representing the current position
            
        Returns:
            str: Name of the detected opening, or None if unknown
        """
        # This is a simple stub - in a real implementation, we would use
        # a database of openings and match the move sequence
        
        # For now, let's use a very simplified approach for demonstration
        move_history = []
        
        # Get the move history
        if hasattr(board, 'move_stack'):
            move_history = [move.uci() for move in board.move_stack]
        
        # Recognize some common openings based on first few moves
        if len(move_history) >= 2:
            if move_history[0] == 'e2e4':
                if move_history[1] == 'c7c6':
                    return "Caro-Kann"
                elif move_history[1] == 'd7d5':
                    return "Scandinavian"
            elif move_history[0] == 'd2d4':
                if len(move_history) >= 3 and move_history[1] == 'd7d5' and move_history[2] == 'c2c4':
                    return "Queen's Gambit"
                if len(move_history) >= 4:
                    if move_history[1] == 'g8f6' and move_history[2] == 'c2c4' and move_history[3] == 'g7g6':
                        return "King's Indian"
            
            # London System often starts with d4 followed by Bf4
            if len(move_history) >= 3:
                if move_history[0] == 'd2d4' and 'c1f4' in move_history[:3]:
                    return "London"
            
            # Vienna Game starts with e4 e5 Nc3
            if len(move_history) >= 3:
                if move_history[0] == 'e2e4' and move_history[1] == 'e7e5' and move_history[2] == 'b1c3':
                    return "Vienna"
        
        return "Unknown"
    
    def calculate_piece_preference_score(self, piece_type: chess.PieceType, move: chess.Move, board: chess.Board) -> float:
        """
        Calculate a score for this move based on the player's piece preferences.
        
        Args:
            piece_type: The type of piece making the move
            move: The candidate move
            board: The current board position
            
        Returns:
            float: A score between 0 and 1 indicating how well this move matches the player's piece preferences
        """
        # Get the piece color
        color = board.turn
        color_name = "white" if color == chess.WHITE else "black"
        piece_name = chess.piece_name(piece_type)
        piece_key = f"{color_name} {piece_name}"
        
        # Default score if we don't have data
        default_score = 0.5
        
        # Try to get piece statistics from enhanced analysis
        try:
            if 'piece_stats' in self.enhanced_analysis:
                if piece_key in self.enhanced_analysis['piece_stats']:
                    # Get symbol for this piece
                    symbol = chess.Piece(piece_type, color).symbol()
                    if symbol in self.enhanced_analysis['piece_stats'][piece_key]:
                        # Get piece stats
                        stats = self.enhanced_analysis['piece_stats'][piece_key][symbol]
                        
                        # Calculate a preference score based on usage frequency in this phase
                        phase_dist = stats.get('phase_distribution', {})
                        phase_moves = phase_dist.get(self.current_phase, 0)
                        total_moves = stats.get('total_moves', 0)
                        
                        if total_moves > 0:
                            # Normalize by dividing by total moves in this phase across all pieces
                            phase_preference = phase_moves / total_moves
                            
                            # Also consider attack vs defense preference
                            is_attacking = False
                            
                            # Check if this move is advancing toward opponent's side
                            from_rank = chess.square_rank(move.from_square)
                            to_rank = chess.square_rank(move.to_square)
                            if (color == chess.WHITE and to_rank > from_rank) or (color == chess.BLACK and to_rank < from_rank):
                                is_attacking = True
                            
                            # Get player's attack vs defense ratio for this piece
                            attack_moves = stats.get('attack_moves', 0)
                            defense_moves = stats.get('defense_moves', 0)
                            if attack_moves + defense_moves > 0:
                                attack_preference = attack_moves / (attack_moves + defense_moves)
                                
                                # Score higher if move matches player's attacking or defending preference
                                if (is_attacking and attack_preference > 0.5) or (not is_attacking and attack_preference <= 0.5):
                                    return 0.7 + 0.3 * phase_preference
                            
                            return 0.4 + 0.6 * phase_preference
        except Exception as e:
            print(f"Error calculating piece preference: {str(e)}")
        
        return default_score
    
    def calculate_square_preference_score(self, piece_type: chess.PieceType, move: chess.Move, board: chess.Board) -> float:
        """
        Calculate a score for this move based on the player's square preferences.
        
        Args:
            piece_type: The type of piece making the move
            move: The candidate move
            board: The current board position
            
        Returns:
            float: A score between 0 and 1 indicating how well this move matches the player's square preferences
        """
        # Get the target square
        to_square = chess.square_name(move.to_square)
        
        # Default score
        default_score = 0.5
        
        # Try to get heatmap data
        try:
            if 'piece_heatmaps' in self.analysis_data:
                piece_symbol = chess.Piece(piece_type, board.turn).symbol()
                if piece_symbol in self.analysis_data['piece_heatmaps']:
                    heatmap = self.analysis_data['piece_heatmaps'][piece_symbol]
                    if to_square in heatmap:
                        # Calculate score based on frequency
                        square_freq = heatmap[to_square]['frequency']
                        
                        # Get max frequency for normalization
                        max_freq = max(data['frequency'] for data in heatmap.values()) if heatmap else 1
                        
                        # Normalize and return
                        return 0.3 + 0.7 * (square_freq / max_freq if max_freq > 0 else 0)
        except Exception as e:
            print(f"Error calculating square preference: {str(e)}")
        
        return default_score
    
    def calculate_move_timing_score(self, board: chess.Board, remaining_time: Optional[float] = None) -> float:
        """
        Calculate a timing score based on how the player typically allocates time.
        
        Args:
            board: The current board position
            remaining_time: The remaining time in the game, if available
            
        Returns:
            float: A factor between 0 and 1 to adjust think time
        """
        # Default timing factor
        default_factor = 0.5
        
        # If we don't have timing data or remaining time, use default
        if remaining_time is None:
            return default_factor
        
        try:
            # Use enhanced analysis if available
            if 'time_control_distribution' in self.enhanced_analysis:
                # Adjust timing based on the current phase
                if self.current_phase == "opening":
                    # Player typically spends less time in opening
                    return 0.3
                elif self.current_phase == "middlegame":
                    # Player typically spends more time in middlegame
                    return 0.7
                elif self.current_phase == "endgame":
                    # Player's endgame timing depends on complexity
                    piece_count = sum(1 for _ in board.piece_map())
                    if piece_count <= 6:  # Very few pieces
                        return 0.4  # Less time needed for simple endgames
                    else:
                        return 0.6  # More time for complex endgames
        except Exception as e:
            print(f"Error calculating timing score: {str(e)}")
        
        return default_factor
    
    def calculate_opening_move_score(self, move: chess.Move, board: chess.Board) -> float:
        """
        Calculate a score for this move based on opening preferences.
        
        Args:
            move: The candidate move
            board: The current board position
            
        Returns:
            float: A score between 0 and 1 for this opening move
        """
        # Default score
        default_score = 0.5
        
        # Try to get opening preferences
        try:
            if self.opening_detected and 'opening_stats' in self.enhanced_analysis:
                if self.opening_detected in self.enhanced_analysis['opening_stats']:
                    opening_stats = self.enhanced_analysis['opening_stats'][self.opening_detected]
                    
                    # Calculate win rate for this opening
                    total_games = opening_stats.get('games', 0)
                    wins = opening_stats.get('wins', 0)
                    
                    if total_games > 0:
                        win_rate = wins / total_games
                        
                        # Higher score for openings with better results
                        opening_score = 0.4 + 0.6 * win_rate
                        
                        # Check if this is a "focus opening"
                        if any(focus in self.opening_detected for focus in ["London", "Vienna", "Caro-Kann", "Scandinavian"]):
                            opening_score *= 1.2  # Boost score for focus openings
                            opening_score = min(opening_score, 1.0)  # Cap at 1.0
                        
                        return opening_score
        except Exception as e:
            print(f"Error calculating opening move score: {str(e)}")
        
        return default_score
    
    def calculate_decisiveness_factor(self) -> float:
        """
        Calculate a factor based on game decisiveness preferences.
        
        Returns:
            float: A factor between 0 and 1 to adjust move aggressiveness
        """
        # Default factor (neutral)
        default_factor = 0.5
        
        try:
            if 'game_decisiveness' in self.enhanced_analysis:
                decisiveness = self.enhanced_analysis['game_decisiveness']
                
                # Calculate ratio of decisive to non-decisive games
                decisive_games = decisiveness.get('checkmate', 0) + decisiveness.get('resignation', 0)
                non_decisive_games = decisiveness.get('draw', 0) + decisiveness.get('stalemate', 0)
                total_games = decisive_games + non_decisive_games
                
                if total_games > 0:
                    decisive_ratio = decisive_games / total_games
                    
                    # Higher ratio means player prefers decisive outcomes
                    return 0.3 + 0.7 * decisive_ratio
        except Exception as e:
            print(f"Error calculating decisiveness factor: {str(e)}")
        
        return default_factor
    
    def score_move(self, move: chess.Move, board: chess.Board) -> float:
        """
        Score a candidate move based on how well it matches the player's style.
        
        Args:
            move: The candidate move
            board: The current board position
            
        Returns:
            float: A score for this move (higher is better)
        """
        # Get the piece making the move
        piece = board.piece_at(move.from_square)
        if piece is None:
            return 0.0  # Invalid move
        
        # Base score
        base_score = 0.5
        
        # Get piece type
        piece_type = piece.piece_type
        
        # Calculate component scores
        piece_preference = self.calculate_piece_preference_score(piece_type, move, board)
        square_preference = self.calculate_square_preference_score(piece_type, move, board)
        
        # Phase-specific scoring
        if self.current_phase == "opening":
            opening_score = self.calculate_opening_move_score(move, board)
            # In opening, prioritize opening book and square preference
            score = 0.4 * opening_score + 0.3 * piece_preference + 0.3 * square_preference
        elif self.current_phase == "middlegame":
            # In middlegame, prioritize piece preference and style consistency
            decisiveness = self.calculate_decisiveness_factor()
            score = 0.4 * piece_preference + 0.4 * square_preference + 0.2 * decisiveness
        else:  # Endgame
            # In endgame, use a different balance
            score = 0.5 * piece_preference + 0.5 * square_preference
        
        # Apply randomness to avoid predictability
        randomness = random.uniform(0.95, 1.05)
        return score * randomness
    
    def select_move(self, board: chess.Board, remaining_time: Optional[float] = None) -> chess.Move:
        """
        Select a move based on the player's style.
        
        Args:
            board: The current board position
            remaining_time: The remaining time in the game, if available
            
        Returns:
            chess.Move: The selected move
        """
        # Update game state
        self.move_count = board.fullmove_number
        self.current_phase = self.detect_game_phase(board)
        
        # Detect opening if we're still in the opening phase
        if self.current_phase == "opening" and self.opening_detected is None:
            self.opening_detected = self.detect_opening(board)
            print(f"Opening detected: {self.opening_detected}")
        
        # Use the search manager to select the best move
        best_move, candidates = self.search_manager.search_best_move(
            board, 
            self.current_phase,
            self.opening_detected
        )
        
        # If no move was found, return a null move
        if best_move is None:
            return chess.Move.null()
            
        # For debugging, print the top candidates
        if len(candidates) > 0:
            print(f"Top move: {best_move.uci()} (Score: {candidates[0].overall_score:.3f})")
            for i, candidate in enumerate(candidates[:3]):
                print(f"  {i+1}. {candidate}")
        
        return best_move
    
    def get_name(self) -> str:
        """Return the engine name."""
        return "Copycat Chess Engine (Data Analytics Edition)"
    
    def get_author(self) -> str:
        """Return the engine author."""
        return "v7p3r (Analytics by GitHub Copilot)"

class CopycatUCIEngine:
    """
    UCI interface for the Copycat Chess Engine.
    """
    
    def __init__(self):
        """Initialize the UCI interface."""
        self.engine = CopycatChessEngine()
        self.board = chess.Board()
        self.debug_mode = False
    
    def uci(self):
        """Identify engine for UCI protocol."""
        print(f"id name {self.engine.get_name()}")
        print(f"id author {self.engine.get_author()}")
        print("option name Debug type check default false")
        print("uciok")
    
    def debug(self, args):
        """Set debug mode."""
        if args == "on":
            self.debug_mode = True
        else:
            self.debug_mode = False
    
    def isready(self):
        """Confirm engine is ready."""
        print("readyok")
    
    def setoption(self, name, value):
        """Set an engine option."""
        name = name.lower()
        if name == "debug":
            self.debug = (value.lower() == "true")
    
    def ucinewgame(self):
        """Start a new game."""
        self.board = chess.Board()
    
    def position(self, args):
        """Set up a position."""
        if not args:
            return
        
        # Starting position
        if args[0] == "startpos":
            self.board = chess.Board()
            args = args[1:]
        
        # Position from FEN
        elif args[0] == "fen":
            fen = " ".join(args[1:7])
            self.board = chess.Board(fen)
            args = args[7:]
        
        # Apply moves if any
        if args and args[0] == "moves":
            for move in args[1:]:
                try:
                    self.board.push_uci(move)
                except ValueError:
                    break
    
    def go(self, args):
        """Calculate and output the best move."""
        # Parse time control parameters
        params = {}
        i = 0
        while i < len(args):
            if args[i] in ["wtime", "btime", "winc", "binc", "movestogo", "depth", "nodes", "movetime"]:
                if i + 1 < len(args):
                    try:
                        params[args[i]] = int(args[i + 1])
                    except ValueError:
                        pass
                i += 2
            else:
                i += 1
        
        # Calculate remaining time if available
        remaining_time = None
        if self.board.turn == chess.WHITE and "wtime" in params:
            remaining_time = params["wtime"] / 1000.0  # Convert from ms to seconds
        elif self.board.turn == chess.BLACK and "btime" in params:
            remaining_time = params["btime"] / 1000.0
        
        # Set a maximum think time
        think_time = 1.0  # Default 1 second
        if "movetime" in params:
            think_time = params["movetime"] / 1000.0
        elif remaining_time is not None:
            # Use about 5% of remaining time, adjusted by timing score
            timing_score = self.engine.calculate_move_timing_score(self.board, remaining_time)
            think_time = remaining_time * 0.05 * timing_score
            
            # Cap think time at reasonable values
            think_time = min(think_time, 5.0)  # Maximum 5 seconds
            think_time = max(think_time, 0.1)  # Minimum 0.1 seconds
        
        # Think for a bit to simulate evaluation
        start_time = time.time()
        
        # Select best move
        best_move = self.engine.select_move(self.board, remaining_time)
        
        # Ensure minimum think time
        elapsed = time.time() - start_time
        if elapsed < think_time:
            time.sleep(think_time - elapsed)
        
        # Output best move
        if best_move:
            print(f"bestmove {best_move.uci()}")
        else:
            print("bestmove (none)")
    
    def run(self):
        """Main UCI protocol loop."""
        while True:
            try:
                line = input().strip()
                
                if not line:
                    continue
                
                parts = line.split()
                command = parts[0].lower()
                args = parts[1:]
                
                if command == "uci":
                    self.uci()
                elif command == "debug":
                    self.debug(args[0] if args else "off")
                elif command == "isready":
                    self.isready()
                elif command == "setoption":
                    if len(args) >= 4 and args[0] == "name" and args[2] == "value":
                        self.setoption(args[1], args[3])
                elif command == "ucinewgame":
                    self.ucinewgame()
                elif command == "position":
                    self.position(args)
                elif command == "go":
                    self.go(args)
                elif command == "quit":
                    break
            except EOFError:
                break
            except Exception as e:
                print(f"info string Error: {str(e)}")

def main():
    """Run the UCI engine."""
    engine = CopycatUCIEngine()
    engine.run()

if __name__ == "__main__":
    main()
