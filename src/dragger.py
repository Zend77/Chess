import pygame as p
from typing import Optional, Any

from const import *


class Dragger:
    piece: Optional[Any]
    mouseX: int
    mouseY: int
    initial_row: int
    initial_col: int
    dragging: bool

    def __init__(self):
        self.piece: Optional[Any] = None
        self.mouseX: int = 0
        self.mouseY: int = 0
        self.initial_row: int = 0
        self.initial_col: int = 0
        self.dragging: bool = False

    def update_blit(self, surface, theme_name: Optional[str]=None) -> None:
        if self.piece is not None:
            self.piece.set_texture(size=128, theme_name=theme_name)
            texture = self.piece.texture
            img = p.image.load(texture)
            img_center = (self.mouseX, self.mouseY)
            self.piece.texture_rect = img.get_rect(center=img_center)
            surface.blit(img, self.piece.texture_rect)

    def update_mouse(self, pos: tuple[int, int]) -> None:
        self.mouseX, self.mouseY = pos

    def save_inital(self, pos: tuple[int, int]) -> None:
        self.initial_row = pos[1] // SQ_SIZE
        self.initial_col = pos[0] // SQ_SIZE

    def drag_piece(self, piece: Any) -> None:
        self.piece = piece
        self.dragging = True

    def undrag_piece(self, theme_name: Optional[str]=None) -> None:
        if self.piece:
            self.piece.set_texture(size=80, theme_name=theme_name)
        self.piece = None
        self.dragging = False