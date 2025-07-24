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
from see import SEE

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
        self.debug_mode = False  # Flag to show evaluation calculations
        
    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode to show evaluation calculations."""
        self.debug_mode = enabled
        
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
        """Root minimax call for the current player with proper alpha-beta."""
        best_move = None
        current_player = board.next_player  # Store BEFORE making moves
        
        # Initialize alpha-beta window
        alpha = -inf
        beta = inf
        
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
                # If White is checkmated, score should be very negative (bad for White)
                # If Black is checkmated, score should be very positive (good for White)
                score = -20000 if current_player == 'white' else 20000
            else:
                # Stalemate
                score = 0
            return SearchResult(None, score, depth)
        
        if self.debug_mode:
            print(f"\n{'='*60}")
            print(f"AI Evaluation Debug - {current_player.upper()} to move")
            print(f"Analyzing {len(moves)} possible moves at depth {depth}")
            print(f"{'='*60}")
        
        move_evaluations = []  # Store move evaluations for debug display
        
        for i, (piece, move) in enumerate(moves):
            if self._should_stop():
                raise TimeoutError("Search time limit exceeded")
            
            # Use fast make/unmake instead of board copying
            move_info = board.make_move_fast(piece, move)
            
            try:
                # After making the move, continue search with proper alpha-beta bounds
                if current_player == 'white':
                    # White made a move, now it's black's turn to respond (minimize)
                    score = self._minimax(board, depth - 1, alpha, beta, False, allow_null=True)
                    if score > best_score:
                        best_score = score
                        best_move = move
                        alpha = max(alpha, score)  # Update alpha for next moves
                else:
                    # Black made a move, now it's white's turn to respond (maximize)  
                    score = self._minimax(board, depth - 1, alpha, beta, True, allow_null=True)
                    
                    if score < best_score:
                        best_score = score
                        best_move = move
                        beta = min(beta, score)  # Update beta for next moves
                
                # Store for debug display
                if self.debug_mode:
                    move_str = f"{piece.name.capitalize()}{chr(97 + move.initial.col)}{8 - move.initial.row}-{chr(97 + move.final.col)}{8 - move.final.row}"
                    if move.captured:
                        move_str += f"x{move.captured.name}"
                    
                    # Get detailed evaluation breakdown
                    components = Evaluation.evaluate_debug(board)
                    
                    move_evaluations.append({
                        'move': move_str,
                        'score': score,
                        'components': components,
                        'is_best': (move == best_move)
                    })
                    
                # Alpha-beta cutoff at root level
                if alpha >= beta:
                    board.unmake_move_fast(piece, move, move_info)
                    break  # Prune remaining moves
                    
            except TimeoutError:
                # Always unmake the move before re-raising timeout
                board.unmake_move_fast(piece, move, move_info)
                raise
            
            # Undo the move
            board.unmake_move_fast(piece, move, move_info)
        
        # Display debug information
        if self.debug_mode and move_evaluations and best_move:
            self._display_move_evaluations(move_evaluations, current_player, best_move)
        
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
        
        # Check transposition table
        board_hash = self._hash_board_fast(board)
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                return entry['score']  # Simple exact match only for speed
        
        # Terminal conditions
        if depth == 0:
            # Use quiescence search to avoid horizon effect
            score = self._quiescence_search_simple(board, alpha, beta, maximizing, 0)
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
    
    def _quiescence_search_simple(self, board: Board, alpha: float, beta: float, maximizing: bool, depth: int = 0) -> float:
        """
        Proper quiescence search with recursion to handle capture sequences.
        This will catch defended pieces and recaptures.
        """
        # Prevent infinite recursion in complex tactical sequences
        if depth > 8:
            return Evaluation.evaluate(board)
            
        # Stand pat evaluation - can we achieve cutoff without any moves?
        stand_pat = Evaluation.evaluate(board)
        
        if maximizing:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)
            
        # Get only capture moves for quiescence
        current_player = 'white' if maximizing else 'black'
        captures = self._get_capture_moves_simple(board, current_player)
        
        # If no captures, return stand pat
        if not captures:
            return stand_pat
            
        for piece, move in captures:
            # SEE pruning: skip obviously bad captures in quiescence
            # But only if we're not in check (bad captures might be forced)
            if depth > 0:  # Only prune deeper in qsearch
                see_value = SEE.evaluate_capture(board, move)
                if see_value < -50:  # Allow small losses for tactics
                    continue
            
            try:
                move_info = board.make_move_fast(piece, move)
                # RECURSIVE call - this will catch recaptures!
                score = self._quiescence_search_simple(board, alpha, beta, not maximizing, depth + 1)
                board.unmake_move_fast(piece, move, move_info)
            except:
                try:
                    board.unmake_move_fast(piece, move, move_info)
                except:
                    pass
                continue
                
            if maximizing:
                if score >= beta:
                    return beta
                alpha = max(alpha, score)
            else:
                if score <= alpha:
                    return alpha
                beta = min(beta, score)
        
        return alpha if maximizing else beta
    
    def _get_capture_moves_simple(self, board: Board, color: str) -> list:
        """Get only capture moves for simple quiescence search."""
        captures = []
        moves = board.get_all_moves(color)
        for piece, move in moves:
            if move.captured is not None:
                captures.append((piece, move))
        return captures
    
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
        """ENHANCED move ordering prioritizing good captures and tactical moves."""
        moves = board.get_all_moves(color)
        
        if not moves:
            return []
        
        # Separate moves by type for better ordering
        winning_captures = []  # SEE > 100 (clearly winning)
        equal_captures = []    # SEE >= 0 but <= 100 (equal exchanges)
        losing_captures = []   # SEE < 0 (losing captures) 
        tactical_moves = []    # Checks, threats, etc.
        quiet_moves = []       # Regular development/positional moves
        
        for piece, move in moves:
            if move.captured:  # It's a capture
                # Use SEE to evaluate the capture
                see_value = SEE.evaluate_capture(board, move)
                
                # CRITICAL: Prioritize clearly winning captures first
                if see_value > 100:  # More than a pawn ahead
                    winning_captures.append((see_value, piece, move))
                elif see_value >= 0:  # Breaking even or small advantage
                    equal_captures.append((see_value, piece, move))
                else:  # Losing material
                    losing_captures.append((see_value, piece, move))
            else:
                # Check if it's a tactical move (check, threat, etc.)
                is_tactical = self._is_tactical_move(board, piece, move)
                if is_tactical:
                    score = self._score_tactical_move(board, piece, move)
                    tactical_moves.append((score, piece, move))
                else:
                    # Score quiet moves with simple heuristics
                    score = self._score_quiet_move(board, piece, move)
                    quiet_moves.append((score, piece, move))
        
        # Sort each category by score (best first)
        winning_captures.sort(reverse=True, key=lambda x: x[0])
        equal_captures.sort(reverse=True, key=lambda x: x[0])
        losing_captures.sort(reverse=True, key=lambda x: x[0])  # Even bad captures might be good in some positions
        tactical_moves.sort(reverse=True, key=lambda x: x[0])
        quiet_moves.sort(reverse=True, key=lambda x: x[0])
        
        # OPTIMAL ORDERING: Best captures, tactics, quiet moves, then bad captures
        result = []
        
        # 1. Clearly winning captures first (e.g., capturing undefended pieces)
        for _, piece, move in winning_captures:
            result.append((piece, move))
        
        # 2. Tactical moves (checks, pins, forks)
        for _, piece, move in tactical_moves:
            result.append((piece, move))
            
        # 3. Equal/small advantage captures
        for _, piece, move in equal_captures:
            result.append((piece, move))
        
        # 4. Quiet positional moves
        for _, piece, move in quiet_moves:
            result.append((piece, move))
            
        # 5. Bad captures last (might still be good in some tactical situations)
        for _, piece, move in losing_captures:
            result.append((piece, move))
        
        return result
    
    def _score_quiet_move(self, board: Board, piece: Piece, move: Move) -> int:
        """Score non-capture moves for ordering."""
        score = 0
        
        # Center control bonus
        if 2 <= move.final.row <= 5 and 2 <= move.final.col <= 5:
            score += 20
            
        # Development bonus for knights and bishops
        if piece.name in ['knight', 'bishop']:
            if (piece.color == 'white' and move.initial.row == 7) or \
               (piece.color == 'black' and move.initial.row == 0):
                score += 15
                
        # Check for castling (king moving 2 squares)
        if piece.name == 'king' and abs(move.final.col - move.initial.col) == 2:
            score += 50
            
        # Forward pawn moves
        if piece.name == 'pawn':
            direction = -1 if piece.color == 'white' else 1
            if move.final.row == move.initial.row + direction:
                score += 10
                
        return score
        if piece.name in ['knight', 'bishop']:
            if (piece.color == 'white' and move.initial.row == 7) or \
               (piece.color == 'black' and move.initial.row == 0):
                score += 15
                
        # Check for castling (king moving 2 squares)
        if piece.name == 'king' and abs(move.final.col - move.initial.col) == 2:
            score += 50
            
        # Forward pawn moves
        if piece.name == 'pawn':
            direction = -1 if piece.color == 'white' else 1
            if move.final.row == move.initial.row + direction:
                score += 10
                
        return score
    
    def _is_tactical_move(self, board: Board, piece: Piece, move: Move) -> bool:
        """Check if a move is tactical (checks, pins, discovered attacks, etc.)."""
        # Make the move temporarily to check for tactics
        move_info = board.make_move_fast(piece, move)
        
        try:
            opponent_color = 'black' if piece.color == 'white' else 'white'
            
            # Check if move gives check
            if board.in_check_king(opponent_color):
                return True
                
            # Check if move creates a discovered attack
            # (This is simplified - full implementation would be more complex)
            
            return False
        finally:
            board.unmake_move_fast(piece, move, move_info)
    
    def _score_tactical_move(self, board: Board, piece: Piece, move: Move) -> int:
        """Score tactical moves."""
        score = 0
        
        # Make the move temporarily to evaluate tactics
        move_info = board.make_move_fast(piece, move)
        
        try:
            opponent_color = 'black' if piece.color == 'white' else 'white'
            
            # Check bonus
            if board.in_check_king(opponent_color):
                score += 100
                
            # Future: Add bonuses for pins, forks, discovered attacks, etc.
            
        finally:
            board.unmake_move_fast(piece, move, move_info)
            
        return score
    
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
    
    def _display_move_evaluations(self, move_evaluations: List[dict], current_player: str, best_move: Move):
        """Display detailed evaluation breakdown for each move."""
        print(f"\nMove Evaluation Breakdown:")
        print(f"{'Move':<12} {'Total':<8} {'Material':<8} {'Position':<8} {'Tactical':<8} {'Opening':<8} {'King':<8}")
        print("-" * 80)
        
        # Sort moves by score (best first for current player)
        if current_player == 'white':
            move_evaluations.sort(key=lambda x: x['score'], reverse=True)
        else:
            move_evaluations.sort(key=lambda x: x['score'])
        
        for eval_data in move_evaluations[:10]:  # Show top 10 moves
            move_str = eval_data['move']
            score = eval_data['score']
            components = eval_data['components']
            
            # Format components for display
            material = components.get('material', 0) / 100.0
            position = components.get('position', 0) / 100.0
            tactical = components.get('tactical', 0) / 100.0
            opening = components.get('opening', 0) / 100.0
            king_safety = components.get('king_safety', 0) / 100.0
            
            # Mark the best move
            marker = " ★" if eval_data.get('is_best', False) else "  "
            
            print(f"{move_str:<12} {score/100.0:+7.2f} {material:+7.2f} {position:+7.2f} {tactical:+7.2f} {opening:+7.2f} {king_safety:+7.2f}{marker}")
        
        print(f"\n★ = AI's chosen move")
        print(f"Scores shown from White's perspective (+good for White, -good for Black)")
        print("-" * 80)
