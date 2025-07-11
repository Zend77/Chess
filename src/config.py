import pygame as p
import os

from sound import Sound
from theme import Theme

class Config:
    
    def __init__(self):
        self.themes = []
        self._add_themes()
        self.idx = 0
        self.theme = self.themes[self.idx]
        self.font = p.font.SysFont('MONOSPACE', 18, bold=True)
        self.move_sound = Sound(
            os.path.join('assets/sounds/move.wav'))
        self.capture_sound = Sound(
            os.path.join('assets/sounds/capture.wav')
        )
    
    def change_themes(self):
        self.idx += 1
        self.idx %= len(self.themes)
        self.theme = self.themes[self.idx]
    
    def _add_themes(self):
        green = Theme(
            light_bg=(118, 150, 86),
            dark_bg=(238, 238, 210),
            light_trace=(246, 246, 105),
            dark_trace=(186, 202, 43),
            light_moves=(246, 246, 105),
            dark_moves=(186, 202, 43),
            light_selected=(255, 0, 0),     
            dark_selected=(200, 0, 0),
            move_highlight=(66, 135, 245)
        )
        brown = Theme(
            light_bg=(181, 136, 99),
            dark_bg=(240, 217, 181),
            light_trace=(246, 246, 105),
            dark_trace=(186, 202, 43),
            light_moves=(246, 246, 105),
            dark_moves=(186, 202, 43),
            light_selected=(255, 0, 0),
            dark_selected=(200, 0, 0),
            move_highlight=(66, 135, 245)
        )
        blue = Theme(
            light_bg=(125, 135, 150),
            dark_bg=(232, 235, 239),
            light_trace=(246, 246, 105),
            dark_trace=(186, 202, 43),
            light_moves=(246, 246, 105),
            dark_moves=(186, 202, 43),
            light_selected=(255, 0, 0),
            dark_selected=(200, 0, 0),
            move_highlight=(66, 135, 245)
        )
        gray = Theme(
            light_bg=(120, 120, 120),
            dark_bg=(200, 200, 200),
            light_trace=(246, 246, 105),
            dark_trace=(186, 202, 43),
            light_moves=(246, 246, 105),
            dark_moves=(186, 202, 43),
            light_selected=(255, 0, 0),
            dark_selected=(200, 0, 0),
            move_highlight=(66, 135, 245)
        )
        
        pink = Theme(
            light_bg=(255, 192, 203),  
            dark_bg=(255, 182, 193),   
            light_trace=(255, 222, 173),  
            dark_trace=(255, 160, 122),   
            light_moves=(255, 105, 180),  
            dark_moves=(255, 20, 147),    
            light_selected=(255, 128, 192),  
            dark_selected=(200, 64, 128),
            move_highlight=(66, 135, 245)
        )

        purple = Theme(
            light_bg=(200, 180, 255),    # light purple
            dark_bg=(120, 70, 180),      # dark purple
            light_trace=(246, 246, 105),
            dark_trace=(186, 202, 43),
            light_moves=(180, 120, 255), # highlight purple
            dark_moves=(120, 70, 180),
            light_selected=(255, 0, 255),    # magenta for selection
            dark_selected=(180, 0, 180),
            move_highlight=(140, 66, 245)   # bluish purple
        )

        hello_kitty = Theme(
            light_bg=(255, 240, 245),      # Lavender blush (very light pink)
            dark_bg=(255, 182, 193),       # Light pink
            light_trace=(255, 228, 225),   # Misty rose (pale pink)
            dark_trace=(255, 192, 203),    # Pink
            light_moves=(255, 182, 193),   # Light pink
            dark_moves=(255, 105, 180),    # Hot pink
            light_selected=(255, 105, 180),# Hot pink for selection
            dark_selected=(255, 20, 147),  # Deep pink for selection
            move_highlight=(255, 215, 0),  # Gold (for a touch of yellow)
            name="hello_kitty"             # <-- Add this line
        )

        self.themes = [green, brown, blue, gray, pink, purple, hello_kitty]