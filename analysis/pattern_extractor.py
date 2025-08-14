#!/usr/bin/env python3
"""
Pattern Extractor for Copycat v3.0
Converts large analysis files into compact, embedded patterns.
"""

import json
import chess
import chess.pgn
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set
import sys

class PatternExtractor:
    """Extract essential patterns from large analysis datasets."""
    
    def __init__(self):
        self.opening_patterns = defaultdict(lambda: {'count': 0, 'wins': 0, 'draws': 0})
        self.tactical_patterns = defaultdict(int)
        self.positional_features = defaultdict(list)
        self.endgame_patterns = defaultdict(lambda: {'count': 0, 'success': 0})
        
    def analyze_games(self, pgn_files: List[str], max_games: int = 50000):
        """Analyze games to extract core patterns."""
        games_processed = 0
        
        for pgn_file in pgn_files:
            if games_processed >= max_games:
                break
                
            try:
                with open(pgn_file, 'r', encoding='utf-8') as f:
                    while games_processed < max_games:
                        game = chess.pgn.read_game(f)
                        if not game:
                            break
                            
                        self._extract_game_patterns(game)
                        games_processed += 1
                        
                        if games_processed % 1000 == 0:
                            print(f"Processed {games_processed} games...")
                            
            except Exception as e:
                print(f"Error processing {pgn_file}: {e}")
                continue
                
        print(f"Total games processed: {games_processed}")
        
    def _extract_game_patterns(self, game):
        """Extract patterns from a single game."""
        board = game.board()
        result = game.headers.get('Result', '*')
        
        # Convert result to numerical
        if result == '1-0':
            white_result, black_result = 1.0, 0.0
        elif result == '0-1':
            white_result, black_result = 0.0, 1.0
        elif result == '1/2-1/2':
            white_result, black_result = 0.5, 0.5
        else:
            return  # Skip incomplete games
            
        move_number = 0
        for move in game.mainline_moves():
            move_number += 1
            
            # Extract opening patterns (first 15 moves)
            if move_number <= 15:
                self._record_opening_move(move, board, white_result if board.turn else black_result)
                
            # Extract tactical patterns
            self._analyze_tactical_features(move, board)
            
            # Extract positional patterns
            if move_number % 5 == 0:  # Sample every 5th move
                self._analyze_positional_features(board)
                
            board.push(move)
            
        # Extract endgame patterns (last 20 moves)
        if move_number > 20:
            self._analyze_endgame_patterns(board, result)
            
    def _record_opening_move(self, move: chess.Move, board: chess.Board, result: float):
        """Record opening move with success rate."""
        move_str = board.san(move)
        key = f"{len(board.move_stack)}_{move_str}"
        
        pattern = self.opening_patterns[key]
        pattern['count'] += 1
        pattern['wins'] += result
        
    def _analyze_tactical_features(self, move: chess.Move, board: chess.Board):
        """Analyze tactical features of the move."""
        # Check for captures
        if board.is_capture(move):
            self.tactical_patterns['captures'] += 1
            
        # Check for checks
        board_copy = board.copy()
        board_copy.push(move)
        if board_copy.is_check():
            self.tactical_patterns['checks'] += 1
            
        # Check for piece development
        piece = board.piece_at(move.from_square)
        if piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
            if move.from_square in [chess.B1, chess.G1, chess.B8, chess.G8]:  # Home squares
                self.tactical_patterns['development'] += 1
                
    def _analyze_positional_features(self, board: chess.Board):
        """Analyze positional features of the position."""
        features = []
        
        # Central control
        center_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
        white_center = sum(1 for sq in center_squares if board.piece_at(sq) and board.piece_at(sq).color)
        black_center = sum(1 for sq in center_squares if board.piece_at(sq) and not board.piece_at(sq).color)
        features.append(('center_control', white_center - black_center))
        
        # King safety (castling)
        if board.has_kingside_castling_rights(chess.WHITE):
            features.append(('white_kingside_castling', 1))
        if board.has_queenside_castling_rights(chess.WHITE):
            features.append(('white_queenside_castling', 1))
            
        self.positional_features['samples'].extend(features)
        
    def _analyze_endgame_patterns(self, board: chess.Board, result: str):
        """Analyze endgame patterns."""
        piece_count = len(board.piece_map())
        
        if piece_count <= 10:  # Endgame threshold
            material = self._get_material_signature(board)
            pattern = self.endgame_patterns[material]
            pattern['count'] += 1
            
            if result == '1-0':
                pattern['success'] += 1 if board.turn else 0
            elif result == '0-1':
                pattern['success'] += 0 if board.turn else 1
            elif result == '1/2-1/2':
                pattern['success'] += 0.5
                
    def _get_material_signature(self, board: chess.Board) -> str:
        """Get a material signature for the position."""
        pieces = defaultdict(int)
        for square, piece in board.piece_map().items():
            pieces[f"{piece.color}_{piece.piece_type}"] += 1
            
        # Sort for consistent signature
        signature_parts = []
        for piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]:
            white_count = pieces.get(f"True_{piece_type}", 0)
            black_count = pieces.get(f"False_{piece_type}", 0)
            if white_count or black_count:
                signature_parts.append(f"{white_count}v{black_count}_{piece_type}")
                
        return "_".join(signature_parts[:3])  # Limit signature length
        
    def generate_compact_patterns(self) -> Dict:
        """Generate the final compact pattern database."""
        patterns = {
            'metadata': {
                'version': '3.0.0',
                'games_analyzed': sum(p['count'] for p in self.opening_patterns.values()),
                'compression_ratio': '99%'  # vs 64MB original
            },
            'opening': self._compress_opening_patterns(),
            'tactical': self._compress_tactical_patterns(),
            'positional': self._compress_positional_patterns(),
            'endgame': self._compress_endgame_patterns()
        }
        
        return patterns
        
    def _compress_opening_patterns(self) -> Dict:
        """Compress opening patterns to top performers."""
        # Only keep patterns with sufficient sample size and good performance
        compressed = {}
        
        for key, data in self.opening_patterns.items():
            if data['count'] >= 10:  # Minimum sample size
                success_rate = data['wins'] / data['count']
                if success_rate >= 0.45:  # Better than random
                    compressed[key] = {
                        'frequency': min(data['count'] / 1000, 1.0),  # Normalize
                        'success': round(success_rate, 3),
                        'weight': round(success_rate * (data['count'] / 100), 3)
                    }
                    
        # Keep only top 500 patterns
        sorted_patterns = sorted(compressed.items(), key=lambda x: x[1]['weight'], reverse=True)
        return dict(sorted_patterns[:500])
        
    def _compress_tactical_patterns(self) -> Dict:
        """Compress tactical patterns."""
        total_moves = sum(self.tactical_patterns.values())
        if total_moves == 0:
            return {}
            
        return {
            'capture_frequency': round(self.tactical_patterns['captures'] / total_moves, 3),
            'check_frequency': round(self.tactical_patterns['checks'] / total_moves, 3),
            'development_frequency': round(self.tactical_patterns['development'] / total_moves, 3),
            'tactical_weight': 1.5  # Bonus for tactical moves
        }
        
    def _compress_positional_patterns(self) -> Dict:
        """Compress positional patterns."""
        if not self.positional_features.get('samples'):
            return {}
            
        # Calculate average positional values
        center_values = [v for f, v in self.positional_features['samples'] if f == 'center_control']
        avg_center = sum(center_values) / len(center_values) if center_values else 0
        
        return {
            'center_importance': round(abs(avg_center) * 0.1, 3),
            'castling_bonus': 0.3,
            'development_bonus': 0.2
        }
        
    def _compress_endgame_patterns(self) -> Dict:
        """Compress endgame patterns."""
        compressed = {}
        
        for material, data in self.endgame_patterns.items():
            if data['count'] >= 5:  # Minimum sample
                success_rate = data['success'] / data['count']
                compressed[material] = round(success_rate, 3)
                
        # Keep only top 50 endgame patterns
        sorted_endgames = sorted(compressed.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_endgames[:50])


