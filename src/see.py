"""
Static Exchange Evaluation (SEE) for chess.
Calculates the material outcome of capture sequences on a given square.
"""

from typing import List, Optional, Tuple
from piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from evaluation import Evaluation

class SEE:
    """
    Static Exchange Evaluation implementation.
    Calculates material exchanges without full search.
    """
    
    @staticmethod
    def evaluate_capture(board, move) -> int:
        """
        Evaluate a capture using Static Exchange Evaluation.
        
        Args:
            board: Current board position
            move: The capture move to evaluate
            
        Returns:
            Material gain/loss in centipawns (positive = good for moving side)
        """
        if not move.captured:
            return 0  # Not a capture
            
        target_square = (move.final.row, move.final.col)
        
        # Get the moving piece from the board
        moving_piece = board.squares[move.initial.row][move.initial.col].piece
        if not moving_piece:
            return 0  # No piece to move
        
        # Get all attackers and defenders of the target square
        white_attackers = SEE._get_attackers(board, target_square, 'white')
        black_attackers = SEE._get_attackers(board, target_square, 'black')
        
        # Remove the moving piece from its respective attacker list
        moving_piece_pos = (move.initial.row, move.initial.col, moving_piece.name)
        if moving_piece.color == 'white':
            white_attackers = [a for a in white_attackers if a != moving_piece_pos]
        else:
            black_attackers = [a for a in black_attackers if a != moving_piece_pos]
        
        # Initial capture value
        captured_value = Evaluation.PIECE_VALUES.get(move.captured.name, 0)
        moving_piece_value = Evaluation.PIECE_VALUES.get(moving_piece.name, 0)
        
        # Simulate the exchange sequence
        return SEE._simulate_exchange(
            white_attackers, black_attackers, 
            captured_value, moving_piece_value,
            moving_piece.color == 'white'
        )
    
    @staticmethod
    def _get_attackers(board, square: Tuple[int, int], color: str) -> List[Tuple[int, int, str]]:
        """
        Get all pieces of given color that can attack the target square.
        
        Returns:
            List of (row, col, piece_name) tuples sorted by piece value (lowest first)
        """
        attackers = []
        target_row, target_col = square
        
        for row in range(8):
            for col in range(8):
                piece = board.squares[row][col].piece
                if not piece or piece.color != color:
                    continue
                    
                if SEE._can_attack_square(board, piece, row, col, target_row, target_col):
                    attackers.append((row, col, piece.name))
        
        # Sort by piece value (use least valuable pieces first)
        attackers.sort(key=lambda x: Evaluation.PIECE_VALUES.get(x[2], 0))
        return attackers
    
    @staticmethod
    def _can_attack_square(board, piece: Piece, from_row: int, from_col: int, 
                          to_row: int, to_col: int) -> bool:
        """
        Check if a piece can attack a given square.
        FIXED: Properly handles all piece types and path checking.
        """
        if from_row == to_row and from_col == to_col:
            return False
            
        piece_name = piece.name.lower()
        
        # Pawn attacks
        if piece_name == 'pawn':
            direction = -1 if piece.color == 'white' else 1
            if (from_row + direction == to_row and 
                abs(from_col - to_col) == 1):
                return True
                
        # Knight attacks
        elif piece_name == 'knight':
            row_diff = abs(from_row - to_row)
            col_diff = abs(from_col - to_col)
            if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
                return True
                
        # Bishop attacks (and queen diagonal)
        elif piece_name == 'bishop' or (piece_name == 'queen' and abs(from_row - to_row) == abs(from_col - to_col)):
            if abs(from_row - to_row) == abs(from_col - to_col):
                return SEE._is_diagonal_clear(board, from_row, from_col, to_row, to_col)
                    
        # Rook attacks (and queen straight)
        elif piece_name == 'rook' or (piece_name == 'queen' and (from_row == to_row or from_col == to_col)):
            if from_row == to_row or from_col == to_col:
                return SEE._is_line_clear(board, from_row, from_col, to_row, to_col)
                    
        # King attacks
        elif piece_name == 'king':
            if abs(from_row - to_row) <= 1 and abs(from_col - to_col) <= 1:
                return True
                
        return False
    
    @staticmethod
    def _is_line_clear(board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if horizontal/vertical line is clear between two squares."""
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
    def _is_diagonal_clear(board, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if diagonal line is clear between two squares."""
        row_step = 1 if to_row > from_row else -1
        col_step = 1 if to_col > from_col else -1
        
        current_row = from_row + row_step
        current_col = from_col + col_step
        
        while current_row != to_row and current_col != to_col:
            if board.squares[current_row][current_col].has_piece:
                return False
            current_row += row_step
            current_col += col_step
            
        return True
    
    @staticmethod
    def _simulate_exchange(white_attackers: List, black_attackers: List, 
                          captured_value: int, moving_piece_value: int, 
                          white_to_move: bool) -> int:
        """
        Simulate the exchange sequence and return net material gain.
        
        Args:
            white_attackers: List of white attacking pieces
            black_attackers: List of black attacking pieces  
            captured_value: Value of initially captured piece
            moving_piece_value: Value of piece making initial capture
            white_to_move: True if white made the initial capture
            
        Returns:
            Net material gain from white's perspective
        """
        # Copy the attacker lists so we can modify them
        white_list = white_attackers.copy()
        black_list = black_attackers.copy()
        
        # Material balance from white's perspective
        material_balance = captured_value if white_to_move else -captured_value
        current_piece_value = moving_piece_value
        is_white_turn = not white_to_move  # Next move is opponent's
        
        # Simulate exchanges until no more attackers or king would be captured
        while True:
            if is_white_turn:
                if not white_list:
                    break
                # White recaptures
                attacker = white_list.pop(0)  # Use least valuable
                attacker_value = Evaluation.PIECE_VALUES.get(attacker[2], 0)
                material_balance += current_piece_value
                current_piece_value = attacker_value
                
                # Don't capture with king if still under attack
                if attacker[2] == 'king' and black_list:
                    break
                    
            else:
                if not black_list:
                    break
                # Black recaptures
                attacker = black_list.pop(0)  # Use least valuable
                attacker_value = Evaluation.PIECE_VALUES.get(attacker[2], 0)
                material_balance -= current_piece_value
                current_piece_value = attacker_value
                
                # Don't capture with king if still under attack
                if attacker[2] == 'king' and white_list:
                    break
            
            is_white_turn = not is_white_turn
        
        return material_balance
    
    @staticmethod
    def is_good_capture(board, move) -> bool:
        """
        Quick check if a capture is materially favorable.
        
        Returns:
            True if the capture gains material or breaks even
        """
        see_value = SEE.evaluate_capture(board, move)
        return see_value >= 0
    
    @staticmethod
    def get_capture_value(board, move) -> int:
        """
        Get the SEE value of a capture.
        Convenience method for move ordering.
        """
        return SEE.evaluate_capture(board, move)
