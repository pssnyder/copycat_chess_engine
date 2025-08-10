#!/usr/bin/env python3
"""
Move Search and Selection Module for Copycat Chess Engine

This module handles the search for the best moves based on style-based pattern matching
rather than traditional alpha-beta or neural network evaluations.
"""

import chess
import numpy as np
import random
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Set, Any
import time

class MoveCandidate:
    """Represents a candidate move with associated scoring metrics."""
    def __init__(self, move: chess.Move):
        self.move = move
        self.overall_score = 0.0
        
        # Component scores
        self.piece_preference_score = 0.0
        self.square_preference_score = 0.0
        self.opening_score = 0.0
        self.decisiveness_score = 0.0
        self.positional_score = 0.0
        self.tactical_score = 0.0
    
    def __lt__(self, other):
        """For sorting candidates."""
        return self.overall_score < other.overall_score
    
    def __str__(self):
        """String representation for debugging."""
        return (f"Move: {self.move.uci()}, Score: {self.overall_score:.3f} "
                f"(Piece: {self.piece_preference_score:.2f}, Square: {self.square_preference_score:.2f}, "
                f"Opening: {self.opening_score:.2f}, Decisive: {self.decisiveness_score:.2f}, "
                f"Positional: {self.positional_score:.2f}, Tactical: {self.tactical_score:.2f})")


import json
import os