def main():
    """Extract patterns from training data."""
    import glob
    
    print("Copycat v3.0 Pattern Extractor")
    print("=" * 40)
    
    # Find all PGN files
    pgn_files = glob.glob("training_positions/*.pgn")
    print(f"Found {len(pgn_files)} PGN files")
    
    if not pgn_files:
        print("No PGN files found in training_positions/")
        return
        
    # Extract patterns
    extractor = PatternExtractor()
    extractor.analyze_games(pgn_files, max_games=30000)  # Reasonable sample
    
    # Generate compact patterns
    patterns = extractor.generate_compact_patterns()
    
    # Save to compact file
    output_file = "src/core/copycat_patterns.py"
    with open(output_file, 'w') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('"""\n')
        f.write('Copycat v3.0 Embedded Patterns\n')
        f.write('Compressed from 64MB analysis to <100KB of essential patterns.\n')
        f.write('"""\n\n')
        f.write(f'COPYCAT_PATTERNS = {json.dumps(patterns, indent=2)}\n')
        
    # Save JSON version for inspection
    with open("results/copycat_patterns_v3.json", 'w') as f:
        json.dump(patterns, f, indent=2)
        
    print(f"\nPattern extraction complete!")
    print(f"Compact patterns saved to: {output_file}")
    print(f"JSON version saved to: results/copycat_patterns_v3.json")
    
    # Report compression stats
    import os
    if os.path.exists(output_file):
        size_kb = os.path.getsize(output_file) / 1024
        print(f"Pattern file size: {size_kb:.1f} KB (vs 64MB original)")
        print(f"Compression ratio: {64000/size_kb:.0f}:1")


if __name__ == "__main__":
    main()
