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

            # AI startup guard - trigger AI for first move only after initial render
            if (game.ai_enabled and game.ai and not game.game_over and 
                game.next_player == game.ai.color and not game.ai_has_moved_initially):
                game.ai_has_moved_initially = True
                game.play_AI_turn(screen)

            # Render the game state - board, pieces, highlights, etc.
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

            # Process all user input events
            # Skip event processing during AI cooldown to prevent phantom moves
            if game.ai_thinking_cooldown > 0:
                game.ai_thinking_cooldown -= 1
                # Clear events and reset dragger state
                p.event.clear()
                game.dragger.dragging = False
                game.dragger.piece = None
                game.selected_square = None
                
                if game.ai_thinking_cooldown == 0:
                    game.ai_is_thinking = False
                    # Final event clear
                    p.event.clear()
                
                # Skip to display update, don't process any events
                clock.tick(MAX_FPS)
                p.display.update()
                continue
                
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
                    elif event.key == p.K_RIGHT:
                        game.redo_move()  # Redo the last undone move
                    elif event.key == p.K_g and not game.game_over:
                        # Toggle AI opponent on/off
                        game.ai_enabled = not game.ai_enabled
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
                    elif event.key == p.K_v and not game.game_over:
                        # Toggle AI debug mode (verbose evaluation)
                        if game.ai:
                            current_debug = getattr(game.ai.search_engine, 'debug_mode', False)
                            game.ai.set_debug_mode(not current_debug)
                            debug_status = "ON" if not current_debug else "OFF"
                            print(f"\n🔍 AI Debug Mode: {debug_status}")
                            if not current_debug:
                                print("Press 'V' again to disable debug output")
                            print("-" * 50)
                        else:
                            print("❌ No AI enabled - press 'G' to enable AI first")
                    elif event.key == p.K_f and not game.game_over:
                        # Load position from FEN notation
                        fen_str = input("Enter FEN: ")
                        game.load_fen(fen_str)
                    elif event.key == p.K_h:
                        # Show help/controls
                        print("\n" + "=" * 50)
                        print("CHESS GAME CONTROLS")
                        print("=" * 50)
                        print("🎮 GAME CONTROLS:")
                        print("   Mouse: Click and drag to move pieces")
                        print("   R: Reset game")
                        print("   G: Toggle AI opponent on/off")
                        print("   ← →: Undo/Redo moves")
                        print("   T: Change visual theme")
                        print("   D: Offer draw (press twice to accept)")
                        print("   F: Load position from FEN")
                        print("   H: Show this help")
                        print("\n🔍 AI DEBUG MODE:")
                        print("   V: Toggle AI evaluation debug (shows calculations)")
                        print("      - See all moves the AI considers")
                        print("      - Breakdown by evaluation components")
                        print("      - Understand AI decision making")
                        print("=" * 50 + "\n")
                elif event.type == p.QUIT:
                    running = False

            clock.tick(MAX_FPS)
            
            p.display.update()

if __name__ == '__main__':
    main = Main()
    main.main_loop()
