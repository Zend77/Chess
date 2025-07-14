from typing import Optional, Any


class Square:
    ALPHACOLS: dict[int, str] = {i: chr(ord('a') + i) for i in range(8)}

    def __init__(self, row: int, col: int, piece: Optional[Any] = None):
        self.row: int = row
        self.col: int = col
        self.piece: Optional[Any] = piece
        self.alphacol: str = self.ALPHACOLS[col]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Square):
            return NotImplemented
        return self.row == other.row and self.col == other.col

    @property
    def has_piece(self) -> bool:
        return self.piece is not None

    @property
    def is_empty(self) -> bool:
        return not self.has_piece

    def has_team_piece(self, color: str) -> bool:
        return self.piece is not None and self.piece.color == color

    def has_enemy_piece(self, color: str) -> bool:
        return self.piece is not None and self.piece.color != color

    def is_empty_or_enemy(self, color: str) -> bool:
        return self.is_empty or self.has_enemy_piece(color)

    @staticmethod
    def in_range(*args: int) -> bool:
        return all(0 <= arg <= 7 for arg in args)

    @classmethod
    def get_alphacol(cls, col: int) -> str:
        return cls.ALPHACOLS[col]
