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
from perft import perft

class Game:
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

    def __init__(self):
        self.next_player = 'white'
        self.selected_square: Optional[Square] = None
        self.game_over = False
        self.end_message = ""
        self.draw_offered = False
        self.ai: Optional[AI] = AI(self.next_player)
        self.ai_enabled = False  # Default to off
        self.AI_color_prompt()
        self.board = Board()
        self.board.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.dragger = Dragger()
        self.config = Config()
        self.fen_history: list[str] = []
        self.record_fen()

    @property
    def theme_name(self) -> Optional[str]:
        return getattr(self.config.theme, "name", None)

    def show_bg(self, surface) -> None:
        theme = self.config.theme
        font = self.config.font  # Use your configured font
        for row in range(ROWS):
            for col in range(COLS):
                color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                rect = (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                p.draw.rect(surface, color, rect)

                # Draw row numbers (1-8) on the leftmost column
                if col == 0:
                    label = font.render(str(ROWS - row), True, (0, 0, 0))
                    surface.blit(label, (5, row * SQ_SIZE + 5))

                # Draw column letters (a-h) on the bottom row using Square.ALPHACOLS
                if row == ROWS - 1:
                    from square import Square  # Local import to avoid circular import
                    label = font.render(Square.ALPHACOLS[col], True, (0, 0, 0))
                    surface.blit(label, (col * SQ_SIZE + SQ_SIZE - 20, HEIGHT - 25))

    def show_highlight(self, surface, squares, color, alpha=160) -> None:
        for square in squares:
            row, col = square.row, square.col
            highlight_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            highlight_surface.fill((*color, alpha))
            surface.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))

    def show_pieces(self, surface) -> None:
        for row in range(ROWS):
            for col in range(COLS):
                square = self.board.squares[row][col]
                if square.has_piece and square.piece is not None:
                    piece = square.piece
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80, theme_name=self.theme_name)
                        img = p.image.load(piece.texture)
                        img_center = col * SQ_SIZE + SQ_SIZE // 2, row * SQ_SIZE + SQ_SIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface) -> None:
        if not (self.dragger.dragging and self.dragger.piece):
            return
        color = self.config.theme.move_highlight
        for move in self.dragger.piece.moves:
            row, col = move.final.row, move.final.col
            highlight_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            highlight_surface.fill((*color, 120))
            surface.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))

    def show_last_move(self, surface) -> None:
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
        if not self.selected_square:
            return
        row, col = self.selected_square.row, self.selected_square.col
        color = self.config.theme.selected.light if (row + col) % 2 == 0 else self.config.theme.selected.dark
        highlight_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
        highlight_surface.fill((*color, 160))
        surface.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))

    def show_hover(self, surface, mouse_pos) -> None:
        col = mouse_pos[0] // SQ_SIZE
        row = mouse_pos[1] // SQ_SIZE
        color = self.config.theme.moves.light if (row + col) % 2 == 0 else self.config.theme.moves.dark
        rect = (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(surface, color, rect, 3)

    def show_check(self, surface) -> None:
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
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def change_theme(self) -> None:
        self.config.change_themes()
    
    def play_sound(self, captured: bool=False) -> None:
        (self.config.capture_sound if captured else self.config.move_sound).play()

    def restart(self) -> None:
        self.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def fen_without_clocks(self, fen: str) -> str:
        # Remove the last two fields (halfmove/fullmove)
        return ' '.join(fen.split()[:4])

    def record_fen(self):
        fen = FEN.get_fen(self.board)
        self.fen_history.append(self.fen_without_clocks(fen))

    def count_fen_occurrences(self, fen: str) -> int:
        fen = self.fen_without_clocks(fen)
        return self.fen_history.count(fen)

    def is_threefold_repetition(self) -> bool:
        fen = FEN.get_fen(self.board)
        fen = self.fen_without_clocks(fen)
        return self.count_fen_occurrences(fen) >= 3

    def handle_mouse_down(self, pos) -> None:
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
        dragger = self.dragger
        board = self.board
        if dragger.dragging:
            dragger.update_mouse(pos)
            released_row = dragger.mouseY // SQ_SIZE
            released_col = dragger.mouseX // SQ_SIZE
            if 0 <= released_row < 8 and 0 <= released_col < 8:
                initial = Square(dragger.initial_row, dragger.initial_col)
                final = Square(released_row, released_col)
                move = Move(initial, final)

                if dragger.piece is not None and board.valid_move(dragger.piece, move):
                    captured = board.squares[released_row][released_col].has_enemy_piece(dragger.piece.color)
                    promotion_piece: Optional[Piece] = None
                    if isinstance(dragger.piece, Pawn) and (released_row == 0 or released_row == 7):
                        promotion_piece = self.prompt_promotion(surface, dragger.piece.color)

                    board.move(dragger.piece, move, surface, promotion_piece=promotion_piece)
                    self.play_sound(captured)
                    self.next_turn()
                    self.selected_square = None

                    # RECORD FEN HERE
                    self.record_fen()

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

                    # After a successful human move and next_turn()
                    if self.ai_enabled and self.ai and self.next_player == self.ai.color and not self.game_over:
                        self.play_AI_turn(surface)

            dragger.undrag_piece(theme_name=self.theme_name)
        else:
            self.selected_square = None

    def prompt_promotion(self, surface, color: str) -> Piece:
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
        screen = p.display.set_mode((WIDTH, HEIGHT))
        font = p.font.SysFont('Arial', 32)
        prompt = font.render("Press W for AI as White, B for AI as Black, N for no AI", True, (255, 255, 255))

        selecting = True
        while selecting:
            screen.fill((0, 0, 0))
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2))
            p.display.flip()

            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    exit()
                if event.type == p.KEYDOWN:
                    if event.key == p.K_w:
                        self.ai = AI('white')
                        self.ai_enabled = True
                        print("AI will play as white.")
                        selecting = False
                    elif event.key == p.K_b:
                        self.ai = AI('black')
                        self.ai_enabled = True
                        print("AI will play as black.")
                        selecting = False
                    elif event.key == p.K_n:
                        self.ai = AI(self.next_player)  # Always have an AI instance
                        self.ai_enabled = False
                        print("No AI will play.")
                        selecting = False

    def play_AI_turn(self, surface) -> None:
        piece, move = self.ai.random_move(self.board) if self.ai else (None, None)
        if piece is not None and move is not None:
            captured = self.board.squares[move.final.row][move.final.col].has_enemy_piece(piece.color)
            self.board.move(piece, move, surface)
            self.play_sound(captured)
            self.next_turn()
            # RECORD FEN HERE
            self.record_fen()
            self.check_game_end()
    
    def show_end_screen(self, surface) -> None:
        font = p.font.SysFont('Arial', 48)
        text = font.render(self.end_message, True, (255, 255, 255))
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        surface.fill((0, 0, 0))
        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 60))
        surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))

    def check_game_end(self) -> None:
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
        self.board.set_fen(fen)
        self.selected_square = None
        self.game_over = False
        self.end_message = ""
        self.draw_offered = False
        self.dragger.undrag_piece(theme_name=self.theme_name)
        self.fen_history = []
        self.record_fen()

    def show_perft_result(self, surface, depth: int = 2) -> None:
        # Run perft for the current position and next player
        result = perft(self.board, self.next_player, depth)
        font = self.config.font
        label = font.render(f"Perft({depth}): {result}", True, (0, 0, 0))
        surface.blit(label, (10, 10))


