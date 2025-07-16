from typing import Any, Optional
from square import Square

class Move:
    """
    Represents a chess move from one square to another.
    Includes information about captured pieces and pawn promotion.
    Used throughout the engine for move generation, validation, and execution.
    """
    
    def __init__(self, initial: Any, final: Any, captured: Any = None, promotion: Optional[str] = None):
        self.initial = initial    # Starting square of the move
        self.final = final        # Destination square of the move
        self.captured = captured  # Piece captured by this move (if any)
        self.promotion = promotion  # Promotion piece for pawn promotion ('q', 'r', 'b', 'n')

    def __str__(self) -> str:
        """String representation showing initial and final coordinates."""
        s = ''
        s += f'({self.initial.col}, {self.initial.row})'
        s += f'({self.final.col}, {self.final.row})'
        return s

    def __eq__(self, other: object) -> bool:
        """
        Two moves are equal if they have the same initial square, final square,
        and promotion piece. Used for move comparison and validation.
        """
        return (
            isinstance(other, Move) and
            self.initial == other.initial and 
            self.final == other.final and 
            self.promotion == other.promotion
        )

    def __hash__(self) -> int:
        """
        Hash function for move objects to enable use in sets and dictionaries.
        Essential for transposition tables and move ordering.
        """
        return hash((
            (self.initial.row, self.initial.col),
            (self.final.row, self.final.col),
            self.promotion
        ))

    def to_algebraic(self) -> str:
        """
        Convert move to algebraic notation (e.g., 'e2e4', 'e7e8q').
        Useful for opening books and move logging.
        """
        initial_sq = f"{chr(ord('a') + self.initial.col)}{8 - self.initial.row}"
        final_sq = f"{chr(ord('a') + self.final.col)}{8 - self.final.row}"
        promotion = self.promotion if self.promotion else ""
        return f"{initial_sq}{final_sq}{promotion}"

    @classmethod
    def from_algebraic(cls, notation: str, board) -> 'Move':
        """
        Create a move from algebraic notation.
        Useful for parsing opening books and saved games.
        """
        if len(notation) < 4:
            raise ValueError(f"Invalid move notation: {notation}")
        
        initial_col = ord(notation[0]) - ord('a')
        initial_row = 8 - int(notation[1])
        final_col = ord(notation[2]) - ord('a')
        final_row = 8 - int(notation[3])
        
        promotion = notation[4] if len(notation) > 4 else None
        captured = board.squares[final_row][final_col].piece if board else None
        
        return cls(
            Square(initial_row, initial_col),
            Square(final_row, final_col),
            captured,
            promotion
        )

    def is_capture(self) -> bool:
        """Check if this move captures a piece."""
        return self.captured is not None

    def is_promotion(self) -> bool:
        """Check if this move is a pawn promotion."""
        return self.promotion is not None