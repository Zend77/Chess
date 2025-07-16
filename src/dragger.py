import pygame as p
from typing import Optional, Any

from const import *


class Dragger:
    """
    Handles drag-and-drop functionality for moving chess pieces.
    Tracks the piece being dragged, mouse position, and original square
    to provide smooth visual feedback during piece movement.
    """
    piece: Optional[Any]
    mouseX: int
    mouseY: int
    initial_row: int
    initial_col: int
    dragging: bool

    def __init__(self):
        self.piece: Optional[Any] = None  # The piece currently being dragged
        self.mouseX: int = 0             # Current mouse X position
        self.mouseY: int = 0             # Current mouse Y position
        self.initial_row: int = 0        # Starting row of the drag
        self.initial_col: int = 0        # Starting column of the drag
        self.dragging: bool = False      # Whether we're currently dragging

    def update_blit(self, surface, theme_name: Optional[str]=None) -> None:
        """
        Draw the dragged piece at the current mouse position.
        Uses a larger texture (128px) to make the dragged piece more prominent.
        """
        if self.piece is not None:
            self.piece.set_texture(size=128, theme_name=theme_name)
            texture = self.piece.texture
            img = p.image.load(texture)
            img_center = (self.mouseX, self.mouseY)  # Center on mouse cursor
            self.piece.texture_rect = img.get_rect(center=img_center)
            surface.blit(img, self.piece.texture_rect)

    def update_mouse(self, pos: tuple[int, int]) -> None:
        """Update the current mouse position for smooth dragging."""
        self.mouseX, self.mouseY = pos

    def save_inital(self, pos: tuple[int, int]) -> None:
        """
        Save the initial square coordinates when starting a drag.
        Converts pixel coordinates to board coordinates.
        """
        self.initial_row = pos[1] // SQ_SIZE
        self.initial_col = pos[0] // SQ_SIZE

    def drag_piece(self, piece: Any) -> None:
        """Start dragging the specified piece."""
        self.piece = piece
        self.dragging = True

    def undrag_piece(self, theme_name: Optional[str]=None) -> None:
        """Stop dragging and clear the dragged piece."""
        if self.piece:
            self.piece.set_texture(size=80, theme_name=theme_name)
        self.piece = None
        self.dragging = False