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
        [-50, -40, -30, -30, -30, -30, -40, -50],  # 8th rank - avoid back rank
        [-40, -20,   0,   0,   5,   0, -20, -40],  # 7th rank - decent outposts
        [-30,   0,  10,  15,  15,  10,   0, -30],  # 6th rank - good outposts
        [-30,   5,  15,  20,  20,  15,   5, -30],  # 5th rank - excellent central squares
        [-30,   0,  15,  20,  20,  15,   0, -30],  # 4th rank - excellent central squares
        [-30,   5,  10,  15,  15,  10,   5, -30],  # 3rd rank - good development
        [-40, -20,   0,   5,   5,   0, -20, -40],  # 2nd rank - early development
        [-50, -40, -30, -30, -30, -30, -40, -50]   # 1st rank - starting position
    ]
    
    BISHOP_TABLE = [
        [-30, -40, -40, -35, -35, -40, -40, -30],  # 8th rank - avoid back rank
        [-40, -20, -10, -10, -10, -10, -20, -40],  # 7th rank - better development  
        [-40, -10,   0,   0,   0,   0, -10, -40],  # 6th rank - reasonable outposts
        [-35, -10,  10,  15,  15,  10, -10, -35],  # 5th rank - good central squares
        [-35, -10,  10,  15,  15,  10, -10, -35],  # 4th rank - good central squares
        [-40, -10,   0,  10,  10,   0, -10, -40],  # 3rd rank - early development
        [-40, -20, -10, -10, -10, -10, -20, -40],  # 2nd rank - starting development
        [-30, -40, -40, -35, -35, -40, -40, -30]   # 1st rank - starting position
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
        ENHANCED evaluation with advanced chess knowledge.
        Includes sophisticated positional understanding and tactical awareness.
        """
        score = 0.0
        
        # 1. MATERIAL - Most important, must be accurate
        score += Evaluation.evaluate_material(board)
        
        # 2. GAME PHASE DETECTION
        game_phase = Evaluation._get_game_phase(board)
        
        # 3. POSITIONAL - Increased weight for better play
        score += Evaluation.evaluate_position(board, game_phase) * 0.6
        
        # 4. OPENING PRINCIPLES - Fixed version with proper perspective
        if game_phase == 'opening':
            score += Evaluation.evaluate_opening_principles(board) * 1.5  # Increased importance
        
        # 5. KING SAFETY - More important in middlegame, scaled by game phase
        if game_phase in ['opening', 'middlegame']:
            king_safety_weight = 0.8 if game_phase == 'middlegame' else 0.5
            score += Evaluation.evaluate_king_safety(board, game_phase) * king_safety_weight
        
        # 6. TEMPO PENALTY - Discourage moving same piece multiple times
        score += Evaluation.evaluate_tempo_penalty(board) * 1.0
        
        # 7. HANGING PIECES - Critical tactical detection  
        score += Evaluation.evaluate_hanging_pieces(board) * 5.0  # MASSIVE penalty!
        
        # 8. PAWN STRUCTURE - Critical for positional understanding
        score += Evaluation.evaluate_pawn_structure(board) * 0.5
        
        # 9. PIECE COORDINATION - Important for piece harmony
        score += Evaluation.evaluate_piece_coordination(board) * 0.4
        
        # 10. ADVANCED PIECE ACTIVITY - New enhanced mobility evaluation
        score += Evaluation.evaluate_piece_activity_advanced(board, game_phase) * 0.3
        
        # 11. ENDGAME FACTORS - Important in endgame
        if game_phase == 'endgame':
            score += Evaluation.evaluate_endgame_factors(board) * 1.0
        
        # 12. TACTICAL THEMES - Enhanced tactical detection
        score += Evaluation.evaluate_tactical_themes_enhanced(board) * 0.4
        
        # 13. SPACE CONTROL - New evaluation for territorial advantage
        score += Evaluation.evaluate_space_control(board, game_phase) * 0.2
        
        return score
    
    @staticmethod
    def evaluate_debug(board) -> Dict[str, float]:
        """
        Debug version that returns all evaluation components separately.
        Uses the same weights as the main evaluation function.
        """
        game_phase = Evaluation._get_game_phase(board)
        
        components = {
            'material': Evaluation.evaluate_material(board),
            'position': Evaluation.evaluate_position(board, game_phase) * 0.6,
            'king_safety': Evaluation.evaluate_king_safety(board, game_phase) * (0.8 if game_phase == 'middlegame' else 0.5),
            'tempo_penalty': Evaluation.evaluate_tempo_penalty(board) * 1.0,
            'hanging_pieces': Evaluation.evaluate_hanging_pieces(board) * 5.0,
            'pawn_structure': Evaluation.evaluate_pawn_structure(board) * 0.5,
            'piece_coordination': Evaluation.evaluate_piece_coordination(board) * 0.4,
            'piece_activity': Evaluation.evaluate_piece_activity_advanced(board, game_phase) * 0.3,
            'tactical_enhanced': Evaluation.evaluate_tactical_themes_enhanced(board) * 0.4,
            'space_control': Evaluation.evaluate_space_control(board, game_phase) * 0.2,
        }
        
        # Game phase specific components
        if game_phase == 'opening':
            components['opening'] = Evaluation.evaluate_opening_principles(board) * 1.5
        else:
            components['opening'] = 0.0
            
        if game_phase == 'endgame':
            components['endgame'] = Evaluation.evaluate_endgame_factors(board) * 1.0
        else:
            components['endgame'] = 0.0
            
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
        IMPROVED opening principles with emphasis on center pawns and balanced development.
        Prioritizes center control and discourages repetitive piece movements.
        """
        score = 0.0
        move_count = board.fullmove_number
        
        # Only apply in opening (first 12 moves)
        if move_count > 12:
            return 0.0
        
        # CENTER PAWN CONTROL - Highest priority in opening
        center_score = 0.0
        
        # Check for center pawn advances (d4, e4, d5, e5)
        if board.squares[4][3].has_piece and board.squares[4][3].piece.name == 'pawn':  # d4
            if board.squares[4][3].piece.color == 'white':
                center_score += 60  # Much stronger bonus for d4
            else:
                center_score -= 60
        
        if board.squares[4][4].has_piece and board.squares[4][4].piece.name == 'pawn':  # e4
            if board.squares[4][4].piece.color == 'white':
                center_score += 80  # Much stronger bonus for e4
            else:
                center_score -= 80
                
        if board.squares[3][3].has_piece and board.squares[3][3].piece.name == 'pawn':  # d5
            if board.squares[3][3].piece.color == 'black':
                center_score -= 80  # Good for black (good for Black = negative for evaluation)
            else:
                center_score -= 40  # White pawn on d5 is advanced but not ideal
                
        if board.squares[3][4].has_piece and board.squares[3][4].piece.name == 'pawn':  # e5
            if board.squares[3][4].piece.color == 'black':
                center_score -= 80  # Good for black (good for Black = negative for evaluation)
            else:
                center_score -= 40  # White pawn on e5 is advanced but can be weak
        
        # Secondary center moves (c4, f4, c5, f5) - still valuable
        if board.squares[4][2].has_piece and board.squares[4][2].piece.name == 'pawn':  # c4
            if board.squares[4][2].piece.color == 'white':
                center_score += 40  # Good bonus for c4
            else:
                center_score -= 40
                
        if board.squares[4][5].has_piece and board.squares[4][5].piece.name == 'pawn':  # f4
            if board.squares[4][5].piece.color == 'white':
                center_score += 60  # Good bonus for f4
            else:
                center_score -= 60
                
        if board.squares[3][2].has_piece and board.squares[3][2].piece.name == 'pawn':  # c5
            if board.squares[3][2].piece.color == 'black':
                center_score -= 60  # Good for black
            else:
                center_score -= 20  # White pawn on c5 is okay but not ideal
                
        if board.squares[3][5].has_piece and board.squares[3][5].piece.name == 'pawn':  # f5
            if board.squares[3][5].piece.color == 'black':
                center_score -= 60  # Good for black
            else:
                center_score -= 20  # White pawn on f5 is okay but not ideal
        
        score += center_score
        
        # BALANCED PIECE DEVELOPMENT - Lower bonus to prioritize center pawns
        white_pieces_developed = 0
        black_pieces_developed = 0
        white_queen_early = False
        black_queen_early = False
        
        # Track specific piece positions for development quality
        white_knights_developed = 0
        black_knights_developed = 0
        white_bishops_developed = 0
        black_bishops_developed = 0
        
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece and square.piece:
                    piece = square.piece
                    
                    if piece.color == 'white':
                        # White development - prefer good squares
                        if piece.name == 'knight' and row < 7:
                            white_knights_developed += 1
                            # Bonus for knights on good squares (f3, c3, f6, c6)
                            if (row, col) in [(5, 2), (5, 5)]:  # c3, f3
                                white_pieces_developed += 1.5
                            else:
                                white_pieces_developed += 1
                        elif piece.name == 'bishop' and row < 7:
                            white_bishops_developed += 1
                            white_pieces_developed += 1
                        elif piece.name == 'queen' and row < 7:
                            white_queen_early = True
                    else:  # black
                        # Black development
                        if piece.name == 'knight' and row > 0:
                            black_knights_developed += 1
                            # Bonus for knights on good squares
                            if (row, col) in [(2, 2), (2, 5)]:  # c6, f6
                                black_pieces_developed += 1.5
                            else:
                                black_pieces_developed += 1
                        elif piece.name == 'bishop' and row > 0:
                            black_bishops_developed += 1
                            black_pieces_developed += 1
                        elif piece.name == 'queen' and row > 0:
                            black_queen_early = True
        
        # REDUCED development bonus to prioritize center pawns
        score += (white_pieces_developed - black_pieces_developed) * 8
        
        # PENALTY for over-developing knights before center pawns
        if move_count <= 4:  # In first 4 moves
            if white_knights_developed >= 2 and center_score <= 0:
                score -= 50  # Strong penalty for developing both knights before center
            if black_knights_developed >= 2 and center_score >= 0:
                score += 50  # Penalty for black doing same
        
        # PENALTY for moving same piece twice in opening
        if move_count <= 6:  # Extended to first 6 moves
            if white_knights_developed >= 1 and center_score <= 0:
                score -= 30  # Penalty for knight moves without center pawns
            if black_knights_developed >= 1 and center_score >= 0:
                score += 30
        
        # Early queen development is bad
        if white_queen_early:
            score -= 60  # Increased penalty
        if black_queen_early:
            score += 60
        
        # Castling bonus (check castling rights)
        if 'K' in board.castling_rights or 'Q' in board.castling_rights:
            score -= 10  # Small penalty for White not castling yet
        if 'k' in board.castling_rights or 'q' in board.castling_rights:
            score += 10  # Small penalty for Black not castling (good for White)
        
        # Castling bonus (check castling rights)
        if 'K' in board.castling_rights or 'Q' in board.castling_rights:
            score -= 15  # Penalty for White not castling yet
        if 'k' in board.castling_rights or 'q' in board.castling_rights:
            score += 15  # Penalty for Black not castling (good for White)
        
        return score

    @staticmethod
    def evaluate_piece_activity_advanced(board, game_phase: str) -> float:
        """
        Advanced piece activity evaluation considering piece-specific factors.
        """
        score = 0.0
        
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if square.has_piece and square.piece:
                    piece = square.piece
                    piece_activity = 0.0
                    
                    # Calculate piece-specific activity bonuses
                    if piece.name == 'knight':
                        # Knights are more active near center
                        center_distance = abs(row - 3.5) + abs(col - 3.5)
                        piece_activity += max(0, 7 - center_distance) * 3
                        
                        # Bonus for outpost squares
                        if Evaluation._is_knight_outpost(board, row, col, piece.color):
                            piece_activity += 15
                            
                    elif piece.name == 'bishop':
                        # Bishops prefer long diagonals
                        if Evaluation._is_on_long_diagonal(row, col):
                            piece_activity += 10
                        
                        # Bishop pair activity
                        if Evaluation._has_bishop_pair(board, piece.color):
                            piece_activity += 5
                            
                    elif piece.name == 'rook':
                        # Rooks on open files
                        if Evaluation._is_on_open_file(board, col):
                            piece_activity += 15
                        
                        # Rooks on 7th rank
                        if (piece.color == 'white' and row == 1) or (piece.color == 'black' and row == 6):
                            piece_activity += 20
                            
                    elif piece.name == 'queen':
                        # Queen centralization (but not in opening)
                        if game_phase != 'opening':
                            center_distance = abs(row - 3.5) + abs(col - 3.5)
                            piece_activity += max(0, 5 - center_distance) * 2
                    
                    # Apply piece activity score
                    if piece.color == 'white':
                        score += piece_activity
                    else:
                        score -= piece_activity
        
        return score
    
    @staticmethod
    def evaluate_tactical_themes_enhanced(board) -> float:
        """
        Enhanced tactical pattern recognition.
        """
        score = 0.0
        
        # Look for pins, forks, and other tactical motifs
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if square.has_piece and square.piece:
                    piece = square.piece
                    
                    # Check for piece attacking multiple targets (fork potential)
                    if piece.name in ['knight', 'queen']:
                        targets = Evaluation._count_attack_targets(board, piece, row, col)
                        if targets >= 2:
                            fork_bonus = targets * 10
                            if piece.color == 'white':
                                score += fork_bonus
                            else:
                                score -= fork_bonus
                    
                    # Check for pieces defending important squares
                    if piece.name in ['bishop', 'rook', 'queen']:
                        defense_value = Evaluation._calculate_defense_value(board, piece, row, col)
                        if piece.color == 'white':
                            score += defense_value
                        else:
                            score -= defense_value
        
        return score
    
    @staticmethod
    def evaluate_space_control(board, game_phase: str) -> float:
        """
        Evaluate territorial control and space advantage.
        """
        score = 0.0
        
        white_controlled = 0
        black_controlled = 0
        
        # Count squares controlled by each side
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                
                # Weight center squares more heavily
                square_weight = 1
                if 2 <= row <= 5 and 2 <= col <= 5:
                    square_weight = 3  # Center squares worth more
                elif 1 <= row <= 6 and 1 <= col <= 6:
                    square_weight = 2  # Extended center
                
                # Check which side controls this square
                white_attackers = Evaluation._count_attackers(board, row, col, 'white')
                black_attackers = Evaluation._count_attackers(board, row, col, 'black')
                
                if white_attackers > black_attackers:
                    white_controlled += square_weight
                elif black_attackers > white_attackers:
                    black_controlled += square_weight
        
        # Space advantage calculation
        space_diff = white_controlled - black_controlled
        score += space_diff * 0.5  # Small bonus per controlled square
        
        return score
    
    @staticmethod
    def _has_bishop_pair(board, color: str) -> bool:
        """Check if the given color has both bishops."""
        bishop_count = 0
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if (square.has_piece and square.piece and 
                    square.piece.name == 'bishop' and square.piece.color == color):
                    bishop_count += 1
        return bishop_count >= 2
    
    @staticmethod
    def _count_attack_targets(board, piece: Piece, row: int, col: int) -> int:
        """Count how many enemy pieces this piece can attack."""
        # This is a simplified version - would need to calculate actual attacks
        targets = 0
        opponent_color = 'black' if piece.color == 'white' else 'white'
        
        # Simple proximity check for demonstration
        for target_row in range(max(0, row-2), min(ROWS, row+3)):
            for target_col in range(max(0, col-2), min(COLS, col+3)):
                target_square = board.squares[target_row][target_col]
                if (target_square.has_piece and target_square.piece and 
                    target_square.piece.color == opponent_color):
                    targets += 1
        
        return min(targets, 3)  # Cap at 3 for performance
    
    @staticmethod
    def _calculate_defense_value(board, piece: Piece, row: int, col: int) -> float:
        """Calculate the defensive value of a piece's position."""
        defense_value = 0.0
        
        # Defending the king area
        king_pos = Evaluation._find_king(board, piece.color)
        if king_pos:
            king_row, king_col = king_pos
            distance_to_king = abs(row - king_row) + abs(col - king_col)
            if distance_to_king <= 3:
                defense_value += max(0, 4 - distance_to_king) * 2
        
        # Defending important squares (center, back rank)
        if piece.color == 'white':
            if row == 7:  # Back rank defense
                defense_value += 3
        else:
            if row == 0:  # Back rank defense
                defense_value += 3
        
        return defense_value
    
    @staticmethod
    def _count_attackers(board, row: int, col: int, color: str) -> int:
        """Count how many pieces of given color attack a square."""
        # Simplified attacker count - real implementation would check piece move patterns
        attackers = 0
        
        # Check adjacent squares for potential attackers
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                check_row, check_col = row + dr, col + dc
                if 0 <= check_row < ROWS and 0 <= check_col < COLS:
                    square = board.squares[check_row][check_col]
                    if (square.has_piece and square.piece and 
                        square.piece.color == color):
                        attackers += 1
        
        return min(attackers, 4)  # Cap for performance

    @staticmethod
    def _is_knight_outpost(board, row: int, col: int, color: str) -> bool:
        """Check if this square is a knight outpost (strong square for knight)."""
        opponent_color = 'black' if color == 'white' else 'white'
        
        # Check if enemy pawns can attack this square
        pawn_direction = 1 if opponent_color == 'white' else -1
        
        # Check adjacent files for enemy pawns that could advance to attack
        for file_offset in [-1, 1]:
            check_col = col + file_offset
            if 0 <= check_col < COLS:
                for check_row in range(ROWS):
                    square = board.squares[check_row][check_col]
                    if (square.has_piece and square.piece and 
                        square.piece.name == 'pawn' and 
                        square.piece.color == opponent_color):
                        # Check if this pawn could eventually attack our square
                        if (opponent_color == 'white' and check_row > row) or \
                           (opponent_color == 'black' and check_row < row):
                            return False  # Pawn can advance to attack
        
        return True  # No enemy pawns can attack - it's an outpost
    
    @staticmethod
    def _is_on_long_diagonal(row: int, col: int) -> bool:
        """Check if position is on a long diagonal (a1-h8 or a8-h1)."""
        return (row == col) or (row + col == 7)
    
    @staticmethod
    def _is_on_open_file(board, col: int) -> bool:
        """Check if a file is open (no pawns)."""
        for row in range(ROWS):
            square = board.squares[row][col]
            if square.has_piece and square.piece and square.piece.name == 'pawn':
                return False
        return True

    @staticmethod
    def evaluate_tempo_penalty(board) -> float:
        """
        Evaluate tempo penalty for moving the same piece multiple times.
        This discourages the AI from obsessively moving the same piece.
        """
        penalty = 0.0
        
        # We can only check the last move for now
        # In a more sophisticated system, we'd track move history
        if board.last_move is None:
            return 0.0
        
        last_move = board.last_move
        last_piece_position = (last_move.final.row, last_move.final.col)
        
        # Get the piece that was moved
        moved_piece = board.squares[last_piece_position[0]][last_piece_position[1]].piece
        if not moved_piece:
            return 0.0
        
        # Apply penalty based on piece type and game situation
        piece_penalty = 0.0
        
        # Knights are especially prone to wandering - penalize heavily
        if moved_piece.name == 'knight':
            piece_penalty = -30.0  # 30 centipawn penalty
            
        # Bishops moving too much in opening/middlegame
        elif moved_piece.name == 'bishop':
            piece_penalty = -20.0  # 20 centipawn penalty
            
        # Queens moving too early (though less relevant in middlegame)
        elif moved_piece.name == 'queen':
            piece_penalty = -25.0  # 25 centipawn penalty
            
        # Less penalty for other pieces
        else:
            piece_penalty = -10.0  # 10 centipawn penalty
        
        # Check if the moved piece is in a "premium" position that might tempt
        # the AI to move it again (like the problematic knight table values)
        row, col = last_piece_position
        
        # For knights, extra penalty if on squares that the old table overvalued
        if moved_piece.name == 'knight':
            # These were the problematic squares in the old table:
            # c7=+100, d6=+74, e6=+73, b6=+67, f7=+62, g6=+62
            problem_squares = [
                (1, 2),  # c7
                (2, 3),  # d6  
                (2, 4),  # e6
                (2, 1),  # b6
                (1, 5),  # f7
                (2, 6),  # g6
                (3, 6),  # g5 (where the knight was going to h7)
            ]
            
            if (row, col) in problem_squares:
                piece_penalty -= 40.0  # Extra penalty for "tempting" squares
        
        # Apply penalty from the current player's perspective
        if moved_piece.color == 'white':
            penalty += piece_penalty
        else:
            penalty -= piece_penalty  # Penalty for white benefits black
        
        return penalty

    @staticmethod
    def evaluate_hanging_pieces(board) -> float:
        """
        ENHANCED hanging piece detection using SEE-like analysis.
        This is critical for preventing blunders like Ba6 where pieces get captured for free.
        """
        hanging_penalty = 0.0
        
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if not square.has_piece or not square.piece:
                    continue
                    
                piece = square.piece
                
                # Check if this piece is hanging using more sophisticated analysis
                hanging_value = Evaluation._calculate_hanging_value(board, piece, row, col)
                
                if hanging_value > 0:  # Piece is hanging (loses material)
                    if piece.color == 'white':
                        hanging_penalty -= hanging_value  # Bad for white
                    else:
                        hanging_penalty += hanging_value  # Good for white (black piece hanging)
        
        return hanging_penalty

    @staticmethod
    def _calculate_hanging_value(board, piece: Piece, row: int, col: int) -> float:
        """
        Calculate how much material is lost if this piece is hanging.
        Uses a SEE-like approach to determine if piece can be captured profitably.
        Returns positive value if piece loses material when captured.
        """
        opponent_color = 'black' if piece.color == 'white' else 'white'
        
        # Get all pieces that can attack this square
        attackers = []
        defenders = []
        
        # Find attackers and defenders
        for r in range(ROWS):
            for c in range(COLS):
                sq = board.squares[r][c]
                if not sq.has_piece or not sq.piece:
                    continue
                    
                attacking_piece = sq.piece
                
                if Evaluation._can_piece_attack(board, attacking_piece, r, c, row, col):
                    piece_value = Evaluation.PIECE_VALUES.get(attacking_piece.name, 100)
                    
                    if attacking_piece.color == opponent_color:
                        attackers.append((piece_value, attacking_piece.name))
                    elif attacking_piece.color == piece.color and not (r == row and c == col):
                        # Don't count the piece itself as a defender
                        defenders.append((piece_value, attacking_piece.name))
        
        if not attackers:
            return 0.0  # No attackers, piece is safe
            
        # Sort by piece value (cheapest pieces attack/defend first)
        attackers.sort(key=lambda x: x[0])
        defenders.sort(key=lambda x: x[0])
        
        # Simulate the exchange
        piece_value = Evaluation.PIECE_VALUES.get(piece.name, 100)
        return Evaluation._simulate_hanging_exchange(attackers, defenders, piece_value)
    
    @staticmethod
    def _simulate_hanging_exchange(attackers: List, defenders: List, target_value: int) -> float:
        """
        Simulate the exchange sequence when a piece is attacked.
        Returns the material loss for the defending side.
        """
        if not attackers:
            return 0.0
            
        material_balance = target_value  # Attacker captures target
        current_piece_value = attackers[0][0] if attackers else 0  # Value of attacking piece
        
        attacker_idx = 1  # Next attacker (first one already used)
        defender_idx = 0  # Next defender
        defender_turn = True  # Defender recaptures next
        
        while True:
            if defender_turn:
                if defender_idx >= len(defenders):
                    break  # No more defenders
                material_balance -= current_piece_value  # Defender recaptures
                current_piece_value = defenders[defender_idx][0]
                defender_idx += 1
            else:
                if attacker_idx >= len(attackers):
                    break  # No more attackers
                material_balance += current_piece_value  # Attacker recaptures
                current_piece_value = attackers[attacker_idx][0]
                attacker_idx += 1
                
            defender_turn = not defender_turn
        
        # Return loss for defending side (positive = defender loses material)
        return max(0, material_balance)
    
    @staticmethod
    def _can_piece_attack(board, piece: Piece, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """
        Check if a piece can attack a target square.
        ENHANCED attack detection for hanging piece analysis.
        """
        if piece.name == 'pawn':
            return Evaluation._pawn_can_attack(piece, from_row, from_col, to_row, to_col)
        elif piece.name == 'knight':
            return Evaluation._knight_can_attack(from_row, from_col, to_row, to_col)
        elif piece.name == 'bishop':
            return Evaluation._bishop_can_attack(board, from_row, from_col, to_row, to_col)
        elif piece.name == 'rook':
            return Evaluation._rook_can_attack(board, from_row, from_col, to_row, to_col)
        elif piece.name == 'queen':
            return (Evaluation._bishop_can_attack(board, from_row, from_col, to_row, to_col) or
                    Evaluation._rook_can_attack(board, from_row, from_col, to_row, to_col))
        elif piece.name == 'king':
            return Evaluation._king_can_attack(from_row, from_col, to_row, to_col)
        
        return False
    
    @staticmethod
    def _pawn_can_attack(pawn: Piece, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if pawn can attack target square."""
        direction = -1 if pawn.color == 'white' else 1
        
        # Pawn attacks diagonally one square
        if (to_row == from_row + direction and 
            abs(to_col - from_col) == 1):
            return True
        return False
    
    @staticmethod
    def _knight_can_attack(from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if knight can attack target square."""
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        # Knight moves in L-shape: 2+1 or 1+2
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
    @staticmethod
    def _bishop_can_attack(board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if bishop can attack target square (diagonal line of sight)."""
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        # Must be diagonal
        if row_diff != col_diff:
            return False
            
        # Check for blocking pieces
        row_step = 1 if to_row > from_row else -1
        col_step = 1 if to_col > from_col else -1
        
        current_row = from_row + row_step
        current_col = from_col + col_step
        
        while current_row != to_row and current_col != to_col:
            if board.squares[current_row][current_col].has_piece:
                return False  # Path blocked
            current_row += row_step
            current_col += col_step
            
        return True
    
    @staticmethod
    def _rook_can_attack(board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if rook can attack target square (horizontal/vertical line of sight)."""
        # Must be same row or column
        if from_row != to_row and from_col != to_col:
            return False
            
        # Check for blocking pieces
        if from_row == to_row:  # Horizontal
            start_col = min(from_col, to_col) + 1
            end_col = max(from_col, to_col)
            for col in range(start_col, end_col):
                if board.squares[from_row][col].has_piece:
                    return False
        else:  # Vertical
            start_row = min(from_row, to_row) + 1
            end_row = max(from_row, to_row)
            for row in range(start_row, end_row):
                if board.squares[row][from_col].has_piece:
                    return False
                    
        return True
    
    @staticmethod
    def _king_can_attack(from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if king can attack target square (one square in any direction)."""
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        # King moves one square in any direction
        return row_diff <= 1 and col_diff <= 1 and (row_diff + col_diff > 0)
        
        return penalty
