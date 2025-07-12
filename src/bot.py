import random
from const import *
from move import Move
from square import Square

class Bot:
    
    def __init__(self, color):
        self.color = 'black'
        
    def bot_move(self, board):
        all_moves = []
        
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if square.has_piece() and square.piece.color == self.color:
                    piece = square.piece
                    board.calc_moves(piece, row, col, filter_checks=True)
                    for move in piece.moves:
                        all_moves.append((piece, move))
        
        if not all_moves:
            return None, None
    
        return random.choice(all_moves)
    