class SearchManager:
    """
    Manages the search for best moves based on style metrics.
    This is not a traditional search engine - instead it uses pattern matching
    and statistical preferences to find moves that match the player's style.
    """
    def __init__(self, analysis_file: Optional[str] = None):
        """
        Initialize the search manager.
        
        Args:
            analysis_file: Path to the analysis JSON file. If None, will look for default location.
        """
        # Configuration
        self.randomization_factor = 0.05  # Small randomization for variety
        self.top_move_count = 3  # Number of top moves to consider in final selection
        
        # Default phase-specific weights
        self.phase_weights = {
            "opening": {
                "opening_pattern": 0.30,
                "piece_preference": 0.20,
                "square_preference": 0.20,
                "decisiveness": 0.00,
                "positional": 0.20,
                "tactical": 0.10
            },
            "middlegame": {
                "opening_pattern": 0.00,
                "piece_preference": 0.25,
                "square_preference": 0.25,
                "decisiveness": 0.15,
                "positional": 0.15,
                "tactical": 0.20
            },
            "endgame": {
                "opening_pattern": 0.00,
                "piece_preference": 0.25,
                "square_preference": 0.20,
                "decisiveness": 0.00,
                "positional": 0.30,
                "tactical": 0.25
            }
        }
        
        # Load analysis data if available
        self.analysis_data = self._load_analysis_data(analysis_file)
        
        # If analysis data is available, update our parameters
        if self.analysis_data:
            self._update_parameters_from_analysis()
    
    def _load_analysis_data(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load analysis data from JSON file
        
        Args:
            file_path: Path to the analysis JSON file
            
        Returns:
            Dictionary containing analysis data, or empty dict if file not found
        """
        # If no path provided, try default locations
        if file_path is None:
            # Try to find a results file
            possible_paths = [
                "results/enhanced_analysis_results.json",
                "results/analysis_results.json",
                "enhanced_analysis_results.json",
                "analysis_results.json"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    file_path = path
                    break
        
        # If we have a valid path, try to load it
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    print(f"Loaded analysis data from {file_path}")
                    return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading analysis data: {e}")
                return {}
        
        print("No analysis data found. Using default style profile.")
        return {}
    
    def _update_parameters_from_analysis(self):
        """Update search parameters based on loaded analysis data"""
        # Example: Update phase weights if available
        if "phase_distribution" in self.analysis_data:
            phase_dist = self.analysis_data["phase_distribution"]
            if "opening" in phase_dist and phase_dist["opening"] > 0.4:
                # Player spends more time in openings, increase opening pattern weight
                self.phase_weights["opening"]["opening_pattern"] = 0.5
            
            if "endgame" in phase_dist and phase_dist["endgame"] > 0.3:
                # Player spends more time in endgames, adjust endgame weights
                self.phase_weights["endgame"]["piece_preference"] = 0.6
        
        # Example: Update style metrics
        if "style_metrics" in self.analysis_data:
            style = self.analysis_data["style_metrics"]
            if "aggressiveness" in style:
                # Adjust decisiveness weight based on aggressiveness
                agg_factor = style["aggressiveness"]
                self.phase_weights["middlegame"]["decisiveness"] = 0.2 * (1 + agg_factor)
        
        # Example: Adjust randomization based on decisiveness
        if "decisiveness" in self.analysis_data:
            decisive_factor = self.analysis_data["decisiveness"]
            # More decisive players get less randomization
            self.randomization_factor = max(0.01, 0.05 * (1 - decisive_factor))
    
    def search_best_move(self, board: chess.Board, 
                         current_phase: str,
                         opening_detected: Optional[str] = None,
                         analyze_callback = None) -> Tuple[Optional[chess.Move], List[MoveCandidate]]:
        """
        Search for the best move according to player style.
        
        Args:
            board: Current chess position
            current_phase: Game phase ("opening", "middlegame", "endgame")
            opening_detected: Name of the detected opening if known
            analyze_callback: Function to call with analysis info (for UCI)
            
        Returns:
            Tuple of (best_move, all_candidates)
        """
        # Get legal moves
        legal_moves = list(board.legal_moves)
        
        # Handle special cases
        if not legal_moves:
            return None, []
        if len(legal_moves) == 1:
            return legal_moves[0], [MoveCandidate(legal_moves[0])]
        
        # Create move candidates
        candidates = [MoveCandidate(move) for move in legal_moves]
        
        # Get phase-specific weights
        weights = self.phase_weights.get(current_phase, self.phase_weights["middlegame"])
        
        # Calculate scores for each candidate
        for candidate in candidates:
            self.score_candidate(candidate, board, current_phase, opening_detected, weights)
        
        # Sort by score (descending)
        candidates.sort(key=lambda c: c.overall_score, reverse=True)
        
        # Send info if callback provided
        if analyze_callback:
            for i, candidate in enumerate(candidates[:5]):  # Show top 5
                analyze_callback(f"info multipv {i+1} score cp {int(candidate.overall_score*100)} pv {candidate.move.uci()}")
        
        # Select from top candidates with weighted probability
        top_candidates = candidates[:min(self.top_move_count, len(candidates))]
        
        if not top_candidates:
            return None, candidates
        
        # Normalize scores for probability calculation
        scores = np.array([c.overall_score for c in top_candidates])
        min_score = scores.min()
        
        # Ensure all scores are positive
        if min_score < 0:
            scores = scores - min_score
        
        # Avoid division by zero
        score_sum = scores.sum()
        if score_sum <= 0:
            # If all scores are zero, use uniform probability
            selected_move = random.choice(top_candidates).move
        else:
            # Calculate selection probabilities
            probs = scores / score_sum
            selected_index = np.random.choice(len(top_candidates), p=probs)
            selected_move = top_candidates[selected_index].move
        
        return selected_move, candidates
    
    def score_candidate(self, candidate: MoveCandidate, 
                        board: chess.Board,
                        current_phase: str,
                        opening_detected: Optional[str],
                        weights: Dict[str, float]):
        """
        Calculate various scores for a move candidate.
        
        Args:
            candidate: The move candidate to score
            board: The current chess position
            current_phase: The current game phase
            opening_detected: The detected opening if available
            weights: The phase-specific weights to apply
        """
        # Get the piece making the move
        piece = board.piece_at(candidate.move.from_square)
        if piece is None:
            candidate.overall_score = 0.0
            return
        
        # Calculate the component scores based on player's style
        
        # Piece preference score (how much the player likes to use this piece type)
        candidate.piece_preference_score = self.calculate_piece_preference(piece, candidate.move, board, current_phase)
        
        # Square preference score (how much the player likes to move to this square)
        candidate.square_preference_score = self.calculate_square_preference(piece, candidate.move, board, current_phase)
        
        # Opening score (only relevant in opening phase)
        if current_phase == "opening" and opening_detected:
            candidate.opening_score = self.calculate_opening_score(candidate.move, board, opening_detected)
        
        # Decisiveness score (more important in middlegame)
        if current_phase == "middlegame":
            candidate.decisiveness_score = self.calculate_decisiveness_score(candidate.move, board)
        
        # Positional score (structure, control, etc.)
        candidate.positional_score = self.calculate_positional_score(candidate.move, board, current_phase)
        
        # Tactical score (captures, checks, threats, etc.)
        candidate.tactical_score = self.calculate_tactical_score(candidate.move, board)
        
        # Apply weights to component scores based on the current phase
        weighted_score = (
            weights["piece_preference"] * candidate.piece_preference_score +
            weights["square_preference"] * candidate.square_preference_score +
            weights["opening_pattern"] * candidate.opening_score +
            weights["decisiveness"] * candidate.decisiveness_score +
            weights["positional"] * candidate.positional_score +
            weights["tactical"] * candidate.tactical_score
        )
        
        # Add small randomization for variety (within configured randomization factor)
        randomization = 1.0 + random.uniform(-self.randomization_factor, self.randomization_factor)
        candidate.overall_score = weighted_score * randomization
    
    def calculate_piece_preference(self, piece: chess.Piece, move: chess.Move, 
                                  board: chess.Board, phase: str) -> float:
        """
        Calculate piece preference score based on the player's historical preferences.
        This function should be connected to the actual player statistics from analysis data.
        
        Args:
            piece: The piece making the move
            move: The candidate move
            board: The current board position
            phase: The game phase
            
        Returns:
            A score between 0 and 1
        """
        # In the integrated version, this would access the enhanced analysis data
        # to get real player preferences. For now, using placeholder data.
        
        # Get piece type and color
        piece_type = piece.piece_type
        color = piece.color
        color_name = "white" if color == chess.WHITE else "black"
        piece_name = chess.piece_name(piece_type)
        
        # Check if this is a capture move
        is_capture = board.is_capture(move)
        
        # Check if this gives check
        test_board = board.copy()
        test_board.push(move)
        gives_check = test_board.is_check()
        
        # Determine if move is attacking or defensive
        # For white, moving toward higher ranks is generally attacking
        # For black, moving toward lower ranks is generally attacking
        from_rank = chess.square_rank(move.from_square)
        to_rank = chess.square_rank(move.to_square)
        is_attacking = (color == chess.WHITE and to_rank > from_rank) or (color == chess.BLACK and to_rank < from_rank)
        
        # Base score by piece type (placeholder - would use actual data)
        if piece_type == chess.KNIGHT:
            base_score = 0.8  # Player prefers knights
        elif piece_type == chess.BISHOP:
            base_score = 0.6  # Less preference for bishops
        elif piece_type == chess.QUEEN:
            base_score = 0.7
        elif piece_type == chess.ROOK:
            base_score = 0.65
        elif piece_type == chess.PAWN:
            # Check if this is a pawn push to 7th/2nd rank
            if (color == chess.WHITE and to_rank == 6) or (color == chess.BLACK and to_rank == 1):
                base_score = 0.85  # Player likes advancing pawns
            else:
                base_score = 0.7
        else:  # KING
            # Check if this is castling
            if board.is_castling(move):
                base_score = 0.9  # Player likes castling
            else:
                base_score = 0.5
        
        # Adjust score based on phase
        if phase == "opening" and piece_type in [chess.KNIGHT, chess.BISHOP]:
            base_score *= 1.2  # Player prefers developing minor pieces in opening
        elif phase == "middlegame" and is_attacking:
            base_score *= 1.1  # Player prefers attacking in middlegame
        elif phase == "endgame" and piece_type == chess.KING:
            base_score *= 1.2  # Player prefers active king in endgame
            
        # Adjust for captures and checks
        if is_capture:
            base_score *= 1.1
        if gives_check:
            base_score *= 1.15
            
        # Cap at 1.0
        return min(base_score, 1.0)
    
    def calculate_square_preference(self, piece: chess.Piece, move: chess.Move, 
                                   board: chess.Board, phase: str) -> float:
        """
        Calculate square preference score based on the player's historical preferences.
        This uses analysis data if available, otherwise falls back to defaults.
        
        Args:
            piece: The piece making the move
            move: The candidate move
            board: The current board position
            phase: The game phase
            
        Returns:
            A score between 0 and 1
        """
        # Get target square
        to_square = chess.square_name(move.to_square)
        piece_type = piece.piece_type
        piece_name = chess.piece_name(piece_type)
        
        # Check if we have piece-square tables in analysis data
        if self.analysis_data and "piece_square_tables" in self.analysis_data:
            tables = self.analysis_data.get("piece_square_tables", {})
            
            # Try to get phase-specific table
            phase_tables = tables.get(phase, {})
            
            # Try to get piece-specific table
            if piece_name in phase_tables:
                square_values = phase_tables[piece_name]
                
                # If the square is in the table, use that value
                if to_square in square_values:
                    # Normalize value to 0-1 range
                    min_val = min(square_values.values())
                    max_val = max(square_values.values())
                    range_val = max_val - min_val
                    
                    if range_val > 0:
                        return (square_values[to_square] - min_val) / range_val
                    else:
                        return 0.5
        
        # Fallback to default preferences if no analysis data is available
        # Default behavior: prefer central squares
        central_squares = {'d4', 'd5', 'e4', 'e5'}
        near_central = {'c3', 'c4', 'c5', 'c6', 'd3', 'd6', 'e3', 'e6', 'f3', 'f4', 'f5', 'f6'}
        
        # Different pieces have different preferred areas
        if piece_type == chess.KNIGHT:
            # Knights like central squares more
            if to_square in central_squares:
                return 0.95
            elif to_square in near_central:
                return 0.8
            else:
                return 0.4
        elif piece_type == chess.BISHOP:
            # Bishops like diagonals and open squares
            if to_square in {'c1', 'c8', 'f1', 'f8', 'a3', 'a6', 'h3', 'h6'}:
                return 0.7  # Common bishop squares
            elif to_square in central_squares:
                return 0.8
            else:
                return 0.5
        elif piece_type == chess.ROOK:
            # Rooks like open files and 7th rank
            rank = chess.square_rank(move.to_square)
            if rank == 6 and piece.color == chess.WHITE or rank == 1 and piece.color == chess.BLACK:
                return 0.9  # 7th rank
            else:
                return 0.6
        elif piece_type == chess.KING:
            # King likes safety in opening/middlegame, central in endgame
            if phase == "endgame":
                if to_square in central_squares:
                    return 0.85
                elif to_square in near_central:
                    return 0.7
                else:
                    return 0.5
            else:
                # In opening/middlegame, king prefers the corners/sides
                edge_squares = {
                    'a1', 'b1', 'c1', 'a2', 'b2',  # White queenside
                    'f1', 'g1', 'h1', 'f2', 'g2', 'h2',  # White kingside
                    'a8', 'b8', 'c8', 'a7', 'b7',  # Black queenside
                    'f8', 'g8', 'h8', 'f7', 'g7', 'h7'   # Black kingside
                }
                if to_square in edge_squares:
                    return 0.8
                else:
                    return 0.4
        else:  # Queen or Pawn
            if to_square in central_squares:
                return 0.9
            elif to_square in near_central:
                return 0.75
            else:
                return 0.5
    
    def calculate_opening_score(self, move: chess.Move, board: chess.Board, 
                               opening_detected: str) -> float:
        """
        Calculate opening score based on the detected opening.
        Uses analysis data if available.
        
        Args:
            move: The candidate move
            board: The current board position
            opening_detected: The name of the detected opening
            
        Returns:
            A score between 0 and 1
        """
        move_uci = move.uci()
        
        # Check if we have opening data in analysis
        if self.analysis_data and "opening_patterns" in self.analysis_data:
            openings = self.analysis_data.get("opening_patterns", {})
            
            # Check if we have data for this specific opening
            if opening_detected.lower() in {k.lower() for k in openings.keys()}:
                # Find the opening key with case-insensitive match
                opening_key = next((k for k in openings.keys() 
                                   if k.lower() == opening_detected.lower()), None)
                
                if opening_key:
                    opening_data = openings[opening_key]
                    
                    # Check if this move appears in the opening data
                    move_stats = opening_data.get("common_moves", {})
                    
                    if move_uci in move_stats:
                        # Normalize the frequency to a score
                        move_freq = move_stats[move_uci]
                        # Assuming move_freq is already normalized between 0-1
                        return move_freq
                    
                    # If we have board position data (FEN-based)
                    position_stats = opening_data.get("position_moves", {})
                    board_fen = board.fen().split(' ')[0]  # Just the piece placement part
                    
                    if board_fen in position_stats:
                        position_moves = position_stats[board_fen]
                        if move_uci in position_moves:
                            return position_moves[move_uci]
        
        # If no analysis data or no match, use some hardcoded defaults
        
        # Common opening principles and popular moves
        if opening_detected == "London System":
            if move_uci in ["c1f4", "d2d4", "g1f3", "e2e3", "c2c3"]:
                return 1.0
        elif "Caro-Kann" in opening_detected:
            if move_uci in ["c7c6", "d5d4", "b8c6"]:
                return 0.9
        elif "Sicilian" in opening_detected:
            if move_uci in ["c7c5", "d7d6", "b8c6", "g8f6"]:
                return 0.9
        elif "French" in opening_detected:
            if move_uci in ["e7e6", "d7d5", "b8c6"]:
                return 0.9
        elif "Ruy Lopez" in opening_detected:
            if move_uci in ["e7e5", "b8c6", "a7a6", "g8f6"]:
                return 0.9
        elif "Italian Game" in opening_detected:
            if move_uci in ["e7e5", "b8c6", "f8c5", "g8f6"]:
                return 0.9
        
        # Generic opening principles
        current_turn = board.turn
        
        # General opening principles
        if current_turn == chess.WHITE:
            # White common first moves
            if move_uci in ["e2e4", "d2d4", "c2c4", "g1f3"]:
                return 0.8
            # Develop minor pieces
            elif move_uci in ["b1c3", "g1f3", "c1f4", "c1g5", "f1c4", "f1b5"]:
                return 0.7
            # Castle
            elif move_uci in ["e1g1", "e1c1"]:
                return 0.85
        else:
            # Black common responses
            if move_uci in ["e7e5", "c7c5", "c7c6", "e7e6", "d7d5", "g7g6", "b7b6"]:
                return 0.8
            # Develop minor pieces
            elif move_uci in ["b8c6", "g8f6", "c8f5", "c8g4", "f8c5", "f8e7"]:
                return 0.7
            # Castle
            elif move_uci in ["e8g8", "e8c8"]:
                return 0.85
                
        # Default score for other moves
        return 0.5
    
    def calculate_decisiveness_score(self, move: chess.Move, board: chess.Board) -> float:
        """
        Calculate decisiveness score based on how much a move leads to decisive positions.
        Uses analysis data if available.
        
        Args:
            move: The candidate move
            board: The current board position
            
        Returns:
            A score between 0 and 1
        """
        # Initialize with a default score
        score = 0.5
        
        # Check if we have decisiveness metrics in analysis data
        decisiveness_profile = None
        if self.analysis_data and "decisiveness" in self.analysis_data:
            decisiveness_profile = self.analysis_data["decisiveness"]
        
        # Create a test board to see the position after the move
        test_board = board.copy()
        test_board.push(move)
        
        # Gather move characteristics
        is_capture = board.is_capture(move)
        gives_check = test_board.is_check()
        is_promotion = move.promotion is not None
        
        # If we have a decisiveness profile from analysis, use it to weight these factors
        if decisiveness_profile:
            # Get weights for different types of moves
            capture_weight = decisiveness_profile.get("capture_weight", 0.2)
            check_weight = decisiveness_profile.get("check_weight", 0.3)
            promotion_weight = decisiveness_profile.get("promotion_weight", 0.4)
            
            # Apply weights based on move characteristics
            if is_capture:
                score += capture_weight
            if gives_check:
                score += check_weight
            if is_promotion:
                score += promotion_weight
                
            # Material imbalance weight
            if is_capture and board.piece_at(move.to_square) is not None:
                captured_piece = board.piece_at(move.to_square).piece_type
                moving_piece = board.piece_at(move.from_square).piece_type
                
                piece_values = decisiveness_profile.get("piece_values", {
                    "pawn": 1,
                    "knight": 3,
                    "bishop": 3,
                    "rook": 5, 
                    "queen": 9,
                    "king": 0
                })
                
                # Convert to chess.py piece types
                chess_piece_values = {
                    chess.PAWN: piece_values.get("pawn", 1),
                    chess.KNIGHT: piece_values.get("knight", 3),
                    chess.BISHOP: piece_values.get("bishop", 3),
                    chess.ROOK: piece_values.get("rook", 5),
                    chess.QUEEN: piece_values.get("queen", 9),
                    chess.KING: piece_values.get("king", 0)
                }
                
                # If capturing higher value piece with lower value piece
                if chess_piece_values[captured_piece] > chess_piece_values[moving_piece]:
                    favorable_exchange_weight = decisiveness_profile.get("favorable_exchange_weight", 0.2)
                    score += favorable_exchange_weight
        else:
            # Fallback to default logic if no analysis data
            if is_capture:
                score += 0.2
                
                # Capturing with a lower value piece is even more decisive
                if board.piece_at(move.to_square) is not None:
                    captured_piece = board.piece_at(move.to_square).piece_type
                    moving_piece = board.piece_at(move.from_square).piece_type
                    
                    piece_values = {
                        chess.PAWN: 1,
                        chess.KNIGHT: 3,
                        chess.BISHOP: 3,
                        chess.ROOK: 5,
                        chess.QUEEN: 9,
                        chess.KING: 0
                    }
                    
                    # If capturing higher value piece with lower value piece
                    if piece_values[captured_piece] > piece_values[moving_piece]:
                        score += 0.2
            
            # Check if move gives check
            if gives_check:
                score += 0.3
                
            # Check if move is a promotion
            if is_promotion:
                score += 0.4
        
        # Additional factors
        
        # Count attacked pieces after the move
        attacked_pieces = 0
        for sq in chess.SQUARES:
            piece = test_board.piece_at(sq)
            if piece and piece.color != board.turn:
                if test_board.is_attacked_by(board.turn, sq):
                    attacked_pieces += 1
        
        # More attacked pieces = more decisive position
        if attacked_pieces > 2:
            score += 0.1
        
        # Cap at 1.0
        return min(score, 1.0)
        
    def calculate_positional_score(self, move: chess.Move, board: chess.Board, phase: str) -> float:
        """
        Calculate a positional score based on structure, control, and other positional factors.
        
        Args:
            move: The candidate move
            board: The current board position
            phase: The current game phase
            
        Returns:
            A score between 0 and 1
        """
        # Initialize score
        score = 0.5
        
        # Create a test board to see the position after the move
        test_board = board.copy()
        test_board.push(move)
        
        # Calculate pawn structure score
        pawn_structure_score = self._evaluate_pawn_structure(test_board)
        
        # Calculate piece mobility score (number of legal moves after this move)
        piece_mobility_score = self._evaluate_mobility(test_board)
        
        # Calculate king safety
        king_safety_score = self._evaluate_king_safety(test_board, phase)
        
        # Calculate center control
        center_control_score = self._evaluate_center_control(test_board)
        
        # Weight the factors based on game phase
        if phase == "opening":
            # In opening, prioritize development and center control
            score = 0.3 * pawn_structure_score + 0.2 * piece_mobility_score + \
                    0.2 * king_safety_score + 0.3 * center_control_score
        elif phase == "middlegame":
            # In middlegame, balance all factors
            score = 0.25 * pawn_structure_score + 0.25 * piece_mobility_score + \
                    0.25 * king_safety_score + 0.25 * center_control_score
        else:  # endgame
            # In endgame, prioritize pawn structure and mobility
            score = 0.4 * pawn_structure_score + 0.4 * piece_mobility_score + \
                    0.1 * king_safety_score + 0.1 * center_control_score
        
        # Apply player's positional style preference if available from analysis data
        if self.analysis_data and "style_metrics" in self.analysis_data:
            style = self.analysis_data.get("style_metrics", {})
            positional_preference = style.get("positional", 0.5)
            
            # Adjust score based on player's positional preference
            # If player has high positional preference, increase the score's impact
            score = 0.5 + (score - 0.5) * positional_preference * 1.5
        
        return min(max(score, 0.0), 1.0)  # Ensure score is between 0 and 1

    def calculate_tactical_score(self, move: chess.Move, board: chess.Board) -> float:
        """
        Calculate a tactical score based on captures, checks, threats, and tactical motifs.
        
        Args:
            move: The candidate move
            board: The current board position
            
        Returns:
            A score between 0 and 1
        """
        # Initialize score
        score = 0.5
        
        # Create a test board to see the position after the move
        test_board = board.copy()
        test_board.push(move)
        
        # Check for basic tactical elements
        is_capture = board.is_capture(move)
        gives_check = test_board.is_check()
        is_promotion = move.promotion is not None
        
        # Calculate material gain/loss from this move
        material_score = self._evaluate_material_change(move, board)
        
        # Check for common tactical motifs
        fork_score = self._detect_fork(move, board)
        pin_score = self._detect_pin(move, board)
        discovered_attack_score = self._detect_discovered_attack(move, board)
        
        # Weight the tactical elements
        tactical_elements = []
        
        if is_capture:
            tactical_elements.append(0.3 + 0.4 * material_score)  # Base capture + material value
        
        if gives_check:
            tactical_elements.append(0.7)  # Checks are generally good
        
        if is_promotion:
            tactical_elements.append(0.9)  # Promotions are very good
        
        if fork_score > 0:
            tactical_elements.append(0.8 * fork_score)
        
        if pin_score > 0:
            tactical_elements.append(0.7 * pin_score)
        
        if discovered_attack_score > 0:
            tactical_elements.append(0.8 * discovered_attack_score)
        
        # If we found tactical elements, use the highest score
        if tactical_elements:
            tactical_score = max(tactical_elements)
        else:
            tactical_score = 0.4  # No tactical elements found
        
        # Apply player's tactical style preference if available from analysis data
        if self.analysis_data and "style_metrics" in self.analysis_data:
            style = self.analysis_data.get("style_metrics", {})
            tactical_preference = style.get("tactical", 0.5)
            
            # Adjust score based on player's tactical preference
            # If player has high tactical preference, increase the score's impact
            tactical_score = tactical_score * (0.7 + 0.6 * tactical_preference)
        
        return min(tactical_score, 1.0)  # Ensure score is between 0 and 1

    def _evaluate_pawn_structure(self, board: chess.Board) -> float:
        """
        Evaluate the pawn structure in the given position.
        
        Args:
            board: The board position to evaluate
            
        Returns:
            A score between 0 and 1 where higher is better
        """
        # This is a simplified evaluation focusing on:
        # - Isolated pawns (bad)
        # - Doubled pawns (bad)
        # - Passed pawns (good)
        # - Pawn chains (good)
        
        # Get all pawn positions for both sides
        white_pawns = board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)
        
        # Evaluate for the side to move
        if board.turn == chess.WHITE:
            friendly_pawns = white_pawns
            enemy_pawns = black_pawns
        else:
            friendly_pawns = black_pawns
            enemy_pawns = white_pawns
        
        # Count pawn structure features
        isolated_pawns = 0
        doubled_pawns = 0
        passed_pawns = 0
        pawn_chains = 0
        
        # Create file occupancy maps
        friendly_files = [0] * 8
        enemy_files = [0] * 8
        
        for square in friendly_pawns:
            file_idx = chess.square_file(square)
            friendly_files[file_idx] += 1
        
        for square in enemy_pawns:
            file_idx = chess.square_file(square)
            enemy_files[file_idx] += 1
        
        # Check for isolated and doubled pawns
        for i in range(8):
            if friendly_files[i] > 0:
                # Check for isolated pawns
                if (i == 0 or friendly_files[i-1] == 0) and (i == 7 or friendly_files[i+1] == 0):
                    isolated_pawns += 1
                
                # Check for doubled pawns
                if friendly_files[i] > 1:
                    doubled_pawns += 1
        
        # Calculate score (simplified)
        # More isolated and doubled pawns are bad, more passed pawns and chains are good
        pawn_count = len(friendly_pawns)
        if pawn_count == 0:
            return 0.5  # Neutral if no pawns
            
        # Calculate penalties and bonuses
        isolated_penalty = isolated_pawns / pawn_count * 0.3
        doubled_penalty = doubled_pawns / pawn_count * 0.2
        
        # Start with a base score and apply penalties
        score = 0.5 - isolated_penalty - doubled_penalty
        
        return min(max(score, 0.0), 1.0)  # Ensure score is between 0 and 1

    def _evaluate_mobility(self, board: chess.Board) -> float:
        """
        Evaluate piece mobility in the given position.
        
        Args:
            board: The board position to evaluate
            
        Returns:
            A score between 0 and 1 where higher is better
        """
        # Count legal moves as a basic mobility metric
        legal_move_count = len(list(board.legal_moves))
        
        # Map number of legal moves to a 0-1 score
        # Assuming average middle game has about 30-40 legal moves
        if legal_move_count >= 40:
            return 0.9  # Excellent mobility
        elif legal_move_count >= 30:
            return 0.8  # Very good mobility
        elif legal_move_count >= 20:
            return 0.7  # Good mobility
        elif legal_move_count >= 10:
            return 0.6  # Average mobility
        elif legal_move_count >= 5:
            return 0.4  # Limited mobility
        else:
            return 0.2  # Poor mobility

    def _evaluate_king_safety(self, board: chess.Board, phase: str) -> float:
        """
        Evaluate king safety in the given position.
        
        Args:
            board: The board position to evaluate
            phase: The game phase
            
        Returns:
            A score between 0 and 1 where higher is better
        """
        # In endgame, king safety is less important
        if phase == "endgame":
            return 0.7  # Default good score for endgame
        
        # Find the king square
        king_square = board.king(board.turn)
        if king_square is None:
            return 0.5  # No king found?
        
        # Check if castled
        is_castled = False
        if board.turn == chess.WHITE:
            if king_square in [chess.G1, chess.C1]:
                is_castled = True
        else:
            if king_square in [chess.G8, chess.C8]:
                is_castled = True
        
        # Count defending pieces around king
        defenders = 0
        attackers = 0
        
        king_rank = chess.square_rank(king_square)
        king_file = chess.square_file(king_square)
        
        # Check surrounding squares
        for rank_offset in [-1, 0, 1]:
            for file_offset in [-1, 0, 1]:
                if rank_offset == 0 and file_offset == 0:
                    continue  # Skip the king's square itself
                    
                rank = king_rank + rank_offset
                file = king_file + file_offset
                
                # Check if square is on the board
                if 0 <= rank < 8 and 0 <= file < 8:
                    square = chess.square(file, rank)
                    piece = board.piece_at(square)
                    
                    if piece is not None:
                        if piece.color == board.turn:
                            defenders += 1
                        else:
                            attackers += 1
        
        # Calculate safety score
        if is_castled:
            base_score = 0.8  # Good starting score for castled king
        else:
            base_score = 0.5  # Average score for uncastled king
        
        # Adjust for defenders and attackers
        safety_score = base_score + (defenders * 0.05) - (attackers * 0.1)
        
        return min(max(safety_score, 0.0), 1.0)  # Ensure score is between 0 and 1

    def _evaluate_center_control(self, board: chess.Board) -> float:
        """
        Evaluate center control in the given position.
        
        Args:
            board: The board position to evaluate
            
        Returns:
            A score between 0 and 1 where higher is better
        """
        # Define central squares
        center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        extended_center = center_squares + [chess.C3, chess.D3, chess.E3, chess.F3,
                                           chess.C4, chess.F4, chess.C5, chess.F5,
                                           chess.C6, chess.D6, chess.E6, chess.F6]
        
        # Count pieces and attacks in the center
        center_occupation = 0
        center_attacks = 0
        
        for square in center_squares:
            # Check occupation
            piece = board.piece_at(square)
            if piece is not None:
                if piece.color == board.turn:
                    center_occupation += 1
            
            # Check attacks
            if board.is_attacked_by(board.turn, square):
                center_attacks += 1
        
        # Calculate extended center control
        extended_occupation = 0
        extended_attacks = 0
        
        for square in extended_center:
            # Check occupation
            piece = board.piece_at(square)
            if piece is not None:
                if piece.color == board.turn:
                    extended_occupation += 1
            
            # Check attacks
            if board.is_attacked_by(board.turn, square):
                extended_attacks += 1
        
        # Calculate score
        center_score = (center_occupation * 0.15) + (center_attacks * 0.1) + \
                       (extended_occupation * 0.05) + (extended_attacks * 0.025)
        
        return min(center_score, 1.0)  # Ensure score is between 0 and 1

    def _evaluate_material_change(self, move: chess.Move, board: chess.Board) -> float:
        """
        Evaluate material gain/loss from a move.
        
        Args:
            move: The candidate move
            board: The current board position
            
        Returns:
            A score between 0 and 1 representing material advantage
        """
        if not board.is_capture(move):
            return 0.5  # Neutral if not a capture
        
        # Standard piece values
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0  # Should not be capturable
        }
        
        # Get the capturing piece
        from_piece = board.piece_at(move.from_square)
        if from_piece is None:
            return 0.5
        
        # Get the captured piece
        to_piece = board.piece_at(move.to_square)
        if to_piece is None:
            # This might be en passant
            if board.is_en_passant(move):
                # In en passant, we always capture a pawn with a pawn
                return 0.5  # Even exchange
            return 0.5
        
        # Calculate the value difference
        value_diff = piece_values.get(to_piece.piece_type, 0) - piece_values.get(from_piece.piece_type, 0)
        
        # Convert to a 0-1 score (0.5 is neutral)
        if value_diff > 0:
            return min(0.5 + (value_diff * 0.05), 1.0)
        else:
            return max(0.5 + (value_diff * 0.05), 0.0)

    def _detect_fork(self, move: chess.Move, board: chess.Board) -> float:
        """
        Detect if a move creates a fork (attacks multiple pieces).
        
        Args:
            move: The candidate move
            board: The current board position
            
        Returns:
            A score between 0 and 1, higher if a good fork is detected
        """
        # Create a test board to see the position after the move
        test_board = board.copy()
        test_board.push(move)
        
        # Get the landing square of the move
        to_square = move.to_square
        
        # Count the number of pieces attacked from this square
        attacked_pieces = []
        total_value = 0
        
        for square in chess.SQUARES:
            piece = test_board.piece_at(square)
            if piece is not None and piece.color != board.turn:
                # Check if this square is attacked by the piece that just moved
                if test_board.is_attacked_by(board.turn, square):
                    # Check if attack is coming from our moved piece
                    if any(test_board.attacks(to_square) & chess.BB_SQUARES[square]):
                        attacked_pieces.append(piece)
                        
                        # Add up the value
                        if piece.piece_type == chess.PAWN:
                            total_value += 1
                        elif piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                            total_value += 3
                        elif piece.piece_type == chess.ROOK:
                            total_value += 5
                        elif piece.piece_type == chess.QUEEN:
                            total_value += 9
        
        # Score based on number and value of attacked pieces
        if len(attacked_pieces) >= 2:
            return min(0.5 + (total_value * 0.05), 1.0)
        
        return 0.0

    def _detect_pin(self, move: chess.Move, board: chess.Board) -> float:
        """
        Detect if a move creates a pin.
        
        Args:
            move: The candidate move
            board: The current board position
            
        Returns:
            A score between 0 and 1, higher if a good pin is detected
        """
        # This is a simplified check that looks for alignment between
        # the moved piece, an enemy piece, and the enemy king
        
        # Create a test board to see the position after the move
        test_board = board.copy()
        test_board.push(move)
        
        # Get the landing square of the move
        to_square = move.to_square
        to_piece = test_board.piece_at(to_square)
        
        # If the piece can't give a pin, return 0
        if to_piece is None or to_piece.piece_type not in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
            return 0.0
        
        # Find the enemy king
        enemy_king_square = test_board.king(not board.turn)
        if enemy_king_square is None:
            return 0.0
        
        # Check if there is exactly one piece between our piece and the enemy king
        # (this is a simplified check that doesn't account for all cases)
        between_squares = list(chess.SquareSet(chess.between(to_square, enemy_king_square)))
        
        if len(between_squares) == 1:
            middle_square = between_squares[0]
            middle_piece = test_board.piece_at(middle_square)
            
            if middle_piece is not None and middle_piece.color != board.turn:
                # We found a pin! Score based on the value of the pinned piece
                if middle_piece.piece_type == chess.QUEEN:
                    return 0.9
                elif middle_piece.piece_type == chess.ROOK:
                    return 0.8
                elif middle_piece.piece_type in [chess.BISHOP, chess.KNIGHT]:
                    return 0.7
                else:  # Pawn
                    return 0.5
        
        return 0.0

    def _detect_discovered_attack(self, move: chess.Move, board: chess.Board) -> float:
        """
        Detect if a move creates a discovered attack.
        
        Args:
            move: The candidate move
            board: The current board position
            
        Returns:
            A score between 0 and 1, higher if a good discovered attack is detected
        """
        # This is a very simplified check
        from_square = move.from_square
        
        # Create two test boards - one before and one after the move
        before_board = board.copy()
        after_board = board.copy()
        after_board.push(move)
        
        # Find the enemy king
        enemy_king_square = before_board.king(not board.turn)
        if enemy_king_square is None:
            return 0.0
        
        # Check if any of our pieces can attack the enemy king or queen after the move
        # but not before
        enemy_queen_square = None
        for square in chess.SQUARES:
            piece = before_board.piece_at(square)
            if piece is not None and piece.color != board.turn and piece.piece_type == chess.QUEEN:
                enemy_queen_square = square
                break
        
        # Check for discovered attack on king
        if not before_board.is_attacked_by(board.turn, enemy_king_square) and after_board.is_attacked_by(board.turn, enemy_king_square):
            return 0.9  # Discovered check is very good
        
        # Check for discovered attack on queen
        if enemy_queen_square is not None:
            if not before_board.is_attacked_by(board.turn, enemy_queen_square) and after_board.is_attacked_by(board.turn, enemy_queen_square):
                return 0.8  # Discovered attack on queen is good
        
        return 0.0
        
    def get_search_stats(self) -> Dict[str, Any]:
        """
        Return statistics about the search process.
        Useful for UCI info output.
        """
        # In a real implementation, this would track nodes searched, etc.
        return {
            "nodes": 0,
            "time": 0,
            "nps": 0,
        }
