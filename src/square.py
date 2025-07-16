from typing import Optional, Any


class Square:
    """
    Represents a single square on the chess board.
    Each square has coordinates (row, col) and may contain a piece.
    Provides utilities for checking piece occupancy and converting to algebraic notation.
    """
    
    # Mapping from column indices to algebraic notation (a-h)
    ALPHACOLS: dict[int, str] = {i: chr(ord('a') + i) for i in range(8)}

    def __init__(self, row: int, col: int, piece: Optional[Any] = None):
        self.row: int = row          # Row index (0-7, where 0 is rank 8)
        self.col: int = col          # Column index (0-7, where 0 is file a)
        self.piece: Optional[Any] = piece  # Piece on this square (if any)
        self.alphacol: str = self.ALPHACOLS[col]  # File letter (a-h)

    def __eq__(self, other: object) -> bool:
        """Two squares are equal if they have the same coordinates."""
        if not isinstance(other, Square):
            return NotImplemented
        return self.row == other.row and self.col == other.col

    @property
    def has_piece(self) -> bool:
        """Check if this square contains a piece."""
        return self.piece is not None

    @property
    def is_empty(self) -> bool:
        """Check if this square is empty."""
        return not self.has_piece

    def has_team_piece(self, color: str) -> bool:
        """Check if this square contains a piece of the specified color."""
        return self.piece is not None and self.piece.color == color

    def has_enemy_piece(self, color: str) -> bool:
        """Check if this square contains an enemy piece (opposite color)."""
        return self.piece is not None and self.piece.color != color

    def is_empty_or_enemy(self, color: str) -> bool:
        """Check if this square is empty or contains an enemy piece (valid move target)."""
        return self.is_empty or self.has_enemy_piece(color)

    @staticmethod
    def in_range(*args: int) -> bool:
        """Check if all given coordinates are within the board (0-7)."""
        return all(0 <= arg <= 7 for arg in args)

    @classmethod
    def get_alphacol(cls, col: int) -> str:
        """Convert column index to algebraic file letter (0->a, 1->b, etc.)."""
        return cls.ALPHACOLS[col]
