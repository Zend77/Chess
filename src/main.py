import pygame as p

from const import *
from AI import AI
from game import Game

class Main:
    def __init__(self):
        p.init()
        self.screen = p.display.set_mode((WIDTH, HEIGHT))
        p.display.set_caption('Chess')
        self.game = Game()
        self.clock = p.time.Clock()
        # Play AI turn if needed at start
        while self.game.ai_enabled and self.game.ai and not self.game.game_over and self.game.next_player == self.game.ai.color:
            self.game.play_AI_turn(self.screen)

    def main_loop(self):
        screen = self.screen
        clock = self.clock

        running = True

        while running:
            game = self.game  # Always get the latest game object
            theme_name = getattr(game.config.theme, "name", None)
            screen.fill((0, 0, 0))

            # Draw board and pieces
            if not game.game_over:
                game.show_bg(screen)
                game.show_last_move(screen)
                game.show_selected(screen)
                game.show_moves(screen)
                game.show_pieces(screen)
                game.show_check(screen)
                game.show_hover(screen, p.mouse.get_pos())

                if game.dragger.dragging:
                    game.dragger.update_blit(screen, theme_name=theme_name)
            else:
                game.show_end_screen(screen)

            for event in p.event.get():
                if event.type == p.MOUSEBUTTONDOWN and not game.game_over:
                    game.handle_mouse_down(event.pos)

                elif event.type == p.MOUSEMOTION and not game.game_over:
                    game.handle_mouse_motion(event.pos, screen)

                elif event.type == p.MOUSEBUTTONUP and not game.game_over:
                    game.handle_mouse_up(event.pos, screen)

                elif event.type == p.KEYDOWN:
                    if event.key == p.K_t and not game.game_over:
                        game.change_theme()
                    elif event.key == p.K_r:
                        self.game = Game()
                        game = self.game
                    elif event.key == p.K_g and not game.game_over:
                        game.ai_enabled = not game.ai_enabled
                        print(f"AI Enabled: {game.ai_enabled}")
                        if game.ai_enabled:
                            if game.ai is None:
                                game.ai = AI(game.next_player)
                            else:
                                game.ai.color = game.next_player
                            # If it's the AI's turn, let it move immediately
                            if game.next_player == game.ai.color:
                                game.play_AI_turn(screen)
                    elif event.key == p.K_d and not game.game_over:
                        if game.draw_offered:
                            game.end_message = "Draw: Mutual Agreement"
                            game.game_over = True
                        else:
                            game.draw_offered = True
                            print("Draw offered. Press 'D' again to accept.")
                elif event.type == p.QUIT:
                    running = False

            clock.tick(MAX_FPS)
            p.display.update()

if __name__ == '__main__':
    main = Main()
    main.main_loop()
