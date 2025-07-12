import pygame as p

from const import *
from game import Game

class Main:
    def __init__(self):
        p.init()
        self.screen = p.display.set_mode((WIDTH, HEIGHT))
        p.display.set_caption('Chess')
        self.game = Game()
        self.clock = p.time.Clock()

    def main_loop(self):
        screen = self.screen
        game = self.game
        clock = self.clock

        running = True

        while running:
            screen.fill((0, 0, 0))

            # Show methods
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_selected(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_check(screen)
            game.show_hover(screen, p.mouse.get_pos())

            if game.dragger.dragging:
                game.dragger.update_blit(screen, theme_name=getattr(game.config.theme, "name", None))

            for event in p.event.get():
                if event.type == p.MOUSEBUTTONDOWN:
                    game.handle_mouse_down(event.pos)

                elif event.type == p.MOUSEMOTION:
                    game.handle_mouse_motion(event.pos, screen)

                elif event.type == p.MOUSEBUTTONUP:
                    game.handle_mouse_up(event.pos, screen)

                elif event.type == p.KEYDOWN:
                    if event.key == p.K_t:
                        game.change_theme()
                    elif event.key == p.K_r:
                        self.game = Game()

                elif event.type == p.QUIT:
                    running = False

            clock.tick(MAX_FPS)
            p.display.update()

if __name__ == '__main__':
    main = Main()
    main.main_loop()
