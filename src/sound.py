import pygame as p

class Sound:
    
    def __init__(self, path):
        self.path = path
        self.sound = p.mixer.Sound(path)
    
    def play(self):
        p.mixer.Sound.play(self.sound)
        