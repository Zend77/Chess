import pygame as p

from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square
from move import Move
from piece import Queen, Rook, Bishop, Knight, Pawn
from bot import Bot

class Game:
    def __init__(self):
        self.next_player = 'white'
        self.selected_square = None
        self.game_over = False
        self.end_message = ""
        self.bot = Bot('black')
        self.bot_enabled = False
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()

    # Show methods
    def show_bg(self, surface):
        theme = self.config.theme
        for row in range(ROWS):
            for col in range(COLS):
                color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                rect = (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                p.draw.rect(surface, color, rect)

    def show_pieces(self, surface):
        theme_name = getattr(self.config.theme, "name", None)
        for row in range(ROWS):
            for col in range(COLS):
                square = self.board.squares[row][col]
                if square.has_piece(): # type: ignore
                    piece = square.piece # type: ignore
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80, theme_name=theme_name)
                        img = p.image.load(piece.texture)
                        img_center = col * SQ_SIZE + SQ_SIZE // 2, row * SQ_SIZE + SQ_SIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        if not (self.dragger.dragging and self.dragger.piece):
            return
        color = self.config.theme.move_highlight
        for move in self.dragger.piece.moves:
            row, col = move.final.row, move.final.col
            highlight_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            highlight_surface.fill((*color, 120))
            surface.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))

    def show_last_move(self, surface):
        theme = self.config.theme
        if not self.board.last_move:
            return
        for square in [self.board.last_move.initial, self.board.last_move.final]:
            row, col = square.row, square.col
            color = theme.trace.light if (row + col) % 2 == 0 else theme.trace.dark
            highlight_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            highlight_surface.fill((*color, 160))
            surface.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))

    def show_selected(self, surface):
        if not self.selected_square:
            return
        row, col = self.selected_square.row, self.selected_square.col
        color = self.config.theme.selected.light if (row + col) % 2 == 0 else self.config.theme.selected.dark
        highlight_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
        highlight_surface.fill((*color, 160))
        surface.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))

    def show_hover(self, surface, mouse_pos):
        col = mouse_pos[0] // SQ_SIZE
        row = mouse_pos[1] // SQ_SIZE
        color = self.config.theme.moves.light if (row + col) % 2 == 0 else self.config.theme.moves.dark
        rect = (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(surface, color, rect, 3)

    def show_check(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                square = self.board.squares[row][col]
                if square.has_piece(): # type: ignore
                    piece = square.piece # type: ignore
                    if piece.name == 'king' and piece.color == self.next_player:
                        if self.board.in_check_king(piece.color):
                            shadow_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                            p.draw.ellipse(shadow_surface, (255, 0, 0, 100), (8, 16, SQ_SIZE - 16, SQ_SIZE - 32))
                            surface.blit(shadow_surface, (col * SQ_SIZE, row * SQ_SIZE))
                        return

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def change_theme(self):
        self.config.change_themes()

    def play_sound(self, captured=False):
        (self.config.capture_sound if captured else self.config.move_sound).play()

    def restart(self):
        self.__init__()

    def handle_mouse_down(self, pos):
        dragger = self.dragger
        board = self.board
        dragger.update_mouse(pos)
        clicked_row = dragger.mouseY // SQ_SIZE
        clicked_col = dragger.mouseX // SQ_SIZE
        if 0 <= clicked_row < 8 and 0 <= clicked_col < 8:
            square = board.squares[clicked_row][clicked_col]
            if square.has_piece() and square.piece.color == self.next_player and not dragger.dragging: # type: ignore
                self.selected_square = square
                board.calc_moves(square.piece, clicked_row, clicked_col, filter_checks=True) # type: ignore
                dragger.save_inital(pos)
                dragger.drag_piece(square.piece) # type: ignore
            else:
                self.selected_square = None
                dragger.undrag_piece(theme_name=getattr(self.config.theme, "name", None))
        else:
            self.selected_square = None
            dragger.undrag_piece(theme_name=getattr(self.config.theme, "name", None))

    def handle_mouse_motion(self, pos, surface):
        if self.dragger.dragging:
            self.dragger.update_mouse(pos)
            self.show_bg(surface)
            self.show_last_move(surface)
            self.show_selected(surface)
            self.show_moves(surface)
            self.show_pieces(surface)
            self.show_check(surface)
            self.show_hover(surface, pos)
            self.dragger.update_blit(surface, theme_name=getattr(self.config.theme, "name", None))

    def handle_mouse_up(self, pos, surface):
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

                if board.valid_move(dragger.piece, move):
                    captured = board.squares[released_row][released_col].has_enemy_piece(dragger.piece.color) # type: ignore
                    promotion_piece = None
                    if isinstance(dragger.piece, Pawn) and (released_row == 0 or released_row == 7):
                        promotion_piece = self.prompt_promotion(surface, dragger.piece.color)

                    board.move(dragger.piece, move, surface, promotion_piece=promotion_piece)
                    self.play_sound(captured)
                    self.next_turn()
                    self.selected_square = None

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

                    # If bot is enbled, let it play a move
                    if self.bot_enabled and self.next_player == self.bot.color and not self.game_over:
                        self.play_bot_turn(surface)

            dragger.undrag_piece(theme_name=getattr(self.config.theme, "name", None))
        else:
            self.selected_square = None



    def prompt_promotion(self, surface, color):
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
    
    
    def play_bot_turn(self, surface):
        piece, move = self.bot.bot_move(self.board)
        if piece and move:
            captured = self.board.squares[move.final.row][move.final.col].has_enemy_piece(piece.color)
            self.board.move(piece, move, surface)
            self.play_sound(captured)
            self.next_turn()
            self.check_game_end()
    
    def show_end_screen(self, surface):
        font = p.font.SysFont('Arial', 48)
        text = font.render(self.end_message, True, (255, 255, 255))
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        surface.fill((0, 0, 0))
        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 60))
        surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))

    
    def check_game_end(self):
        if self.board.is_checkmate(self.next_player):
            self.end_message = "Checkmate!"
            self.game_over = True
        elif self.board.is_stalemate(self.next_player):
            self.end_message = "Stalemate!"
            self.game_over = True
