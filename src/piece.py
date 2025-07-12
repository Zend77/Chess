import os
from move import Move
from square import Square

class Piece:
    def __init__(self, name, color, value):
        self.name = name
        self.color = color
        self.value = value * (1 if color == 'white' else -1)
        self.moves = []
        self.moved = False
        self.texture = None
        self.texture_rect = None

    def set_texture(self, size=80, theme_name=None):
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
        self.moves.append(move)

    def clear_moves(self):
        self.moves = []

class Pawn(Piece):
    def __init__(self, color):
        super().__init__('pawn', color, 1.0)
        self.dir = -1 if color == 'white' else 1
        self.en_passant = False

    def get_directions(self, row, col, board):
        moves = []
        start_row = 6 if self.color == 'white' else 1

        # Forward move
        one_step = row + self.dir
        if Square.in_range(one_step) and board.squares[one_step][col].is_empty():
            moves.append(Move(Square(row, col), Square(one_step, col)))

            # Two steps from start position
            two_step = row + 2 * self.dir
            if row == start_row and board.squares[two_step][col].is_empty():
                moves.append(Move(Square(row, col), Square(two_step, col)))

        # Captures
        for dc in [-1, 1]:
            r, c = one_step, col + dc
            if Square.in_range(r, c):
                target = board.squares[r][c]
                if target.has_enemy_piece(self.color):
                    moves.append(Move(Square(row, col), Square(r, c, target.piece)))

        # En passant captures
        # (Logic for en passant will go here if needed)

        return moves

class Knight(Piece):
    def __init__(self, color):
        super().__init__('knight', color, 3.0)

    def get_directions(self, row, col, board):
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

    def get_directions(self, row, col, board):
        return self._slide_directions(row, col, board, [(-1, -1), (-1, 1), (1, -1), (1, 1)]) # type: ignore

class Rook(Piece):
    def __init__(self, color):
        super().__init__('rook', color, 5.0)

    def get_directions(self, row, col, board):
        return self._slide_directions(row, col, board, [(-1, 0), (1, 0), (0, -1), (0, 1)]) # type: ignore

class Queen(Piece):
    def __init__(self, color):
        super().__init__('queen', color, 9.0)

    def get_directions(self, row, col, board):
        return self._slide_directions(row, col, board, [ # type: ignore
            (-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)
        ])

class King(Piece):
    def __init__(self, color):
        super().__init__('king', color, 10000.0)

    def get_directions(self, row, col, board):
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        moves = []

        # Normal adjacent moves
        for dr, dc in offsets:
            r, c = row + dr, col + dc
            if Square.in_range(r, c):
                dest_square = board.squares[r][c]
                if dest_square.is_empty_or_enemy(self.color):
                    moves.append(Move(Square(row, col), Square(r, c, dest_square.piece)))

        # Castling candidates (pseudo-legal)
        if not self.moved:
            back_row = 7 if self.color == 'white' else 0

            # King-side
            rook_sq = board.squares[back_row][7]
            if isinstance(rook_sq.piece, Rook) and not rook_sq.piece.moved:
                if all(board.squares[back_row][c].is_empty() for c in [5, 6]):
                    moves.append(Move(Square(row, col), Square(back_row, 6)))

            # Queen-side
            rook_sq = board.squares[back_row][0]
            if isinstance(rook_sq.piece, Rook) and not rook_sq.piece.moved:
                if all(board.squares[back_row][c].is_empty() for c in [1, 2, 3]):
                    moves.append(Move(Square(row, col), Square(back_row, 2)))

        return moves




    # Shared sliding logic for Bishop, Rook, Queen
    def _slide_directions(self, row, col, board, increments):
        moves = []
        for dr, dc in increments:
            r, c = row + dr, col + dc
            while Square.in_range(r, c):
                dest_square = board.squares[r][c]
                if dest_square.is_empty():
                    moves.append(Move(Square(row, col), Square(r, c)))
                elif dest_square.has_enemy_piece(self.color):
                    moves.append(Move(Square(row, col), Square(r, c, dest_square.piece)))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves

# Add _slide_directions to Bishop, Rook, Queen via mixin or inheritance
for cls in [Bishop, Rook, Queen]:
    cls._slide_directions = King._slide_directions
