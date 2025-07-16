import random
from typing import Optional, Tuple
from const import *
from move import Move
from square import Square
from piece import Piece

class AI:
    """
    Simple AI player that makes random legal moves.
    This is a basic implementation for testing and casual play.
    Could be expanded with more sophisticated algorithms like minimax or neural networks.
    """
    color: Optional[str]

    def __init__(self, color: Optional[str]):
        self.color = color  # 'white' or 'black' - which side the AI plays

    def random_move(self, board) -> Tuple[Optional[Piece], Optional[Move]]:
        """
        Select a random legal move from all available moves.
        This provides unpredictable but legal gameplay for casual opponents.
        
        Args:
            board: Current board state
            
        Returns:
            Tuple of (piece to move, move to make) or (None, None) if no moves available
        """
        all_moves: list[tuple[Piece, Move]] = []
        
        # Collect all legal moves for AI's pieces
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if square.has_piece and square.piece.color == self.color:
                    piece: Piece = square.piece
                    # Calculate legal moves (filtering out moves that leave king in check)
                    board.calc_moves(piece, row, col, filter_checks=True)
                    for move in piece.moves:
                        all_moves.append((piece, move))
        
        # Return a random legal move, or None if no moves available (stalemate/checkmate)
        if not all_moves:
            return None, None
        return random.choice(all_moves)



