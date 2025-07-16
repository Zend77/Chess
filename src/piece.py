import os
from move import Move
from square import Square

class Piece:
    """
    Base class for all chess pieces. Defines common properties and methods
    that all pieces share, including movement tracking, textures, and basic move handling.
    """
    
    def __init__(self, name, color, value):
        self.name = name    # Piece type name (e.g., 'pawn', 'king', 'queen')
        self.color = color  # 'white' or 'black'
        self.value = value * (1 if color == 'white' else -1)  # Material value for evaluation
        self.moves = []     # List of currently valid moves for this piece
        self.moved = False  # Track if piece has moved (important for castling and pawn moves)
        self.texture = None # Path to piece image file
        self.texture_rect = None  # Pygame rectangle for rendering

    def set_texture(self, size=80, theme_name=None):
        """
        Set the piece's texture path based on theme and size.
        Supports both standard pieces and hello kitty theme.
        """
        if theme_name == "hello_kitty":
            folder_size = 120 if size > 80 else 80
            self.texture = os.path.join(
                f'assets/hello_kitty_images/hello_kitty_{folder_size}px/{self.color}_hello_kitty_{self.name}_{folder_size}px.png'
            )
        else:
            self.texture = os.path.join(
                f'assets/images/imgs-{size}px/{self.color}_{self.name}.png'
            )

    def add_move(self, move):
        """Add a valid move to this piece's move list."""
        self.moves.append(move)

    def clear_moves(self):
        """Clear all moves for this piece (called after move generation)."""
        self.moves = []

    def get_moves(self, row, col, board):
        """
        Generate all valid moves for this piece at the given position.
        To be overridden by subclasses with piece-specific movement rules.
        """
        return []

class Pawn(Piece):
    """
    Pawn piece with complex movement rules including two-square initial moves,
    diagonal captures, en passant, and promotion when reaching the opposite end.
    """
    
    def __init__(self, color):
        super().__init__('pawn', color, 1.0)
        # Pawns move in opposite directions based on color
        self.dir = -1 if color == 'white' else 1  # White moves up (negative), black moves down
        self.en_passant = False  # Track en passant availability

    def get_moves(self, row, col, board):
        """
        Generate pawn moves including forward movement, captures, en passant, and promotion.
        Pawns have the most complex movement rules of any piece.
        """
        moves = []
        start_row = 6 if self.color == 'white' else 1  # Starting rank for two-square moves
        promotion_row = 0 if self.color == 'white' else 7  # Rank where promotion occurs

        # Forward movement (one square)
        one_step = row + self.dir
        if Square.in_range(one_step) and board.squares[one_step][col].is_empty:
            # Check if this move reaches promotion rank
            if one_step == promotion_row:
                # Add all four promotion options
                for promo in ['q', 'r', 'b', 'n']:  # Queen, Rook, Bishop, Knight
                    moves.append(Move(Square(row, col), Square(one_step, col), promotion=promo))
            else:
                moves.append(Move(Square(row, col), Square(one_step, col)))
                
                # Two-square initial move from starting position
                two_step = row + 2 * self.dir
                if row == start_row and board.squares[two_step][col].is_empty:
                    moves.append(Move(Square(row, col), Square(two_step, col)))

        # Diagonal captures (left and right)
        for dc in [-1, 1]:
            r, c = one_step, col + dc
            if Square.in_range(r, c):
                target = board.squares[r][c]
                if target.has_enemy_piece(self.color):
                    # Regular capture
                    if r == promotion_row:
                        # Capture with promotion
                        for promo in ['q', 'r', 'b', 'n']:
                            moves.append(Move(Square(row, col), Square(r, c), captured=target.piece, promotion=promo))
                    else:
                        moves.append(Move(Square(row, col), Square(r, c), captured=target.piece))
                        
        # En passant capture - special pawn capture rule
        last_move = board.last_move
        if last_move:
            last_piece = board.squares[last_move.final.row][last_move.final.col].piece
            if isinstance(last_piece, Pawn):
                # Check if enemy pawn just moved two squares
                if abs(last_move.initial.row - last_move.final.row) == 2:
                    # Check if enemy pawn is adjacent to our pawn
                    if last_move.final.row == row and abs(last_move.final.col - col) == 1:
                        ep_row = row + self.dir
                        ep_col = last_move.final.col
                        moves.append(Move(Square(row, col), Square(ep_row, ep_col, last_piece)))
        return moves

