"""
Move information structure for efficient make/unmake operations.
Stores all information needed to undo a move without board copying.
"""

from typing import Optional
from piece import Piece

class MoveInfo:
    """
    Stores information needed to undo a move.
    This replaces expensive board copying with fast incremental updates.
    """
    
    def __init__(self):
        # Captured piece information
        self.captured_piece: Optional[Piece] = None
        self.captured_square_row: int = -1
        self.captured_square_col: int = -1
        
        # En passant capture information
        self.en_passant_capture: bool = False
        self.en_passant_captured_piece: Optional[Piece] = None
        self.en_passant_capture_row: int = -1
        self.en_passant_capture_col: int = -1
        
        # Castling information
        self.is_castling: bool = False
        self.rook_initial_row: int = -1
        self.rook_initial_col: int = -1
        self.rook_final_row: int = -1
        self.rook_final_col: int = -1
        self.rook_was_moved: bool = False  # Store rook's original moved status
        
        # Game state before move (for restoration)
        self.prev_castling_rights: str = ""
        self.prev_en_passant: str = ""
        self.prev_halfmove_clock: int = 0
        self.prev_fullmove_number: int = 0
        self.prev_next_player: str = ""
        
        # Piece state changes
        self.piece_was_moved: bool = False
        
        # Promotion information
        self.is_promotion: bool = False
        self.promoted_from_piece: Optional[Piece] = None
