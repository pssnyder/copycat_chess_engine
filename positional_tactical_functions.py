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
