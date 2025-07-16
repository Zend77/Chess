from typing import Any, Optional

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