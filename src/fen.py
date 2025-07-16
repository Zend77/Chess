from typing import TYPE_CHECKING, Optional
from piece import Pawn, Knight, Bishop, Rook, Queen, King, Piece

if TYPE_CHECKING:
    from board import Board

# Mapping of FEN piece characters to piece classes
PIECE_MAP = {
    'p': Pawn,
    'n': Knight,
    'b': Bishop,
    'r': Rook,
    'q': Queen,
    'k': King
}

class FEN:
    """
    Handles loading chess positions from FEN (Forsyth-Edwards Notation).
    FEN is the standard notation for describing a chess position including
    piece placement, turn, castling rights, en passant, and move counters.
    """
    
    @staticmethod
    def load(board: "Board", fen: str) -> None:
        """
        Parse a FEN string and set up the board accordingly.
        FEN format: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        Components: pieces active_color castling en_passant halfmove fullmove
        """
        parts = fen.strip().split()
        if len(parts) < 6:
            raise ValueError("Invalid FEN: not enough fields")

        # Clear the board before loading new position
        for r in range(8):
            for c in range(8):
                board.squares[r][c].piece = None

        # 1. Piece placement (from rank 8 to rank 1, left to right)
        rows = parts[0].split('/')
        for r, row in enumerate(rows):
            file = 0  # Column index
            for char in row:
                if char.isdigit():
                    # Numbers represent empty squares
                    file += int(char)
                else:
                    # Letters represent pieces (uppercase=white, lowercase=black)
                    color = 'white' if char.isupper() else 'black'
                    piece_type = PIECE_MAP[char.lower()]
                    board.squares[r][file].piece = piece_type(color)
                    file += 1
            # Fill remaining squares in row if needed
            while file < 8:
                board.squares[r][file].piece = None
                file += 1

        # 2. Active color ('w' for white, 'b' for black)
        board.next_player = 'white' if parts[1] == 'w' else 'black'

        # 3. Castling rights (KQkq: K=white kingside, Q=white queenside, etc.)
        board.castling_rights = parts[2] if parts[2] != '-' else ''

        # 4. En passant target square (algebraic notation or '-' for none)
        board.en_passant = parts[3]

        # 5. Halfmove clock (moves since last pawn move or capture, for fifty-move rule)
        try:
            board.halfmove_clock = int(parts[4])
        except Exception:
            board.halfmove_clock = 0

        # 6. Fullmove number (increments after black's move, starts at 1)
        try:
            board.fullmove_number = int(parts[5])
        except Exception:
            board.fullmove_number = 1

        # Update piece .moved flags based on castling rights
        # If castling rights are missing, the corresponding pieces must have moved
        wk = board.squares[7][4].piece  # White king on e1
        if isinstance(wk, King):
            wk.moved = 'K' not in board.castling_rights and 'Q' not in board.castling_rights
        
        bk = board.squares[0][4].piece  # Black king on e8
        if isinstance(bk, King):
            bk.moved = 'k' not in board.castling_rights and 'q' not in board.castling_rights
        
        # Update rook .moved flags based on castling availability
        wrk = board.squares[7][7].piece  # White kingside rook on h1
        if isinstance(wrk, Rook):
            wrk.moved = 'K' not in board.castling_rights
        
        wq = board.squares[7][0].piece  # White queenside rook on a1
        if isinstance(wq, Rook):
            wq.moved = 'Q' not in board.castling_rights
        
        brk = board.squares[0][7].piece  # Black kingside rook on h8
        if isinstance(brk, Rook):
            brk.moved = 'k' not in board.castling_rights
        
        bq = board.squares[0][0].piece  # Black queenside rook on a8
        if isinstance(bq, Rook):
            bq.moved = 'q' not in board.castling_rights

    @staticmethod
    def get_fen(board: "Board") -> str:
        """Generate a FEN string from the current board state."""
        rows = []
        for r in range(8):
            row = ''
            empty = 0
            for c in range(8):
                piece = board.squares[r][c].piece
                if piece is None:
                    empty += 1
                else:
                    if empty > 0:
                        row += str(empty)
                        empty = 0
                    symbol = ''
                    for k, v in PIECE_MAP.items():
                        if isinstance(piece, v):
                            symbol = k
                            break
                    row += symbol.upper() if piece.color == 'white' else symbol.lower()
            if empty > 0:
                row += str(empty)
            rows.append(row)
        fen = '/'.join(rows)
        fen += ' ' + ('w' if board.next_player == 'white' else 'b')
        fen += ' ' + (board.castling_rights if board.castling_rights else '-')
        fen += ' ' + (board.en_passant if board.en_passant else '-')
        fen += f' {board.halfmove_clock if hasattr(board, "halfmove_clock") else 0}'
        fen += f' {board.fullmove_number if hasattr(board, "fullmove_number") else 1}'
        return fen