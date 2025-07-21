import pygame as p
from typing import Optional

from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square
from move import Move
from piece import Queen, Rook, Bishop, Knight, Pawn, Piece
from AI import AI
from fen import FEN

class Game:
    """
    Main game controller that manages the chess game state, player interactions,
    AI opponent, and visual rendering. Handles move validation, game ending conditions,
    and provides interfaces for both human and computer players.
    """
    next_player: str
    selected_square: Optional[Square]
    game_over: bool
    end_message: str
    draw_offered: bool
    ai: Optional[AI]
    ai_enabled: bool
    board: Board
    dragger: Dragger
    config: Config
    fen_history: list[str]
    redo_history: list[str]  # Track undone positions for redo functionality

    def __init__(self):
        self.next_player = 'white'  # White always moves first in chess
        self.selected_square: Optional[Square] = None  # Currently selected square for piece movement
        self.game_over = False
        self.end_message = ""
        self.draw_offered = False
        self.ai: Optional[AI] = None  # Don't create AI until after color prompt
        self.ai_enabled = False  # AI opponent disabled by default
        self.ai_is_thinking = False  # Flag to prevent mouse handler from triggering during AI moves
        self.ai_thinking_cooldown = 0  # Frame counter to delay flag clearing
        self.ai_has_moved_initially = False  # Flag to track if AI has made its first move
        self.in_book = True  # Track if both players are still following book moves
        self.AI_color_prompt()  # Let user choose AI color - creates AI here
        self.board = Board()
        # Set up the standard starting position
        self.board.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.dragger = Dragger()  # Handles drag-and-drop piece movement
        self.config = Config()  # Visual themes and settings
        self.fen_history: list[str] = []  # Track position history for threefold repetition
        self.redo_history: list[str] = []  # Track undone positions for redo functionality
        self.record_fen()
        
    def update_book_status_after_human_move(self):
        """Check if the current position is still in the opening book after a human move."""
        if self.ai and self.in_book:
            current_fen = FEN.get_fen(self.board)
            if not self.ai.opening_book.is_in_book(current_fen):
                self.in_book = False

    @property
    def theme_name(self) -> Optional[str]:
        """Get the current visual theme name for piece textures."""
        return getattr(self.config.theme, "name", None)

    def show_bg(self, surface) -> None:
        """
        Draw the chess board background with alternating light and dark squares.
        Also draws rank numbers (1-8) and file letters (a-h) for reference.
        """
        theme = self.config.theme
        font = self.config.font
        
        for row in range(ROWS):
            for col in range(COLS):
                # Alternate square colors in checkerboard pattern
                color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                rect = (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                p.draw.rect(surface, color, rect)

                # Draw rank numbers (1-8) on the left edge
                if col == 0:
                    label = font.render(str(ROWS - row), True, (0, 0, 0))
                    surface.blit(label, (5, row * SQ_SIZE + 5))

                # Draw file letters (a-h) on the bottom edge
                if row == ROWS - 1:
                    from square import Square  # Local import to avoid circular dependency
                    label = font.render(Square.ALPHACOLS[col], True, (0, 0, 0))
                    surface.blit(label, (col * SQ_SIZE + SQ_SIZE - 20, HEIGHT - 25))

    def show_highlight(self, surface, squares, color, alpha=160) -> None:
        """
        Draw colored highlights on specified squares.
        Used for showing selected pieces, valid moves, checks, etc.
        """
        for square in squares:
            row, col = square.row, square.col
            highlight_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            highlight_surface.fill((*color, alpha))  # Color with transparency
            surface.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))

    def show_pieces(self, surface) -> None:
        """
        Render all pieces on the board using the current theme.
        Skips the piece being dragged (shown separately by dragger).
        """
        for row in range(ROWS):
            for col in range(COLS):
                square = self.board.squares[row][col]
                if square.has_piece and square.piece is not None:
                    piece = square.piece
                    # Don't draw the piece being dragged here
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80, theme_name=self.theme_name)
                        img = p.image.load(piece.texture)
                        img_center = col * SQ_SIZE + SQ_SIZE // 2, row * SQ_SIZE + SQ_SIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface) -> None:
        """
        Highlight all valid moves for the currently dragged piece.
        Provides visual feedback to help players see legal moves.
        """
        if not (self.dragger.dragging and self.dragger.piece):
            return
        
        color = self.config.theme.move_highlight
        for move in self.dragger.piece.moves:
            row, col = move.final.row, move.final.col
            highlight_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            highlight_surface.fill((*color, 120))  # Semi-transparent highlight
            surface.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))

    def show_last_move(self, surface) -> None:
        """
        Highlight the squares involved in the last move made.
        Helps players track the game progression and opponent moves.
        """
        if not self.board.last_move:
            return
        theme = self.config.theme
        squares = [self.board.last_move.initial, self.board.last_move.final]
        for square in squares:
            row, col = square.row, square.col
            color = theme.trace.light if (row + col) % 2 == 0 else theme.trace.dark
            highlight_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            highlight_surface.fill((*color, 160))
            surface.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))

    def show_selected(self, surface) -> None:
        """
        Highlight the currently selected square where a piece is chosen to move from.
        Provides clear indication to the player about their current selection.
        """
        if not self.selected_square:
            return
        row, col = self.selected_square.row, self.selected_square.col
        color = self.config.theme.selected.light if (row + col) % 2 == 0 else self.config.theme.selected.dark
        highlight_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
        highlight_surface.fill((*color, 160))
        surface.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))

    def show_hover(self, surface, mouse_pos) -> None:
        """
        Show a visual cue on the square under the mouse cursor.
        Helps players identify where a piece will be dropped if dragged.
        """
        col = mouse_pos[0] // SQ_SIZE
        row = mouse_pos[1] // SQ_SIZE
        color = self.config.theme.moves.light if (row + col) % 2 == 0 else self.config.theme.moves.dark
        rect = (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(surface, color, rect, 3)

    def show_check(self, surface) -> None:
        """
        Draw a visual indicator (red ellipse) around the king if it's in check.
        Provides a critical alert to the player about the king's safety.
        """
        for row in range(ROWS):
            for col in range(COLS):
                square = self.board.squares[row][col]
                if square.has_piece and square.piece is not None:
                    piece = square.piece
                    if piece.name == 'king' and piece.color == self.next_player:
                        if self.board.in_check_king(piece.color):
                            shadow_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                            p.draw.ellipse(shadow_surface, (255, 0, 0, 100), (8, 16, SQ_SIZE - 16, SQ_SIZE - 32))
                            surface.blit(shadow_surface, (col * SQ_SIZE, row * SQ_SIZE))
                        return

    def next_turn(self) -> None:
        """Switch the active player from white to black or black to white."""
        old_player = self.next_player
        self.next_player = 'white' if self.next_player == 'black' else 'black'
        self.board.next_player = self.next_player  # Keep board in sync
        
        # Reset AI moves counter when switching away from AI's turn
        if hasattr(self, '_ai_moves_this_turn'):
            if self.ai and self.next_player != self.ai.color:
                self._ai_moves_this_turn = 0

    def change_theme(self) -> None:
        """Cycle through available themes for the chess board and pieces."""
        self.config.change_themes()
    
    def play_sound(self, captured: bool=False) -> None:
        """
        Play sound effect for a move.
        Distinguishes between regular move sound and capture sound.
        """
        (self.config.capture_sound if captured else self.config.move_sound).play()

    def restart(self) -> None:
        """Reset the game to the initial starting position."""
        self.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def fen_without_clocks(self, fen: str) -> str:
        """
        Remove the move counters from the end of the FEN string.
        Returns the FEN string without the halfmove and fullmove fields.
        """
        return ' '.join(fen.split()[:4])

    def record_fen(self):
        """
        Record the current board position in FEN format to the history.
        This allows undo functionality and threefold repetition detection.
        """
        fen = FEN.get_fen(self.board)
        self.fen_history.append(fen)  # Store complete FEN for undo functionality
        # Clear redo history when a new move is made
        self.redo_history.clear()

    def count_fen_occurrences(self, fen: str) -> int:
        """
        Count how many times a given FEN position (without clocks) has occurred in history.
        Used to detect threefold repetition draws.
        """
        fen_without_clocks = self.fen_without_clocks(fen)
        # Count occurrences in history by comparing without clocks
        count = 0
        for historical_fen in self.fen_history:
            if self.fen_without_clocks(historical_fen) == fen_without_clocks:
                count += 1
        return count

    def is_threefold_repetition(self) -> bool:
        """
        Check if the current position has occurred three times in the game history.
        This includes the current position and is used to detect draw conditions.
        """
        fen = FEN.get_fen(self.board)
        fen = self.fen_without_clocks(fen)
        return self.count_fen_occurrences(fen) >= 3

    def undo_move(self) -> bool:
        """
        Undo the last move by restoring the previous position from FEN history.
        Returns True if undo was successful, False if no moves to undo.
        """
        # Need at least 2 positions in history (current + previous)
        if len(self.fen_history) < 2:
            print("No moves to undo")
            return False
        
        # Save current position to redo history before undoing
        current_fen = self.fen_history.pop()
        self.redo_history.append(current_fen)
        
        # Get previous position
        previous_fen = self.fen_history[-1]
        
        # Restore the board state without adding to history again
        self.board.set_fen(previous_fen)
        
        # Clear any selected squares and dragging state
        self.selected_square = None
        self.dragger.undrag_piece(theme_name=self.theme_name)
        
        # Update next player based on the restored position
        # The FEN loading should have set board.next_player correctly
        self.next_player = self.board.next_player
        
        # Clear any game over state in case we're undoing the final move
        self.game_over = False
        self.end_message = ""
        self.draw_offered = False
        
        print(f"Move undone. Next player: {self.next_player}. Position restored to: {previous_fen}")
        return True

    def redo_move(self) -> bool:
        """
        Redo a previously undone move by restoring it from the redo history.
        Returns True if redo was successful, False if no moves to redo.
        """
        # Need at least 1 position in redo history
        if len(self.redo_history) < 1:
            print("No moves to redo")
            return False
        
        # Get the next position to redo
        next_fen = self.redo_history.pop()
        
        # Add it back to the main history
        self.fen_history.append(next_fen)
        
        # Restore the board state
        self.board.set_fen(next_fen)
        
        # Clear any selected squares and dragging state
        self.selected_square = None
        self.dragger.undrag_piece(theme_name=self.theme_name)
        
        # Update next player based on the restored position
        self.next_player = self.board.next_player
        
        # Clear any game over state in case we're redoing the final move
        self.game_over = False
        self.end_message = ""
        self.draw_offered = False
        
        print(f"Move redone. Next player: {self.next_player}. Position restored to: {next_fen}")
        return True

    def handle_mouse_down(self, pos) -> None:
        """
        Handle mouse button press events for selecting and dragging pieces.
        Determines which square was clicked and initiates piece dragging if valid.
        """
        # Don't process mouse events during AI moves or shortly after
        if self.ai_is_thinking or self.ai_thinking_cooldown > 0:
            # Clear any remaining events
            import pygame as p
            p.event.clear()
            return
        
        # Don't process mouse events when it's the AI's turn
        if self.ai_enabled and self.ai and self.next_player == self.ai.color:
            return
        
        dragger = self.dragger
        board = self.board
        dragger.update_mouse(pos)
        clicked_row = dragger.mouseY // SQ_SIZE
        clicked_col = dragger.mouseX // SQ_SIZE
        if 0 <= clicked_row < 8 and 0 <= clicked_col < 8:
            square = board.squares[clicked_row][clicked_col]
            if square.has_piece and square.piece is not None and square.piece.color == self.next_player and not dragger.dragging:
                self.selected_square = square
                board.calc_moves(square.piece, clicked_row, clicked_col, filter_checks=True)
                dragger.save_inital(pos)
                dragger.drag_piece(square.piece)
            else:
                self.selected_square = None
                dragger.undrag_piece(theme_name=self.theme_name)
        else:
            self.selected_square = None
            dragger.undrag_piece(theme_name=self.theme_name)

    def handle_mouse_motion(self, pos, surface) -> None:
        """
        Handle mouse motion events during piece dragging.
        Updates the display to show the piece being dragged and its valid movement squares.
        """
        # Don't process mouse events during AI moves or shortly after
        if self.ai_is_thinking or self.ai_thinking_cooldown > 0:
            return
        
        # Don't process mouse events when it's the AI's turn
        if self.ai_enabled and self.ai and self.next_player == self.ai.color:
            return
        
        if self.dragger.dragging:
            self.dragger.update_mouse(pos)
            self.show_bg(surface)
            self.show_last_move(surface)
            self.show_selected(surface)
            self.show_moves(surface)
            self.show_pieces(surface)
            self.show_check(surface)
            self.show_hover(surface, pos)
            self.dragger.update_blit(surface, theme_name=self.theme_name)

    def handle_mouse_up(self, pos, surface) -> None:
        """
        Handle mouse button release events to drop pieces on the board.
        Validates the move, updates the game state, and plays the AI turn if applicable.
        """
        # Don't process mouse events during AI moves or shortly after
        if self.ai_is_thinking or self.ai_thinking_cooldown > 0:
            # Always reset dragger state and clear events to prevent phantom moves
            self.dragger.dragging = False
            self.dragger.piece = None
            self.selected_square = None
            # Clear pygame events to prevent accumulation
            import pygame as p
            p.event.clear()
            return
        
        # Don't process mouse events when it's the AI's turn
        if self.ai_enabled and self.ai and self.next_player == self.ai.color:
            # Always reset dragger state to prevent phantom moves
            self.dragger.dragging = False
            self.dragger.piece = None
            self.selected_square = None
            return
        
        # Initialize AI trigger variables
        should_trigger_ai = False
        ai_color = None
            
        dragger = self.dragger
        board = self.board
        if dragger.dragging:
            dragger.update_mouse(pos)
            released_row = dragger.mouseY // SQ_SIZE
            released_col = dragger.mouseX // SQ_SIZE
            if 0 <= released_row < 8 and 0 <= released_col < 8:
                initial = Square(dragger.initial_row, dragger.initial_col)
                final = Square(released_row, released_col)
                
                # Check if there's a captured piece
                captured_piece = board.squares[released_row][released_col].piece if board.squares[released_row][released_col].has_piece else None
                
                # Check if this is a promotion move first
                promotion_piece: Optional[Piece] = None
                if isinstance(dragger.piece, Pawn) and (released_row == 0 or released_row == 7):
                    promotion_piece = self.prompt_promotion(surface, dragger.piece.color)
                    # Create move with promotion info and captured piece
                    promotion_char = self.piece_to_promotion_char(promotion_piece)
                    move = Move(initial, final, captured=captured_piece, promotion=promotion_char)
                else:
                    move = Move(initial, final, captured=captured_piece)

                if dragger.piece is not None and board.valid_move(dragger.piece, move):
                    captured = board.squares[released_row][released_col].has_enemy_piece(dragger.piece.color)

                    board.move(dragger.piece, move, surface, promotion_piece=promotion_piece)
                    self.play_sound(captured)
                    self.next_turn()
                    self.selected_square = None

                    # Record fen here
                    self.record_fen()

                    # Update book status after human move
                    self.update_book_status_after_human_move()

                    # Check for game over after the move
                    self.check_game_end()

                    # Show material advantage
                    white_score, black_score = self.board.evaluate_material()
                    diff = round(white_score + black_score, 1)
                    if diff > 0:
                        print(f"Material Advantage: White +{diff}")
                    elif diff < 0:
                        print(f"Material Advantage: Black +{abs(diff)}")
                    else:
                        print("Material Advantage: Even")

                    # Store AI trigger info but don't execute yet
                    should_trigger_ai = (self.ai_enabled and self.ai and self.next_player == self.ai.color and 
                                       not self.game_over and not self.ai_is_thinking)
                    ai_color = self.ai.color if (should_trigger_ai and self.ai) else None

            # Always clean up dragger state before potentially triggering AI
            dragger.undrag_piece(theme_name=self.theme_name)
            
            # After complete UI cleanup, trigger AI if needed
            if should_trigger_ai:
                # Double-check that we should actually trigger AI
                if self.ai and self.next_player == self.ai.color:
                    # Force complete visual update
                    surface.fill((0, 0, 0))  # Clear screen
                    self.show_bg(surface)
                    self.show_last_move(surface) 
                    self.show_pieces(surface)
                    self.show_check(surface)
                    import pygame as p
                    p.display.flip()  # Force immediate screen update
                    
                    # Small delay to ensure visual state is settled
                    p.time.wait(50)  # 50ms delay
                    
                    self.play_AI_turn(surface)
                else:
                    return
        else:
            dragger.undrag_piece(theme_name=self.theme_name)
            self.selected_square = None

    def prompt_promotion(self, surface, color: str) -> Piece:
        """
        Prompt the player to choose a piece for pawn promotion.
        Displays options for queen, rook, bishop, and knight.
        """
        font = p.font.SysFont('Arial', 32)
        options = [('Queen', 'Q'), ('Rook', 'R'), ('Bishop', 'B'), ('Knight', 'K')]
        selecting = True

        while selecting:
            surface.fill((30, 30, 30))
            prompt = font.render("Promote pawn to:", True, (255, 255, 255))
            surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 150))

            for i, (name, key) in enumerate(options):
                text = font.render(f"{name} - Press {key}", True, (255, 255, 255))
                surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 50))

            p.display.flip()

            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    exit()
                if event.type == p.KEYDOWN:
                    if event.key == p.K_q:
                        return Queen(color)
                    elif event.key == p.K_r:
                        return Rook(color)
                    elif event.key == p.K_b:
                        return Bishop(color)
                    elif event.key == p.K_k:
                        return Knight(color)

        return Queen(color)
    
    def AI_color_prompt(self) -> None:
        """
        Prompt the user to select the AI's color and difficulty.
        Configures the game accordingly based on user input.
        """
        screen = p.display.set_mode((WIDTH, HEIGHT))
        font = p.font.SysFont('Arial', 24)
        title = p.font.SysFont('Arial', 32)
        
        # First select AI color
        color_prompt = title.render("AI Color Selection", True, (255, 255, 255))
        option1 = font.render("Press W for AI as White", True, (255, 255, 255))
        option2 = font.render("Press B for AI as Black", True, (255, 255, 255))
        option3 = font.render("Press N for no AI", True, (255, 255, 255))

        ai_color = None
        selecting_color = True
        
        while selecting_color:
            screen.fill((0, 0, 0))
            screen.blit(color_prompt, (WIDTH // 2 - color_prompt.get_width() // 2, HEIGHT // 2 - 100))
            screen.blit(option1, (WIDTH // 2 - option1.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(option2, (WIDTH // 2 - option2.get_width() // 2, HEIGHT // 2))
            screen.blit(option3, (WIDTH // 2 - option3.get_width() // 2, HEIGHT // 2 + 40))
            p.display.flip()

            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    exit()
                if event.type == p.KEYDOWN:
                    if event.key == p.K_w:
                        ai_color = 'white'
                        selecting_color = False
                    elif event.key == p.K_b:
                        ai_color = 'black'
                        selecting_color = False
                    elif event.key == p.K_n:
                        self.ai = None  # No AI created
                        self.ai_enabled = False
                        return

        # If AI was selected, choose difficulty
        if ai_color:
            difficulty_prompt = title.render("AI Difficulty Selection", True, (255, 255, 255))
            diff1 = font.render("Press 1 for Easy (depth 2, 15s)", True, (255, 255, 255))
            diff2 = font.render("Press 2 for Medium (depth 3, 15s)", True, (255, 255, 255))
            diff3 = font.render("Press 3 for Hard (depth 4, 30s)", True, (255, 255, 255))
            diff4 = font.render("Press 4 for Expert (depth 6, 45s)", True, (255, 255, 255))
            diff5 = font.render("Press 5 for Master (depth 8, 60s)", True, (255, 255, 255))
            diff6 = font.render("Press 6 for Grandmaster (depth 10, 120s)", True, (255, 255, 255))

            selecting_difficulty = True
            while selecting_difficulty:
                screen.fill((0, 0, 0))
                screen.blit(difficulty_prompt, (WIDTH // 2 - difficulty_prompt.get_width() // 2, HEIGHT // 2 - 150))
                screen.blit(diff1, (WIDTH // 2 - diff1.get_width() // 2, HEIGHT // 2 - 100))
                screen.blit(diff2, (WIDTH // 2 - diff2.get_width() // 2, HEIGHT // 2 - 70))
                screen.blit(diff3, (WIDTH // 2 - diff3.get_width() // 2, HEIGHT // 2 - 40))
                screen.blit(diff4, (WIDTH // 2 - diff4.get_width() // 2, HEIGHT // 2 - 10))
                screen.blit(diff5, (WIDTH // 2 - diff5.get_width() // 2, HEIGHT // 2 + 20))
                screen.blit(diff6, (WIDTH // 2 - diff6.get_width() // 2, HEIGHT // 2 + 50))
                p.display.flip()

                for event in p.event.get():
                    if event.type == p.QUIT:
                        p.quit()
                        exit()
                    if event.type == p.KEYDOWN:
                        difficulty_map = {
                            p.K_1: "easy",
                            p.K_2: "medium", 
                            p.K_3: "hard",
                            p.K_4: "expert",
                            p.K_5: "master",
                            p.K_6: "grandmaster"
                        }
                        if event.key in difficulty_map:
                            difficulty = difficulty_map[event.key]
                            self.ai = AI(ai_color, difficulty)
                            self.ai_enabled = True
                            selecting_difficulty = False

    def play_AI_turn(self, surface) -> None:
        """
        Execute the best move found by the AI using minimax algorithm.
        The AI's turn is played automatically after the human player.
        """
        # Prevent multiple simultaneous AI calls
        if self.ai_is_thinking:
            return
            
        # Set thinking flag immediately to block all other events
        self.ai_is_thinking = True
            
        if not self.ai:
            self.ai_is_thinking = False
            return
            
        if not self.ai_enabled:
            self.ai_is_thinking = False
            return
            
        # Track consecutive AI moves to detect multiple moves per turn
        if not hasattr(self, '_ai_moves_this_turn'):
            self._ai_moves_this_turn = 0
        self._ai_moves_this_turn += 1
        
        if self._ai_moves_this_turn > 1:
            # Emergency abort - AI trying to make multiple moves
            self.ai_is_thinking = False
            return
        
        # Verify it's actually the AI's turn
        if self.next_player != self.ai.color:
            self.ai_is_thinking = False
            self.ai_thinking_cooldown = 0
            return
        
        # Completely clear all UI state and pygame events to prevent phantom moves
        self.dragger.dragging = False
        self.dragger.piece = None
        self.dragger.initial_row = -1
        self.dragger.initial_col = -1
        self.dragger.mouseX = 0
        self.dragger.mouseY = 0
        self.selected_square = None
        
        # Clear pygame event queue to remove any queued mouse events
        import pygame as p
        p.event.clear()
        
        # Only use book move if still in book
        piece, move = self.ai.get_best_move(self.board, use_book=self.in_book)
        
        # After timeout, validate that piece and move are consistent with current board
        if piece is not None and move is not None:
            actual_piece = self.board.squares[move.initial.row][move.initial.col].piece
            if actual_piece != piece:
                # Force AI to recalculate with current board state
                piece, move = self.ai._emergency_fallback(self.board)
        
        if piece is not None and move is not None:
            # Validate the move is actually legal
            if self.ai.color:  # Type check
                legal_moves = self.board.get_all_moves(self.ai.color)
                legal_move_strings = [m.to_algebraic() for p, m in legal_moves]
                
                if move.to_algebraic() not in legal_move_strings:
                    self.ai_is_thinking = False
                    self.ai_thinking_cooldown = 0
                    return
            
            captured = self.board.squares[move.final.row][move.final.col].has_enemy_piece(piece.color)
            
            self.board.move(piece, move, surface)
            
            # Force immediate screen update after each move
            import pygame as p
            surface.fill((0, 0, 0))
            self.show_bg(surface)
            self.show_pieces(surface)
            p.display.flip()
            p.time.wait(100)  # 100ms pause to make move visible
            
            self.play_sound(captured)
            self.next_turn()
            # Record FEN here
            self.record_fen()
            self.check_game_end()
            
        else:
            if self.ai.color:  # Type check
                legal_moves = self.board.get_all_moves(self.ai.color)
                if not legal_moves:
                    self.check_game_end()
        
        # Always clear the thinking flag when AI turn ends - but use cooldown to prevent race conditions
        self.ai_thinking_cooldown = 60  # 1 second at 60 FPS - enough to see moves clearly
        # ai_is_thinking will remain True until cooldown expires

    def show_end_screen(self, surface) -> None:
        """
        Display the end game screen with the result (checkmate, stalemate, etc.)
        Provides an option to restart the game.
        """
        font = p.font.SysFont('Arial', 48)
        text = font.render(self.end_message, True, (255, 255, 255))
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        surface.fill((0, 0, 0))
        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 60))
        surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))

    def check_game_end(self) -> None:
        """
        Check and update the game state for checkmate, stalemate, dead position,
        fifty-move rule, and threefold repetition. Updates the end message and game_over flag.
        """
        if self.board.is_checkmate(self.next_player):
            self.end_message = "Checkmate!"
            self.game_over = True
        elif self.board.is_stalemate(self.next_player):
            self.end_message = "Stalemate!"
            self.game_over = True
        elif self.board.is_dead_position():
            self.end_message = "Draw: Dead Position!"
            self.game_over = True
        elif self.board.is_fifty_move_rule():
            self.end_message = "Draw: 50-Move Rule"
            self.game_over = True
        elif self.is_threefold_repetition():
            self.end_message = "Draw: Threefold Repetition"
            self.game_over = True

    def load_fen(self, fen: str) -> None:
        """
        Load a position from a FEN string and reset the game state accordingly.
        Clears any existing selection and dragging, and resets the game over state.
        """
        self.board.set_fen(fen)
        self.selected_square = None
        self.game_over = False
        self.end_message = ""
        self.draw_offered = False
        self.dragger.undrag_piece(theme_name=self.theme_name)
        self.fen_history = []
        self.redo_history = []  # Clear redo history on new position
        self.record_fen()

   

    def piece_to_promotion_char(self, piece: Optional[Piece]) -> Optional[str]:
        """Convert a promotion piece to its character representation."""
        if piece is None:
            return None
        
        piece_name = piece.name.lower()
        if piece_name == 'queen':
            return 'q'
        elif piece_name == 'rook':
            return 'r'
        elif piece_name == 'bishop':
            return 'b'
        elif piece_name == 'knight':
            return 'n'
        return None


