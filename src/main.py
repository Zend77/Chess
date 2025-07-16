import pygame as p

from const import *
from AI import AI
from game import Game

class Main:
    """
    Main game controller that handles the pygame loop, user input, and game state.
    Manages the display, AI interactions, and various game modes like perft testing.
    """
    def __init__(self):
        p.init()
        self.screen = p.display.set_mode((WIDTH, HEIGHT))
        p.display.set_caption('Chess')
        self.game = Game()
        self.clock = p.time.Clock()
        # Perft testing display options - used for engine verification
        self.show_perft = False
        self.perft_depth = 2  # Default perft depth
        
        # If AI is enabled and it's the AI's turn, let it move immediately
        while self.game.ai_enabled and self.game.ai and not self.game.game_over and self.game.next_player == self.game.ai.color:
            self.game.play_AI_turn(self.screen)

    def main_loop(self):
        """
        Main game loop that handles rendering, events, and game state updates.
        Processes user input including mouse clicks, keyboard shortcuts, and AI moves.
        """
        screen = self.screen
        clock = self.clock

        running = True

        while running:
            game = self.game  # Always get the latest game object
            theme_name = getattr(game.config.theme, "name", None)
            screen.fill((0, 0, 0))

            # Render the game state - board, pieces, highlights, etc.
            if not game.game_over:
                game.show_bg(screen)
                game.show_last_move(screen)
                game.show_selected(screen)
                game.show_moves(screen)
                game.show_pieces(screen)
                game.show_check(screen)
                game.show_hover(screen, p.mouse.get_pos())

                # Show perft analysis overlay for engine testing (press 'P' to toggle)
                if self.show_perft:
                    game.show_perft_result(screen, self.perft_depth)

                if game.dragger.dragging:
                    game.dragger.update_blit(screen, theme_name=theme_name)
            else:
                game.show_end_screen(screen)

            # Process all user input events
            for event in p.event.get():
                # Handle mouse interactions for piece movement
                if event.type == p.MOUSEBUTTONDOWN and not game.game_over:
                    game.handle_mouse_down(event.pos)

                elif event.type == p.MOUSEMOTION and not game.game_over:
                    game.handle_mouse_motion(event.pos, screen)

                elif event.type == p.MOUSEBUTTONUP and not game.game_over:
                    game.handle_mouse_up(event.pos, screen)

                # Handle keyboard shortcuts for various game functions
                elif event.type == p.KEYDOWN:
                    if event.key == p.K_t and not game.game_over:
                        game.change_theme()  # Change visual theme
                    elif event.key == p.K_r:
                        self.game = Game()  # Reset game
                        game = self.game
                    elif event.key == p.K_LEFT:
                        game.undo_move()  # Undo the last move
                    elif event.key == p.K_g and not game.game_over:
                        # Toggle AI opponent on/off
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
                        # Handle draw offers (press D twice to accept)
                        if game.draw_offered:
                            game.end_message = "Draw: Mutual Agreement"
                            game.game_over = True
                        else:
                            game.draw_offered = True
                            print("Draw offered. Press 'D' again to accept.")
                    elif event.key == p.K_f and not game.game_over:
                        # Load position from FEN notation
                        fen_str = input("Enter FEN: ")
                        game.load_fen(fen_str)
                    elif event.key == p.K_p and not game.game_over:
                        # Toggle perft display for engine testing
                        self.show_perft = not self.show_perft
                        print(f"Perft display: {self.show_perft}")
                    # Set perft testing depth (1-3 keys)
                    elif event.key == p.K_1:
                        self.perft_depth = 1
                        print("Perft depth set to 1")
                    elif event.key == p.K_2:
                        self.perft_depth = 2
                        print("Perft depth set to 2")
                    elif event.key == p.K_3:
                        self.perft_depth = 3
                        print("Perft depth set to 3")
                elif event.type == p.QUIT:
                    running = False

            clock.tick(MAX_FPS)
            p.display.update()

if __name__ == '__main__':
    main = Main()
    main.main_loop()
