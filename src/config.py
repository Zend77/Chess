import pygame as p
import os

from sound import Sound
from theme import Theme

class Config:
    """
    Manages game configuration including visual themes, fonts, and sound effects.
    Provides multiple color schemes and handles theme switching during gameplay.
    """
    
    def __init__(self):
        self.themes = []  # List of available visual themes
        self._add_themes()  # Initialize all theme options
        self.idx = 0  # Current theme index
        self.theme = self.themes[self.idx]  # Currently active theme
        self.font = p.font.SysFont('MONOSPACE', 18, bold=True)  # UI font
        # Sound effects for game actions
        self.move_sound = Sound(
            os.path.join('assets/sounds/move.wav'))
        self.capture_sound = Sound(
            os.path.join('assets/sounds/capture.wav')
        )
    
    def change_themes(self):
        """Cycle to the next available theme."""
        self.idx += 1
        self.idx %= len(self.themes)  # Wrap around to first theme
        self.theme = self.themes[self.idx]
    
    def _add_themes(self):
        """
        Define all available visual themes with their color schemes.
        Each theme specifies colors for board squares, highlights, and UI elements.
        """
        # Classic green theme (traditional tournament style)
        green = Theme(
            light_bg=(118, 150, 86),       # Light green squares
            dark_bg=(238, 238, 210),       # Cream/white squares
            light_trace=(246, 246, 105),   # Yellow highlight for last move
            dark_trace=(186, 202, 43),     # Darker yellow highlight
            light_moves=(246, 246, 105),   # Yellow for valid moves
            dark_moves=(186, 202, 43),     # Darker yellow for valid moves
            light_selected=(255, 0, 0),    # Red for selected piece
            dark_selected=(200, 0, 0),     # Darker red for selected piece
            move_highlight=(66, 135, 245)  # Blue for move highlights
        )
        
        # Warm brown theme (wood-style board)
        brown = Theme(
            light_bg=(181, 136, 99),       # Light brown squares
            dark_bg=(240, 217, 181),       # Cream squares
            light_trace=(246, 246, 105),   # Yellow highlight for last move
            dark_trace=(186, 202, 43),     # Darker yellow highlight
            light_moves=(246, 246, 105),   # Yellow for valid moves
            dark_moves=(186, 202, 43),     # Darker yellow for valid moves
            light_selected=(255, 0, 0),    # Red for selected piece
            dark_selected=(200, 0, 0),     # Darker red for selected piece
            move_highlight=(66, 135, 245)  # Blue for move highlights
        )
        
        # Cool blue theme (modern digital style)
        blue = Theme(
            light_bg=(125, 135, 150),      # Light blue-gray squares
            dark_bg=(232, 235, 239),       # Very light gray squares
            light_trace=(246, 246, 105),   # Yellow highlight for last move
            dark_trace=(186, 202, 43),     # Darker yellow highlight
            light_moves=(246, 246, 105),   # Yellow for valid moves
            dark_moves=(186, 202, 43),     # Darker yellow for valid moves
            light_selected=(255, 0, 0),    # Red for selected piece
            dark_selected=(200, 0, 0),     # Darker red for selected piece
            move_highlight=(66, 135, 245)  # Blue for move highlights
        )
        
        # Neutral gray theme (high contrast, modern look)
        gray = Theme(
            light_bg=(120, 120, 120),      # Medium gray squares
            dark_bg=(200, 200, 200),       # Light gray squares
            light_trace=(246, 246, 105),   # Yellow highlight for last move
            dark_trace=(186, 202, 43),     # Darker yellow highlight
            light_moves=(246, 246, 105),   # Yellow for valid moves
            dark_moves=(186, 202, 43),     # Darker yellow for valid moves
            light_selected=(255, 0, 0),    # Red for selected piece
            dark_selected=(200, 0, 0),     # Darker red for selected piece
            move_highlight=(66, 135, 245)  # Blue for move highlights
        )
        
        # Playful pink theme (vibrant and colorful)
        pink = Theme(
            light_bg=(255, 192, 203),      # Light pink squares
            dark_bg=(255, 182, 193),       # Lighter pink squares
            light_trace=(255, 222, 173),   # Light peach highlight for last move
            dark_trace=(255, 160, 122),    # Darker peach highlight
            light_moves=(255, 105, 180),   # Vivid pink for valid moves
            dark_moves=(255, 20, 147),     # Darker pink for valid moves
            light_selected=(255, 128, 192),  # Soft pink for selected piece
            dark_selected=(200, 64, 128),  # Darker pink for selected piece
            move_highlight=(66, 135, 245)  # Blue for move highlights
        )

        # Royal purple theme (rich and elegant)
        purple = Theme(
            light_bg=(200, 180, 255),      # Light lavender squares
            dark_bg=(120, 70, 180),        # Deep purple squares
            light_trace=(246, 246, 105),   # Yellow highlight for last move
            dark_trace=(186, 202, 43),     # Darker yellow highlight
            light_moves=(180, 120, 255),   # Light purple for valid moves
            dark_moves=(120, 70, 180),     # Darker purple for valid moves
            light_selected=(255, 0, 255),  # Magenta for selected piece
            dark_selected=(180, 0, 180),   # Darker magenta for selected piece
            move_highlight=(140, 66, 245)  # Rich blue for move highlights
        )

        # Hello Kitty theme (cute and playful, inspired by the character)
        hello_kitty = Theme(
            light_bg=(255, 240, 245),      # Very light pink squares
            dark_bg=(255, 182, 193),       # Light pink squares
            light_trace=(255, 228, 225),   # Very light peach highlight for last move
            dark_trace=(255, 192, 203),    # Light peach highlight
            light_moves=(255, 182, 193),   # Light pink for valid moves
            dark_moves=(255, 105, 180),    # Vivid pink for valid moves
            light_selected=(255, 105, 180),  # Soft pink for selected piece
            dark_selected=(255, 20, 147),  # Darker pink for selected piece
            move_highlight=(255, 215, 0),  # Bright yellow for move highlights
            name="hello_kitty"              # Identifier for the theme
        )

        self.themes = [green, brown, blue, gray, pink, purple, hello_kitty]