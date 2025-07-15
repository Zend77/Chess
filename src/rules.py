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
            start_row = 6 if piece.color == 'white' else 1  # Starting rank for pawns
            # Forward
            if Square.in_range(row + dir) and board.squares[row + dir][col].is_empty:
                moves.append(Move(Square(row, col), Square(row + dir, col)))
                # Double first move - only from starting rank
                if row == start_row and Square.in_range(row + dir * 2) and board.squares[row + dir * 2][col].is_empty:
                    moves.append(Move(Square(row, col), Square(row + dir * 2, col)))
            # Captures
            for dc in [-1, 1]:
                if Square.in_range(row + dir, col + dc):
                    sq = board.squares[row + dir][col + dc]
                    if sq.has_enemy_piece(piece.color):
                        moves.append(Move(Square(row, col), Square(row + dir, col + dc, sq.piece)))
                # En passant
                if row == (3 if piece.color == 'white' else 4) and Square.in_range(col + dc):
                    # Check if the target square matches the en passant square
                    target_col_letter = Square.get_alphacol(col + dc)
                    target_row_num = str(8 - (row + dir))  # Convert to chess notation
                    target_square = f"{target_col_letter}{target_row_num}"
                    
                    if board.en_passant == target_square:
                        # There should be an enemy pawn beside us
                        side_sq = board.squares[row][col + dc]
                        if side_sq.has_piece and isinstance(side_sq.piece, Pawn) and side_sq.piece.color != piece.color:
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
                    if sq.is_empty:
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
            if not piece.moved and board.castling_rights:
                back_row = 7 if piece.color == 'white' else 0
                
                # Check castling rights from board state
                can_castle_kingside = ('K' in board.castling_rights) if piece.color == 'white' else ('k' in board.castling_rights)
                can_castle_queenside = ('Q' in board.castling_rights) if piece.color == 'white' else ('q' in board.castling_rights)

                # King cannot castle if currently in check
                enemy_color = 'black' if piece.color == 'white' else 'white'
                if Rules.is_square_attacked_simple(board, row, col, enemy_color):
                    pass  # King is in check, no castling allowed
                else:
                    # King-side castle
                    if can_castle_kingside:
                        rook_sq = board.squares[back_row][7]
                        if isinstance(rook_sq.piece, Rook) and not rook_sq.piece.moved:
                            if all(board.squares[back_row][c].is_empty for c in [5, 6]):
                                # Check that king doesn't pass through or land on attacked squares
                                if (not Rules.is_square_attacked_simple(board, back_row, 5, enemy_color) and 
                                    not Rules.is_square_attacked_simple(board, back_row, 6, enemy_color)):
                                    moves.append(Move(Square(row, col), Square(back_row, 6)))

                    # Queen-side castle
                    if can_castle_queenside:
                        rook_sq = board.squares[back_row][0]
                        if isinstance(rook_sq.piece, Rook) and not rook_sq.piece.moved:
                            if all(board.squares[back_row][c].is_empty for c in [1, 2, 3]):
                                # Check that king doesn't pass through or land on attacked squares
                                if (not Rules.is_square_attacked_simple(board, back_row, 3, enemy_color) and 
                                    not Rules.is_square_attacked_simple(board, back_row, 2, enemy_color)):
                                    moves.append(Move(Square(row, col), Square(back_row, 2)))

        return moves

    @staticmethod
    def is_square_attacked(board, row, col, by_color):
        """Return True if the square (row, col) is attacked by any piece of by_color."""
        for r in range(8):
            for c in range(8):
                sq = board.squares[r][c]
                if sq.has_piece and sq.piece.color == by_color:
                    for move in sq.piece.get_moves(r, c, board):
                        if move.final.row == row and move.final.col == col:
                            return True
        return False

    @staticmethod
    def is_square_attacked_simple(board, row, col, by_color):
        """
        Return True if the square (row, col) is attacked by any piece of by_color.
        This version excludes castling moves to avoid recursion during castling checks.
        """
        for r in range(8):
            for c in range(8):
                sq = board.squares[r][c]
                if sq.has_piece and sq.piece.color == by_color:
                    # Get moves without castling to avoid recursion
                    if sq.piece.name == 'king':
                        # For king, only check basic king moves (no castling)
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if dr == 0 and dc == 0:
                                    continue
                                new_row, new_col = r + dr, c + dc
                                if (0 <= new_row <= 7 and 0 <= new_col <= 7 and
                                    new_row == row and new_col == col):
                                    return True
                    else:
                        # For other pieces, use normal move generation
                        for move in sq.piece.get_moves(r, c, board):
                            if move.final.row == row and move.final.col == col:
                                return True
        return False

    @staticmethod
    def find_king(board, color):
        for r in range(8):
            for c in range(8):
                sq = board.squares[r][c]
                if sq.has_piece and sq.piece.name == 'king' and sq.piece.color == color:
                    return r, c
        raise Exception("King not found!")

    @staticmethod
    def is_in_check(board, color):
        king_row, king_col = Rules.find_king(board, color)
        enemy_color = 'white' if color == 'black' else 'black'
        return Rules.is_square_attacked(board, king_row, king_col, by_color=enemy_color)

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