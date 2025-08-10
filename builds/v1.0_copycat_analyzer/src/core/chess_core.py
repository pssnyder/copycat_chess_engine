#!/usr/bin/env python3
"""
Chess Core Module for Copycat Chess Engine
Provides essential chess functionality and utilities.
"""

import chess
import chess.pgn
import io
from typing import Dict, List, Tuple, Optional, Set, Union, Any
import random

def get_piece_square_tables() -> Dict[str, Dict[str, List[List[int]]]]:
    """
    Get the piece-square tables for evaluation.
    
    Returns:
        Dict: A dictionary of piece-square tables by piece type and game phase
    """
    # Piece-square tables for middlegame and endgame
    tables = {
        "middlegame": {
            "P": [  # Pawns (White)
                [0,  0,  0,  0,  0,  0,  0,  0],
                [50, 50, 50, 50, 50, 50, 50, 50],
                [10, 10, 20, 30, 30, 20, 10, 10],
                [5,  5, 10, 25, 25, 10,  5,  5],
                [0,  0,  0, 20, 20,  0,  0,  0],
                [5, -5,-10,  0,  0,-10, -5,  5],
                [5, 10, 10,-20,-20, 10, 10,  5],
                [0,  0,  0,  0,  0,  0,  0,  0]
            ],
            "N": [  # Knights (White)
                [-50,-40,-30,-30,-30,-30,-40,-50],
                [-40,-20,  0,  0,  0,  0,-20,-40],
                [-30,  0, 10, 15, 15, 10,  0,-30],
                [-30,  5, 15, 20, 20, 15,  5,-30],
                [-30,  0, 15, 20, 20, 15,  0,-30],
                [-30,  5, 10, 15, 15, 10,  5,-30],
                [-40,-20,  0,  5,  5,  0,-20,-40],
                [-50,-40,-30,-30,-30,-30,-40,-50]
            ],
            "B": [  # Bishops (White)
                [-20,-10,-10,-10,-10,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0, 10, 10, 10, 10,  0,-10],
                [-10,  5,  5, 10, 10,  5,  5,-10],
                [-10,  0,  5, 10, 10,  5,  0,-10],
                [-10,  5,  5,  5,  5,  5,  5,-10],
                [-10,  0,  5,  0,  0,  5,  0,-10],
                [-20,-10,-10,-10,-10,-10,-10,-20]
            ],
            "R": [  # Rooks (White)
                [0,  0,  0,  0,  0,  0,  0,  0],
                [5, 10, 10, 10, 10, 10, 10,  5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [0,  0,  0,  5,  5,  0,  0,  0]
            ],
            "Q": [  # Queen (White)
                [-20,-10,-10, -5, -5,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0,  5,  5,  5,  5,  0,-10],
                [-5,  0,  5,  5,  5,  5,  0, -5],
                [0,  0,  5,  5,  5,  5,  0, -5],
                [-10,  5,  5,  5,  5,  5,  0,-10],
                [-10,  0,  5,  0,  0,  0,  0,-10],
                [-20,-10,-10, -5, -5,-10,-10,-20]
            ],
            "K": [  # King (White)
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-20,-30,-30,-40,-40,-30,-30,-20],
                [-10,-20,-20,-20,-20,-20,-20,-10],
                [20, 20,  0,  0,  0,  0, 20, 20],
                [20, 30, 10,  0,  0, 10, 30, 20]
            ]
        },
        "endgame": {
            "P": [  # Pawns (White)
                [0,  0,  0,  0,  0,  0,  0,  0],
                [80, 80, 80, 80, 80, 80, 80, 80],
                [50, 50, 50, 50, 50, 50, 50, 50],
                [30, 30, 30, 30, 30, 30, 30, 30],
                [20, 20, 20, 20, 20, 20, 20, 20],
                [10, 10, 10, 10, 10, 10, 10, 10],
                [10, 10, 10, 10, 10, 10, 10, 10],
                [0,  0,  0,  0,  0,  0,  0,  0]
            ],
            "N": [  # Knights (White)
                [-50,-40,-30,-30,-30,-30,-40,-50],
                [-40,-20,  0,  0,  0,  0,-20,-40],
                [-30,  0, 10, 15, 15, 10,  0,-30],
                [-30,  5, 15, 20, 20, 15,  5,-30],
                [-30,  0, 15, 20, 20, 15,  0,-30],
                [-30,  5, 10, 15, 15, 10,  5,-30],
                [-40,-20,  0,  5,  5,  0,-20,-40],
                [-50,-40,-30,-30,-30,-30,-40,-50]
            ],
            "B": [  # Bishops (White)
                [-20,-10,-10,-10,-10,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0, 10, 10, 10, 10,  0,-10],
                [-10,  5,  5, 10, 10,  5,  5,-10],
                [-10,  0,  5, 10, 10,  5,  0,-10],
                [-10,  5,  5,  5,  5,  5,  5,-10],
                [-10,  0,  5,  0,  0,  5,  0,-10],
                [-20,-10,-10,-10,-10,-10,-10,-20]
            ],
            "R": [  # Rooks (White)
                [0,  0,  0,  0,  0,  0,  0,  0],
                [5, 10, 10, 10, 10, 10, 10,  5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [0,  0,  0,  5,  5,  0,  0,  0]
            ],
            "Q": [  # Queen (White)
                [-20,-10,-10, -5, -5,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0,  5,  5,  5,  5,  0,-10],
                [-5,  0,  5,  5,  5,  5,  0, -5],
                [0,  0,  5,  5,  5,  5,  0, -5],
                [-10,  5,  5,  5,  5,  5,  0,-10],
                [-10,  0,  5,  0,  0,  0,  0,-10],
                [-20,-10,-10, -5, -5,-10,-10,-20]
            ],
            "K": [  # King (White) - Different for endgame
                [-50,-40,-30,-20,-20,-30,-40,-50],
                [-30,-20,-10,  0,  0,-10,-20,-30],
                [-30,-10, 20, 30, 30, 20,-10,-30],
                [-30,-10, 30, 40, 40, 30,-10,-30],
                [-30,-10, 30, 40, 40, 30,-10,-30],
                [-30,-10, 20, 30, 30, 20,-10,-30],
                [-30,-30,  0,  0,  0,  0,-30,-30],
                [-50,-30,-30,-30,-30,-30,-30,-50]
            ]
        }
    }
    
    return tables

def detect_game_phase(board: chess.Board) -> str:
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

def evaluate_position(board: chess.Board) -> float:
    """
    Simple position evaluation function.
    
    Args:
        board: A chess.Board object to evaluate
        
    Returns:
        float: Score from white's perspective (positive is good for white)
    """
    if board.is_checkmate():
        # Return a high value for checkmate, with perspective
        return -10000 if board.turn == chess.WHITE else 10000
    
    if board.is_stalemate() or board.is_insufficient_material():
        # Draw
        return 0
    
    # Piece values
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    
    # Get piece-square tables
    tables = get_piece_square_tables()
    game_phase = detect_game_phase(board)
    phase_tables = tables[game_phase if game_phase != "opening" else "middlegame"]
    
    score = 0
    
    # Material and piece-square tables
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            # Material value
            value = piece_values[piece.piece_type]
            
            # Piece-square table bonus
            symbol = piece.symbol().upper()
            rank, file = chess.square_rank(square), chess.square_file(square)
            
            # Flip rank for black pieces to use the same tables
            if piece.color == chess.BLACK:
                value = -value
                rank = 7 - rank
            
            # Add piece-square table value if we have it
            if symbol in phase_tables:
                value += phase_tables[symbol][7 - rank][file]
            
            score += value
    
    # Mobility (count of legal moves)
    legal_moves = len(list(board.legal_moves))
    board.push(chess.Move.null())  # Switch to opponent's perspective
    opponent_moves = len(list(board.legal_moves))
    board.pop()  # Restore the board
    
    # Add mobility bonus (small weight)
    mobility_factor = 0.1
    score += mobility_factor * (legal_moves - opponent_moves)
    
    # Add bonus for having bishops, knights in more open positions
    if game_phase != "opening":
        bishop_pair_bonus = 30
        if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
            score += bishop_pair_bonus
        if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
            score -= bishop_pair_bonus
    
    return score

def analyze_move_quality(board: chess.Board, move: chess.Move) -> Dict[str, Any]:
    """
    Analyze the quality of a move based on simple heuristics.
    
    Args:
        board: A chess.Board object
        move: The move to analyze
        
    Returns:
        Dict: A dictionary with move quality metrics
    """
    result = {
        "is_capture": board.is_capture(move),
        "is_check": board.gives_check(move),
        "is_promotion": move.promotion is not None,
        "captured_piece": None,
        "piece_moved": None,
        "piece_value": 0,
        "target_value": 0,
        "is_hanging_piece": False,
        "center_control": False,
        "piece_development": False
    }
    
    # Get the piece being moved
    piece = board.piece_at(move.from_square)
    if piece:
        result["piece_moved"] = chess.piece_name(piece.piece_type)
        
        # Determine piece value
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0  # King's value isn't relevant for captures
        }
        result["piece_value"] = piece_values.get(piece.piece_type, 0)
    
    # Check if it's a capture and what is captured
    if result["is_capture"]:
        target = board.piece_at(move.to_square)
        if target:
            result["captured_piece"] = chess.piece_name(target.piece_type)
            result["target_value"] = piece_values.get(target.piece_type, 0)
            
            # Is it a hanging piece capture?
            result["is_hanging_piece"] = not board.is_attacked_by(not piece.color, move.to_square)
    
    # Center control (e4, d4, e5, d5)
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    result["center_control"] = move.to_square in center_squares
    
    # Piece development in opening
    if detect_game_phase(board) == "opening":
        # Knight or Bishop development
        if (piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP] and
                chess.square_rank(move.from_square) in [0, 7] and
                chess.square_rank(move.to_square) not in [0, 7]):
            result["piece_development"] = True
        
        # Pawn development opening center
        if (piece and piece.piece_type == chess.PAWN and
                move.to_square in center_squares and
                chess.square_file(move.from_square) in [4, 3]):  # Files E and D
            result["piece_development"] = True
    
    return result

