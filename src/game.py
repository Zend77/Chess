import pygame as p

from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square

class Game:
    def __init__(self):
        self.next_player = 'white'
        self.selected_square = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()
        
    
    # Show methods
    def show_bg(self, surface):
        theme = self.config.theme

        for row in range(ROWS):
            for col in range(COLS):
                # Color
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                # Rect
                rect = (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                # Blit
                p.draw.rect(surface, color, rect)
                
                # Row coords
                if col == 0:
                    # Color
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    # Lable
                    lable = self.config.font.render(str(ROWS-row), 1, color)
                    lable_pos = (5, 5 + row * SQ_SIZE)
                    # Blit
                    surface.blit(lable, lable_pos)
                    
                # Col coords
                if row == 7:
                    # Color
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    # Lable
                    lable = self.config.font.render(Square.get_alphacol(col), 1, color)
                    lable_pos = (col * SQ_SIZE + SQ_SIZE - 20, HEIGHT - 20)
                    # Blit
                    surface.blit(lable, lable_pos)
    
    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                # piece ?
                if self.board.squares[row][col].has_piece(): # type: ignore 
                    piece = self.board.squares[row][col].piece # type: ignore 
                   
                    if piece is not self.dragger.piece: 
                        img = p.image.load(piece.texture) # type: ignore 
                        img_center = col * SQ_SIZE + SQ_SIZE // 2, row * SQ_SIZE + SQ_SIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center) # type: ignore 
                        surface.blit(img, piece.texture_rect) # type: ignore 
    
    def show_moves(self, surface):
        if not (self.dragger.dragging and self.dragger.piece):
            return

        piece = self.dragger.piece
        color = self.config.theme.move_highlight

        for move in piece.moves:
            row, col = move.final.row, move.final.col

            highlight_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            highlight_surface.fill((*color, 120))  # Blue highlight with transparency
            surface.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))
                
    def show_last_move(self, surface):
        theme = self.config.theme

        if not self.board.last_move:
            return

        initial = self.board.last_move.initial
        final = self.board.last_move.final

        for square in [initial, final]:
            row, col = square.row, square.col

            # Use light or dark trace color depending on square color
            color = theme.trace.light if (row + col) % 2 == 0 else theme.trace.dark

            highlight_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            highlight_surface.fill((*color, 160))  # 160 alpha transparency
            surface.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))

    
    def show_selected(self, surface):
        theme = self.config.theme

        if not self.selected_square:
            return

        row, col = self.selected_square.row, self.selected_square.col

        color = theme.selected.light if (row + col) % 2 == 0 else theme.selected.dark

        highlight_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
        highlight_surface.fill((*color, 160))  # semi-transparent highlight
        surface.blit(highlight_surface, (col * SQ_SIZE, row * SQ_SIZE))

        
    def show_hover(self, surface, mouse_pos):
        theme = self.config.theme

        col = mouse_pos[0] // SQ_SIZE
        row = mouse_pos[1] // SQ_SIZE

        # Choose color based on square color
        color = theme.moves.light if (row + col) % 2 == 0 else theme.moves.dark
        # Rect
        rect = (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        # Blit
        p.draw.rect(surface, color, rect, 3)  # outline width = 3

    # Other methods
    
    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'
        
    def change_theme(self):
        self.config.change_themes()
        
    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()
            
    def restart(self):
        self.__init__()
