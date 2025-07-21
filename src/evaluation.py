"""
Advanced chess position evaluation module for AI.
Provides sophisticated evaluation including material, positional, tactical, and endgame evaluation.
"""

from typing import Dict, List, Tuple, Optional
from const import *
from piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King

class Evaluation:
    """
    Advanced chess position evaluation for strong AI play.
    Combines multiple evaluation factors with proper weighting.
    """
    
    # Piece values in centipawns
    PIECE_VALUES = {
        'pawn': 100,
        'knight': 320,
        'bishop': 330,
        'rook': 500,
        'queen': 900,
        'king': 20000
    }
    
    # Piece-Square Tables
    # Tables are oriented from WHITE's perspective (row 0 = rank 8, row 7 = rank 1)
    PAWN_TABLE = [
        [  0,   0,   0,   0,   0,   0,   0,   0],  
        [ 78,  83,  86,  73, 102,  82,  85,  90],
        [  7,  29,  21,  44,  40,  31,  44,   7],
        [-17,  16,  -2,  15,  14,   0,  15, -13],
        [-26,   3,  10,  9,   6,   1,   0,  -23],
        [-22,   9,   5, -11, -10,  -2,   3, -19],
        [  5,  10,  10, -20, -20,  10,  10,   5],
        [  0,   0,   0,   0,   0,   0,   0,   0]
    ]
    
    KNIGHT_TABLE = [
        [-66, -53, -75, -75, -10, -55, -58, -70],
        [ -3,  -6, 100, -36,   4,  62,  -4, -14],
        [ 10,  67,   1,  74,  73,  27,  62,  -2],
        [ 24,  24,  45,  37,  33,  41,  25,  17],
        [ -1,   5,  31,  21,  22,  35,   2,   0],
        [-18,  10,  13,  22,  18,  15,  11, -14],
        [-23, -15,   2,   0,   2,   0, -23, -20],
        [-74, -23, -26, -24, -19, -35, -22, -69]
    ]
    
    BISHOP_TABLE = [
        [-59, -78, -82, -76, -23,-107, -37, -50],
        [-11,  20,  35, -42, -39,  31,   2, -22],
        [ -9,  39, -32,  41,  52, -10,  28, -14],
        [ 25,  17,  20,  34,  26,  25,  15,  10],
        [ 13,  10,  17,  23,  17,  16,   0,   7],
        [ 14,  25,  24,  15,   8,  25,  20,  15],
        [ 19,  20,  11,   6,   7,   6,  20,  16],
        [ -7,   2, -15, -12, -14, -15, -10, -10]
    ]
    
    ROOK_TABLE = [
        [ 35,  29,  33,   4,  37,  33,  56,  50],
        [ 55,  29,  56,  67,  55,  62,  34,  60],
        [ 19,  35,  28,  33,  45,  27,  25,  15],
        [  0,   5,  16,  13,  18,  -4,  -9,  -6],
        [-28, -35, -16, -21, -13, -29, -46, -30],
        [-42, -28, -42, -25, -25, -35, -26, -46],
        [-53, -38, -31, -26, -29, -43, -44, -53],
        [-30, -24, -18,   5,  -2, -18, -31, -32]
    ]
    
    QUEEN_TABLE = [
        [-20, -15, -10,  -5,  -5, -10, -15, -20], 
        [-15, -10,  -5,   0,   0,  -5, -10, -15],  
        [-10,  -5,   5,   8,   8,   5,  -5, -10],  
        [ -5,   0,   8,  10,  10,   8,   0,  -5],  
        [ -5,   0,   8,  10,  10,   8,   0,  -5],    
        [-10,  -5,   5,   8,   8,   5,  -5, -10],  
        [-15, -10,  -5,   0,   0,  -5, -10, -15],  
        [-20, -15, -10,  -5,  -5, -10, -15, -20]   
    ]
    
    KING_MIDDLEGAME_TABLE = [
        [-80, -70, -70, -70, -70, -70, -70, -80],
        [-70, -60, -60, -60, -60, -60, -60, -70],
        [-60, -50, -50, -50, -50, -50, -50, -60],
        [-50, -40, -40, -40, -40, -40, -40, -50],
        [-40, -30, -30, -30, -30, -30, -30, -40],
        [-30, -20, -20, -20, -20, -20, -20, -30],
        [ 10,  15,   5,  -5,  -5,   5,  15,  10],
        [ 20,  30,  10,   0,   0,  10,  30,  20]
    ]
    
    KING_ENDGAME_TABLE = [
        [-74, -35, -18, -18, -11,  15,   4, -17],
        [-12,  17,  14,  17,  17,  38,  23,  11],
        [ 10,  17,  23,  15,  20,  45,  44,  13],
        [ -8,  22,  24,  27,  26,  33,  26,   3],
        [-18,  -4,  21,  24,  27,  23,   9, -11],
        [-19,  -3,  11,  21,  23,  16,   7,  -9],
        [-27, -11,   4,  13,  14,   4,  -5, -17],
        [-53, -34, -21, -11, -28, -14, -24, -43]
    ]
    
    @staticmethod
    def evaluate(board) -> float:
        """
        IMPROVED evaluation with essential chess knowledge.
        Returns value in centipawns from white's perspective.
        """
        score = 0.0
        
        # Core evaluations
        score += Evaluation.evaluate_material(board)
        
        # Determine game phase for tactical evaluation
        game_phase = Evaluation._get_game_phase(board)
        score += Evaluation.evaluate_position(board, game_phase) * 0.5
        
        # Add back ESSENTIAL evaluations (but lightweight versions):
        
        # King safety (very important for tactical soundness)
        if game_phase in ['opening', 'middlegame']:
            score += Evaluation.evaluate_king_safety(board, game_phase) * 0.3  # Reduced weight
        
        # Basic pawn structure (important for positional understanding)
        score += Evaluation.evaluate_pawn_structure(board) * 0.3  # Reduced weight
        
        # Skip the most expensive ones:
        # - evaluate_mobility (VERY EXPENSIVE - generates all moves)
        # - evaluate_piece_coordination (expensive piece analysis) 
        # - evaluate_tactical_themes (very expensive pattern matching)
        
        return score
    
    @staticmethod
    def evaluate_debug(board) -> Dict[str, float]:
        """
        Debug version that returns all evaluation components separately.
        """
        game_phase = Evaluation._get_game_phase(board)
        
        components = {
            'material': Evaluation.evaluate_material(board),
            'position': Evaluation.evaluate_position(board, game_phase) * 0.1,
            'mobility': Evaluation.evaluate_mobility(board) * 0.1,
            'king_safety': Evaluation.evaluate_king_safety(board, game_phase),
            'pawn_structure': Evaluation.evaluate_pawn_structure(board),
            'piece_coordination': Evaluation.evaluate_piece_coordination(board),
            'tactical': Evaluation.evaluate_tactical_themes(board) * 3.0,
        }
        
        if game_phase == 'endgame':
            components['endgame'] = Evaluation.evaluate_endgame_factors(board)
        else:
            components['endgame'] = 0.0
            
        if game_phase == 'opening':
            components['opening'] = Evaluation.evaluate_opening_principles(board)
        else:
            components['opening'] = 0.0
            
        components['total'] = sum(components.values())
        return components
    
    @staticmethod
    def evaluate_material(board) -> float:
        """Enhanced material evaluation with imbalance bonuses."""
        score = 0.0
        piece_counts = {'white': {}, 'black': {}}
        
        # Count pieces and calculate basic material
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if square.has_piece and square.piece:
                    piece = square.piece
                    if piece.name != 'king':
                        color = piece.color
                        piece_type = piece.name
                        
                        if piece_type not in piece_counts[color]:
                            piece_counts[color][piece_type] = 0
                        piece_counts[color][piece_type] += 1
                        
                        value = Evaluation.PIECE_VALUES[piece_type]
                        if color == 'white':
                            score += value
                        else:
                            score -= value
        
        # Bishop pair bonus
        if piece_counts['white'].get('bishop', 0) >= 2:
            score += 30
        if piece_counts['black'].get('bishop', 0) >= 2:
            score -= 30
        
        # Knight vs Bishop in closed positions (simplified)
        total_pawns = piece_counts['white'].get('pawn', 0) + piece_counts['black'].get('pawn', 0)
        if total_pawns >= 12:  # Closed position
            knight_bonus = 10
            score += (piece_counts['white'].get('knight', 0) - piece_counts['black'].get('knight', 0)) * knight_bonus
        
        return score
    
    @staticmethod
    def evaluate_position(board, game_phase: str) -> float:
        """Enhanced positional evaluation using piece-square tables."""
        score = 0.0
        
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if square.has_piece and square.piece:
                    piece = square.piece
                    value = Evaluation._get_piece_square_value(piece, row, col, game_phase)
                    
                    if piece.color == 'white':
                        score += value
                    else:
                        score -= value
        
        return score
    
    @staticmethod
    def _get_piece_square_value(piece: Piece, row: int, col: int, game_phase: str) -> float:
        """Get positional value with game phase consideration."""
        # For black pieces, flip the row
        eval_row = row if piece.color == 'white' else 7 - row
        
        table_map = {
            'pawn': Evaluation.PAWN_TABLE,
            'knight': Evaluation.KNIGHT_TABLE,
            'bishop': Evaluation.BISHOP_TABLE,
            'rook': Evaluation.ROOK_TABLE,
            'queen': Evaluation.QUEEN_TABLE,
        }
        
        if piece.name in table_map:
            return table_map[piece.name][eval_row][col]
        elif piece.name == 'king':
            if game_phase == 'endgame':
                return Evaluation.KING_ENDGAME_TABLE[eval_row][col]
            else:
                return Evaluation.KING_MIDDLEGAME_TABLE[eval_row][col]
        
        return 0.0
    
    @staticmethod
    def evaluate_mobility(board) -> float:
        """Evaluate piece mobility and space control."""
        white_mobility = 0
        black_mobility = 0
        
        # Count legal moves for each side
        for color, mobility_counter in [('white', lambda: white_mobility), ('black', lambda: black_mobility)]:
            moves = board.get_all_moves(color)
            move_count = len(moves)
            
            if color == 'white':
                white_mobility = move_count
            else:
                black_mobility = move_count
        
        return (white_mobility - black_mobility) * 4  # 4 centipawns per move
    
    @staticmethod
    def evaluate_king_safety(board, game_phase: str) -> float:
        """Enhanced king safety evaluation with severe penalties for exposed kings."""
        score = 0.0
        
        # King safety multiplier based on game phase
        safety_multiplier = {
            'opening': 2.0,
            'middlegame': 3.0,  # Very important in middlegame
            'endgame': 0.5      # Less important in endgame
        }.get(game_phase, 2.0)
        
        # Find kings and evaluate safety
        for color in ['white', 'black']:
            king_pos = Evaluation._find_king(board, color)
            if king_pos:
                safety_score = Evaluation._king_safety_score(board, king_pos, color, game_phase)
                safety_score *= safety_multiplier
                
                if color == 'white':
                    score += safety_score
                else:
                    score -= safety_score
        
        return score
    
    @staticmethod
    def _find_king(board, color: str) -> Optional[Tuple[int, int]]:
        """Find king position for given color."""
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if (square.has_piece and isinstance(square.piece, King) and 
                    square.piece.color == color):
                    return (row, col)
        return None
    
    @staticmethod
    def _king_safety_score(board, king_pos: Tuple[int, int], color: str, game_phase: str = 'middlegame') -> float:
        """Calculate detailed king safety score with game phase awareness."""
        row, col = king_pos
        score = 0.0
        
        # Base king position penalties/bonuses
        if game_phase != 'endgame':
            # Severe penalty for king in center during middlegame
            if 2 <= row <= 5 and 2 <= col <= 5:
                score -= 100  # Very dangerous in middlegame
            
            # Penalty for king on advanced ranks
            if color == 'white' and row < 6:
                score -= (6 - row) * 30  # Penalty increases as king advances
            elif color == 'black' and row > 1:
                score -= (row - 1) * 30
        
        # Pawn shield evaluation
        pawn_direction = -1 if color == 'white' else 1
        shield_rows = [row + pawn_direction, row + 2 * pawn_direction]
        
        pawn_shield_count = 0
        for shield_row in shield_rows:
            if 0 <= shield_row < ROWS:
                for shield_col in range(max(0, col-1), min(COLS, col+2)):
                    square = board.squares[shield_row][shield_col]
                    if (square.has_piece and isinstance(square.piece, Pawn) and 
                        square.piece.color == color):
                        score += 25 if shield_row == shield_rows[0] else 15
                        pawn_shield_count += 1
        
        # Severe penalty for no pawn shield in middlegame
        if game_phase != 'endgame' and pawn_shield_count == 0:
            score -= 80
        
        # Penalty for king on open files
        files_to_check = [col-1, col, col+1]
        open_files = 0
        for file_col in files_to_check:
            if 0 <= file_col < COLS:
                has_own_pawn = False
                for check_row in range(ROWS):
                    square = board.squares[check_row][file_col]
                    if (square.has_piece and isinstance(square.piece, Pawn) and 
                        square.piece.color == color):
                        has_own_pawn = True
                        break
                
                if not has_own_pawn:
                    open_files += 1
        
        # Penalty scales with number of open files
        if game_phase != 'endgame':
            score -= open_files * 25
        
        # Bonus for castling safety (king on g1/c1 for white, g8/c8 for black)
        if game_phase != 'endgame':
            safe_squares = {
                'white': [(7, 6), (7, 2)],  # g1, c1
                'black': [(0, 6), (0, 2)]   # g8, c8
            }
            if (row, col) in safe_squares.get(color, []):
                score += 40
        
        return score
        
        return score
    
    @staticmethod
    def evaluate_pawn_structure(board) -> float:
        """Enhanced pawn structure evaluation."""
        score = 0.0
        
        for color in ['white', 'black']:
            pawn_positions = []
            for row in range(ROWS):
                for col in range(COLS):
                    square = board.squares[row][col]
                    if (square.has_piece and isinstance(square.piece, Pawn) and 
                        square.piece.color == color):
                        pawn_positions.append((row, col))
            
            structure_score = Evaluation._analyze_pawn_structure(pawn_positions, color, board)
            if color == 'white':
                score += structure_score
            else:
                score -= structure_score
        
        return score
    
    @staticmethod
    def _analyze_pawn_structure(pawn_positions: List[Tuple[int, int]], color: str, board) -> float:
        """Detailed pawn structure analysis."""
        score = 0.0
        
        # Create file map
        files = {}
        for row, col in pawn_positions:
            if col not in files:
                files[col] = []
            files[col].append(row)
        
        for row, col in pawn_positions:
            # Doubled pawns penalty
            if len(files[col]) > 1:
                score -= 25
            
            # Isolated pawn penalty
            adjacent_files = [col-1, col+1]
            has_adjacent_pawns = any(f in files for f in adjacent_files if 0 <= f < COLS)
            if not has_adjacent_pawns:
                score -= 20
            
            # Backward pawn penalty
            if Evaluation._is_backward_pawn(row, col, color, files):
                score -= 15
            
            # Passed pawn bonus
            if Evaluation._is_passed_pawn(row, col, color, board):
                distance_bonus = (7 - abs(row - (7 if color == 'white' else 0))) * 10
                score += 20 + distance_bonus
            
            # Connected pawns bonus
            if Evaluation._has_pawn_support(row, col, pawn_positions):
                score += 10
        
        return score
    
    @staticmethod
    def _is_backward_pawn(row: int, col: int, color: str, files: Dict[int, List[int]]) -> bool:
        """Check if pawn is backward."""
        adjacent_files = [col-1, col+1]
        for adj_file in adjacent_files:
            if adj_file in files:
                for adj_row in files[adj_file]:
                    if color == 'white' and adj_row < row:
                        return False
                    elif color == 'black' and adj_row > row:
                        return False
        return True
    
    @staticmethod
    def _is_passed_pawn(row: int, col: int, color: str, board) -> bool:
        """Check if pawn is passed."""
        direction = -1 if color == 'white' else 1
        opponent_color = 'black' if color == 'white' else 'white'
        
        # Check files in front of pawn
        check_files = [col-1, col, col+1]
        for check_col in check_files:
            if 0 <= check_col < COLS:
                check_row = row + direction
                while 0 <= check_row < ROWS:
                    square = board.squares[check_row][check_col]
                    if (square.has_piece and isinstance(square.piece, Pawn) and 
                        square.piece.color == opponent_color):
                        return False
                    check_row += direction
        
        return True
    
    @staticmethod
    def _has_pawn_support(row: int, col: int, pawn_positions: List[Tuple[int, int]]) -> bool:
        """Check if pawn has diagonal support."""
        support_positions = [(row+1, col-1), (row+1, col+1), (row-1, col-1), (row-1, col+1)]
        return any(pos in pawn_positions for pos in support_positions)
    
    @staticmethod
    def evaluate_piece_coordination(board) -> float:
        """Evaluate piece coordination and harmony."""
        score = 0.0
        
        # This is a simplified coordination evaluation
        # In a full engine, you'd analyze piece cooperation, control of key squares, etc.
        
        return score
    
    @staticmethod
    def evaluate_tactical_themes(board) -> float:
        """Evaluate tactical themes and piece safety."""
        score = 0.0
        
        # Check for hanging pieces (pieces that can be captured)
        for color in ['white', 'black']:
            hanging_penalty = Evaluation._evaluate_hanging_pieces(board, color)
            if color == 'white':
                score -= hanging_penalty
            else:
                score += hanging_penalty
        
        # Check for pieces under attack
        for color in ['white', 'black']:
            attack_penalty = Evaluation._evaluate_attacked_pieces(board, color)
            if color == 'white':
                score -= attack_penalty
            else:
                score += attack_penalty
        
        return score
    
    @staticmethod
    def _evaluate_hanging_pieces(board, color: str) -> float:
        """Check for undefended pieces that can be captured."""
        penalty = 0.0
        opponent_color = 'black' if color == 'white' else 'white'
        
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if square.has_piece and square.piece and square.piece.color == color:
                    piece = square.piece
                    
                    # Skip pawns and kings for this analysis
                    if piece.name in ['pawn', 'king']:
                        continue
                    
                    # Check if piece can be captured by opponent
                    can_be_captured = Evaluation._can_be_captured(board, row, col, opponent_color)
                    is_defended = Evaluation._is_defended(board, row, col, color)
                    
                    if can_be_captured and not is_defended:
                        piece_value = Evaluation.PIECE_VALUES.get(piece.name, 0)
                        penalty += piece_value * 0.8  # 80% penalty for hanging pieces
        
        return penalty
    
    @staticmethod
    def _evaluate_attacked_pieces(board, color: str) -> float:
        """Evaluate pieces under attack."""
        penalty = 0.0
        opponent_color = 'black' if color == 'white' else 'white'
        
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if square.has_piece and square.piece and square.piece.color == color:
                    piece = square.piece
                    
                    # Check if important pieces are under attack
                    if piece.name in ['queen', 'rook']:
                        can_be_captured = Evaluation._can_be_captured(board, row, col, opponent_color)
                        if can_be_captured:
                            penalty += 20  # Penalty for having valuable pieces under attack
        
        return penalty
    
    @staticmethod
    def _can_be_captured(board, row: int, col: int, by_color: str) -> bool:
        """Check if a piece can be captured by the given color."""
        # Generate all moves for the attacking color and see if any target this square
        attacking_moves = board.get_all_moves(by_color)
        target_square = (row, col)
        
        for piece, move in attacking_moves:
            if (move.final.row, move.final.col) == target_square:
                return True
        
        return False
    
    @staticmethod
    def _is_defended(board, row: int, col: int, by_color: str) -> bool:
        """Check if a piece is defended by friendly pieces."""
        # Generate all moves for the defending color and see if any can recapture
        defending_moves = board.get_all_moves(by_color)
        target_square = (row, col)
        
        for piece, move in defending_moves:
            if (move.final.row, move.final.col) == target_square:
                return True
        
        return False
    
    @staticmethod
    def evaluate_endgame_factors(board) -> float:
        """Endgame-specific evaluation factors."""
        score = 0.0
        
        # King activity in endgame
        for color in ['white', 'black']:
            king_pos = Evaluation._find_king(board, color)
            if king_pos:
                king_row, king_col = king_pos
                # Centralization bonus
                center_distance = abs(king_row - 3.5) + abs(king_col - 3.5)
                activity_score = (7 - center_distance) * 5
                
                if color == 'white':
                    score += activity_score
                else:
                    score -= activity_score
        
        return score
    
    @staticmethod
    def _get_game_phase(board) -> str:
        """Determine game phase based on material."""
        total_pieces = 0
        for row in range(ROWS):
            for col in range(COLS):
                if board.squares[row][col].has_piece:
                    piece = board.squares[row][col].piece
                    if piece and piece.name != 'king' and piece.name != 'pawn':
                        total_pieces += 1
        
        if total_pieces <= 6:
            return 'endgame'
        elif total_pieces <= 12:
            return 'middlegame'
        else:
            return 'opening'
    
    @staticmethod
    def evaluate_opening_principles(board) -> float:
        """
        Evaluate adherence to opening principles.
        Heavily penalizes early queen development and other opening mistakes.
        """
        score = 0.0
        move_count = board.fullmove_number
        
        # Only apply opening penalties in the first 10 moves
        if move_count > 10:
            return 0.0
        
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece and square.piece:
                    piece = square.piece
                    
                    # Penalize early queen development
                    if piece.name == 'queen':
                        original_row = 0 if piece.color == 'black' else 7
                        original_col = 3  # Queen starts on d-file
                        
                        # Heavy penalty if queen has moved from starting square early in game
                        if row != original_row or col != original_col:
                            # Penalty increases with how early the queen moved
                            early_penalty = max(0, 12 - move_count) * 15  # Up to -180 centipawns
                            
                            # Extra penalty for very exposed squares
                            if piece.color == 'white':
                                if row <= 3:  # Queen in enemy territory early
                                    early_penalty += 30
                                if row <= 1:  # Queen very advanced
                                    early_penalty += 50
                            else:
                                if row >= 4:  # Queen in enemy territory early
                                    early_penalty += 30
                                if row >= 6:  # Queen very advanced
                                    early_penalty += 50
                            
                            # Apply penalty
                            if piece.color == 'white':
                                score -= early_penalty
                            else:
                                score += early_penalty
                    
                    # Bonus for developing knights and bishops early
                    elif piece.name in ['knight', 'bishop'] and move_count <= 5:
                        original_row = 0 if piece.color == 'black' else 7
                        
                        # Bonus if piece has been developed from back rank
                        if row != original_row:
                            development_bonus = 10
                            if piece.color == 'white':
                                score += development_bonus
                            else:
                                score -= development_bonus
                    
                    # Strong penalty for moving same piece multiple times in opening
                    # This will heavily penalize moves like Nf3-g5
                    elif piece.name in ['knight', 'bishop'] and move_count <= 8:
                        # Check if this piece type has "over-developed" by counting pieces off starting squares
                        if piece.name == 'knight':
                            # For knights, if we see a knight in an "unusual" square early, it might be a second move
                            # Knights should ideally go to c3, d2, e2, f3, c6, d7, e7, f6
                            good_knight_squares = {
                                'white': [(5, 2), (5, 3), (5, 4), (5, 5), (6, 2), (6, 5)],  # c3, d3, e3, f3, c2, f2
                                'black': [(2, 2), (2, 3), (2, 4), (2, 5), (1, 2), (1, 5)]   # c6, d6, e6, f6, c7, f7
                            }
                            
                            # Heavy penalty for knights on poor squares in opening
                            if (row, col) not in good_knight_squares.get(piece.color, []):
                                # Squares like g5, h5, g4, h4, a5, b5 for white are very poor early
                                if piece.color == 'white' and row <= 4 and col in [6, 7]:  # g5, h5, g4, h4, etc
                                    poor_knight_penalty = 100  # Very heavy penalty
                                elif piece.color == 'black' and row >= 3 and col in [6, 7]:  # g5, h5, g4, h4, etc  
                                    poor_knight_penalty = 100
                                else:
                                    poor_knight_penalty = 50  # Medium penalty for other poor squares
                                    
                                if piece.color == 'white':
                                    score -= poor_knight_penalty
                                else:
                                    score += poor_knight_penalty
                    
                    # Penalty for early h/a pawn moves (weakening moves)
                    elif piece.name == 'pawn' and move_count <= 6:
                        if col in [0, 7]:  # a-file or h-file pawns
                            original_row = 1 if piece.color == 'black' else 6
                            if row != original_row:
                                wing_pawn_penalty = 15
                                if piece.color == 'white':
                                    score -= wing_pawn_penalty
                                else:
                                    score += wing_pawn_penalty
        
        return score