def parse_pgn_from_string(pgn_string: str) -> chess.pgn.Game:
    """
    Parse a PGN string into a chess.pgn.Game object.
    
    Args:
        pgn_string: The PGN string to parse
        
    Returns:
        chess.pgn.Game: The parsed game
    """
    pgn_io = io.StringIO(pgn_string)
    game = chess.pgn.read_game(pgn_io)
    if game is None:
        raise ValueError("Failed to parse PGN string")
    return game

def get_common_openings() -> Dict[str, Dict[str, Union[str, List[str]]]]:
    """
    Get a dictionary of common chess openings with their ECO codes and moves.
    
    Returns:
        Dict: A dictionary of common chess openings
    """
    openings = {
        "Ruy Lopez": {
            "eco": "C60-C99",
            "moves": ["e4", "e5", "Nf3", "Nc6", "Bb5"]
        },
        "Italian Game": {
            "eco": "C50-C59",
            "moves": ["e4", "e5", "Nf3", "Nc6", "Bc4"]
        },
        "Sicilian Defense": {
            "eco": "B20-B99",
            "moves": ["e4", "c5"]
        },
        "French Defense": {
            "eco": "C00-C19",
            "moves": ["e4", "e6"]
        },
        "Caro-Kann Defense": {
            "eco": "B10-B19",
            "moves": ["e4", "c6"]
        },
        "Queen's Gambit": {
            "eco": "D00-D69",
            "moves": ["d4", "d5", "c4"]
        },
        "King's Indian Defense": {
            "eco": "E60-E99",
            "moves": ["d4", "Nf6", "c4", "g6"]
        },
        "Nimzo-Indian Defense": {
            "eco": "E20-E59",
            "moves": ["d4", "Nf6", "c4", "e6", "Nc3", "Bb4"]
        },
        "London System": {
            "eco": "D00-D05",
            "moves": ["d4", "d5", "Bf4"]
        },
        "English Opening": {
            "eco": "A10-A39",
            "moves": ["c4"]
        }
    }
    
    return openings

