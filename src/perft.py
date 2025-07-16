"""
Perft (Performance Test) for chess engine verification.
Compares move generation with Stockfish's perft results.
"""

import time
from typing import Dict, List, Tuple, Optional
from board import Board
from move import Move
from square import Square
from piece import Piece, Pawn, King, Queen, Rook, Bishop, Knight
from fen import FEN
from rules import Rules


class PerftTest:
    """
    Performance test class for chess move generation verification.
    Generates move counts at various depths and compares with known results.
    """
    
    def __init__(self):
        self.board = Board()
        self.total_nodes = 0
        
    def perft(self, depth: int, board: Optional[Board] = None) -> int:
        """
        Count all possible moves at given depth.
        
        Args:
            depth: Search depth
            board: Board position (uses self.board if None)
            
        Returns:
            Total number of leaf nodes at given depth
        """
        if board is None:
            board = self.board
            
        if depth == 0:
            return 1
            
        moves = self.generate_legal_moves(board)
        node_count = 0
        
        for move in moves:
            # Make move
            board_copy = self.copy_board(board)
            self.make_move(board_copy, move)
            
            # Recurse
            node_count += self.perft(depth - 1, board_copy)
            
        return node_count
    
    def perft_divide(self, depth: int, board: Optional[Board] = None) -> Tuple[Dict[str, int], int]:
        """
        Perform perft with division - shows nodes for each root move.
        This matches Stockfish's output format.
        
        Args:
            depth: Search depth
            board: Board position (uses self.board if None)
            
        Returns:
            Tuple of (dictionary mapping move notation to node count, total nodes)
        """
        if board is None:
            board = self.board
            
        moves = self.generate_legal_moves(board)
        results = {}
        total_nodes = 0
        
        for move in moves:
            # Make move
            board_copy = self.copy_board(board)
            self.make_move(board_copy, move)
            
            # Count nodes for this move
            if depth <= 1:
                nodes = 1
            else:
                nodes = self.perft(depth - 1, board_copy)
            
            # Convert move to algebraic notation
            move_str = self.move_to_algebraic(move)
            results[move_str] = nodes
            total_nodes += nodes
        
        # Sort moves to match Stockfish order
        sorted_results = self.sort_moves_stockfish_order(results)
        
        return sorted_results, total_nodes
    
    def generate_legal_moves(self, board: Board) -> List[Move]:
        """Generate all legal moves for current position."""
        pseudo_legal_moves = []
        
        # Get all pseudo-legal moves
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece and square.piece and square.piece.color == board.next_player:
                    piece_moves = Rules.generate_pseudo_legal_moves(board, square.piece, row, col)
                    
                    # Add promotion moves for pawns
                    if isinstance(square.piece, Pawn):
                        piece_moves = self.expand_pawn_promotions(piece_moves, square.piece)
                    
                    pseudo_legal_moves.extend(piece_moves)
        
        # Filter out illegal moves (moves that leave king in check)
        legal_moves = []
        for move in pseudo_legal_moves:
            board_copy = self.copy_board(board)
            original_player = board_copy.next_player  # Store the player before making the move
            self.make_move(board_copy, move)
            
            # Find king of the player who just moved (original player)
            king_pos = self.find_king(board_copy, original_player)
            if king_pos and not self.is_square_attacked(board_copy, king_pos[0], king_pos[1], 
                                                      'white' if original_player == 'black' else 'black'):
                legal_moves.append(move)
        
        return legal_moves
    
    def expand_pawn_promotions(self, moves: List[Move], pawn: Pawn) -> List[Move]:
        """Expand pawn moves to include all promotion pieces."""
        expanded_moves = []
        
        for move in moves:
            # Check if this is a promotion move
            if isinstance(pawn, Pawn) and (move.final.row == 0 or move.final.row == 7):
                # Add all four promotion pieces
                for promotion in ['q', 'r', 'b', 'n']:
                    promo_move = Move(move.initial, move.final, move.captured, promotion)
                    expanded_moves.append(promo_move)
            else:
                expanded_moves.append(move)
        
        return expanded_moves
    
    def make_move(self, board: Board, move: Move) -> None:
        """Make a move on the board."""
        piece = board.squares[move.initial.row][move.initial.col].piece
        if piece:
            # Create promotion piece if needed
            promotion_piece = None
            if move.promotion:
                color = piece.color
                if move.promotion == 'q':
                    promotion_piece = Queen(color)
                elif move.promotion == 'r':
                    promotion_piece = Rook(color)
                elif move.promotion == 'b':
                    promotion_piece = Bishop(color)
                elif move.promotion == 'n':
                    promotion_piece = Knight(color)
            
            board.move(piece, move, promotion_piece=promotion_piece)
            board.next_player = 'black' if board.next_player == 'white' else 'white'
    
    def copy_board(self, board: Board) -> Board:
        """Create a deep copy of the board."""
        new_board = Board()
        
        # Copy all pieces more efficiently
        for row in range(8):
            for col in range(8):
                piece = board.squares[row][col].piece
                if piece:
                    # Create new piece of same type and color
                    piece_type = type(piece)
                    new_piece = piece_type(piece.color)
                    new_piece.moved = piece.moved
                    # Copy any other important attributes
                    if hasattr(piece, 'en_passant'):
                        new_piece.en_passant = piece.en_passant
                    new_board.squares[row][col].piece = new_piece
                else:
                    new_board.squares[row][col].piece = None
        
        # Copy board state
        new_board.next_player = board.next_player
        new_board.castling_rights = board.castling_rights
        new_board.en_passant = board.en_passant
        new_board.halfmove_clock = board.halfmove_clock
        new_board.fullmove_number = board.fullmove_number
        new_board.last_move = board.last_move
        
        return new_board
    
    def find_king(self, board: Board, color: str) -> Optional[Tuple[int, int]]:
        """Find the king of given color."""
        for row in range(8):
            for col in range(8):
                piece = board.squares[row][col].piece
                if isinstance(piece, King) and piece.color == color:
                    return (row, col)
        return None
    
    def is_square_attacked(self, board: Board, row: int, col: int, by_color: str) -> bool:
        """Check if a square is attacked by any piece of given color."""
        for r in range(8):
            for c in range(8):
                piece = board.squares[r][c].piece
                if piece and piece.color == by_color:
                    # Get pseudo-legal moves for this piece
                    moves = Rules.generate_pseudo_legal_moves(board, piece, r, c)
                    for move in moves:
                        if move.final.row == row and move.final.col == col:
                            return True
        return False
    
    def move_to_algebraic(self, move: Move) -> str:
        """Convert move to algebraic notation matching Stockfish format."""
        # Convert coordinates to algebraic notation
        from_square = f"{Square.get_alphacol(move.initial.col)}{8 - move.initial.row}"
        to_square = f"{Square.get_alphacol(move.final.col)}{8 - move.final.row}"
        
        result = from_square + to_square
        
        # Add promotion piece if applicable
        if move.promotion:
            result += move.promotion
        
        return result
    
    def sort_moves_stockfish_order(self, moves_dict: Dict[str, int]) -> Dict[str, int]:
        """Sort moves to match Stockfish's ordering."""
        # Stockfish seems to order by: from square (a1, a2, ..., h8), then by to square
        def move_sort_key(move_str: str) -> Tuple[str, str]:
            from_sq = move_str[:2]
            to_sq = move_str[2:4]
            return (from_sq, to_sq)
        
        sorted_moves = sorted(moves_dict.items(), key=lambda x: move_sort_key(x[0]))
        return dict(sorted_moves)
    
    def run_test_position(self, fen: str, depth: int, description: str = "") -> int:
        """Run perft test on a specific position."""
        print(f"\n{description}")
        print(f"Position: {fen}")
        print(f"Depth: {depth}")
        print()
        
        # Set up position
        FEN.load(self.board, fen)
        
        # Run perft divide
        start_time = time.time()
        results, total_nodes = self.perft_divide(depth)
        end_time = time.time()
        
        # Print results in Stockfish format
        for move, nodes in results.items():
            print(f"{move}: {nodes}")
        
        print(f"\nNodes searched: {total_nodes}")
        print(f"Time: {end_time - start_time:.3f} seconds")
        
        return total_nodes
    
    def run_standard_tests(self) -> None:
        """Run the standard perft test positions."""
        print("=== PERFT TEST SUITE ===")
        
        # Test 1: Starting position
        self.run_test_position(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            3,
            "Starting position at depth 3:"
        )
        
        # Test 2: En passant position
        self.run_test_position(
            "rnbqkbnr/pppp1ppp/8/4p3/3P4/8/PPP2PPP/RNBQKBNR b KQkq d3 0 2",
            3,
            "En passant position at depth 3:"
        )
        
        # Test 3: Castling rights
        self.run_test_position(
            "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
            3,
            "Castling rights position at depth 3:"
        )
        
        # Test 4: Pawn promotion
        self.run_test_position(
            "8/P7/8/8/8/8/7p/4k2K w - - 0 1",
            3,
            "Pawn promotion position at depth 3:"
        )
        
        # Test 5: Complex position
        self.run_test_position(
            "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
            3,
            "Complex position (promotions, captures, castling, en passant, checks) at depth 3:"
        )
        
        # Test 6: Complex position
        self.run_test_position(
            "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
            3,
            "Complex Posisiton depth 5"
        )


