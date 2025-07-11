import pygame as p

from const import *
from game import Game
from move import Move
from square import Square
from move import Move

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
                dragger.update_blit(screen)
            
            for event in p.event.get(): 
                # CLick mouse
                if event.type == p.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)
                    
                    clicked_row = dragger.mouseY // SQ_SIZE
                    clicked_col = dragger.mouseX // SQ_SIZE
                    
                    # If clicked square has piece ?
                    if board.squares[clicked_row][clicked_col].has_piece(): # type: ignore
                        piece = board.squares[clicked_row][clicked_col].piece # type: ignore
                        # Valid piece (color)
                        if piece.color == game.next_player: # type: ignore
                            game.selected_square = board.squares[clicked_row][clicked_col] # type: ignore
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
                        game.selected_square = None
                        
                # Mouse motion
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
                        dragger.update_blit(screen)
                        
                # Release mouse
                elif event.type == p.MOUSEBUTTONUP:
                    
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        
                        released_row = dragger.mouseY // SQ_SIZE
                        released_col = dragger.mouseX // SQ_SIZE

                        # Only proceed if released square is on the board
                        if 0 <= released_row < 8 and 0 <= released_col < 8:
                            # Create possible move
                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)
                            
                            # Valid move ? 
                            if board.valid_move(dragger.piece, move):
                                # Normal capture
                                captured = board.squares[released_row][released_col].has_enemy_piece(piece.color) # type: ignore
                                board.move(dragger.piece, move, screen)
                                # If you dont immedietly capture via en passant, dont allow it to happen on next move
                                board.set_true_en_passant(dragger.piece)
                                # Sounds
                                game.play_sound(captured)
                                # Show methods
                                game.show_bg(screen)
                                game.show_pieces(screen)
                                game.show_check(screen)
                                # Next turn
                                game.next_turn()
                                game.selected_square = None
                        # If not on board, just undrag (do nothing)
                    
                    dragger.undrag_piece()
                    
                # Key press
                elif event.type == p.KEYDOWN:
                    # Change theme using 't'
                    if event.key == p.K_t:
                        game.change_theme() 
                        
                    if event.key == p.K_r:
                        game.restart()
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger
                        clock = self.clock
                                
                # Quit application
                elif event.type == p.QUIT:
                    running = False
                    
            clock.tick(MAX_FPS)
            p.display.update()
    
main = Main()
main.main_loop()