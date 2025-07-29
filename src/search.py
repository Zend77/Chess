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
        self.transposition_table = {}  # Enhanced transposition table with mate support
        self.killer_moves = {}  # Killer move heuristic
        self.mate_cache = {}  # Mate distance hash table (Solution 1)
        self.mate_sequences = {}  # Move sequence caching (Solution 7)
        self.debug_mode = False  # Disabled by default for performance
        
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
        # Note: We intentionally keep mate_cache and mate_sequences between searches
        # as they contain valuable long-term knowledge
        
        # Periodic cache cleanup to prevent memory bloat
        if len(self.mate_cache) > 1000:
            # Keep only the most recent 500 entries
            items = list(self.mate_cache.items())
            self.mate_cache = dict(items[-500:])
            print("🧹 Cleaned mate cache (kept 500 most recent entries)")
        
        if len(self.mate_sequences) > 200:
            # Keep only the most recent 100 sequences  
            items = list(self.mate_sequences.items())
            self.mate_sequences = dict(items[-100:])
            print("🧹 Cleaned mate sequence cache (kept 100 most recent entries)")
        
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
                
                # For mate verification, we need to search deeper to see defensive moves
                # Updated threshold to work with new mate scoring system (19999 instead of 20000)
                if abs(result.score) >= 19990:  # Mate detected (allowing for mate distance variations)
                    # For mate positions, we want to search deeper to find the fastest mate
                    min_mate_verification_depth = max(4, depth - 1)  # Search deeper for mate verification
                    
                    # Check if this is mate in 1 (the most urgent)
                    mate_distance = 19999 - abs(result.score)
                    is_mate_in_one = mate_distance <= 1
                    
                    if is_mate_in_one:
                        print(f"Mate in 1 found at depth {current_depth} (score: {result.score/100.0:+.2f}), executing immediately")
                        break
                    elif current_depth >= min_mate_verification_depth:
                        print(f"Mate verified at depth {current_depth} (score: {result.score/100.0:+.2f}), stopping search")
                        break
                    else:
                        print(f"Potential mate at depth {current_depth} (score: {result.score/100.0:+.2f}), continuing to depth {min_mate_verification_depth} to find fastest mate")
                        # Continue searching to find the fastest mate sequence
                
                # REMOVED: Early termination for advantage - was causing poor decisions
                    
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
        from evaluation import Evaluation  # Import at function start to avoid scoping issues
        
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
        
        # SOLUTION 1 & 7: Check mate cache first (immediate lookup without search)
        board_hash = hash(str(board.squares))  # Simple position hash
        if board_hash in self.mate_cache:
            mate_entry = self.mate_cache[board_hash]
            # Verify the cached mate is still valid (moves haven't been undone)
            if mate_entry['depth'] >= depth:  # Cached result is at least as deep
                cached_move = mate_entry.get('best_move')
                if cached_move and self._is_move_legal(board, cached_move, current_player):
                    print(f"🎯 MATE CACHE HIT: {cached_move.to_algebraic()} (mate in {mate_entry['mate_distance']})")
                    return SearchResult(cached_move, mate_entry['score'], depth)
        
        # Check mate sequence cache for multi-move forced sequences
        if board_hash in self.mate_sequences:
            sequence_entry = self.mate_sequences[board_hash]
            if sequence_entry['moves_to_mate'] <= 5:  # Only use for short sequences
                first_move = sequence_entry['sequence'][0] if sequence_entry['sequence'] else None
                if first_move and self._is_move_legal(board, first_move, current_player):
                    print(f"🎯 MATE SEQUENCE HIT: {first_move.to_algebraic()} (sequence of {len(sequence_entry['sequence'])} moves)")
                    mate_score = 19999 - sequence_entry['moves_to_mate'] if current_player == 'white' else -19999 + sequence_entry['moves_to_mate']
                    return SearchResult(first_move, mate_score, depth)
        
        moves = self._get_ordered_moves(board, current_player)
        
        if not moves:
            # No legal moves available
            if board.in_check_king(current_player):
                # Checkmate - bad for current player
                # Use consistent mate scoring with distance preference
                mate_distance = self.max_depth - depth  # Distance from root
                if current_player == 'white':
                    # White is checkmated (bad for white)
                    score = -19999 + mate_distance
                else:
                    # Black is checkmated (good for white)
                    score = 19999 - mate_distance
            else:
                # Stalemate
                score = 0
            return SearchResult(None, score, depth)
        
        # Quick check for immediate checkmate at root level
        if depth == self.max_depth:  # Only at root level to avoid overhead
            for piece, move in moves[:5]:  # Check first 5 moves from ordering (which prioritizes checkmates)
                move_info = board.make_move_fast(piece, move)
                try:
                    opponent_color = 'black' if current_player == 'white' else 'white'
                    if board.is_checkmate(opponent_color):
                        # Found immediate checkmate!
                        mate_score = 19999 if current_player == 'white' else -19999
                        print(f"🎯 IMMEDIATE CHECKMATE FOUND: {move.to_algebraic()} (score: {mate_score/100.0:+.2f})")
                        return SearchResult(move, mate_score, depth)
                finally:
                    board.unmake_move_fast(piece, move, move_info)
        
        if self.debug_mode:
            print(f"\n{'='*60}")
            print(f"AI Evaluation Debug - {current_player.upper()} to move")
            print(f"Analyzing {len(moves)} possible moves at depth {depth}")
            print(f"{'='*60}")
        
        move_evaluations = []  # Store move evaluations for debug display (only if debug enabled)
        
        for i, (piece, move) in enumerate(moves):
            if self._should_stop():
                raise TimeoutError("Search time limit exceeded")
            
            # Use fast make/unmake instead of board copying
            move_info = board.make_move_fast(piece, move)
            
            try:
                # BLUNDER PREVENTION: Check for hanging pieces at root level (balanced approach)
                if depth >= self.max_depth - 1:  # At or near root level
                    post_move_hanging = Evaluation.evaluate_hanging_pieces(board)
                    
                    # Only reject moves that hang pieces worth 2+ pawns (more conservative than before)
                    hanging_threshold = 200  # 2 pawns instead of 2.5
                    if current_player == 'white' and post_move_hanging < -hanging_threshold:
                        board.unmake_move_fast(piece, move, move_info)
                        continue
                    elif current_player == 'black' and post_move_hanging > hanging_threshold:
                        board.unmake_move_fast(piece, move, move_info)
                        continue
                
                # After making the move, continue search with proper alpha-beta bounds
                if current_player == 'white':
                    # White made a move, now it's black's turn to respond (minimize)
                    score = self._minimax(board, depth - 1, alpha, beta, False, allow_null=True)
                    
                    move_score = score  # Store the score for debug display
                    
                    if score > best_score:
                        best_score = score
                        best_move = move
                        # Only update alpha for search efficiency - always update in non-debug mode
                        # Note: In debug mode we disabled alpha-beta updates to get individual scores
                        # but this may be causing search inconsistencies
                        alpha = max(alpha, score)
                else:
                    # Black made a move, now it's white's turn to respond (maximize)  
                    score = self._minimax(board, depth - 1, alpha, beta, True, allow_null=True)
                    
                    move_score = score  # Store the score for debug display
                    
                    if score < best_score:
                        best_score = score
                        best_move = move
                        # Only update beta for search efficiency - always update in non-debug mode
                        # Note: In debug mode we disabled alpha-beta updates to get individual scores  
                        # but this may be causing search inconsistencies
                        beta = min(beta, score)
                
                # Store for debug display
                if self.debug_mode:
                    move_str = f"{piece.name.capitalize()}{chr(97 + move.initial.col)}{8 - move.initial.row}-{chr(97 + move.final.col)}{8 - move.final.row}"
                    if move.captured:
                        move_str += f"x{move.captured.name}"
                    
                    # IMPORTANT: Get evaluation breakdown BEFORE undoing the move
                    # Use move_score (individual) instead of score (potentially modified by alpha-beta)
                    # The 'components' will show the evaluation at the current position after this move
                    components = Evaluation.evaluate_debug(board)
                    
                    # Verify accuracy
                    verification = Evaluation.verify_debug_accuracy(board)
                    if not verification['matches']:
                        # Check for discrepancy
                        actual_score = verification['actual_score']
                        debug_total = components.get('total', 0)
                        discrepancy = abs(actual_score - debug_total)
                        tolerance = 0.01
                        
                        if discrepancy > tolerance:
                            error_msg = f"MISMATCH: Actual={actual_score:.3f}, Debug={debug_total:.3f}, Diff={discrepancy:.3f}"
                            print(f"⚠️ DEBUG ACCURACY WARNING for {move_str}: {error_msg}")
                    
                    move_evaluations.append({
                        'move': move_str,
                        'move_obj': move,  # Store the actual move object for comparison
                        'piece': piece,
                        'score': move_score,  # Use individual move score, not alpha-beta modified score
                        'components': components,  # This is static evaluation of current position
                        'is_best': False,  # Will be updated after all moves are evaluated
                        'verification': verification,
                        'depth_used': depth  # Track what depth this score came from
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
        
        # Mark the actual best move in debug data
        if self.debug_mode and move_evaluations and best_move:
            for eval_data in move_evaluations:
                # Compare moves properly
                if (eval_data['move_obj'].initial.row == best_move.initial.row and
                    eval_data['move_obj'].initial.col == best_move.initial.col and
                    eval_data['move_obj'].final.row == best_move.final.row and
                    eval_data['move_obj'].final.col == best_move.final.col):
                    eval_data['is_best'] = True
                    break
        
        # Display debug information
        if self.debug_mode and move_evaluations and best_move:
            self._display_move_evaluations(move_evaluations, current_player, best_move)
        
        # SOLUTION 7: Store mate sequences for future use
        if best_move and abs(best_score) >= 19990:  # Mate found
            mate_distance = 19999 - abs(best_score)
            if mate_distance <= 5:  # Only cache short mate sequences
                sequence = self._extract_mate_sequence(board, best_move, current_player, int(mate_distance))
                if sequence:
                    self.mate_sequences[board_hash] = {
                        'moves_to_mate': mate_distance,
                        'sequence': sequence,
                        'validated': True
                    }
                    print(f"💾 CACHING MATE SEQUENCE: {len(sequence)} moves starting with {best_move.to_algebraic()}")
        
        # Store the result in transposition table with best move
        board_hash = hash(str(board.squares))
        self._store_transposition_simple(board_hash, depth, best_score, best_move)
        
        # Return the score from the correct perspective
        # Since evaluation is always from white's perspective, we need to return
        # the score as-is (it's already in the right perspective)
        return SearchResult(best_move, best_score, depth)
    
    def _minimax(self, board: Board, depth: int, alpha: float, beta: float, maximizing: bool, allow_null: bool = True, extension_count: int = 0) -> float:
        """
        Minimax algorithm with alpha-beta pruning, null move pruning, and late move reductions.
        
        Args:
            board: Current board position
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing: True if maximizing player (white), False for minimizing (black)
            allow_null: True if null move pruning is allowed (prevents double null moves)
            extension_count: Number of extensions already applied (prevents infinite extension)
            
        Returns:
            Evaluation score of the position
        """
        self.nodes_searched += 1
        
        # FAIL-SAFE: Prevent infinite recursion
        if depth < 0:
            return Evaluation.evaluate(board)
        
        # Check transposition table
        board_hash = self._hash_board_fast(board)
        # Re-enabled transposition table for performance
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                return entry['score']  # Simple exact match only for speed
        
        # Terminal conditions
        if depth == 0:
            # CRITICAL: Always use the main evaluation function that includes hanging pieces
            # This ensures consistency between search and static evaluation
            # DISABLED: quiescence search for debugging - it was causing evaluation inconsistencies
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
                # Score mate based on distance: faster mates are better
                mate_distance = self.max_depth - depth  # How many moves from root to mate
                
                if maximizing:
                    # White is in checkmate (bad for white)
                    # Use negative score, with faster mates being worse (more negative)
                    score = -19999 + mate_distance  # Mate in 1 = -19999, mate in 2 = -19998, etc.
                else:
                    # Black is in checkmate (good for white)  
                    # Use positive score, with faster mates being better (more positive)
                    score = 19999 - mate_distance   # Mate in 1 = 19999, mate in 2 = 19998, etc.
                
                self._store_transposition_simple(board_hash, depth, score)
                return score
            else:
                self._store_transposition_simple(board_hash, depth, 0)
                return 0  # Stalemate or draw
        
        # Null Move Pruning - Balanced approach (not too aggressive)
        current_player = 'white' if maximizing else 'black'
        in_check = board.in_check_king(current_player)
        
        if (allow_null and 
            depth >= 3 and  # Restored to depth >= 3 for better decision quality
            not in_check and 
            not self._is_endgame(board)):
            
            # Get current evaluation to see if position is promising
            current_eval = Evaluation.evaluate(board)
            # Convert to current player's perspective
            if not maximizing:  # Black's turn
                current_eval = -current_eval
            
            # Conservative beta cutoff threshold (restored)
            if current_eval >= beta:
                # Make null move
                original_player = self._make_null_move(board)
                
                try:
                    # Search with moderate reduction for balanced speed/accuracy
                    reduction = 3  # Fixed reduction instead of aggressive variable reduction
                    null_score = self._minimax(board, depth - reduction, -beta, -beta + 1, not maximizing, allow_null=False, extension_count=extension_count)
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
                    eval_score = self._minimax(board, search_depth, alpha, beta, False, allow_null=True, extension_count=extension_count)
                    
                    # Hanging pieces are already evaluated in Evaluation.evaluate()
                    
                    # LMR Re-search: Only if we got a really good score and used reduction
                    if reduction > 0 and eval_score > alpha and search_depth < depth - 1:
                        # Re-search at full depth if the reduced search found a good move
                        full_eval_score = self._minimax(board, depth - 1, alpha, beta, False, allow_null=True)
                        eval_score = full_eval_score
                    
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
                    eval_score = self._minimax(board, search_depth, alpha, beta, True, allow_null=True, extension_count=extension_count)
                    
                    # Hanging pieces are already evaluated in Evaluation.evaluate()
                    
                    # LMR Re-search: Only if we got a really good score and used reduction
                    if reduction > 0 and eval_score < beta and search_depth < depth - 1:
                        # Re-search at full depth if the reduced search found a good move
                        full_eval_score = self._minimax(board, depth - 1, alpha, beta, True, allow_null=True)
                        eval_score = full_eval_score
                    
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
        """Ultra-fast board hash using bit operations."""
        hash_val = 0
        shift = 0
        
        # More efficient hashing using bit operations
        for row in range(8):
            for col in range(8):
                square = board.squares[row][col]
                if square.has_piece and square.piece:
                    piece = square.piece
                    # Combine piece type (3 bits) + color (1 bit) + position (6 bits) = 10 bits per piece
                    piece_code = (1 if piece.name == 'pawn' else 
                                2 if piece.name == 'knight' else 
                                3 if piece.name == 'bishop' else 
                                4 if piece.name == 'rook' else 
                                5 if piece.name == 'queen' else 6)
                    color_bit = 0 if piece.color == 'white' else 8
                    position = row * 8 + col
                    
                    piece_hash = (piece_code | color_bit) << shift
                    hash_val ^= piece_hash ^ (position << (shift + 4))
                    shift = (shift + 10) % 64  # Rotate shift to spread bits
        
        # Include turn with a simple bit flip
        if board.next_player == 'black':
            hash_val ^= 0x5555555555555555  # XOR with pattern
            
        return hash_val
    
    def _store_transposition_simple(self, board_hash: int, depth: int, score: float, best_move: Optional[Move] = None):
        """Enhanced transposition table storage with mate support (Solution 4)."""
        # Re-enabled transposition table storage for performance
        # Only store if table isn't too big
        if len(self.transposition_table) < 50000:
            entry = {
                'depth': depth,
                'score': score,
                'best_move': best_move
            }
            
            # SOLUTION 4: Enhanced transposition table with mate flags
            if abs(score) >= 19990:  # Mate score detected
                mate_distance = 19999 - abs(score)
                entry['flag'] = 'EXACT_MATE'
                entry['mate_distance'] = mate_distance
                
                # SOLUTION 1: Store in mate cache for instant lookup
                self.mate_cache[board_hash] = {
                    'score': score,
                    'depth': depth,
                    'mate_distance': mate_distance,
                    'best_move': best_move
                }
                
                if best_move:
                    print(f"💾 CACHING MATE: {best_move.to_algebraic()} (mate in {mate_distance})")
            
            self.transposition_table[board_hash] = entry
    
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
        
        # DEBUG: Track quiescence search decisions
        if depth == 0 and abs(stand_pat) > 200:  # Only debug significant positions
            current_player = 'white' if maximizing else 'black'
            print(f"🔍 Q-Search DEBUG (depth {depth}, {current_player}): stand_pat = {stand_pat/100.0:+.2f}")
            captures = self._get_capture_moves_simple(board, current_player)
            print(f"  📊 Found {len(captures)} captures: {[move.to_algebraic() for piece, move in captures[:5]]}")
        
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
                
                # DEBUG: Track if this capture improved the score significantly
                if depth == 0 and abs(stand_pat) > 200:  # Only debug significant positions
                    improvement = score - stand_pat if maximizing else stand_pat - score
                    if improvement > 100:  # More than 1 pawn improvement
                        print(f"  🎯 Capture {move.to_algebraic()}: {stand_pat/100.0:+.2f} → {score/100.0:+.2f} (improvement: {improvement/100.0:+.2f})")
                        
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
        
        final_result = alpha if maximizing else beta
        
        # DEBUG: Show final quiescence result
        if depth == 0 and abs(stand_pat) > 200:  # Only debug significant positions
            improvement = final_result - stand_pat if maximizing else stand_pat - final_result
            if abs(improvement) > 50:  # Significant change
                print(f"  🏁 Q-Search FINAL: {stand_pat/100.0:+.2f} → {final_result/100.0:+.2f} (change: {improvement/100.0:+.2f})")
            
        return final_result
    
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
        """FAST move ordering prioritizing checkmate, good captures and tactical moves."""
        moves = board.get_all_moves(color)
        
        if not moves:
            return []
        
        # Check for immediate checkmate moves first
        checkmate_moves = []
        captures = []
        non_captures = []
        
        for piece, move in moves:
            # Test if this move delivers checkmate
            move_info = board.make_move_fast(piece, move)
            try:
                opponent_color = 'black' if color == 'white' else 'white'
                if board.is_checkmate(opponent_color):
                    # This move delivers checkmate - highest priority!
                    checkmate_moves.append((piece, move))
                    board.unmake_move_fast(piece, move, move_info)
                    continue
            finally:
                board.unmake_move_fast(piece, move, move_info)
            
            # Not a checkmate move, categorize normally
            if move.captured:
                # Quick SEE evaluation - only for clearly winning/losing captures
                captured_value = self._get_piece_value(move.captured.name)
                attacker_value = self._get_piece_value(piece.name)
                
                # Simple heuristic: if we're capturing something more valuable, prioritize
                if captured_value >= attacker_value:
                    score = captured_value * 10 + (1000 - attacker_value)  # MVV-LVA
                    captures.append((score, piece, move))
                else:
                    # For questionable captures, do proper SEE but cache results
                    see_value = SEE.evaluate_capture(board, move)
                    score = see_value + captured_value  # Combine SEE with capture value
                    captures.append((score, piece, move))
            else:
                # Quick scoring for non-captures
                score = self._score_quiet_move_fast(board, piece, move)
                non_captures.append((score, piece, move))
        
        # Sort by score (best first)
        captures.sort(reverse=True, key=lambda x: x[0])
        non_captures.sort(reverse=True, key=lambda x: x[0])
        
        # Return checkmate moves first, then captures, then non-captures
        result = []
        # Checkmate moves have absolute priority
        for piece, move in checkmate_moves:
            result.append((piece, move))
        # Then good captures
        for _, piece, move in captures:
            result.append((piece, move))
        # Finally quiet moves
        for _, piece, move in non_captures:
            result.append((piece, move))
        
        return result
    
    def _score_quiet_move_fast(self, board: Board, piece: Piece, move: Move) -> int:
        """Fast scoring for non-capture moves."""
        score = 0
        
        # Center control bonus (quick check)
        row, col = move.final.row, move.final.col
        if 2 <= row <= 5 and 2 <= col <= 5:
            score += 20
            
        # Castling bonus
        if piece.name == 'king' and abs(move.final.col - move.initial.col) == 2:
            score += 50
            
        # Development bonus (only check if piece is on back rank)
        if piece.name in ['knight', 'bishop']:
            if (piece.color == 'white' and move.initial.row == 7) or \
               (piece.color == 'black' and move.initial.row == 0):
                score += 15
                
        return score
    
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
        Balanced approach for good performance without sacrificing decision quality.
        """
        if is_dangerous or move_index < 4:  # Don't reduce first 4 moves or dangerous moves
            return 0
        
        if depth < 3:  # Don't reduce in shallow searches
            return 0
        
        # Conservative reduction to maintain decision quality
        if move_index < 8:
            return 1  # Small reduction for moves 4-7
        elif move_index < 16:
            return 2  # Medium reduction for moves 8-15
        else:
            return min(2, depth // 3)  # Limited reduction for later moves
    
    def _make_null_move(self, board: Board) -> str:
        """Make a null move (just switch the current player)."""
        original_player = board.next_player
        board.next_player = 'black' if board.next_player == 'white' else 'white'
        return original_player
    
    def _unmake_null_move(self, board: Board, original_player: str) -> None:
        """Unmake a null move (restore the original player)."""
        board.next_player = original_player
    
    def _display_move_evaluations(self, move_evaluations: List[dict], current_player: str, best_move: Move):
        """Display enhanced evaluation breakdown for each move with complete transparency."""
        print(f"\n" + "="*100)
        print(f"🔍 DETAILED AI EVALUATION BREAKDOWN - {current_player.upper()} TO MOVE")
        print(f"="*100)
        
        # Sort moves by score (best first for current player)
        if current_player == 'white':
            move_evaluations.sort(key=lambda x: x['score'], reverse=True)
        else:
            move_evaluations.sort(key=lambda x: x['score'])
        
        # Show the best move's complete breakdown first
        if move_evaluations:
            best_eval = next((eval_data for eval_data in move_evaluations if eval_data.get('is_best', False)), move_evaluations[0])
            components = best_eval['components']
            
            print(f"\n🌟 BEST MOVE: {best_eval['move']} (Score: {best_eval['score']/100.0:+.2f})")
            game_phase = str(components.get('game_phase', 'unknown')).upper()
            print(f"Game Phase: {game_phase}")
            print("-" * 100)
            
            # Create detailed breakdown table
            print(f"{'Component':<20} {'Raw Value':<12} {'Weight':<8} {'Weighted':<12} {'Impact':<10}")
            print("-" * 100)
            
            total_weighted = components.get('total', 0)
            
            # Show each component with its contribution
            eval_components = [
                ('Material', 'raw_material', 'weight_material', 'material'),
                ('Position', 'raw_position', 'weight_position', 'position'),
                ('King Safety', 'raw_king_safety', 'weight_king_safety', 'king_safety'),
                ('Tempo Penalty', 'raw_tempo_penalty', 'weight_tempo_penalty', 'tempo_penalty'),
                ('Hanging Pieces', 'raw_hanging_pieces', 'weight_hanging_pieces', 'hanging_pieces'),
                ('Pawn Structure', 'raw_pawn_structure', 'weight_pawn_structure', 'pawn_structure'),
                ('Piece Coordination', 'raw_piece_coordination', 'weight_piece_coordination', 'piece_coordination'),
                ('Piece Activity', 'raw_piece_activity', 'weight_piece_activity', 'piece_activity'),
                ('Tactical Themes', 'raw_tactical_enhanced', 'weight_tactical_enhanced', 'tactical_enhanced'),
                ('Space Control', 'raw_space_control', 'weight_space_control', 'space_control'),
                ('Opening Principles', 'raw_opening', 'weight_opening', 'opening'),
                ('Endgame Factors', 'raw_endgame', 'weight_endgame', 'endgame')
            ]
            
            # Add rescue bonus if present
            if 'rescue_bonus' in components and components['rescue_bonus'] != 0:
                eval_components.append(('Piece Rescue Bonus', 'rescue_bonus', 'rescue_bonus', 'rescue_bonus'))
            
            for name, raw_key, weight_key, final_key in eval_components:
                # Special handling for rescue bonus (it doesn't have separate raw/weight)
                if name == 'Piece Rescue Bonus':
                    final_val = components.get('rescue_bonus', 0)
                    raw_val = final_val  # Same value
                    weight = 1.0  # Always applied fully
                else:
                    raw_val = components.get(raw_key, 0)
                    weight = components.get(weight_key, 0)
                    final_val = components.get(final_key, 0)
                
                # Skip components with zero weight and zero final value
                if weight == 0 and final_val == 0:
                    continue
                    
                # Calculate percentage impact
                impact_pct = (abs(final_val) / abs(total_weighted) * 100) if total_weighted != 0 else 0
                
                # Color code significant impacts
                impact_str = f"{impact_pct:.1f}%"
                if impact_pct > 20:
                    impact_str = f"🔴 {impact_str}"
                elif impact_pct > 10:
                    impact_str = f"🟡 {impact_str}"
                elif impact_pct > 5:
                    impact_str = f"🟢 {impact_str}"
                
                print(f"{name:<20} {raw_val/100.0:+11.2f} {weight:7.1f} {final_val/100.0:+11.2f} {impact_str:<10}")
            
            print("-" * 100)
            print(f"{'TOTAL':<20} {components.get('total_raw', 0)/100.0:+11.2f} {'N/A':<7} {total_weighted/100.0:+11.2f} {'100.0%':<10}")
            
            # Verification check
            manual_total = sum(components.get(final_key, 0) for _, _, _, final_key in eval_components)
            if abs(manual_total - total_weighted) > 0.01:
                print(f"⚠️  WARNING: Total mismatch! Manual: {manual_total/100.0:+.2f}, Reported: {total_weighted/100.0:+.2f}")
            
            # Show verification status for this move
            verification = best_eval.get('verification', {})
            if not verification.get('matches', True):
                print(f"⚠️  VERIFICATION WARNING: {verification.get('error_message', 'Unknown mismatch')}")
            else:
                print(f"✅ Verification: Debug breakdown matches actual evaluation")
        
        # Now show summary table of all moves
        print(f"\n📊 MOVE COMPARISON TABLE:")
        print(f"{'Move':<15} {'Minimax':<8} {'Static':<8} {'Material':<9} {'Hanging':<9} {'Position':<9} {'Tactical':<9} {'King':<8} {'Rescue':<8}")
        print("-" * 110)
        
        # Count how many moves are marked as best (should be exactly 1)
        best_count = sum(1 for eval_data in move_evaluations if eval_data.get('is_best', False))
        if best_count != 1:
            print(f"⚠️ DEBUG WARNING: {best_count} moves marked as best (should be 1)")
        
        for i, eval_data in enumerate(move_evaluations[:8]):  # Show top 8 moves
            move_str = eval_data['move']
            components = eval_data['components']
            
            minimax_score = eval_data['score'] / 100.0  # Minimax search result
            static_score = components.get('total', 0) / 100.0  # Static evaluation
            material = components.get('material', 0) / 100.0
            hanging = components.get('hanging_pieces', 0) / 100.0
            position = components.get('position', 0) / 100.0
            tactical = components.get('tactical_enhanced', 0) / 100.0
            king_safety = components.get('king_safety', 0) / 100.0
            rescue_bonus = components.get('rescue_bonus', 0) / 100.0
            
            # Mark the best move (should be exactly one)
            if eval_data.get('is_best', False):
                marker = " ⭐"
            else:
                marker = f" #{i+1}"
            
            print(f"{move_str:<15} {minimax_score:+7.2f} {static_score:+7.2f} {material:+8.2f} {hanging:+8.2f} {position:+8.2f} {tactical:+8.2f} {king_safety:+7.2f} {rescue_bonus:+7.2f}{marker}")
        
        # Show additional debug info about the best move
        best_eval_data = next((eval_data for eval_data in move_evaluations if eval_data.get('is_best', False)), None)
        if best_eval_data:
            print(f"\n🔍 BEST MOVE ANALYSIS:")
            print(f"   Move: {best_eval_data['move']}")
            print(f"   Static Eval (components): {best_eval_data['components'].get('total', 0)/100.0:+.2f}")
            print(f"   Minimax Score (depth {best_eval_data.get('depth_used', '?')}): {best_eval_data['score']/100.0:+.2f}")
            
            # Check if they match (they usually won't for deep searches)
            score_diff = abs(best_eval_data['components'].get('total', 0) - best_eval_data['score'])
            if score_diff > 0.01:
                print(f"   📊 Score difference: {score_diff/100.0:.2f}")
                print(f"   💡 This is normal - minimax looks ahead, static eval is immediate position")
            else:
                print(f"   ✅ Scores match (unusual for depth > 1)")
        
        print(f"\n💡 EVALUATION NOTES:")
        depth_info = best_eval_data.get('depth_used', '?') if best_eval_data else '?'
        print(f"   • Minimax column: Score after looking ahead {depth_info} moves (AI uses this)")
        print(f"   • Static column: Immediate evaluation of position after move")
        print(f"   • Material/Hanging/etc: Components of the static evaluation")
        print(f"   • ⭐ = AI's chosen move based on minimax score, not static eval")
        print(f"   • Large differences between Minimax and Static reveal tactical themes!")
        print("="*100)

    def _calculate_piece_rescue_bonus(self, board: Board, piece: Piece, move: Move, current_player: str, depth: int = 0) -> float:
        """
        Calculate bonus for moves that save hanging pieces.
        
        Args:
            board: Current board position (after the move)
            piece: The piece that was moved
            move: The move that was made
            current_player: The player who made the move
            depth: Current search depth (for depth-based multiplier)
            
        Returns:
            Bonus score for rescuing a hanging piece
        """
        # Check if the piece was hanging in its original position
        original_row, original_col = move.initial.row, move.initial.col
        
        # Temporarily put the piece back to check if it was hanging
        current_square = board.squares[move.final.row][move.final.col]
        original_square = board.squares[original_row][original_col]
        
        # Temporarily restore original position
        original_square.piece = piece
        current_square.piece = move.captured  # Restore captured piece if any
        
        # Check if piece was hanging in original position
        was_hanging = Evaluation._is_piece_hanging_at_position(board, piece, original_row, original_col)
        
        # Restore current position
        current_square.piece = piece
        original_square.piece = None
        
        if not was_hanging:
            return 0.0  # Piece wasn't hanging originally, no rescue bonus
        
        # Check if piece is safe in new position
        is_now_safe = not Evaluation._is_piece_hanging_at_position(board, piece, move.final.row, move.final.col)
        
        if is_now_safe:
            # Piece was successfully rescued!
            piece_value = Evaluation.SEE_PIECE_VALUES.get(piece.name, 100)
            base_rescue_bonus = piece_value * 0.4  # 40% of piece value as base rescue bonus
            
            # Apply depth-based multiplier - stronger influence at shallow depths (near root)
            # depth = 0 is leaf nodes, higher depth = closer to root
            if depth is not None and hasattr(self, 'max_depth'):
                # Create a multiplier that goes from 0.2 at depth=0 to 1.0 at max_depth
                depth_ratio = min(depth / max(self.max_depth, 1), 1.0)
                depth_multiplier = 0.2 + (0.8 * depth_ratio)  # Range: 0.2 to 1.0
            else:
                depth_multiplier = 1.0  # Full strength if depth not provided
            
            rescue_bonus = base_rescue_bonus * depth_multiplier
            
            # Apply bonus from the perspective of the moving player
            if current_player == 'white':
                return rescue_bonus  # Positive for white
            else:
                return -rescue_bonus  # Negative for white (black rescued a piece)
        
        return 0.0  # Piece moved but is still hanging
    
    def _is_move_legal(self, board: Board, move: Move, color: str) -> bool:
        """Quick check if a move is legal for the given color."""
        if not move or not move.initial or not move.final:
            return False
        
        # Check if there's a piece of the right color at the initial square
        initial_square = board.squares[move.initial.row][move.initial.col]
        if not initial_square.has_piece or not initial_square.piece:
            return False
        
        if initial_square.piece.color != color:
            return False
        
        # Check if move is in the piece's legal moves
        piece = initial_square.piece
        board.calc_moves(piece, move.initial.row, move.initial.col, filter_checks=True)
        
        # Check if this specific move is in the piece's legal moves
        for legal_move in piece.moves:
            if (legal_move.initial.row == move.initial.row and 
                legal_move.initial.col == move.initial.col and
                legal_move.final.row == move.final.row and 
                legal_move.final.col == move.final.col):
                return True
        
        return False
    
    def _extract_mate_sequence(self, board: Board, first_move: Move, color: str, max_moves: int) -> List[Move]:
        """Extract the mate sequence by performing a shallow search (Solution 7)."""
        sequence = [first_move]
        
        # Make a copy of the board to explore the sequence
        temp_board = Board()
        temp_board.squares = [[sq for sq in row] for row in board.squares]
        temp_board.next_player = board.next_player
        temp_board.last_move = board.last_move
        
        # Try to play out the sequence
        current_color = color
        for move_count in range(max_moves):
            if move_count >= len(sequence):
                break
                
            move = sequence[move_count]
            
            # Verify the move is still legal
            piece = temp_board.squares[move.initial.row][move.initial.col].piece
            if not piece or piece.color != current_color:
                break
            
            # Make the move
            move_info = temp_board.make_move_fast(piece, move)
            
            # Check if this results in checkmate
            opponent_color = 'black' if current_color == 'white' else 'white'
            if temp_board.is_checkmate(opponent_color):
                # Found checkmate, sequence is complete
                break
            
            # If not checkmate, try to find the opponent's best response and our continuation
            if move_count < max_moves - 1:
                # Quick search for forced continuation
                opponent_moves = temp_board.get_all_moves(opponent_color)
                if len(opponent_moves) == 1:
                    # Forced move for opponent
                    opp_piece, opp_move = opponent_moves[0]
                    temp_board.make_move_fast(opp_piece, opp_move)
                    
                    # Now find our next move
                    our_moves = temp_board.get_all_moves(current_color)
                    for our_piece, our_move in our_moves:
                        test_info = temp_board.make_move_fast(our_piece, our_move)
                        final_opponent_color = 'black' if current_color == 'white' else 'white'
                        if temp_board.is_checkmate(final_opponent_color):
                            # Found the next move in the sequence
                            sequence.append(opp_move)
                            sequence.append(our_move)
                            temp_board.unmake_move_fast(our_piece, our_move, test_info)
                            break
                        temp_board.unmake_move_fast(our_piece, our_move, test_info)
                    break
            
            current_color = opponent_color
        
        return sequence
