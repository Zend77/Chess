import pygame as p

from const import *


class Dragger:
    
    def __init__(self):
        self.piece = None
        self.mouseX = 0
        self.mouseY = 0
        self.initial_row = 0
        self.initial_col = 0
        self.dragging = False
        
    # Blit method
        
    def update_blit(self, surface):
        # Texture
        self.piece.set_texture(size=128) # type: ignore
        texture = self.piece.texture # type: ignore
        # Img
        img = p.image.load(texture)
        # Rect
        img_center = (self.mouseX, self.mouseY)
        self.piece.texture_rect = img.get_rect(center=img_center) # type: ignore
        # Blit
        surface.blit(img, self.piece.texture_rect) # type: ignore
        
    # Other methods
    
    def update_mouse(self, pos):
        self.mouseX, self.mouseY = pos # (xcord, ycord)
        
    def save_inital(self, pos):
        self.initial_row = pos[1] // SQ_SIZE
        self.initial_col = pos[0] // SQ_SIZE
        
    def drag_piece(self, piece):
        self.piece = piece
        self.dragging = True
    
    def undrag_piece(self):
        if self.piece:
            self.piece.set_texture(size=80)
        self.piece = None
        self.dragging = False