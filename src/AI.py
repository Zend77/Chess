import random
from typing import Optional, Tuple
from const import *
from move import Move
from square import Square
from piece import Piece
from search import Search, SearchResult
from evaluation import Evaluation
from opening_book import OpeningBook
from fen import FEN

class AI:
    """
    Advanced AI player using minimax algorithm with alpha-beta pruning.
    Supports multiple difficulty levels and playing styles.
    """
    
    def __init__(self, color: Optional[str], difficulty: str = "medium"):
        self.color = color  # 'white' or 'black' - which side the AI plays
        self.difficulty = difficulty  # 'easy', 'medium', 'hard', 'expert'
        self.search_engine = Search()
        self.opening_book = OpeningBook()
        
        # Configure AI based on difficulty
        self.depth, self.time_limit = self._get_difficulty_settings(difficulty)
    
    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode to show evaluation calculations."""
        self.search_engine.set_debug_mode(enabled)
    
    def _get_difficulty_settings(self, difficulty: str) -> Tuple[int, float]:
        """Get search depth and time limit based on difficulty level."""
        settings = {
            'easy': (2, 15.0),       
            'medium': (3, 15.0),    
            'hard': (4, 30.0),        
            'expert': (6, 45.0),
            'master': (10, 60.0),
            'grandmaster': (12, 120.0)    
        }
        return settings.get(difficulty, (3, 2.0))
    
    def get_best_move(self, board, use_book=True) -> Tuple[Optional[Piece], Optional[Move]]:
        """
        Get the best move using opening book first, then minimax algorithm.
        
        Args:
            board: Current board state
            
        Returns:
            Tuple of (piece to move, move to make) or (None, None) if no moves available
        """
        # First check opening book
        if use_book:
            current_fen = FEN.get_fen(board)
            book_move = self.opening_book.get_book_move(current_fen)
            
            if book_move:
                try:
                    # Convert algebraic notation to move object
                    move = Move.from_algebraic(book_move, board)
                    piece = board.squares[move.initial.row][move.initial.col].piece
                    
                    if piece and piece.color == self.color:
                        # Verify the book move is legal
                        board.calc_moves(piece, move.initial.row, move.initial.col, filter_checks=True)
                        if move in piece.moves:
                            return piece, move
                except Exception as e:
                    pass
        
        # Fall back to search if no book move
        result = self.search_engine.search(board, self.depth, self.time_limit)
        
        if result.best_move:
            # Find the piece to move
            piece = board.squares[result.best_move.initial.row][result.best_move.initial.col].piece
            
            # Validate piece exists and belongs to AI
            if piece and piece.color == self.color:
                return piece, result.best_move
            else:
                return self._emergency_fallback(board)
        else:
            # Search failed (timeout or no moves found) - use fallback
            return self._emergency_fallback(board)
    
    def random_move(self, board) -> Tuple[Optional[Piece], Optional[Move]]:
        """
        Select a random legal move from all available moves.
        Fallback method for testing or when search fails.
        
        Args:
            board: Current board state
            
        Returns:
            Tuple of (piece to move, move to make) or (None, None) if no moves available
        """
        all_moves = board.get_all_moves(self.color)
        
        if not all_moves:
            return None, None
        
        piece, move = random.choice(all_moves)
        return piece, move
    
    def evaluate_position(self, board) -> float:
        """
        Evaluate the current position from AI's perspective.
        
        Args:
            board: Current board state
            
        Returns:
            Evaluation score (positive = good for AI, negative = bad for AI)
        """
        score = Evaluation.evaluate(board)
        
        # Flip score if AI is playing black
        if self.color == 'black':
            score = -score
            
        return score
    
    def set_difficulty(self, difficulty: str) -> None:
        self.difficulty = difficulty
        self.depth, self.time_limit = self._get_difficulty_settings(difficulty)
    
    def analyze_position(self, board) -> dict:
        # Placeholder for position analysis logic
        return {}
    
    def _get_material_balance(self, board) -> dict:
        """
        Calculate material balance for both sides.
        
        Args:
            board: Current board state
            
        Returns:
            Dictionary with material values for white, black, and the difference
        """
        white_material = 0
        black_material = 0
        
        for row in board.squares:
            for square in row:
                if square.has_piece and square.piece:
                    value = square.piece.value
                    if square.piece.color == 'white':
                        white_material += value
                    else:
                        black_material += value
        
        return {
            'white': white_material,
            'black': black_material,
            'difference': white_material - black_material
        }
    
    def _get_game_phase(self, board) -> str:
        """Determine current game phase based on material."""
        material = self._get_material_balance(board)
        total_material = material['white'] + material['black']
        
        if total_material > 6000:  # ~3000 per side
            return 'opening'
        elif total_material > 3000:  # ~1500 per side
            return 'middlegame'
        else:
            return 'endgame'
    
    def _classify_position(self, board) -> str:
        """Classify the type of position."""
        if board.is_checkmate(board.next_player):
            return 'checkmate'
        elif board.is_stalemate(board.next_player):
            return 'stalemate'
        elif board.in_check_king(board.next_player):
            return 'check'
        elif board.is_dead_position():
            return 'dead_position'
        elif board.is_fifty_move_rule():
            return 'fifty_move_rule'
        else:
            return 'normal'
    
    def _emergency_fallback(self, board) -> Tuple[Optional[Piece], Optional[Move]]:
        """
        Emergency fallback when search fails due to timeout or other issues.
        Quickly selects a reasonable move to avoid the 'no legal moves' bug.
        """
        # Get all legal moves
        all_moves = board.get_all_moves(self.color)
        
        if not all_moves:
            return None, None
        
        # Try to find a good move quickly
        # Priority: 1) Captures 2) Center moves 3) Safe moves 4) Any move
        
        captures = []
        center_moves = []
        safe_moves = []
        
        for piece, move in all_moves:
            if move.is_capture():
                captures.append((piece, move))
            elif self._is_center_move(move):
                center_moves.append((piece, move))
            elif not self._is_hanging_move(board, piece, move):
                safe_moves.append((piece, move))
        
        # Select best available option
        if captures:
            piece, move = random.choice(captures)
        elif center_moves:
            piece, move = random.choice(center_moves)
        elif safe_moves:
            piece, move = random.choice(safe_moves)
        else:
            piece, move = random.choice(all_moves)
        
        return piece, move
    
    def _is_center_move(self, move: Move) -> bool:
        """Check if move goes to center squares (d4, d5, e4, e5)."""
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        return (move.final.row, move.final.col) in center_squares
    
    def _is_hanging_move(self, board, piece: Piece, move: Move) -> bool:
        """Quick check if move leaves piece hanging (very basic)."""
        # For now, just check if moving to a square attacked by pawns
        target_row, target_col = move.final.row, move.final.col
        opponent_color = 'black' if self.color == 'white' else 'white'
        
        # Check if target square is attacked by opponent pawns
        if opponent_color == 'white':
            # White pawns attack from below
            if target_row < 7:
                for pawn_col in [target_col - 1, target_col + 1]:
                    if 0 <= pawn_col < 8:
                        pawn_square = board.squares[target_row + 1][pawn_col]
                        if (pawn_square.has_piece and pawn_square.piece and 
                            pawn_square.piece.name == 'pawn' and 
                            pawn_square.piece.color == 'white'):
                            return True
        else:
            # Black pawns attack from above
            if target_row > 0:
                for pawn_col in [target_col - 1, target_col + 1]:
                    if 0 <= pawn_col < 8:
                        pawn_square = board.squares[target_row - 1][pawn_col]
                        if (pawn_square.has_piece and pawn_square.piece and 
                            pawn_square.piece.name == 'pawn' and 
                            pawn_square.piece.color == 'black'):
                            return True
        
        return False



