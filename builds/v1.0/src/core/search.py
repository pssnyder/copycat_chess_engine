#!/usr/bin/env python3
"""
Search module for Copycat Chess Engine - Data Analytics Edition
Handles move search and selection based on player's historical style.
"""

import chess
import json
import random
import os
from collections import defaultdict
from typing import List, Dict, Tuple, Any, Optional, Union

class MoveCandidate:
    """Class to represent a candidate move with various scores."""
    def __init__(self, move: chess.Move, board: chess.Board):
        self.move = move
        self.piece = board.piece_at(move.from_square)
        self.piece_type = self.piece.piece_type if self.piece else None
        self.piece_symbol = self.piece.symbol() if self.piece else None
        self.is_capture = board.is_capture(move)
        self.is_check = board.gives_check(move)
        self.is_promotion = move.promotion is not None
        
        # From square and to square as algebraic notation
        self.from_square = chess.square_name(move.from_square)
        self.to_square = chess.square_name(move.to_square)
        
        # Score components
        self.style_score = 0.0
        self.position_score = 0.0
        self.tactical_score = 0.0
        self.frequency_score = 0.0
        self.opening_score = 0.0
        self.overall_score = 0.0
    
    def __str__(self) -> str:
        """String representation of the move candidate."""
        move_str = f"{self.move.uci()} ({self.piece_symbol})"
        details = []
        
        if self.is_capture:
            details.append("capture")
        if self.is_check:
            details.append("check")
        if self.is_promotion and self.move.promotion is not None:
            details.append(f"promotion:{chess.piece_symbol(self.move.promotion)}")
        
        score_str = f"Score: {self.overall_score:.3f} (Style: {self.style_score:.2f}, " \
                    f"Pos: {self.position_score:.2f}, Tac: {self.tactical_score:.2f}, " \
                    f"Freq: {self.frequency_score:.2f}, Op: {self.opening_score:.2f})"
        
        if details:
            return f"{move_str} [{', '.join(details)}] - {score_str}"
        else:
            return f"{move_str} - {score_str}"


