from typing import Optional, List, Tuple
from piece import *
from const import *
from square import Square
from move import Move
from fen import FEN
from piece import Queen, Rook, Bishop, Knight

class Board:
    """
    Represents the chess board state including piece positions, move tracking,
    and game rules like castling rights, en passant, and move counters.
    Handles the core game logic for making moves and updating board state.
    """
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
        self.castling_rights: str = 'KQkq'  # K=white kingside, Q=white queenside, k=black kingside, q=black queenside
        self.en_passant: str = '-'  # Target square for en passant capture in algebraic notation
        self._create()

    def move(self, piece: Piece, move: Move, surface=None, promotion_piece: Optional[Piece]=None) -> None:
        """
        Execute a move on the board, handling all special cases and updating game state.
        This includes castling, en passant, promotion, and move counters.
        """
        initial = move.initial
        final = move.final
        captured_piece: Optional[Piece] = self.squares[final.row][final.col].piece

        # Reset halfmove clock on pawn moves or captures (for 50-move rule)
        if isinstance(piece, Pawn) or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # Handle special move types in order
        self._handle_en_passant(piece, initial, final)
        self._move_piece(piece, initial, final)
        self._handle_castling(piece, initial, final)
        self._handle_promotion(piece, final, promotion_piece)

        # Update piece state and move tracking
        piece.moved = True
        piece.clear_moves()
        self.last_move = move

        # Update castling rights based on piece movements
        self.update_castling_rights(piece, initial, final)

        # Increment fullmove counter after black's turn
        if self.next_player == 'black':
            self.fullmove_number += 1

    def _handle_en_passant(self, piece: Piece, initial: Square, final: Square) -> None:
        """
        Handle en passant logic - both setting the target square for two-square pawn moves
        and capturing the enemy pawn when an en passant capture occurs.
        """
        if isinstance(piece, Pawn):
            # Set en passant target square when pawn moves two squares from starting position
            if abs(final.row - initial.row) == 2:
                col_letter = Square.ALPHACOLS[initial.col]
                # Calculate the square the pawn "jumped over" - this becomes the en passant target
                en_passant_row = (initial.row + final.row) // 2
                row_num = str(8 - en_passant_row)  # Convert array index to chess rank notation
                self.en_passant = f"{col_letter}{row_num}"
            else:
                self.en_passant = '-'
            
            # Handle en passant capture - remove the captured pawn
            diff = final.col - initial.col
            if diff != 0 and self.squares[final.row][final.col].is_empty:
                # Diagonal move to empty square means en passant capture
                self.squares[initial.row][initial.col + diff].piece = None
        else:
            self.en_passant = '-'

    def _move_piece(self, piece: Piece, initial: Square, final: Square) -> None:
        """Basic piece movement - clear the initial square and place piece on final square."""
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

    def _handle_castling(self, piece: Piece, initial: Square, final: Square) -> None:
        """
        Handle castling by moving the rook to its final position when the king castles.
        Detects castling by checking if king moved 2 squares horizontally.
        """
        if isinstance(piece, King) and abs(initial.col - final.col) == 2:
            # Determine which rook to move based on castling direction
            rook_col = 0 if final.col < initial.col else 7  # Queenside or kingside
            rook = self.squares[initial.row][rook_col].piece
            rook_final_col = 3 if final.col < initial.col else 5  # Final rook position
            
            # Move the rook
            self.squares[initial.row][rook_col].piece = None
            self.squares[initial.row][rook_final_col].piece = rook
            if rook:
                rook.moved = True

    def _handle_promotion(self, piece: Piece, final: Square, promotion_piece: Optional[Piece]) -> None:
        """
        Handle pawn promotion when a pawn reaches the opposite end of the board.
        Promotes to queen by default, or to the specified piece type.
        """
        if isinstance(piece, Pawn) and (final.row == 0 or final.row == 7):
            promo = None
            if promotion_piece:
                promo = promotion_piece
            elif self.last_move is not None and hasattr(self.last_move, "promotion") and self.last_move.promotion:
                # Parse promotion piece from move notation (e.g., 'q' for queen)
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
        """Check if a move is in the piece's list of valid moves."""
        return move in piece.moves

    def in_check(self, piece: Piece, move: Move) -> bool:
        """
        Test if making a move would leave the moving player's king in check.
        Temporarily makes the move on the board, checks for check, then undoes it.
        Special handling for castling to ensure king doesn't pass through check.
        """
        initial_square = self.squares[move.initial.row][move.initial.col]
        final_square = self.squares[move.final.row][move.final.col]
        captured_piece = final_square.piece

        # Detect en passant capture (diagonal pawn move to empty square)
        en_passant = (
            isinstance(piece, Pawn) and
            abs(move.final.col - move.initial.col) == 1 and
            initial_square.row != move.final.row and
            final_square.is_empty
        )

        # Handle en passant capture setup
        captured_en_passant: Optional[Piece] = None
        if en_passant:
            captured_square = self.squares[move.initial.row][move.final.col]
            captured_en_passant = captured_square.piece
            captured_square.piece = None

        # Temporarily make the move
        final_square.piece = piece
        initial_square.piece = None

        # Special castling check - king cannot pass through attacked squares
        if isinstance(piece, King) and abs(move.final.col - move.initial.col) == 2:
            step = 1 if move.final.col > move.initial.col else -1
            # Check each square the king passes through during castling
            for intermediate_col in range(move.initial.col, move.final.col + step, step):
                temp_square = self.squares[move.initial.row][intermediate_col]
                original_piece = temp_square.piece
                temp_square.piece = piece

                if self.in_check_king(piece.color):
                    # King would be in check during castling - restore and reject
                    temp_square.piece = original_piece
                    initial_square.piece = piece
                    final_square.piece = captured_piece
                    if en_passant:
                        captured_square.piece = captured_en_passant
                    return True

                temp_square.piece = original_piece

            # Restore board state after castling check
            initial_square.piece = piece
            final_square.piece = captured_piece
            if en_passant:
                captured_square.piece = captured_en_passant
            return False

        # Check if king is in check after the move
        king_in_check = self.in_check_king(piece.color)

        # Restore the board to original state
        initial_square.piece = piece
        final_square.piece = captured_piece
        if en_passant:
            captured_square.piece = captured_en_passant

        return king_in_check

    def in_check_king(self, color: str) -> bool:
        """
        Check if the king of the specified color is currently in check.
        Searches the board for the king and tests if any enemy piece can attack it.
        """
        # First, find the king's position
        king_row, king_col = -1, -1
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece and square.piece and square.piece.name == 'king' and square.piece.color == color:
                    king_row, king_col = row, col

        # Then, check if any enemy piece can reach the king's square
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
        """
        Calculate and store all valid moves for a piece at the given position.
        Optionally filters out moves that would leave the king in check.
        """
        piece.clear_moves()
        moves = piece.get_moves(row, col, self)
        for move in moves:
            # Skip moves that would leave our king in check (if filtering enabled)
            if filter_checks and self.in_check(piece, move):
                continue
            piece.add_move(move)
            
    def evaluate_material(self) -> Tuple[float, float]:
        """
        Calculate material balance for both sides.
        Returns tuple of (white_score, black_score) based on piece values.
        """
        white_score = 0.0
        black_score = 0.0
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece and square.piece:
                    # Sum up piece values, excluding kings (value >= 10)
                    if square.piece.color == 'white' and square.piece.value < 10:
                        white_score += square.piece.value
                    elif square.piece.color == 'black' and square.piece.value > -10:
                        black_score += square.piece.value
        return white_score, black_score

    def _create(self) -> None:
        """Initialize the 8x8 board with empty squares."""
        self.squares = [[Square(row, col) for col in range(COLS)] for row in range(ROWS)]

    def _add_pieces(self, color: str) -> None:
        """
        Add pieces for one side to their starting positions.
        Used during initial board setup.
        """
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)
        
        # Add pawns on the second rank
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))
        
        # Add other pieces on the back rank in standard order
        placements = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_class in enumerate(placements):
            self.squares[row_other][col] = Square(row_other, col, piece_class(color))

    def set_fen(self, fen: str) -> None:
        """Load a position from FEN notation."""
        from fen import FEN
        FEN.load(self, fen)

    def update_castling_rights(self, piece: Piece, initial: Square, final: Square) -> None:
        """
        Update castling rights when pieces move or are captured.
        Castling rights are lost when kings or rooks move from their original squares,
        or when rooks are captured on their original squares.
        """
        rights = self.castling_rights.replace('-', '')
        
        # Store captured piece before move is made
        captured_piece = self.squares[final.row][final.col].piece

        # White king moves from e1 - lose both white castling rights
        if isinstance(piece, King) and piece.color == 'white' and initial.row == 7 and initial.col == 4:
            rights = rights.replace('K', '').replace('Q', '')
        
        # Black king moves from e8 - lose both black castling rights
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
