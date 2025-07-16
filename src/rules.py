from move import Move
from square import Square
from piece import *

class Rules:
    """
    Contains all chess rules logic including move generation, check detection,
    and legal move filtering. Handles complex rules like castling, en passant,
    and ensures moves don't leave the king in check.
    """

    @staticmethod
    def generate_pseudo_legal_moves(board, piece, row, col):
        """
        Generate all pseudo-legal moves for a piece (moves that follow basic piece rules
        but may leave the king in check). These moves are later filtered for legality.
        """
        moves = []

        def add_move_if_valid(r, c):
            """Helper function to add a move if the target square is valid and not occupied by own piece."""
            if Square.in_range(r, c):
                sq = board.squares[r][c]
                if sq.is_empty_or_enemy(piece.color):
                    moves.append(Move(Square(row, col), Square(r, c, sq.piece)))

        # Pawn movement rules - most complex piece due to special moves
        if isinstance(piece, Pawn):
            dir = piece.dir  # 1 for white (moving up), -1 for black (moving down)
            start_row = 6 if piece.color == 'white' else 1  # Starting rank for two-square moves
            
            # Forward movement (one square)
            if Square.in_range(row + dir) and board.squares[row + dir][col].is_empty:
                moves.append(Move(Square(row, col), Square(row + dir, col)))
                # Two-square initial move from starting position
                if row == start_row and Square.in_range(row + dir * 2) and board.squares[row + dir * 2][col].is_empty:
                    moves.append(Move(Square(row, col), Square(row + dir * 2, col)))
            
            # Diagonal captures
            for dc in [-1, 1]:  # Left and right diagonals
                if Square.in_range(row + dir, col + dc):
                    sq = board.squares[row + dir][col + dc]
                    if sq.has_enemy_piece(piece.color):
                        moves.append(Move(Square(row, col), Square(row + dir, col + dc, sq.piece)))
                
                # En passant capture - pawn captures diagonally to empty square
                if row == (3 if piece.color == 'white' else 4) and Square.in_range(col + dc):
                    # Calculate target square in algebraic notation
                    target_col_letter = Square.get_alphacol(col + dc)
                    target_row_num = str(8 - (row + dir))  # Convert array index to chess rank
                    target_square = f"{target_col_letter}{target_row_num}"
                    
                    # Check if this matches the en passant target square
                    if board.en_passant == target_square:
                        # Verify there's an enemy pawn next to us to capture
                        side_sq = board.squares[row][col + dc]
                        if side_sq.has_piece and isinstance(side_sq.piece, Pawn) and side_sq.piece.color != piece.color:
                            moves.append(Move(Square(row, col), Square(row + dir, col + dc, side_sq.piece)))

        # Knight moves - L-shaped jumps to all 8 possible positions
        elif isinstance(piece, Knight):
            knight_moves = [(-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)]
            for dr, dc in knight_moves:
                add_move_if_valid(row + dr, col + dc)

        # Sliding pieces: Bishops, Rooks, Queens
        elif isinstance(piece, Bishop) or isinstance(piece, Rook) or isinstance(piece, Queen):
            directions = []
            # Bishops and Queens move diagonally
            if isinstance(piece, Bishop) or isinstance(piece, Queen):
                directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Four diagonal directions
            # Rooks and Queens move orthogonally
            if isinstance(piece, Rook) or isinstance(piece, Queen):
                directions += [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Four cardinal directions
            
            # For each direction, slide until hitting a piece or board edge
            for dr, dc in directions:
                r, c = row + dr, col + dc
                while Square.in_range(r, c):
                    sq = board.squares[r][c]
                    if sq.is_empty:
                        moves.append(Move(Square(row, col), Square(r, c)))
                    elif sq.has_enemy_piece(piece.color):
                        # Can capture enemy piece, but can't continue sliding
                        moves.append(Move(Square(row, col), Square(r, c, sq.piece)))
                        break
                    else:
                        # Blocked by own piece
                        break
                    r += dr
                    c += dc

        # King moves - one square in any direction plus castling
        elif isinstance(piece, King):
            # Regular king moves - one square in any direction
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue  # Skip the center (no move)
                    add_move_if_valid(row + dr, col + dc)

            # Castling - special king move under specific conditions
            if not piece.moved and board.castling_rights:
                back_row = 7 if piece.color == 'white' else 0
                
                # Check castling rights from board FEN notation
                can_castle_kingside = ('K' in board.castling_rights) if piece.color == 'white' else ('k' in board.castling_rights)
                can_castle_queenside = ('Q' in board.castling_rights) if piece.color == 'white' else ('q' in board.castling_rights)

                # King cannot castle while in check
                enemy_color = 'black' if piece.color == 'white' else 'white'
                if Rules.is_square_attacked_simple(board, row, col, enemy_color):
                    pass  # King is in check, no castling allowed
                else:
                    # Kingside castling (short castle)
                    if can_castle_kingside:
                        rook_sq = board.squares[back_row][7]
                        if isinstance(rook_sq.piece, Rook) and not rook_sq.piece.moved:
                            # Check that squares between king and rook are empty
                            if all(board.squares[back_row][c].is_empty for c in [5, 6]):
                                # King cannot pass through or land on attacked squares
                                if (not Rules.is_square_attacked_simple(board, back_row, 5, enemy_color) and 
                                    not Rules.is_square_attacked_simple(board, back_row, 6, enemy_color)):
                                    moves.append(Move(Square(row, col), Square(back_row, 6)))

                    # Queenside castling (long castle)
                    if can_castle_queenside:
                        rook_sq = board.squares[back_row][0]
                        if isinstance(rook_sq.piece, Rook) and not rook_sq.piece.moved:
                            # Check that squares between king and rook are empty
                            if all(board.squares[back_row][c].is_empty for c in [1, 2, 3]):
                                # King cannot pass through or land on attacked squares
                                if (not Rules.is_square_attacked_simple(board, back_row, 3, enemy_color) and 
                                    not Rules.is_square_attacked_simple(board, back_row, 2, enemy_color)):
                                    moves.append(Move(Square(row, col), Square(back_row, 2)))

        return moves

    @staticmethod
    def is_square_attacked(board, row, col, by_color):
        """
        Check if a square is under attack by any piece of the specified color.
        Used for check detection and castling validation.
        """
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
        Simplified version of is_square_attacked that excludes castling moves.
        Used during castling validation to avoid infinite recursion when checking
        if squares are attacked during the castling process.
        """
        for r in range(8):
            for c in range(8):
                sq = board.squares[r][c]
                if sq.has_piece and sq.piece.color == by_color:
                    # Special handling for kings to avoid castling recursion
                    if sq.piece.name == 'king':
                        # Only check basic king moves (one square in any direction)
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
        """Locate the king of the specified color on the board."""
        for r in range(8):
            for c in range(8):
                sq = board.squares[r][c]
                if sq.has_piece and sq.piece.name == 'king' and sq.piece.color == color:
                    return r, c
        raise Exception("King not found!")

    @staticmethod
    def is_in_check(board, color):
        """Check if the king of the specified color is currently in check."""
        king_row, king_col = Rules.find_king(board, color)
        enemy_color = 'white' if color == 'black' else 'black'
        return Rules.is_square_attacked(board, king_row, king_col, by_color=enemy_color)

    @staticmethod
    def filter_legal_moves(board, piece, row, col):
        """
        Filter pseudo-legal moves to only include truly legal moves.
        A move is legal if it doesn't leave the player's own king in check.
        This involves making each move temporarily and checking for check.
        """
        legal_moves = []
        for move in Rules.generate_pseudo_legal_moves(board, piece, row, col):
            # Temporarily make the move
            captured = board.squares[move.final.row][move.final.col].piece
            board.squares[move.initial.row][move.initial.col].piece = None
            board.squares[move.final.row][move.final.col].piece = piece

            # Check if this move leaves our king in check
            if not Rules.is_in_check(board, piece.color):
                legal_moves.append(move)

            # Restore the board state
            board.squares[move.initial.row][move.initial.col].piece = piece
            board.squares[move.final.row][move.final.col].piece = captured

        return legal_moves