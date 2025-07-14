from typing import Optional, List, Tuple
from piece import *
from const import *
from square import Square
from move import Move
from sound import Sound

class Board:
    squares: List[List[Square]]
    last_move: Optional[Move]
    halfmove_clock: int

    def __init__(self):
        self.squares: List[List[Square]] = []
        self.last_move: Optional[Move] = None
        self.halfmove_clock: int = 0
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece: Piece, move: Move, surface=None, promotion_piece: Optional[Piece]=None) -> None:
        initial = move.initial
        final = move.final
        captured_piece: Optional[Piece] = self.squares[final.row][final.col].piece

        if isinstance(piece, Pawn) or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        self._handle_en_passant(piece, initial, final)
        self._move_piece(piece, initial, final)
        self._handle_castling(piece, initial, final)
        self._handle_promotion(piece, final, promotion_piece)

        piece.moved = True
        piece.clear_moves()
        self.last_move = move

    def _handle_en_passant(self, piece: Piece, initial: Square, final: Square) -> None:
        if isinstance(piece, Pawn):
            diff = final.col - initial.col
            if diff != 0 and self.squares[final.row][final.col].is_empty:
                self.squares[initial.row][initial.col + diff].piece = None

    def _move_piece(self, piece: Piece, initial: Square, final: Square) -> None:
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

    def _handle_castling(self, piece: Piece, initial: Square, final: Square) -> None:
        if isinstance(piece, King) and abs(initial.col - final.col) == 2:
            rook_col = 0 if final.col < initial.col else 7
            rook = self.squares[initial.row][rook_col].piece
            rook_final_col = 3 if final.col < initial.col else 5
            self.squares[initial.row][rook_col].piece = None
            self.squares[initial.row][rook_final_col].piece = rook
            if rook:
                rook.moved = True

    def _handle_promotion(self, piece: Piece, final: Square, promotion_piece: Optional[Piece]) -> None:
        if isinstance(piece, Pawn) and (final.row == 0 or final.row == 7) and promotion_piece:
            promotion_piece.moved = True
            self.squares[final.row][final.col].piece = promotion_piece

    def valid_move(self, piece: Piece, move: Move) -> bool:
        return move in piece.moves

    def in_check(self, piece: Piece, move: Move) -> bool:
        initial_square = self.squares[move.initial.row][move.initial.col]
        final_square = self.squares[move.final.row][move.final.col]
        captured_piece = final_square.piece

        en_passant = (
            isinstance(piece, Pawn) and
            abs(move.final.col - move.initial.col) == 1 and
            initial_square.row != move.final.row and
            final_square.is_empty
        )

        captured_en_passant: Optional[Piece] = None
        if en_passant:
            captured_square = self.squares[move.initial.row][move.final.col]
            captured_en_passant = captured_square.piece
            captured_square.piece = None

        final_square.piece = piece
        initial_square.piece = None

        if isinstance(piece, King) and abs(move.final.col - move.initial.col) == 2:
            step = 1 if move.final.col > move.initial.col else -1
            for intermediate_col in range(move.initial.col, move.final.col + step, step):
                temp_square = self.squares[move.initial.row][intermediate_col]
                original_piece = temp_square.piece
                temp_square.piece = piece

                if self.in_check_king(piece.color):
                    temp_square.piece = original_piece
                    initial_square.piece = piece
                    final_square.piece = captured_piece
                    if en_passant:
                        captured_square.piece = captured_en_passant
                    return True

                temp_square.piece = original_piece

            initial_square.piece = piece
            final_square.piece = captured_piece
            if en_passant:
                captured_square.piece = captured_en_passant
            return False

        king_in_check = self.in_check_king(piece.color)

        initial_square.piece = piece
        final_square.piece = captured_piece
        if en_passant:
            captured_square.piece = captured_en_passant

        return king_in_check

    def in_check_king(self, color: str) -> bool:
        king_row, king_col = -1, -1
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece and square.piece and square.piece.name == 'king' and square.piece.color == color:
                    king_row, king_col = row, col

        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_enemy_piece(color):
                    enemy_piece = square.piece
                    if enemy_piece:
                        self.calc_moves(enemy_piece, row, col, filter_checks=False)
                        for move in enemy_piece.moves:
                            if move.final.row == king_row and move.final.col == king_col:
                                return True
        return False

    def is_checkmate(self, color: str) -> bool:
        if not self.in_check_king(color):
            return False
        return not self.player_has_moves(color)

    def is_stalemate(self, color: str) -> bool:
        if self.in_check_king(color):
            return False
        return not self.player_has_moves(color)
    
    def is_dead_position(self) -> bool:
        pieces: List[Piece] = []
        for row in self.squares:
            for square in row:
                if square.has_piece and square.piece:
                    pieces.append(square.piece)
        if len(pieces) == 2:
            return True
        if len(pieces) == 3:
            piece_names = [p.name for p in pieces if p.name != 'king']
            if 'bishop' in piece_names or 'knight' in piece_names:
                return True
        if len(pieces) == 4:
            bishops = [p for p in pieces if p.name == 'bishop']
            if len(bishops) == 2 and bishops[0].color != bishops[1].color:
                return True
        return False
    
    def is_fifty_move_rule(self) -> bool:
        return self.halfmove_clock >= 100

    def player_has_moves(self, color: str) -> bool:
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece and square.piece and square.piece.color == color:
                    self.calc_moves(square.piece, row, col, filter_checks=True)
                    if square.piece.moves:
                        return True
        return False

    def calc_moves(self, piece: Piece, row: int, col: int, filter_checks: bool=True) -> None:
        piece.clear_moves()
        moves = piece.get_moves(row, col, self)
        for move in moves:
            if filter_checks and self.in_check(piece, move):
                continue
            piece.add_move(move)
            
    def evaluate_material(self) -> Tuple[float, float]:
        white_score = 0.0
        black_score = 0.0
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece and square.piece:
                    if square.piece.color == 'white' and square.piece.value < 10:
                        white_score += square.piece.value
                    elif square.piece.color == 'black' and square.piece.value > -10:
                        black_score += square.piece.value
        return white_score, black_score

    def _create(self) -> None:
        self.squares = [[Square(row, col) for col in range(COLS)] for row in range(ROWS)]

    def _add_pieces(self, color: str) -> None:
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))
        placements = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_class in enumerate(placements):
            self.squares[row_other][col] = Square(row_other, col, piece_class(color))