class SearchManager:
    """Manages the search for the best move based on analysis data."""
    
    def __init__(self, analysis_file: Optional[str] = None):
        """Initialize the search manager with analysis data."""
        self.analysis_data = {}
        self.move_frequencies = defaultdict(lambda: defaultdict(float))
        self.piece_heatmaps = defaultdict(lambda: defaultdict(float))
        self.opening_moves = defaultdict(list)
        self.phase_preferences = defaultdict(lambda: defaultdict(float))
        
        # Load analysis data if provided
        if analysis_file and os.path.exists(analysis_file):
            self.load_analysis_data(analysis_file)
            print(f"Analysis data loaded from {analysis_file}")
    
    def load_analysis_data(self, file_path: str) -> None:
        """
        Load analysis data from a JSON file.
        
        Args:
            file_path: Path to the JSON analysis file
        """
        try:
            with open(file_path, 'r') as f:
                self.analysis_data = json.load(f)
            
            # Extract move frequencies by phase if available
            if 'move_frequencies' in self.analysis_data:
                for phase, moves in self.analysis_data['move_frequencies'].items():
                    for move_uci, freq in moves.items():
                        self.move_frequencies[phase][move_uci] = freq
            
            # Extract piece heatmaps if available
            if 'piece_heatmaps' in self.analysis_data:
                for piece, squares in self.analysis_data['piece_heatmaps'].items():
                    for square, data in squares.items():
                        self.piece_heatmaps[piece][square] = data.get('frequency', 0)
            
            # Extract opening preferences if available
            if 'opening_stats' in self.analysis_data:
                for opening, stats in self.analysis_data['opening_stats'].items():
                    if 'common_moves' in stats:
                        self.opening_moves[opening] = stats['common_moves']
            
            # Extract phase preferences if available
            if 'phase_preferences' in self.analysis_data:
                for phase, preferences in self.analysis_data['phase_preferences'].items():
                    for pref_type, value in preferences.items():
                        self.phase_preferences[phase][pref_type] = value
        
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading analysis data: {str(e)}")
    
    def calculate_style_score(self, candidate: MoveCandidate, phase: str) -> float:
        """
        Calculate a score for how well this move matches the player's style.
        
        Args:
            candidate: The move candidate
            phase: Current game phase ("opening", "middlegame", "endgame")
            
        Returns:
            float: A score between 0 and 1
        """
        # Default style score
        style_score = 0.5
        
        # Get phase-specific style preferences
        phase_prefs = self.phase_preferences.get(phase, {})
        
        # Check if this move matches player's aggressiveness preference
        aggressiveness = phase_prefs.get('aggressiveness', 0.5)
        if candidate.is_capture or candidate.is_check:
            style_score += 0.2 * aggressiveness  # More points for aggressive moves if player is aggressive
        else:
            style_score += 0.2 * (1 - aggressiveness)  # More points for quiet moves if player is not aggressive
        
        # Check piece preferences
        if 'piece_preferences' in self.analysis_data and candidate.piece_symbol in self.analysis_data['piece_preferences']:
            piece_pref = self.analysis_data['piece_preferences'][candidate.piece_symbol]
            style_score += 0.2 * piece_pref  # More points for preferred pieces
        
        # Check capture preferences
        if 'capture_stats' in self.analysis_data:
            capture_pref = self.analysis_data['capture_stats'].get('capture_frequency', 0.5)
            if candidate.is_capture:
                style_score += 0.1 * capture_pref  # More points for captures if player prefers them
            else:
                style_score += 0.1 * (1 - capture_pref)  # More points for non-captures if player avoids them
        
        # Check check/attack preferences
        if 'check_stats' in self.analysis_data:
            check_pref = self.analysis_data['check_stats'].get('check_frequency', 0.5)
            if candidate.is_check:
                style_score += 0.1 * check_pref  # More points for checks if player prefers them
            else:
                style_score += 0.1 * (1 - check_pref)  # More points for non-checks if player avoids them
        
        # Normalize the score to be between 0 and 1
        style_score = min(max(style_score, 0), 1)
        
        return style_score
    
    def calculate_position_score(self, candidate: MoveCandidate) -> float:
        """
        Calculate a score for this move based on the player's positional preferences.
        
        Args:
            candidate: The move candidate
            
        Returns:
            float: A score between 0 and 1
        """
        # Default position score
        position_score = 0.5
        
        # Check if this square is in the player's heatmap
        if candidate.piece_symbol in self.piece_heatmaps:
            piece_map = self.piece_heatmaps[candidate.piece_symbol]
            if candidate.to_square in piece_map:
                # Get the frequency for this square
                frequency = piece_map[candidate.to_square]
                
                # Normalize by the maximum frequency
                max_freq = max(piece_map.values()) if piece_map else 1
                if max_freq > 0:
                    normalized_freq = frequency / max_freq
                    position_score = 0.3 + 0.7 * normalized_freq  # Scale between 0.3 and 1.0
        
        # Apply some randomness to avoid always choosing the same squares
        position_score *= random.uniform(0.9, 1.1)
        position_score = min(max(position_score, 0), 1)
        
        return position_score
    
    def calculate_tactical_score(self, candidate: MoveCandidate, board: chess.Board) -> float:
        """
        Calculate a tactical score for this move.
        
        Args:
            candidate: The move candidate
            board: The current board position
            
        Returns:
            float: A score between 0 and 1
        """
        # Default tactical score
        tactical_score = 0.5
        
        # Give more points for captures
        if candidate.is_capture:
            # Get the piece being captured
            captured_piece = board.piece_at(candidate.move.to_square)
            if captured_piece:
                # Use piece values for scoring
                # Pawn=1, Knight/Bishop=3, Rook=5, Queen=9, King=Infinity
                piece_values = {
                    chess.PAWN: 1,
                    chess.KNIGHT: 3,
                    chess.BISHOP: 3,
                    chess.ROOK: 5,
                    chess.QUEEN: 9,
                    chess.KING: 100
                }
                
                capturing_value = piece_values.get(candidate.piece_type, 1) if candidate.piece_type is not None else 1
                captured_value = piece_values.get(captured_piece.piece_type, 1)
                
                # Captures of higher value pieces get higher scores
                if captured_value > capturing_value:
                    tactical_score += 0.3  # Good trade
                elif captured_value == capturing_value:
                    tactical_score += 0.15  # Equal trade
                else:
                    tactical_score += 0.05  # Bad trade but still a capture
        
        # Give more points for checks
        if candidate.is_check:
            tactical_score += 0.2
        
        # Give more points for promotions
        if candidate.is_promotion:
            promotion_piece = candidate.move.promotion
            if promotion_piece == chess.QUEEN:
                tactical_score += 0.3
            elif promotion_piece in (chess.ROOK, chess.BISHOP, chess.KNIGHT):
                tactical_score += 0.15
        
        # Normalize the score to be between 0 and 1
        tactical_score = min(max(tactical_score, 0), 1)
        
        return tactical_score
    
    def calculate_frequency_score(self, candidate: MoveCandidate, phase: str) -> float:
        """
        Calculate a score based on how frequently the player makes similar moves.
        
        Args:
            candidate: The move candidate
            phase: Current game phase
            
        Returns:
            float: A score between 0 and 1
        """
        # Default frequency score
        frequency_score = 0.5
        
        # Check if this move is in the player's move frequency database
        if phase in self.move_frequencies:
            phase_moves = self.move_frequencies[phase]
            
            # Try to match the exact move
            if candidate.move.uci() in phase_moves:
                frequency = phase_moves[candidate.move.uci()]
                
                # Normalize by the maximum frequency
                max_freq = max(phase_moves.values()) if phase_moves else 1
                if max_freq > 0:
                    normalized_freq = frequency / max_freq
                    frequency_score = 0.3 + 0.7 * normalized_freq  # Scale between 0.3 and 1.0
        
        # Apply some randomness to avoid always choosing the same moves
        frequency_score *= random.uniform(0.9, 1.1)
        frequency_score = min(max(frequency_score, 0), 1)
        
        return frequency_score
    
    def calculate_opening_score(self, candidate: MoveCandidate, opening: Optional[str]) -> float:
        """
        Calculate a score based on opening preferences.
        
        Args:
            candidate: The move candidate
            opening: The detected opening, if any
            
        Returns:
            float: A score between 0 and 1
        """
        # Default opening score
        opening_score = 0.5
        
        # If no opening detected or not in the opening phase, return default
        if not opening:
            return opening_score
        
        # Check if this opening is in our database
        if opening in self.opening_moves:
            opening_move_list = self.opening_moves[opening]
            
            # Check if this move appears in the common moves for this opening
            for move_data in opening_move_list:
                if 'move' in move_data and move_data['move'] == candidate.move.uci():
                    # Calculate score based on win rate and frequency
                    win_rate = move_data.get('win_rate', 0.5)
                    frequency = move_data.get('frequency', 0)
                    
                    # Higher win rate and frequency give higher score
                    opening_score = 0.3 + 0.4 * win_rate + 0.3 * min(frequency / 10, 1)
                    break
        
        return opening_score
    
    def search_best_move(self, board: chess.Board, phase: str, opening: Optional[str] = None) -> Tuple[Optional[chess.Move], List[MoveCandidate]]:
        """
        Search for the best move based on player's style and preferences.
        
        Args:
            board: The current board position
            phase: Current game phase ("opening", "middlegame", "endgame")
            opening: The detected opening, if any
            
        Returns:
            Tuple[Optional[chess.Move], List[MoveCandidate]]: The best move and the list of candidates
        """
        # Get all legal moves
        legal_moves = list(board.legal_moves)
        
        # If no legal moves, return None
        if not legal_moves:
            return None, []
        
        # Create candidates for each move
        candidates = []
        for move in legal_moves:
            candidate = MoveCandidate(move, board)
            
            # Calculate scores
            candidate.style_score = self.calculate_style_score(candidate, phase)
            candidate.position_score = self.calculate_position_score(candidate)
            candidate.tactical_score = self.calculate_tactical_score(candidate, board)
            candidate.frequency_score = self.calculate_frequency_score(candidate, phase)
            candidate.opening_score = self.calculate_opening_score(candidate, opening) if phase == "opening" else 0.0
            
            # Calculate overall score based on the current phase
            if phase == "opening":
                # In opening, prioritize opening book and frequency
                candidate.overall_score = 0.4 * candidate.opening_score + \
                                        0.2 * candidate.style_score + \
                                        0.2 * candidate.position_score + \
                                        0.1 * candidate.tactical_score + \
                                        0.1 * candidate.frequency_score
            elif phase == "middlegame":
                # In middlegame, prioritize style and tactics
                candidate.overall_score = 0.3 * candidate.style_score + \
                                        0.3 * candidate.tactical_score + \
                                        0.2 * candidate.position_score + \
                                        0.2 * candidate.frequency_score
            else:  # endgame
                # In endgame, prioritize tactics and position
                candidate.overall_score = 0.4 * candidate.tactical_score + \
                                        0.3 * candidate.position_score + \
                                        0.2 * candidate.style_score + \
                                        0.1 * candidate.frequency_score
            
            candidates.append(candidate)
        
        # Sort candidates by overall score
        candidates.sort(key=lambda c: c.overall_score, reverse=True)
        
        # Select the best move
        # With some randomness to avoid predictability
        if len(candidates) > 3:
            # 80% chance to pick the best move, 15% for second, 5% for third
            choice = random.choices(candidates[:3], weights=[0.8, 0.15, 0.05], k=1)[0]
            best_move = choice.move
        else:
            best_move = candidates[0].move
        
        return best_move, candidates
