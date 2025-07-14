import random
from typing import Optional, Tuple
from const import *
from move import Move
from square import Square
from piece import Piece

class AI:
    color: Optional[str]

    def __init__(self, color: Optional[str]):
        self.color = color

    def random_move(self, board) -> Tuple[Optional[Piece], Optional[Move]]:
        all_moves: list[tuple[Piece, Move]] = []
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if square.has_piece and square.piece.color == self.color:
                    piece: Piece = square.piece
                    board.calc_moves(piece, row, col, filter_checks=True)
                    for move in piece.moves:
                        all_moves.append((piece, move))
        if not all_moves:
            return None, None
        return random.choice(all_moves)



