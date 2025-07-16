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
    
    def _get_difficulty_settings(self, difficulty: str) -> Tuple[int, float]:
        """Get search depth and time limit based on difficulty level."""
        settings = {
            'easy': (3, 2.0),      # Depth 3, 2 seconds
            'medium': (4, 5.0),    # Depth 4, 5 seconds  
            'hard': (6, 10.0),     # Depth 6, 10 seconds
            'expert': (8, 20.0),   # Depth 8, 20 seconds
            'master': (10, 30.0),  # Depth 10, 30 seconds
            'grandmaster': (12, 60.0)  # Depth 12, 60 seconds
        }
        return settings.get(difficulty, (4, 5.0))
    
    def get_best_move(self, board) -> Tuple[Optional[Piece], Optional[Move]]:
        """
        Get the best move using opening book first, then minimax algorithm.
        
        Args:
            board: Current board state
            
        Returns:
            Tuple of (piece to move, move to make) or (None, None) if no moves available
        """
        print(f"AI ({self.color}) thinking... (depth {self.depth}, time limit {self.time_limit}s)")
        
        # First check opening book
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
                        print(f"AI used opening book: {book_move}")
                        return piece, move
            except Exception as e:
                print(f"Book move failed: {e}")
        
        # Fall back to search if no book move
        print("AI searching with minimax algorithm...")
        result = self.search_engine.search(board, self.depth, self.time_limit)
        
        if result.best_move:
            # Find the piece to move
            piece = board.squares[result.best_move.initial.row][result.best_move.initial.col].piece
            # Convert centipawns to pawns for display
            eval_in_pawns = result.score / 100.0
            print(f"AI evaluation: {eval_in_pawns:+.2f} pawns")
            print(f"AI chose: {result.best_move.to_algebraic()}")
            return piece, result.best_move
        else:
            # Search failed (timeout or no moves found) - use fallback
            print("Search failed, using fallback move selection...")
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
        print(f"AI chose random move: {move.to_algebraic()}")
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
        """Change AI difficulty level."""
        self.difficulty = difficulty
        self.depth, self.time_limit = self._get_difficulty_settings(difficulty)
        print(f"AI difficulty set to {difficulty} (depth {self.depth}, time {self.time_limit}s)")
    
    def analyze_position(self, board) -> dict:
        """
        Provide detailed position analysis.
        
        Returns:
            Dictionary with analysis details
        """
        evaluation = self.evaluate_position(board)
        all_moves = board.get_all_moves(self.color)
        
        analysis = {
            'evaluation': evaluation / 100.0,  # Convert to pawns
            'move_count': len(all_moves),
            'material_balance': self._get_material_balance(board),
            'game_phase': self._get_game_phase(board),
            'position_type': self._classify_position(board)
        }
        
        return analysis
    
    def _get_material_balance(self, board) -> dict:
        """Calculate material balance for both sides."""
        white_material = 0
        black_material = 0
        
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if square.has_piece and square.piece:
                    piece = square.piece
                    value = Evaluation.PIECE_VALUES.get(piece.name, 0)
                    if piece.name != 'king':  # Exclude king from material count
                        if piece.color == 'white':
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
            print("No legal moves available - checkmate or stalemate")
            return None, None
        
        print(f"Emergency fallback: selecting from {len(all_moves)} legal moves")
        
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
            print(f"Emergency: selected capture {move.to_algebraic()}")
        elif center_moves:
            piece, move = random.choice(center_moves)
            print(f"Emergency: selected center move {move.to_algebraic()}")
        elif safe_moves:
            piece, move = random.choice(safe_moves)
            print(f"Emergency: selected safe move {move.to_algebraic()}")
        else:
            piece, move = random.choice(all_moves)
            print(f"Emergency: selected random move {move.to_algebraic()}")
        
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