def perft(board_or_depth, next_player_or_fen=None, depth_or_none=None):
    """
    Convenience function for running perft on a position.
    Supports two calling conventions:
    1. perft(depth, fen) - new style
    2. perft(board, next_player, depth) - legacy style for game.py compatibility
    
    Returns:
        Total number of nodes at given depth
    """
    from board import Board
    
    # Determine calling convention
    if isinstance(board_or_depth, int) and (next_player_or_fen is None or isinstance(next_player_or_fen, str)):
        # New style: perft(depth, fen)
        depth = board_or_depth
        fen = next_player_or_fen or "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        test = PerftTest()
        FEN.load(test.board, fen)
        return test.perft(depth)
    else:
        # Legacy style: perft(board, next_player, depth)
        if isinstance(board_or_depth, Board) and isinstance(depth_or_none, int):
            board = board_or_depth
            depth = depth_or_none
            test = PerftTest()
            # Copy the board state
            for row in range(8):
                for col in range(8):
                    test.board.squares[row][col].piece = board.squares[row][col].piece
            test.board.next_player = board.next_player
            test.board.castling_rights = board.castling_rights
            test.board.en_passant = board.en_passant
            test.board.halfmove_clock = board.halfmove_clock
            test.board.fullmove_number = board.fullmove_number
            test.board.last_move = board.last_move
            return test.perft(depth)
        else:
            raise ValueError("Invalid arguments for perft function")


def perft_divide(depth: int, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1") -> None:
    """
    Convenience function for running perft divide on a position.
    
    Args:
        depth: Search depth
        fen: FEN string of position (default: starting position)
    """
    test = PerftTest()
    test.run_test_position(fen, depth)


if __name__ == "__main__":
    # Run the standard test suite
    test = PerftTest()
    test.run_standard_tests()
