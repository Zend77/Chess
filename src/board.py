from typing import Optional, List, Tuple
from piece import *
from const import *
from square import Square
from move import Move
from fen import FEN
from piece import Queen, Rook, Bishop, Knight

class Board:
    squares: List[List[Square]]
    last_move: Optional[Move]
    halfmove_clock: int
    next_player: str
    castling_rights: str
    en_passant: str
    fullmove_number: int

    def __init__(self):
        self.squares: List[List[Square]] = []
        self.last_move: Optional[Move] = None
        self.halfmove_clock: int = 0
        self.fullmove_number: int = 1
        self.next_player: str = 'white'
        self.castling_rights: str = 'KQkq'
        self.en_passant: str = '-'
        self._create()

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

        # Castling rights update
        self.update_castling_rights(piece, initial, final)

        # At the end of the move, increment fullmove_number if black just moved
        if self.next_player == 'black':
            self.fullmove_number += 1

    def _handle_en_passant(self, piece: Piece, initial: Square, final: Square) -> None:
        if isinstance(piece, Pawn):
            # Set en passant target if pawn moves two squares
            if abs(final.row - initial.row) == 2:
                col_letter = Square.ALPHACOLS[initial.col]
                row_num = str((initial.row + final.row) // 2 + 1)
                self.en_passant = f"{col_letter}{row_num}"
            else:
                self.en_passant = '-'
            # Handle en passant capture
            diff = final.col - initial.col
            if diff != 0 and self.squares[final.row][final.col].is_empty:
                self.squares[initial.row][initial.col + diff].piece = None
        else:
            self.en_passant = '-'

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
        if isinstance(piece, Pawn) and (final.row == 0 or final.row == 7):
            promo = None
            if promotion_piece:
                promo = promotion_piece
            elif self.last_move is not None and hasattr(self.last_move, "promotion") and self.last_move.promotion:
                color = piece.color
                p = self.last_move.promotion
                if p == 'q':
                    promo = Queen(color)
                elif p == 'r':
                    promo = Rook(color)
                elif p == 'b':
                    promo = Bishop(color)
                elif p == 'n':
                    promo = Knight(color)
            if promo:
                promo.moved = True
                self.squares[final.row][final.col].piece = promo

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

    def set_fen(self, fen: str) -> None:
        from fen import FEN
        FEN.load(self, fen)

    def update_castling_rights(self, piece: Piece, initial: Square, final: Square) -> None:
        # Remove castling rights if king or rook moves from their original squares, or rook is captured on original square
        rights = self.castling_rights.replace('-', '')
        
        # Store captured piece before move is made
        captured_piece = self.squares[final.row][final.col].piece

        # White king moves from original square (e1/row 7, col 4)
        if isinstance(piece, King) and piece.color == 'white' and initial.row == 7 and initial.col == 4:
            rights = rights.replace('K', '').replace('Q', '')
        # Black king moves from original square (e8/row 0, col 4)
        if isinstance(piece, King) and piece.color == 'black' and initial.row == 0 and initial.col == 4:
            rights = rights.replace('k', '').replace('q', '')
        # White rook moves from a1
        if isinstance(piece, Rook) and piece.color == 'white' and initial.row == 7 and initial.col == 0:
            rights = rights.replace('Q', '')
        # White rook moves from h1
        if isinstance(piece, Rook) and piece.color == 'white' and initial.row == 7 and initial.col == 7:
            rights = rights.replace('K', '')
        # Black rook moves from a8
        if isinstance(piece, Rook) and piece.color == 'black' and initial.row == 0 and initial.col == 0:
            rights = rights.replace('q', '')
        # Black rook moves from h8
        if isinstance(piece, Rook) and piece.color == 'black' and initial.row == 0 and initial.col == 7:
            rights = rights.replace('k', '')

        # Rook is captured on its original square
        if isinstance(captured_piece, Rook):
            if captured_piece.color == 'white':
                if final.row == 7 and final.col == 0:
                    rights = rights.replace('Q', '')
                if final.row == 7 and final.col == 7:
                    rights = rights.replace('K', '')
            if captured_piece.color == 'black':
                if final.row == 0 and final.col == 0:
                    rights = rights.replace('q', '')
                if final.row == 0 and final.col == 7:
                    rights = rights.replace('k', '')

        self.castling_rights = rights if rights else '-'

        self.castling_rights = rights if rights else '-'
