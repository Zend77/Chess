from move import Move
from square import Square
from piece import *

class Rules:

    @staticmethod
    def generate_pseudo_legal_moves(board, piece, row, col):
        moves = []

        def add_move_if_valid(r, c):
            if Square.in_range(r, c):
                sq = board.squares[r][c]
                if sq.is_empty_or_enemy(piece.color):
                    moves.append(Move(Square(row, col), Square(r, c, sq.piece)))

        # Pawns
        if isinstance(piece, Pawn):
            dir = piece.dir
            # Forward
            if Square.in_range(row + dir) and board.squares[row + dir][col].is_empty():
                moves.append(Move(Square(row, col), Square(row + dir, col)))
                # Double first move
                if not piece.moved and board.squares[row + dir * 2][col].is_empty():
                    moves.append(Move(Square(row, col), Square(row + dir * 2, col)))
            # Captures
            for dc in [-1, 1]:
                if Square.in_range(row + dir, col + dc):
                    sq = board.squares[row + dir][col + dc]
                    if sq.has_enemy_piece(piece.color):
                        moves.append(Move(Square(row, col), Square(row + dir, col + dc, sq.piece)))
                # En passant
                if row == (3 if piece.color == 'white' else 4):
                    side_sq = board.squares[row][col + dc] if Square.in_range(col + dc) else None
                    if side_sq and isinstance(side_sq.piece, Pawn) and side_sq.piece.color != piece.color and side_sq.piece.en_passant:
                        moves.append(Move(Square(row, col), Square(row + dir, col + dc, side_sq.piece)))

        # Knights
        elif isinstance(piece, Knight):
            for dr, dc in [(-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)]:
                add_move_if_valid(row + dr, col + dc)

        # Bishops, Rooks, Queens (sliding pieces)
        elif isinstance(piece, Bishop) or isinstance(piece, Rook) or isinstance(piece, Queen):
            directions = []
            if isinstance(piece, Bishop) or isinstance(piece, Queen):
                directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            if isinstance(piece, Rook) or isinstance(piece, Queen):
                directions += [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                r, c = row + dr, col + dc
                while Square.in_range(r, c):
                    sq = board.squares[r][c]
                    if sq.is_empty():
                        moves.append(Move(Square(row, col), Square(r, c)))
                    elif sq.has_enemy_piece(piece.color):
                        moves.append(Move(Square(row, col), Square(r, c, sq.piece)))
                        break
                    else:
                        break
                    r += dr
                    c += dc

        # Kings
        elif isinstance(piece, King):
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    add_move_if_valid(row + dr, col + dc)

            # Castling
            if not piece.moved:
                back_row = 7 if piece.color == 'white' else 0

                # King-side castle
                rook_sq = board.squares[back_row][7]
                if isinstance(rook_sq.piece, Rook) and not rook_sq.piece.moved:
                    if all(board.squares[back_row][c].is_empty() for c in [5, 6]):
                        moves.append(Move(Square(row, col), Square(back_row, 6)))

                # Queen-side castle
                rook_sq = board.squares[back_row][0]
                if isinstance(rook_sq.piece, Rook) and not rook_sq.piece.moved:
                    if all(board.squares[back_row][c].is_empty() for c in [1, 2, 3]):
                        moves.append(Move(Square(row, col), Square(back_row, 2)))

        return moves

    @staticmethod
    def is_in_check(board, color):
        king_row, king_col = Rules.find_king(board, color)
        return Rules.is_square_attacked(board, king_row, king_col, by_color=('white' if color == 'black' else 'black'))

    @staticmethod
    def is_square_attacked(board, row, col, by_color):
        for r in range(8):
            for c in range(8):
                sq = board.squares[r][c]
                if sq.has_piece() and sq.piece.color == by_color:
                    for move in Rules.generate_pseudo_legal_moves(board, sq.piece, r, c):
                        if move.final.row == row and move.final.col == col:
                            return True
        return False

    @staticmethod
    def find_king(board, color):
        for r in range(8):
            for c in range(8):
                sq = board.squares[r][c]
                if sq.has_piece() and sq.piece.name == 'king' and sq.piece.color == color:
                    return r, c
        raise Exception("King not found!")

    @staticmethod
    def filter_legal_moves(board, piece, row, col):
        legal_moves = []
        for move in Rules.generate_pseudo_legal_moves(board, piece, row, col):
            captured = board.squares[move.final.row][move.final.col].piece
            board.squares[move.initial.row][move.initial.col].piece = None
            board.squares[move.final.row][move.final.col].piece = piece

            if not Rules.is_in_check(board, piece.color):
                legal_moves.append(move)

            board.squares[move.initial.row][move.initial.col].piece = piece
            board.squares[move.final.row][move.final.col].piece = captured

        return legal_moves