def detect_opening_from_moves(move_list: List[str]) -> Optional[str]:
    """
    Detect chess opening from a list of moves in algebraic notation.
    
    Args:
        move_list: List of moves in algebraic notation (e.g., ["e4", "e5", ...])
        
    Returns:
        Optional[str]: The name of the detected opening, or None if unknown
    """
    common_openings = get_common_openings()
    
    # Convert move list to lowercase for consistent comparison
    move_list_lower = [m.lower() for m in move_list]
    
    best_match = None
    best_match_length = 0
    
    for opening_name, opening_info in common_openings.items():
        opening_moves = [m.lower() for m in opening_info["moves"]]
        match_length = 0
        
        # Count how many moves match from the beginning
        for i, move in enumerate(opening_moves):
            if i >= len(move_list_lower) or move_list_lower[i] != move:
                break
            match_length += 1
        
        # If we matched all moves for this opening and it's longer than our best match
        if match_length == len(opening_moves) and match_length > best_match_length:
            best_match = opening_name
            best_match_length = match_length
    
    return best_match

def move_to_algebraic(move: chess.Move, board: chess.Board) -> str:
    """
    Convert a chess.Move to algebraic notation (e.g., "e4", "Nf3").
    
    Args:
        move: The chess.Move to convert
        board: The board position before the move
        
    Returns:
        str: The move in algebraic notation
    """
    return board.san(move)

def algebraic_to_move(move_str: str, board: chess.Board) -> chess.Move:
    """
    Convert algebraic notation to a chess.Move.
    
    Args:
        move_str: The move in algebraic notation (e.g., "e4", "Nf3")
        board: The current board position
        
    Returns:
        chess.Move: The corresponding chess.Move
    """
    try:
        return board.parse_san(move_str)
    except ValueError:
        # Try UCI notation as a fallback
        try:
            return chess.Move.from_uci(move_str)
        except ValueError:
            raise ValueError(f"Invalid move: {move_str}")

def is_tactical_position(board: chess.Board) -> bool:
    """
    Determine if the current position has tactical elements.
    
    Args:
        board: The current board position
        
    Returns:
        bool: True if the position has tactical elements
    """
    # Check if any piece is under attack
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            # Check if it's under attack by the opponent
            if board.is_attacked_by(not piece.color, square):
                # Check if it's defended
                is_defended = board.is_attacked_by(piece.color, square)
                
                # If it's a higher value piece or undefended, it's tactical
                if piece.piece_type >= chess.KNIGHT and not is_defended:
                    return True
    
    # Check for possible forks and pins
    # (This is a simplified approximation)
    for move in board.legal_moves:
        board.push(move)
        attacked_pieces = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None and piece.color != board.turn:
                if board.is_attacked_by(board.turn, square):
                    attacked_pieces += 1
        board.pop()
        
        # If a move attacks multiple pieces, it might be a fork
        if attacked_pieces >= 2:
            return True
    
    return False
