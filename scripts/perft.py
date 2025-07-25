"""
Perft (Performance Test) for chess engine verification.
Compares move generation with Stockfish's perft results to ensure the engine
follows chess rules correctly and generates the exact same move counts.
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
    Generates move counts at various depths and compares with known results
    from established chess engines like Stockfish. Essential for validating
    that the engine correctly implements all chess rules.
    """
    
    def __init__(self):
        self.board = Board()
        self.total_nodes = 0
        
    def perft(self, depth: int, board: Optional[Board] = None) -> int:
        """
        Count all possible legal moves at a given depth (leaf node counting).
        This is the core perft function that recursively explores the game tree
        and counts positions at the target depth.
        
        Args:
            depth: Search depth (number of moves to look ahead)
            board: Board position to analyze (uses self.board if None)
            
        Returns:
            Total number of leaf nodes (positions) at the given depth
        """
        if board is None:
            board = self.board
            
        if depth == 0:
            return 1  # Leaf node reached
            
        moves = self.generate_legal_moves(board)
        node_count = 0
        
        for move in moves:
            # Make the move on a copy of the board
            board_copy = board.copy()
            self.make_move(board_copy, move)
            
            # Recursively count nodes from this position
            node_count += self.perft(depth - 1, board_copy)
            
        return node_count
    
    def perft_divide(self, depth: int, board: Optional[Board] = None) -> Tuple[Dict[str, int], int]:
        """
        Perform perft with division - shows node count for each root move.
        This is useful for debugging as it matches Stockfish's output format
        and helps identify which specific moves are generating incorrect counts.
        
        Args:
            depth: Search depth
            board: Board position to analyze (uses self.board if None)
            
        Returns:
            Tuple of (dictionary mapping move notation to node count, total nodes)
        """
        if board is None:
            board = self.board
            
        moves = self.generate_legal_moves(board)
        results = {}
        total_nodes = 0
        
        for move in moves:
            # Make the move on a copy of the board
            board_copy = board.copy()
            self.make_move(board_copy, move)
            
            # Count nodes for this specific root move
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
        """
        Generate all legal moves for the current player.
        This combines pseudo-legal move generation with legality checking
        to ensure no move leaves the king in check.
        """
        pseudo_legal_moves = []
        
        # Get all pseudo-legal moves for the current player's pieces
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece and square.piece and square.piece.color == board.next_player:
                    piece_moves = Rules.generate_pseudo_legal_moves(board, square.piece, row, col)
                    
                    # Handle pawn promotion - expand single moves into multiple promotion options
                    if isinstance(square.piece, Pawn):
                        piece_moves = self.expand_pawn_promotions(piece_moves, square.piece)
                    
                    pseudo_legal_moves.extend(piece_moves)
        
        # Filter out moves that would leave the king in check
        legal_moves = []
        for move in pseudo_legal_moves:
            board_copy = board.copy()
            original_player = board_copy.next_player  # Store the player before making the move
            self.make_move(board_copy, move)
            
            # Check if the move leaves the player's own king in check
            king_pos = self.find_king(board_copy, original_player)
            if king_pos and not self.is_square_attacked(board_copy, king_pos[0], king_pos[1], 
                                                      'white' if original_player == 'black' else 'black'):
                legal_moves.append(move)
        
        return legal_moves
    
    def expand_pawn_promotions(self, moves: List[Move], pawn: Pawn) -> List[Move]:
        """
        Expand pawn moves to include all four promotion options.
        When a pawn reaches the opposite end, it can promote to queen, rook, bishop, or knight.
        """
        expanded_moves = []
        
        for move in moves:
            # Check if this move reaches the promotion rank
            if isinstance(pawn, Pawn) and (move.final.row == 0 or move.final.row == 7):
                # Create separate moves for each promotion piece
                for promotion in ['q', 'r', 'b', 'n']:  # Queen, Rook, Bishop, Knight
                    promo_move = Move(move.initial, move.final, move.captured, promotion)
                    expanded_moves.append(promo_move)
            else:
                expanded_moves.append(move)
        
        return expanded_moves
    
    def make_move(self, board: Board, move: Move) -> None:
        """
        Execute a move on the board and switch the active player.
        Handles promotion pieces if the move includes promotion notation.
        """
        piece = board.squares[move.initial.row][move.initial.col].piece
        if piece:
            # Create the promoted piece if this is a promotion move
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
            
            # Execute the move using the board's move method
            board.move(piece, move, promotion_piece=promotion_piece)
            # Switch to the other player
            board.next_player = 'black' if board.next_player == 'white' else 'white'
    
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
