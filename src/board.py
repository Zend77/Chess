from const import *
from piece import *
from move import Move
from square import Square
from sound import Sound
from rules import Rules

class Board:
    def __init__(self):
        self.squares = [[Square(row, col) for col in range(COLS)] for row in range(ROWS)]
        self.last_move = None
        self._add_pieces("white")
        self._add_pieces("black")

    def move(self, piece, move, surface=None, testing=False):
        initial = move.initial
        final = move.final

        target_piece = self.squares[final.row][final.col].piece

        # Handle en passant
        if isinstance(piece, Pawn):
            if initial.col != final.col and target_piece is None:
                captured_pawn_row = initial.row
                self.squares[captured_pawn_row][final.col].piece = None

        # Handle castling
        if isinstance(piece, King) and abs(initial.col - final.col) == 2:
            rook_start_col = 0 if final.col < initial.col else 7
            rook_end_col = 3 if final.col < initial.col else 5
            rook = self.squares[initial.row][rook_start_col].piece
            self.squares[initial.row][rook_start_col].piece = None
            self.squares[initial.row][rook_end_col].piece = rook
            if rook:
                rook.moved = True

        # Update en passant flags
        for r in self.squares:
            for sq in r:
                if isinstance(sq.piece, Pawn):
                    sq.piece.en_passant = False

        if isinstance(piece, Pawn) and abs(final.row - initial.row) == 2:
            piece.en_passant = True

        # Perform the move
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        # Mark as moved
        piece.moved = True

        # Set last move
        self.last_move = move

        # Clear the piece's move list
        piece.clear_moves()

    def valid_move(self, piece, move):
        return move in piece.moves

    def calc_moves(self, piece, row, col, bool=True):
        if bool:
            piece.moves = Rules.filter_legal_moves(self, piece, row, col)
        else:
            piece.moves = Rules.generate_pseudo_legal_moves(self, piece, row, col)

    def in_check(self, piece, move, surface=None):
        return Rules.is_in_check(self, piece.color)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == "white" else (1, 0)
        for col in range(COLS):
            self.squares[row_pawn][col].piece = Pawn(color)
        self.squares[row_other][0].piece = Rook(color)
        self.squares[row_other][7].piece = Rook(color)
        self.squares[row_other][1].piece = Knight(color)
        self.squares[row_other][6].piece = Knight(color)
        self.squares[row_other][2].piece = Bishop(color)
        self.squares[row_other][5].piece = Bishop(color)
        self.squares[row_other][3].piece = Queen(color)
        self.squares[row_other][4].piece = King(color)