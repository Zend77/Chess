from piece import *
from const import *
from square import Square
from move import Move
from sound import Sound

class Board:
    def __init__(self):
        self.squares = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.last_move = None
        self.halfmove_clock = 0
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move, surface=None, promotion_piece=None):
        initial = move.initial
        final = move.final
        captured_piece = self.squares[final.row][final.col].piece
        
        # 50 move draw
        if isinstance(piece, Pawn) or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1


        # En passant capture
        en_passant_empty = self.squares[final.row][final.col].is_empty()
        if isinstance(piece, Pawn):
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                self.squares[initial.row][initial.col + diff].piece = None

        # Move piece
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece
        piece.moved = True

        # Handle castling
        if isinstance(piece, King) and abs(initial.col - final.col) == 2:
            rook_col = 0 if final.col < initial.col else 7
            rook = self.squares[initial.row][rook_col].piece
            rook_final_col = 3 if final.col < initial.col else 5
            self.squares[initial.row][rook_col].piece = None
            self.squares[initial.row][rook_final_col].piece = rook
            rook.moved = True

        # Handle pawn promotion
        if isinstance(piece, Pawn) and (final.row == 0 or final.row == 7) and promotion_piece:
            promotion_piece.moved = True
            self.squares[final.row][final.col].piece = promotion_piece

        # Clear valid moves
        piece.clear_moves()

        # Update last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves

    def in_check(self, piece, move):
        initial_square = self.squares[move.initial.row][move.initial.col]
        final_square = self.squares[move.final.row][move.final.col]
        captured_piece = final_square.piece

        # Special case: en passant
        en_passant = (
            isinstance(piece, Pawn) and
            abs(move.final.col - move.initial.col) == 1 and
            initial_square.row != move.final.row and
            final_square.is_empty()
        )

        captured_en_passant = None
        if en_passant:
            captured_square = self.squares[move.initial.row][move.final.col]
            captured_en_passant = captured_square.piece
            captured_square.piece = None

        # Simulate move
        final_square.piece = piece
        initial_square.piece = None

        # Special case: castling
        if isinstance(piece, King) and abs(move.final.col - move.initial.col) == 2:
            step = 1 if move.final.col > move.initial.col else -1
            for intermediate_col in range(move.initial.col, move.final.col + step, step):
                temp_square = self.squares[move.initial.row][intermediate_col]
                original_piece = temp_square.piece
                temp_square.piece = piece

                if self.in_check_king(piece.color):
                    # Undo castling simulation
                    temp_square.piece = original_piece
                    initial_square.piece = piece
                    final_square.piece = captured_piece
                    if en_passant:
                        captured_square.piece = captured_en_passant
                    return True

                temp_square.piece = original_piece

            # No check in any intermediate square
            initial_square.piece = piece
            final_square.piece = captured_piece
            if en_passant:
                captured_square.piece = captured_en_passant
            return False

        # Standard check detection
        king_in_check = self.in_check_king(piece.color)

        # Undo simulated move
        initial_square.piece = piece
        final_square.piece = captured_piece
        if en_passant:
            captured_square.piece = captured_en_passant

        return king_in_check


    def in_check_king(self, color):
        king_row, king_col = -1, -1
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece() and square.piece.name == 'king' and square.piece.color == color: # type: ignore
                    king_row, king_col = row, col

        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_enemy_piece(color): # type: ignore
                    enemy_piece = square.piece # type: ignore
                    self.calc_moves(enemy_piece, row, col, filter_checks=False)
                    for move in enemy_piece.moves:
                        if move.final.row == king_row and move.final.col == king_col:
                            return True
        return False

    def is_checkmate(self, color):
        if not self.in_check_king(color):
            return False
        return not self.player_has_moves(color)

    def is_stalemate(self, color):
        if self.in_check_king(color):
            return False
        return not self.player_has_moves(color)
    
    def is_dead_position(self):
        pieces = []
        for row in self.squares:
            for square in row:
                if square.has_piece():
                    pieces.append(square.piece)
        if len(pieces) == 2:  # King vs King
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
    
    def is_fifty_move_rule(self):
        return self.halfmove_clock >= 100


    def player_has_moves(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece() and square.piece.color == color: # type: ignore
                    self.calc_moves(square.piece, row, col, filter_checks=True) # type: ignore
                    if square.piece.moves: # type: ignore
                        return True
        return False

    def calc_moves(self, piece, row, col, filter_checks=True):
        piece.clear_moves()

        # Get possible directions from the piece
        directions = piece.get_directions(row, col, self)

        # Add moves, filtering out illegal ones if filter_checks is True
        for move in directions:
            if filter_checks and self.in_check(piece, move):
                continue
            piece.add_move(move)
            
    def evaluate_material(self):
        white_score = 0
        black_score = 0
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece() and square.piece.color == 'white' and square.piece.value < 10: # type: ignore
                    white_score += square.piece.value  # type: ignore
                elif square.has_piece() and square.piece.color == 'black' and square.piece.value > -10: # type: ignore
                    black_score += square.piece.value # type: ignore
                
        return white_score, black_score

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col) # type: ignore

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color)) # type: ignore

        placements = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_class in enumerate(placements):
            self.squares[row_other][col] = Square(row_other, col, piece_class(color)) # type: ignore
