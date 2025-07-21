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
        self.max_time = 2.0  # Reduced time for Python performance
        self.max_depth = 4   # Reduced depth for Python performance
        self.transposition_table = {}  # Simple transposition table
        self.killer_moves = {}  # Killer move heuristic
        
    def search(self, board: Board, depth: int = 4, max_time: float = 2.0) -> SearchResult:
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
        previous_score = None  # Track previous depth's score for bug detection
        
        # Always try at least depth 1 to ensure we have some move
        for current_depth in range(1, depth + 1):
            # Give more time to deeper searches - don't abort too early
            if current_depth > 1 and self._should_stop() and current_depth > depth // 2:
                break
                
            try:
                result = self._minimax_root(board, current_depth)
                if result.best_move:
                    # Always update with deeper search results in iterative deepening
                    # Deeper searches are more accurate even if the score seems worse
                    best_result = result
                    best_result.depth = current_depth
                    
                print(f"Depth {current_depth}: {result.score/100.0:+.2f} pawns - {result.best_move.to_algebraic() if result.best_move else 'None'}")
                
                # IMPROVED DEBUGGING: Only flag as bug if scores get significantly WORSE at deeper depths
                # It's normal for Black to choose moves that are positive (bad for Black) if they're the best available
                # The bug is when deeper search makes BLACK choose WORSE moves (higher positive scores)
                if (board.next_player == 'black' and 
                    current_depth > 1 and 
                    previous_score is not None):
                    
                    score_change = result.score - previous_score
                    if score_change > 200:  # Score got 2+ pawns worse for Black
                        print(f"  🚨 POTENTIAL BUG: Black's score got {score_change/100.0:.2f} pawns WORSE at depth {current_depth}")
                        print(f"  🚨 Previous: {previous_score/100.0:+.2f}, Current: {result.score/100.0:+.2f}")
                        print(f"  🚨 This suggests search is optimizing for White instead of Black!")
                
                # Store current score for next iteration comparison
                previous_score = result.score
                
                # Debug: Show if the move changed between depths
                if best_result.best_move and result.best_move:
                    if best_result.best_move.to_algebraic() != result.best_move.to_algebraic():
                        print(f"  → Move changed from {best_result.best_move.to_algebraic()} to {result.best_move.to_algebraic()}")
                        print(f"  → Score changed from {best_result.score/100.0:+.2f} to {result.score/100.0:+.2f}")
                
                # If we found a mate, no need to search deeper
                if abs(result.score) > 19000:
                    print(f"Mate found at depth {current_depth}, stopping search")
                    break
                    
            except TimeoutError:
                print(f"Search timeout at depth {current_depth}, using depth {best_result.depth}")
                break
        
        best_result.nodes = self.nodes_searched
        elapsed = time.time() - self.start_time
        nps = best_result.nodes / elapsed if elapsed > 0 else 0
        print(f"Search completed: {best_result.nodes} nodes in {elapsed:.2f}s ({nps:.0f} n/s)")
        
        return best_result
    
    def _minimax_root(self, board: Board, depth: int) -> SearchResult:
        """Root minimax call for the current player."""
        best_move = None
        current_player = board.next_player  # Store BEFORE making moves
        
        # Since evaluation is always from white's perspective:
        # - White wants to MAXIMIZE the evaluation score
        # - Black wants to MINIMIZE the evaluation score  
        if current_player == 'white':
            best_score = -inf  # White maximizes
        else:
            best_score = inf   # Black minimizes
        
        moves = self._get_ordered_moves(board, current_player)
        
        if not moves:
            # No legal moves available
            if board.in_check_king(current_player):
                # Checkmate - bad for current player
                score = -20000 if current_player == 'white' else 20000
            else:
                # Stalemate
                score = 0
            return SearchResult(None, score, depth)
        
        for piece, move in moves:
            if self._should_stop():
                raise TimeoutError("Search time limit exceeded")
            
            # Use fast make/unmake instead of board copying
            move_info = board.make_move_fast(piece, move)
            
            try:
                # After making the move, the position is evaluated from white's perspective
                # But we need to continue the search from the opponent's perspective with proper bounds
                if current_player == 'white':
                    # White made a move, now it's black's turn to respond (minimize)
                    score = self._minimax(board, depth - 1, -inf, inf, False, allow_null=True)
                    if score > best_score:
                        best_score = score
                        best_move = move
                else:
                    # Black made a move, now it's white's turn to respond (maximize)  
                    score = self._minimax(board, depth - 1, -inf, inf, True, allow_null=True)
                    if score < best_score:
                        best_score = score
                        best_move = move
            except TimeoutError:
                # Always unmake the move before re-raising timeout
                board.unmake_move_fast(piece, move, move_info)
                raise
            
            # Undo the move
            board.unmake_move_fast(piece, move, move_info)
        
        # Return the score from the correct perspective
        # Since evaluation is always from white's perspective, we need to return
        # the score as-is (it's already in the right perspective)
        return SearchResult(best_move, best_score, depth)
    
    def _minimax(self, board: Board, depth: int, alpha: float, beta: float, maximizing: bool, allow_null: bool = True) -> float:
        """
        Minimax algorithm with alpha-beta pruning, null move pruning, and late move reductions.
        
        Args:
            board: Current board position
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing: True if maximizing player (white), False for minimizing (black)
            allow_null: True if null move pruning is allowed (prevents double null moves)
            
        Returns:
            Evaluation score of the position
        """
        self.nodes_searched += 1
        
        # FAIL-SAFE: Prevent infinite recursion
        if depth < 0:
            return Evaluation.evaluate(board)
        
        # Check transposition table - RE-ENABLED with careful sign handling
        board_hash = self._hash_board_fast(board)
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                return entry['score']  # Simple exact match only for speed
        
        # Terminal conditions
        if depth == 0:
            # SIMPLIFIED: Direct evaluation instead of expensive quiescence
            # The quiescence search was calling get_all_moves() which is very slow
            score = Evaluation.evaluate(board)
            self._store_transposition_simple(board_hash, depth, score)
            return score
        
        if self._should_stop():
            raise TimeoutError("Search time limit exceeded")
        
        # Game over check
        current_player = 'white' if maximizing else 'black'
        if board.is_game_over():
            if board.is_checkmate(current_player):
                # Checkmate is bad for the current player
                # Closer checkmates are worse (more urgent)
                mate_penalty = (self.max_depth - depth)  # Closer = higher penalty
                if maximizing:
                    score = -20000 - mate_penalty  # Very bad for maximizer (white)
                else:
                    score = 20000 + mate_penalty   # Very good for maximizer (white)
                self._store_transposition_simple(board_hash, depth, score)
                return score
            else:
                self._store_transposition_simple(board_hash, depth, 0)
                return 0  # Stalemate or draw
        
        # Null Move Pruning - RE-ENABLED with proper sign handling
        current_player = 'white' if maximizing else 'black'
        in_check = board.in_check_king(current_player)
        
        if (allow_null and 
            depth >= 3 and 
            not in_check and 
            not self._is_endgame(board)):
            
            # Get current evaluation to see if position is promising
            current_eval = Evaluation.evaluate(board)
            # Convert to current player's perspective
            if not maximizing:  # Black's turn
                current_eval = -current_eval
            
            # Only try null move if position looks good (above beta)
            if current_eval >= beta:
                # Make null move
                original_player = self._make_null_move(board)
                
                try:
                    # Search with reduced depth and narrow window
                    # FIXED: Remove the incorrect negation - minimax returns values from White's perspective
                    null_score = self._minimax(board, depth - 3, -beta, -beta + 1, not maximizing, allow_null=False)
                except TimeoutError:
                    # Unmake null move on timeout
                    self._unmake_null_move(board, original_player)
                    raise
                
                # Unmake null move
                self._unmake_null_move(board, original_player)
                
                # Null move cutoff
                if null_score >= beta:
                    return beta
        
        moves = self._get_ordered_moves(board, current_player)
        
        if not moves:
            # self._store_transposition(board_hash, depth, 0, 'exact')  # Disabled for performance
            return 0  # No legal moves (shouldn't happen if game_over check works)
        
        original_alpha = alpha
        best_score = -inf if maximizing else inf
        
        if maximizing:
            for move_index, (piece, move) in enumerate(moves):
                # CLEAN ALPHA-BETA WITH LMR
                # Determine if this move is dangerous (shouldn't be reduced)
                is_dangerous = self._is_dangerous_move(board, piece, move)
                
                # Calculate Late Move Reduction amount
                reduction = self._calculate_lmr_reduction(move_index, depth, is_dangerous)
                # Ensure depth always decreases by at least 1
                search_depth = max(0, depth - 1 - reduction)
                
                move_info = board.make_move_fast(piece, move)
                try:
                    # WHITE's turn (maximizing): after move, BLACK responds (minimizing)
                    eval_score = self._minimax(board, search_depth, alpha, beta, False, allow_null=True)
                    
                    # LMR Re-search: Only if we got a really good score and used reduction
                    if reduction > 0 and eval_score > alpha and search_depth < depth - 1:
                        # Re-search at full depth if the reduced search found a good move
                        eval_score = self._minimax(board, depth - 1, alpha, beta, False, allow_null=True)
                    
                except TimeoutError:
                    board.unmake_move_fast(piece, move, move_info)
                    raise
                board.unmake_move_fast(piece, move, move_info)
                
                # Update best score for maximizing player
                if eval_score > best_score:
                    best_score = eval_score
                
                # Alpha-beta pruning: update alpha
                if eval_score > alpha:
                    alpha = eval_score
                    
                # Beta cutoff: if alpha >= beta, prune remaining moves
                if alpha >= beta:
                    # Store killer move for non-captures
                    if not move.is_capture():
                        self._store_killer_move(move, depth)
                    break  # Beta cutoff
        else:
            for move_index, (piece, move) in enumerate(moves):
                # CLEAN ALPHA-BETA WITH LMR
                # Determine if this move is dangerous (shouldn't be reduced)
                is_dangerous = self._is_dangerous_move(board, piece, move)
                
                # Calculate Late Move Reduction amount
                reduction = self._calculate_lmr_reduction(move_index, depth, is_dangerous)
                # Ensure depth always decreases by at least 1
                search_depth = max(0, depth - 1 - reduction)
                
                move_info = board.make_move_fast(piece, move)
                try:
                    # BLACK's turn (minimizing): after move, WHITE responds (maximizing)
                    eval_score = self._minimax(board, search_depth, alpha, beta, True, allow_null=True)
                    
                    # LMR Re-search: Only if we got a really good score and used reduction
                    if reduction > 0 and eval_score < beta and search_depth < depth - 1:
                        # Re-search at full depth if the reduced search found a good move
                        eval_score = self._minimax(board, depth - 1, alpha, beta, True, allow_null=True)
                    
                except TimeoutError:
                    board.unmake_move_fast(piece, move, move_info)
                    raise
                board.unmake_move_fast(piece, move, move_info)
                
                # Update best score for minimizing player
                if eval_score < best_score:
                    best_score = eval_score
                
                # Alpha-beta pruning: update beta
                if eval_score < beta:
                    beta = eval_score
                    
                # Alpha cutoff: if alpha >= beta, prune remaining moves
                if alpha >= beta:
                    # Store killer move for non-captures
                    if not move.is_capture():
                        self._store_killer_move(move, depth)
                    break  # Alpha cutoff
        
        # Store in transposition table
        # Store result in transposition table
        self._store_transposition_simple(board_hash, depth, best_score)
        return best_score
    
    def _hash_board_fast(self, board: Board) -> int:
        """Ultra-fast board hash - only hash piece positions, ignore details."""
        hash_val = 0
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece and square.piece:
                    piece = square.piece
                    # Simple hash: position * piece_type * color
                    piece_code = 1 if piece.name == 'pawn' else \
                               2 if piece.name == 'knight' else \
                               3 if piece.name == 'bishop' else \
                               4 if piece.name == 'rook' else \
                               5 if piece.name == 'queen' else 6
                    color_code = 10 if piece.color == 'white' else 20
                    hash_val += (row * 8 + col + 1) * piece_code * color_code
        
        # Include turn
        if board.next_player == 'black':
            hash_val += 999999
            
        return hash_val
    
    def _store_transposition_simple(self, board_hash: int, depth: int, score: float):
        """Simple transposition table storage."""
        # Only store if table isn't too big
        if len(self.transposition_table) < 50000:
            self.transposition_table[board_hash] = {
                'depth': depth,
                'score': score
            }
    
    def _quiescence_search_simple(self, board: Board, alpha: float, beta: float, maximizing: bool) -> float:
        """Ultra-simple quiescence - only check obvious captures."""
        stand_pat = Evaluation.evaluate(board)
        
        # Stand pat cutoffs
        if maximizing and stand_pat >= beta:
            return beta
        if not maximizing and stand_pat <= alpha:
            return alpha
            
        # Only look at captures of high-value pieces
        current_player = 'white' if maximizing else 'black'
        moves = board.get_all_moves(current_player)
        
        best_score = stand_pat
        
        for piece, move in moves:
            # Only consider captures of queen/rook for speed
            if move.captured and move.captured.name in ('queen', 'rook'):
                try:
                    move_info = board.make_move_fast(piece, move)
                    score = Evaluation.evaluate(board)  # Just static eval, no recursion
                    board.unmake_move_fast(piece, move, move_info)
                except TimeoutError:
                    board.unmake_move_fast(piece, move, move_info)
                    raise
                
                if maximizing:
                    best_score = max(best_score, score)
                    if best_score >= beta:
                        return beta
                else:
                    best_score = min(best_score, score)
                    if best_score <= alpha:
                        return alpha
        
        return best_score
    
    def _store_transposition(self, board_hash: int, depth: int, score: float, entry_type: str):
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
    
    def _get_ordered_moves(self, board: Board, color: str) -> List[Tuple[Piece, Move]]:
        """Get moves with ultra-fast ordering optimized for Python."""
        moves = board.get_all_moves(color)
        
        if not moves:
            return []
        
        # In Python, sorting is expensive. Just separate captures vs non-captures
        # This gives us 80% of the benefit with 20% of the cost
        captures = []
        quiet_moves = []
        
        for piece, move in moves:
            if move.captured:  # Faster than calling is_capture()
                # Simple capture priority: victim value minus attacker value
                victim_val = 900 if move.captured.name == 'queen' else \
                           500 if move.captured.name == 'rook' else \
                           300 if move.captured.name in ('knight', 'bishop') else 100
                attacker_val = 900 if piece.name == 'queen' else \
                             500 if piece.name == 'rook' else \
                             300 if piece.name in ('knight', 'bishop') else 100
                captures.append((victim_val - attacker_val, piece, move))
            else:
                quiet_moves.append((0, piece, move))
        
        # Only sort captures (much smaller list)
        captures.sort(reverse=True, key=lambda x: x[0])
        
        # Return format without score
        result = [(piece, move) for _, piece, move in captures]
        result.extend([(piece, move) for _, piece, move in quiet_moves])
        return result
    
    def _get_piece_value(self, piece_name: str) -> int:
        """Fast piece value lookup."""
        values = {'pawn': 100, 'knight': 300, 'bishop': 300, 'rook': 500, 'queen': 900, 'king': 10000}
        return values.get(piece_name, 100)
    
    def _is_center_square(self, row: int, col: int) -> bool:
        """Fast center square check."""
        return 2 <= row <= 5 and 2 <= col <= 5
    
    def _should_stop(self) -> bool:
        """Check if search should be stopped due to time limit."""
        return time.time() - self.start_time >= self.max_time
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
        
        # SAFETY CHECK: Heavily penalize moves that put pieces in danger
        if self._move_puts_piece_in_danger(board, piece, move):
            from evaluation import Evaluation
            piece_value = Evaluation.PIECE_VALUES.get(piece.name, 0)
            score -= piece_value * 0.9  # 90% penalty for dangerous moves
        
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
        # Use fast make/unmake instead of expensive board copying
        try:
            move_info = board.make_move_fast(piece, move)
            opponent_color = 'black' if piece.color == 'white' else 'white'
            result = board.in_check_king(opponent_color)
            board.unmake_move_fast(piece, move, move_info)
        except TimeoutError:
            board.unmake_move_fast(piece, move, move_info)
            raise
        return result
            
        return False
    
    def _is_square_attacked_by_major_pieces(self, board: Board, row: int, col: int, by_color: str) -> bool:
        """Quick check if square is attacked by major pieces (queen, rook, bishop)."""
        # Check for queen, rook, and bishop attacks only (faster than full search)
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Rook/Queen directions
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Bishop/Queen directions
        ]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                square = board.squares[r][c]
                if square.has_piece and square.piece:
                    piece = square.piece
                    if piece.color == by_color:
                        # Check if this piece can attack the target square
                        if ((piece.name in ['queen', 'rook'] and (dr == 0 or dc == 0)) or
                            (piece.name in ['queen', 'bishop'] and dr != 0 and dc != 0)):
                            return True
                    break  # Piece blocks further attacks in this direction
                r += dr
                c += dc
        return False
    
    def _quiescence_search(self, board: Board, alpha: float, beta: float, maximizing: bool, depth: int = 0) -> float:
        """
        Quiescence search to avoid horizon effect by searching all captures.
        This prevents the engine from missing tactical shots at the search frontier.
        """
        if depth > 10:  # Prevent infinite quiescence
            return Evaluation.evaluate(board)
            
        # Stand-pat evaluation - can we achieve beta with no further moves?
        stand_pat = Evaluation.evaluate(board)
        
        if maximizing:
            if stand_pat >= beta:
                return beta  # Beta cutoff
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha  # Alpha cutoff  
            beta = min(beta, stand_pat)
        
        # Get capture moves only
        current_player = 'white' if maximizing else 'black'
        captures = self._get_capture_moves(board, current_player)
        
        if not captures:
            return stand_pat
        
        # Search captures
        for piece, move in captures:
            if self._should_stop():
                break
                
            try:
                move_info = board.make_move_fast(piece, move)
                score = self._quiescence_search(board, alpha, beta, not maximizing, depth + 1)
                board.unmake_move_fast(piece, move, move_info)
            except TimeoutError:
                board.unmake_move_fast(piece, move, move_info)
                raise
            
            if maximizing:
                if score >= beta:
                    return beta  # Beta cutoff
                alpha = max(alpha, score)
            else:
                if score <= alpha:
                    return alpha  # Alpha cutoff
                beta = min(beta, score)
        
        return alpha if maximizing else beta
    
    def _get_capture_moves(self, board: Board, color: str) -> list[tuple[Piece, Move]]:
        """Get only capture moves for quiescence search."""
        captures = []
        moves = board.get_all_moves(color)
        for piece, move in moves:
            if move.is_capture():
                captures.append((piece, move))
        return captures
    
    def _is_square_attacked_by_color(self, board: Board, row: int, col: int, by_color: str) -> bool:
        """Check if a square is attacked by any piece of the given color."""
        for r in range(8):
            for c in range(8):
                square = board.squares[r][c]
                if square.has_piece and square.piece and square.piece.color == by_color:
                    attacking_piece = square.piece
                    # Generate moves for this piece
                    board.calc_moves(attacking_piece, r, c, filter_checks=False)
                    for move in attacking_piece.moves:
                        if move.final.row == row and move.final.col == col:
                            return True
        return False
    
    def _is_square_defended_by_color(self, board: Board, row: int, col: int, by_color: str) -> bool:
        """Check if a square is defended by any piece of the given color."""
        return self._is_square_attacked_by_color(board, row, col, by_color)
    
    def _is_endgame(self, board: Board) -> bool:
        """
        Detect endgame positions to avoid null move pruning in zugzwang positions.
        Simple heuristic: endgame if both sides have <= 13 points of material (excluding kings).
        """
        white_material = black_material = 0
        material_values = {'queen': 9, 'rook': 5, 'bishop': 3, 'knight': 3, 'pawn': 1}
        
        for row in range(8):
            for col in range(8):
                piece = board.squares[row][col].piece
                if piece and piece.name != 'king':
                    value = material_values.get(piece.name, 0)
                    if piece.color == 'white':
                        white_material += value
                    else:
                        black_material += value
        
        # Endgame if both sides have low material
        return white_material <= 13 and black_material <= 13
    
    def _is_dangerous_move(self, board: Board, piece: Piece, move: Move) -> bool:
        """
        Check if a move should avoid Late Move Reduction.
        Dangerous moves include: captures, checks, promotions, killer moves, and important pieces.
        """
        # Always search captures at full depth
        if move.is_capture():
            return True
        
        # Always search promotions at full depth
        if hasattr(move, 'promotion') and move.promotion:
            return True
        
        # Check if move gives check (requires temporary move)
        if self._gives_check(board, piece, move):
            return True
        
        # IMPORTANT: Don't reduce queen moves - they're often critical
        if piece.name == 'queen':
            return True
        
        # Don't reduce king moves - always critical for safety
        if piece.name == 'king':
            return True
        
        # Check if it's a killer move (stored from previous searches)
        # You could enhance this by checking against stored killer moves
        
        return False
    
    def _calculate_lmr_reduction(self, move_index: int, depth: int, is_dangerous: bool) -> int:
        """
        Calculate Late Move Reduction amount based on move characteristics.
        Returns the reduction amount (0 = no reduction, 1+ = reduce by this amount).
        """
        if is_dangerous or move_index < 4:  # Don't reduce first 4 moves or dangerous moves
            return 0
        
        if depth < 3:  # Don't reduce in shallow searches
            return 0
        
        # Progressive reduction: later moves get reduced more
        # Logarithmic reduction to avoid over-reducing
        if move_index < 8:
            return 1  # Small reduction for moves 4-7
        elif move_index < 16:
            return 2  # Medium reduction for moves 8-15
        else:
            return min(3, depth // 2)  # Larger reduction for later moves
    
    def _make_null_move(self, board: Board) -> str:
        """Make a null move (just switch the current player)."""
        original_player = board.next_player
        board.next_player = 'black' if board.next_player == 'white' else 'white'
        return original_player
    
    def _unmake_null_move(self, board: Board, original_player: str) -> None:
        """Unmake a null move (restore the original player)."""
        board.next_player = original_player
