import pygame as p

from const import *
from game import Game
from move import Move
from square import Square

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
        board = self.game.board
        dragger = self.game.dragger
        clock = self.clock
        
        running = True
        
        while running:
            theme_name = getattr(game.config.theme, "name", None)
            screen.fill((0,0,0))
            
            # Show methods
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_selected(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_check(screen)
            game.show_hover(screen, p.mouse.get_pos())
            
            if dragger.dragging:
                dragger.update_blit(screen, theme_name=theme_name)
            
            for event in p.event.get(): 
                if event.type == p.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)
                    clicked_row = dragger.mouseY // SQ_SIZE
                    clicked_col = dragger.mouseX // SQ_SIZE

                    # Only allow clicks inside the board
                    if 0 <= clicked_row < 8 and 0 <= clicked_col < 8:
                        square = board.squares[clicked_row][clicked_col]
                        if square.has_piece(): # type: ignore
                            piece = square.piece # type: ignore
                            # Only allow selecting your own piece and not while dragging
                            if piece.color == game.next_player and not dragger.dragging: # type: ignore
                                game.selected_square = square # type: ignore
                                board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                dragger.save_inital(event.pos)
                                dragger.drag_piece(piece)
                                # Show methods
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_selected(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)
                                game.show_check(screen)
                                game.show_hover(screen, p.mouse.get_pos())
                            else:
                                # Clicked on opponent's piece or while dragging: clear selection/drag
                                game.selected_square = None
                                dragger.undrag_piece(theme_name=theme_name)
                        else:
                            # Clicked empty square: clear selection/drag
                            game.selected_square = None
                            dragger.undrag_piece(theme_name=theme_name)
                    else:
                        # Clicked outside board: clear selection/drag
                        game.selected_square = None
                        dragger.undrag_piece(theme_name=theme_name)
                        
                elif event.type == p.MOUSEMOTION:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_selected(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_check(screen)
                        game.show_hover(screen, p.mouse.get_pos())
                        dragger.update_blit(screen, theme_name=theme_name)
                        
                elif event.type == p.MOUSEBUTTONUP:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        released_row = dragger.mouseY // SQ_SIZE
                        released_col = dragger.mouseX // SQ_SIZE

                        if 0 <= released_row < 8 and 0 <= released_col < 8:
                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)
                            if board.valid_move(dragger.piece, move):
                                captured = board.squares[released_row][released_col].has_enemy_piece(dragger.piece.color) # type: ignore
                                board.move(dragger.piece, move, screen)
                                board.set_true_en_passant(dragger.piece)
                                game.play_sound(captured)
                                game.show_bg(screen)
                                game.show_pieces(screen)
                                game.show_check(screen)
                                game.next_turn()
                                game.selected_square = None
                        # Always undrag, even if not a valid move
                        dragger.undrag_piece(theme_name=theme_name)
                    else:
                        # Mouse released but not dragging: clear selection
                        game.selected_square = None
                        
                elif event.type == p.KEYDOWN:
                    if event.key == p.K_t:
                        game.change_theme() 
                    if event.key == p.K_r:
                        game.restart()
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger
                        clock = self.clock
                                
                elif event.type == p.QUIT:
                    running = False
                    
            clock.tick(MAX_FPS)
            p.display.update()
    
if __name__ == '__main__':
    main = Main()
    main.main_loop()