class Knight(Piece):
    def __init__(self, color):
        super().__init__('knight', color, 3.0)

    def get_moves(self, row, col, board):
        offsets = [(-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)]
        moves = []
        for dr, dc in offsets:
            r, c = row + dr, col + dc
            if Square.in_range(r, c):
                dest_square = board.squares[r][c]
                if dest_square.is_empty_or_enemy(self.color):
                    moves.append(Move(Square(row, col), Square(r, c, dest_square.piece)))
        return moves

class Bishop(Piece):
    def __init__(self, color):
        super().__init__('bishop', color, 3.001)

    def get_moves(self, row, col, board):
        return self._slide_moves(row, col, board, [(-1, -1), (-1, 1), (1, 1), (1, -1)])

    def _slide_moves(self, row, col, board, increments):
        moves = []
        for dr, dc in increments:
            r, c = row + dr, col + dc
            while Square.in_range(r, c):
                dest_square = board.squares[r][c]
                if dest_square.is_empty:
                    moves.append(Move(Square(row, col), Square(r, c)))
                elif dest_square.has_enemy_piece(self.color):
                    moves.append(Move(Square(row, col), Square(r, c, dest_square.piece)))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves

class Rook(Piece):
    def __init__(self, color):
        super().__init__('rook', color, 5.0)

    def get_moves(self, row, col, board):
        return self._slide_moves(row, col, board, [(-1, 0), (1, 0), (0, -1), (0, 1)])

    def _slide_moves(self, row, col, board, increments):
        moves = []
        for dr, dc in increments:
            r, c = row + dr, col + dc
            while Square.in_range(r, c):
                dest_square = board.squares[r][c]
                if dest_square.is_empty:
                    moves.append(Move(Square(row, col), Square(r, c)))
                elif dest_square.has_enemy_piece(self.color):
                    moves.append(Move(Square(row, col), Square(r, c, dest_square.piece)))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves

class Queen(Piece):
    def __init__(self, color):
        super().__init__('queen', color, 9.0)

    def get_moves(self, row, col, board):
        return self._slide_moves(row, col, board, [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)])

    def _slide_moves(self, row, col, board, increments):
        moves = []
        for dr, dc in increments:
            r, c = row + dr, col + dc
            while Square.in_range(r, c):
                dest_square = board.squares[r][c]
                if dest_square.is_empty:
                    moves.append(Move(Square(row, col), Square(r, c)))
                elif dest_square.has_enemy_piece(self.color):
                    moves.append(Move(Square(row, col), Square(r, c, dest_square.piece)))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves

class King(Piece):
    def __init__(self, color):
        super().__init__('king', color, 10000.0)

    def get_moves(self, row, col, board):
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        moves = []

        # Normal adjacent moves
        for dr, dc in offsets:
            r, c = row + dr, col + dc
            if Square.in_range(r, c):
                dest_square = board.squares[r][c]
                if dest_square.is_empty_or_enemy(self.color):
                    moves.append(Move(Square(row, col), Square(r, c, dest_square.piece)))

        # Castling candidates (legal castling checks)
        if not self.moved and board.castling_rights:
            back_row = 7 if self.color == 'white' else 0
            
            # Check castling rights from board state
            can_castle_kingside = ('K' in board.castling_rights) if self.color == 'white' else ('k' in board.castling_rights)
            can_castle_queenside = ('Q' in board.castling_rights) if self.color == 'white' else ('q' in board.castling_rights)

            # King cannot castle if currently in check
            enemy_color = 'black' if self.color == 'white' else 'white'
            from rules import Rules
            if Rules.is_square_attacked_simple(board, row, col, enemy_color):
                pass  # King is in check, no castling allowed
            else:
                # King-side
                if can_castle_kingside:
                    rook_sq = board.squares[back_row][7]
                    if isinstance(rook_sq.piece, Rook) and not rook_sq.piece.moved:
                        if all(board.squares[back_row][c].is_empty for c in [5, 6]):
                            # Check that king doesn't pass through or land on attacked squares
                            if (not Rules.is_square_attacked_simple(board, back_row, 5, enemy_color) and 
                                not Rules.is_square_attacked_simple(board, back_row, 6, enemy_color)):
                                moves.append(Move(Square(row, col), Square(back_row, 6)))

                # Queen-side
                if can_castle_queenside:
                    rook_sq = board.squares[back_row][0]
                    if isinstance(rook_sq.piece, Rook) and not rook_sq.piece.moved:
                        if all(board.squares[back_row][c].is_empty for c in [1, 2, 3]):
                            # Check that king doesn't pass through or land on attacked squares
                            if (not Rules.is_square_attacked_simple(board, back_row, 3, enemy_color) and 
                                not Rules.is_square_attacked_simple(board, back_row, 2, enemy_color)):
                                moves.append(Move(Square(row, col), Square(back_row, 2)))

        return moves
