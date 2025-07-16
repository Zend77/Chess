"""
Chess search algorithms including minimax with alpha-beta pruning.
Implements the core AI decision-making logic.
"""

import time
from typing import Optional, Tuple, List
from math import inf
from board import Board
from move import Move
from piece import Piece, King
from evaluation import Evaluation

class SearchResult:
    """Container for search results."""
    def __init__(self, best_move: Optional[Move] = None, score: float = 0.0, depth: int = 0, nodes: int = 0):
        self.best_move = best_move
        self.score = score
        self.depth = depth
        self.nodes = nodes

class Search:
    """
    Chess search engine implementing minimax with alpha-beta pruning.
    Handles move ordering, time management, and search optimization.
    """
    
    def __init__(self):
        self.nodes_searched = 0
        self.start_time = 0.0
        self.max_time = 5.0  # Default search time in seconds
        self.max_depth = 6   # Default maximum search depth
        self.transposition_table = {}  # Simple transposition table
        self.killer_moves = {}  # Killer move heuristic
        
    def search(self, board: Board, depth: int = 6, max_time: float = 5.0) -> SearchResult:
        """
        Main search function using iterative deepening.
        
        Args:
            board: Current board position
            depth: Maximum search depth
            max_time: Maximum search time in seconds
            
        Returns:
            SearchResult containing best move and evaluation
        """
        self.nodes_searched = 0
        self.start_time = time.time()
        self.max_time = max_time
        self.max_depth = depth
        
        # Clear tables for new search
        self.transposition_table.clear()
        self.killer_moves.clear()
        
        best_result = SearchResult()
        
        # Always try at least depth 1 to ensure we have some move
        for current_depth in range(1, depth + 1):
            if current_depth > 1 and self._should_stop():
                break
                
            try:
                result = self._minimax_root(board, current_depth)
                if result.best_move:
                    best_result = result
                    best_result.depth = current_depth
                    
                print(f"Depth {current_depth}: {result.score/100.0:+.2f} pawns - {result.best_move.to_algebraic() if result.best_move else 'None'}")
                
                # If we found a mate, no need to search deeper
                if abs(result.score) > 19000:
                    break
                    
            except TimeoutError:
                break
        
        best_result.nodes = self.nodes_searched
        elapsed = time.time() - self.start_time
        nps = best_result.nodes / elapsed if elapsed > 0 else 0
        print(f"Search completed: {best_result.nodes} nodes in {elapsed:.2f}s ({nps:.0f} n/s)")
        
        return best_result
    
    def _minimax_root(self, board: Board, depth: int) -> SearchResult:
        """Root minimax call for the current player."""
        best_move = None
        best_score = -inf if board.next_player == 'white' else inf
        
        moves = self._get_ordered_moves(board, board.next_player)
        
        if not moves:
            # No legal moves available
            if board.in_check_king(board.next_player):
                # Checkmate
                score = -20000 if board.next_player == 'white' else 20000
            else:
                # Stalemate
                score = 0
            return SearchResult(None, score, depth)
        
        for piece, move in moves:
            if self._should_stop():
                raise TimeoutError("Search time limit exceeded")
            
            # Make move on copy
            new_board = board.make_move_copy(piece, move)
            
            if board.next_player == 'white':
                score = self._minimax(new_board, depth - 1, -inf, inf, False)
                if score > best_score:
                    best_score = score
                    best_move = move
            else:
                score = self._minimax(new_board, depth - 1, -inf, inf, True)
                if score < best_score:
                    best_score = score
                    best_move = move
        
        return SearchResult(best_move, best_score, depth)
    
    def _minimax(self, board: Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            board: Current board position
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing: True if maximizing player (white), False for minimizing (black)
            
        Returns:
            Evaluation score of the position
        """
        self.nodes_searched += 1
        
        # Check transposition table
        board_hash = self._hash_board(board)
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                if entry['type'] == 'exact':
                    return entry['score']
                elif entry['type'] == 'lower' and entry['score'] >= beta:
                    return beta
                elif entry['type'] == 'upper' and entry['score'] <= alpha:
                    return alpha
        
        # Terminal conditions
        if depth == 0:
            score = self._quiescence_search(board, alpha, beta, maximizing, 3)
            self._store_transposition(board_hash, depth, score, 'exact')
            return score
        
        if self._should_stop():
            raise TimeoutError("Search time limit exceeded")
        
        # Game over check
        current_player = 'white' if maximizing else 'black'
        if board.is_game_over():
            if board.is_checkmate(current_player):
                score = -20000 + (self.max_depth - depth) if maximizing else 20000 - (self.max_depth - depth)
                self._store_transposition(board_hash, depth, score, 'exact')
                return score
            else:
                self._store_transposition(board_hash, depth, 0, 'exact')
                return 0  # Stalemate or draw
        
        moves = self._get_ordered_moves(board, current_player)
        
        if not moves:
            self._store_transposition(board_hash, depth, 0, 'exact')
            return 0  # No legal moves (shouldn't happen if game_over check works)
        
        original_alpha = alpha
        best_score = -inf if maximizing else inf
        
        if maximizing:
            for piece, move in moves:
                new_board = board.make_move_copy(piece, move)
                eval_score = self._minimax(new_board, depth - 1, alpha, beta, False)
                best_score = max(best_score, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    # Store killer move for non-captures
                    if not move.is_capture():
                        self._store_killer_move(move, depth)
                    break  # Beta cutoff
        else:
            for piece, move in moves:
                new_board = board.make_move_copy(piece, move)
                eval_score = self._minimax(new_board, depth - 1, alpha, beta, True)
                best_score = min(best_score, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    # Store killer move for non-captures
                    if not move.is_capture():
                        self._store_killer_move(move, depth)
                    break  # Alpha cutoff
        
        # Store in transposition table
        if best_score <= original_alpha:
            entry_type = 'upper'
        elif best_score >= beta:
            entry_type = 'lower'
        else:
            entry_type = 'exact'
        
        self._store_transposition(board_hash, depth, best_score, entry_type)
        return best_score
    
    def _hash_board(self, board: Board) -> str:
        """Create a simple hash of the board position."""
        # Simple FEN-like hash for transposition table
        position_str = ""
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece and square.piece:
                    piece = square.piece
                    position_str += f"{piece.color[0]}{piece.name[0]}"
                else:
                    position_str += "."
        position_str += f"_{board.next_player}"
        return position_str
    
    def _store_transposition(self, board_hash: str, depth: int, score: float, entry_type: str):
        """Store position in transposition table."""
        # Simple replacement scheme - always replace
        self.transposition_table[board_hash] = {
            'depth': depth,
            'score': score,
            'type': entry_type
        }
        
        # Limit table size to prevent memory issues
        if len(self.transposition_table) > 100000:
            # Remove oldest entries (simple implementation)
            keys_to_remove = list(self.transposition_table.keys())[:10000]
            for key in keys_to_remove:
                del self.transposition_table[key]
    
    def _quiescence_search(self, board: Board, alpha: float, beta: float, maximizing: bool, depth: int) -> float:
        """
        Quiescence search to avoid horizon effect.
        Only searches captures and checks to find quiet positions.
        """
        self.nodes_searched += 1
        
        # Stand pat - evaluate current position
        stand_pat = Evaluation.evaluate(board)
        
        if depth <= 0:
            return stand_pat
        
        if maximizing:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)
        
        # Generate only captures and checks
        current_player = 'white' if maximizing else 'black'
        captures = self._get_tactical_moves(board, current_player)
        
        # Order captures by MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
        captures.sort(key=lambda x: self._mvv_lva_score(x[1]), reverse=True)
        
        for piece, move in captures:
            new_board = board.make_move_copy(piece, move)
            score = self._quiescence_search(new_board, alpha, beta, not maximizing, depth - 1)
            
            if maximizing:
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
            else:
                beta = min(beta, score)
                if alpha >= beta:
                    break
        
        return alpha if maximizing else beta
    
    def _get_ordered_moves(self, board: Board, color: str) -> List[Tuple[Piece, Move]]:
        """Get moves ordered for better alpha-beta pruning with improved move ordering."""
        moves = board.get_all_moves(color)
        
        if not moves:
            return []
        
        # Categorize moves for better ordering
        captures = []
        killer_moves_list = []
        other_moves = []
        
        for piece, move in moves:
            move_score = self._calculate_move_score(board, piece, move)
            
            if move.is_capture():
                captures.append((piece, move, move_score))
            elif self._is_killer_move(move):
                killer_moves_list.append((piece, move, move_score))
            else:
                other_moves.append((piece, move, move_score))
        
        # Sort each category by score (highest first)
        captures.sort(key=lambda x: x[2], reverse=True)
        killer_moves_list.sort(key=lambda x: x[2], reverse=True)
        other_moves.sort(key=lambda x: x[2], reverse=True)
        
        # Combine in order: captures, killers, others
        ordered_moves = []
        for piece, move, score in captures + killer_moves_list + other_moves:
            ordered_moves.append((piece, move))
        
        return ordered_moves
    
    def _calculate_move_score(self, board: Board, piece: Piece, move: Move) -> float:
        """Calculate a score for move ordering."""
        score = 0.0
        
        # Captures: MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
        if move.is_capture() and move.captured:
            from evaluation import Evaluation
            victim_value = Evaluation.PIECE_VALUES.get(move.captured.name, 0)
            attacker_value = Evaluation.PIECE_VALUES.get(piece.name, 0)
            score += victim_value - (attacker_value / 10)  # Prefer low-value attackers
        
        # Promotions
        if move.is_promotion():
            score += 900  # High value for promotions
        
        # Center control bonus
        if self._is_center_move(move):
            score += 10
        
        # Castling bonus (check if king moves 2 squares)
        if piece.name == 'king' and abs(move.final.col - move.initial.col) == 2:
            score += 50
        
        # Penalty for moving to squares attacked by opponent pawns
        if self._is_square_attacked_by_pawns(board, move.final, piece.color):
            score -= 20
        
        return score
    
    def _is_center_move(self, move: Move) -> bool:
        """Check if move goes to center squares."""
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        extended_center = [(2, 2), (2, 3), (2, 4), (2, 5), 
                          (3, 2), (3, 5), (4, 2), (4, 5),
                          (5, 2), (5, 3), (5, 4), (5, 5)]
        
        target = (move.final.row, move.final.col)
        if target in center_squares:
            return True
        elif target in extended_center:
            return True  # Lesser bonus for extended center
        return False
    
    def _is_square_attacked_by_pawns(self, board: Board, square, piece_color: str) -> bool:
        """Quick check if square is attacked by opponent pawns."""
        row, col = square.row, square.col
        opponent_color = 'black' if piece_color == 'white' else 'white'
        
        if opponent_color == 'white':
            # White pawns attack from below
            if row < 7:
                for pawn_col in [col - 1, col + 1]:
                    if 0 <= pawn_col < 8:
                        pawn_square = board.squares[row + 1][pawn_col]
                        if (pawn_square.has_piece and pawn_square.piece and 
                            pawn_square.piece.name == 'pawn' and 
                            pawn_square.piece.color == 'white'):
                            return True
        else:
            # Black pawns attack from above  
            if row > 0:
                for pawn_col in [col - 1, col + 1]:
                    if 0 <= pawn_col < 8:
                        pawn_square = board.squares[row - 1][pawn_col]
                        if (pawn_square.has_piece and pawn_square.piece and 
                            pawn_square.piece.name == 'pawn' and 
                            pawn_square.piece.color == 'black'):
                            return True
        return False
    
    def _is_killer_move(self, move: Move) -> bool:
        """Check if move is a killer move (good non-capture move)."""
        # Simple killer move implementation
        move_key = f"{move.initial.row},{move.initial.col}-{move.final.row},{move.final.col}"
        return move_key in self.killer_moves
    
    def _store_killer_move(self, move: Move, depth: int):
        """Store a killer move for this depth."""
        move_key = f"{move.initial.row},{move.initial.col}-{move.final.row},{move.final.col}"
        if depth not in self.killer_moves:
            self.killer_moves[depth] = []
        
        if move_key not in self.killer_moves[depth]:
            self.killer_moves[depth].append(move_key)
            # Keep only best 2 killer moves per depth
            if len(self.killer_moves[depth]) > 2:
                self.killer_moves[depth].pop(0)
    
    def _is_castling(self, piece: Piece, move: Move) -> bool:
        """Check if move is castling."""
        return (isinstance(piece, King) and 
                abs(move.final.col - move.initial.col) == 2)
    
    def _promotion_value(self, move: Move) -> float:
        """Get value of promotion piece."""
        if not move.promotion:
            return 0
        promo_values = {'q': 900, 'r': 500, 'b': 330, 'n': 320}
        return promo_values.get(move.promotion, 0)
    
    def _positional_move_value(self, board: Board, piece: Piece, move: Move) -> float:
        """Estimate positional value of a move."""
        from evaluation import Evaluation
        
        # Simple heuristic: difference in piece-square table values
        initial_value = Evaluation._get_piece_square_value(
            piece, move.initial.row, move.initial.col, 'middlegame'
        )
        final_value = Evaluation._get_piece_square_value(
            piece, move.final.row, move.final.col, 'middlegame'
        )
        
        return final_value - initial_value
    
    def _mvv_lva_score(self, move: Move) -> float:
        """
        Enhanced Most Valuable Victim - Least Valuable Attacker scoring.
        """
        if not move.is_capture() or not move.captured:
            return 0
        
        from evaluation import Evaluation
        victim_value = Evaluation.PIECE_VALUES.get(move.captured.name, 0)
        
        # Bonus for capturing more valuable pieces
        # Could be enhanced with attacker piece value when available
        return victim_value
    
    def _get_tactical_moves(self, board: Board, color: str) -> List[Tuple[Piece, Move]]:
        """Get only tactical moves (captures, checks, promotions)."""
        all_moves = board.get_all_moves(color)
        tactical_moves = []
        
        for piece, move in all_moves:
            if (move.is_capture() or move.is_promotion() or 
                self._gives_check(board, piece, move)):
                tactical_moves.append((piece, move))
        
        return tactical_moves
    
    def _gives_check(self, board: Board, piece: Piece, move: Move) -> bool:
        """Check if a move gives check to the opponent."""
        # Make the move and see if opponent king is in check
        new_board = board.make_move_copy(piece, move)
        opponent_color = 'black' if piece.color == 'white' else 'white'
        return new_board.in_check_king(opponent_color)
    
    def _should_stop(self) -> bool:
        """Check if search should be stopped due to time limit."""
        return time.time() - self.start_time >= self.max_time
