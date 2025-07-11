import pygame as p
import copy
import os

from piece import *
from const import *
from square import Square
from move import Move
from sound import Sound

class Board:
    def __init__(self):
        # Create an empty 8x8 list of squares, initially None
        self.squares: list[list[Square | None]] = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')
        
    def move(self, piece, move, surface=None, testing=False):
        initial = move.initial
        final = move.final
        
        en_passant_empty = self.squares[final.row][final.col].is_empty()

        # Move the piece within the square structure
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        # En passant and promotion
        if isinstance(piece, Pawn):
            # En passant capture
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                # Move the piece within the square structure
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Sound(os.path.join(
                        'assets/sounds/capture.wav'
                    ))
                    sound.play()
                
            # Promotion
            if (final.row == 0 or final.row == 7) and surface is not None:
                self.check_promotion(surface, piece, final)

        # Castling
        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.queen_side_rook if (diff < 0) else piece.king_side_rook
                self.move(rook, rook.moves[-1], surface) # type: ignore

        # Mark the piece as moved
        piece.moved = True

        # Clear valid moves
        piece.clear_moves()

        # Set last move
        self.last_move = move     
    
    def valid_move(self, piece, move):
        return move in piece.moves
    
    def check_promotion(self, surface, piece, final):
        if final.row != 0 and final.row != 7:
            return  # Not a promotion square

        # Create a simple prompt window
        font = p.font.SysFont('Arial', 32)
        options = [('Queen', 'Q'), ('Rook', 'R'), ('Bishop', 'B'), ('Knight', 'K')]
        selecting = True

        while selecting:
            surface.fill((30, 30, 30))  # Dark background

            # Render instruction
            prompt = font.render("Promote pawn to:", True, (255, 255, 255))
            surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 150))

            # Render options vertically
            for i, (name, key) in enumerate(options):
                text = font.render(f"{name} - Press {key}", True, (255, 255, 255))
                surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 50))

            p.display.flip()

            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    exit()

                if event.type == p.KEYDOWN:
                    if event.key == p.K_q:
                        selected_piece = 'Q'
                        selecting = False
                    elif event.key == p.K_r:
                        selected_piece = 'R'
                        selecting = False
                    elif event.key == p.K_b:
                        selected_piece = 'B'
                        selecting = False
                    elif event.key == p.K_k:
                        selected_piece = 'K'
                        selecting = False

        # Create the chosen piece
        color = piece.color
        if selected_piece == 'Q':
            new_piece = Queen(color)
        elif selected_piece == 'R':
            new_piece = Rook(color)
        elif selected_piece == 'B':
            new_piece = Bishop(color)
        elif selected_piece == 'K':
            new_piece = Knight(color)

        self.squares[final.row][final.col].piece = new_piece
        
    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2
    
    def set_true_en_passant(self, piece):
        if not isinstance(piece, Pawn):
            return
        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn): # type: ignore
                    self.squares[row][col].piece.en_passant = False # type: ignore
        
        piece.en_passant = True
                            
    def in_check(self, piece, move, surface=None):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move, surface, testing=True)

        # Find the king's position after the move
        king_row, king_col = move.final.row, move.final.col
        if piece.name != 'king':
            # If not moving the king, find the king's current position
            for row in range(ROWS):
                for col in range(COLS):
                    sq = temp_board.squares[row][col]
                    if sq.has_piece() and sq.piece.name == 'king' and sq.piece.color == piece.color: # type: ignore
                        king_row, king_col = row, col

        # Now check if any enemy piece attacks the king's square
        for row in range(ROWS):
            for col in range(COLS):
                sq = temp_board.squares[row][col]
                if sq.has_enemy_piece(piece.color): # type: ignore
                    enemy_piece = sq.piece # type: ignore
                    temp_board.calc_moves(enemy_piece, row, col, bool=False)
                    for m in enemy_piece.moves: # type: ignore
                        if m.final.row == king_row and m.final.col == king_col:
                            return True
        return False
                        
    def calc_moves(self, piece, row, col, bool=True):
        '''
            Calculate all possible (valid) moves of a specific piece in a specific position
        '''
        piece.clear_moves()
        
        def pawn_moves():
            # One square forward
            one_step_row = row + piece.dir
            if Square.in_range(one_step_row):
                if self.squares[one_step_row][col].is_empty():
                    initial = Square(row, col)
                    final = Square(one_step_row, col)
                    move = Move(initial, final)
                    if bool:
                        if not self.in_check(piece, move):
                            piece.add_move(move)
                    else:
                        piece.add_move(move)
                    
                    # Two squares forward (only if first move and one square forward is empty)
                    two_step_row = row + piece.dir * 2
                    if not piece.moved and Square.in_range(two_step_row):
                        if self.squares[two_step_row][col].is_empty():
                            initial = Square(row, col)
                            final = Square(two_step_row, col)
                            move = Move(initial, final)
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)

            # Diagonal moves
            possible_move_row = row + piece.dir
            possible_move_cols = [col-1, col+1]
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                        # Create initial and final move squares
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        # Create a new move
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                # Append new move
                                piece.add_move(move)
                        else:
                            # Append new move
                            piece.add_move(move)
                            
            # En passant moves
            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5
            # Left en passant
            if Square.in_range(col+1) and row == r:
                if self.squares[row][col+1].has_enemy_piece(piece.color):
                    piece_to_capture = self.squares[row][col+1].piece
                    if isinstance(piece_to_capture, Pawn):
                        if piece_to_capture.en_passant:
                            # Create initial and final move squares
                            initial = Square(row, col)
                            final = Square(fr, col+1, piece_to_capture)
                            # Create a new move
                            move = Move(initial, final)
                            if bool:
                                if not self.in_check(piece, move):
                                    # Append new move
                                    piece.add_move(move)
                            else:
                                # Append new move
                                piece.add_move(move)
            # Right en passant
            if Square.in_range(col-1) and row == r:
                if self.squares[row][col-1].has_enemy_piece(piece.color):
                    piece_to_capture = self.squares[row][col-1].piece
                    if isinstance(piece_to_capture, Pawn):
                        if piece_to_capture.en_passant:
                            # Create initial and final move squares
                            initial = Square(row, col)
                            final = Square(fr, col-1, piece_to_capture)
                            # Create a new move
                            move = Move(initial, final)
                            if bool:
                                if not self.in_check(piece, move):
                                    # Append new move
                                    piece.add_move(move)
                            else:
                                # Append new move
                                piece.add_move(move)
                            
                        
        def knight_moves():
            possible_moves = [
                (row-2, col+1), (row-1, col+2), (row+1, col+2), (row+2, col+1),
                (row+2, col-1), (row+1, col-2), (row-1, col-2), (row-2, col-1)
            ]
            for possible_move_row, possible_move_col in possible_moves:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].is_empty_or_enemy(piece.color):
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else:
                                continue  # FIXED
                        else:
                            piece.add_move(move)

        def straight_line_moves(increments):
            for row_increment, col_increment in increments:
                possible_move_row = row + row_increment
                possible_move_col = col + col_increment
                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial, final)
                        if self.squares[possible_move_row][possible_move_col].is_empty():
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                                else:
                                    continue  # FIXED
                            else:
                                piece.add_move(move)
                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                                else:
                                    continue  # FIXED
                            else:
                                piece.add_move(move)
                            break
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break
                    else:
                        break
                    possible_move_row += row_increment
                    possible_move_col += col_increment
                        
        def king_moves():
            adjacent = [
                (row-1, col-1),  # Up-Left
                (row-1, col+0),  # Up
                (row-1, col+1),  # Up-Right
                (row+0, col-1),  # Left
                (row+0, col+1),  # Right
                (row+1, col-1),  # Down-Left
                (row+1, col+0),  # Down
                (row+1, col+1)   # Down-Right
            ]

            # Normal moves
            for possible_move in adjacent:
                possible_move_row, possible_move_col = possible_move
                
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].is_empty_or_enemy(piece.color):
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else:
                                continue
                        else:
                            piece.add_move(move)

            # Castling moves
            if not piece.moved:
                # Long castle (O-O-O)
                queen_side_rook = self.squares[row][0].piece
                if isinstance(queen_side_rook, Rook) and not queen_side_rook.moved:
                    # Squares between king and rook must be empty
                    if all(not self.squares[row][c].has_piece() for c in range(1, 4)):
                        # Squares king passes through: col 4 (current), 3, 2
                        can_castle = True
                        for c in [4, 3, 2]:
                            test_king = copy.deepcopy(piece)
                            test_move = Move(Square(row, 4), Square(row, c))
                            if self.in_check(test_king, test_move):
                                can_castle = False
                                break
                        if can_castle:
                            piece.queen_side_rook = queen_side_rook
                            # Rook move
                            initial = Square(row, 0)
                            final = Square(row, 3)
                            move_R = Move(initial, final)
                            # King move
                            initial = Square(row, col)
                            final = Square(row, 2)
                            move_K = Move(initial, final)
                            if bool:
                                queen_side_rook.add_move(move_R)
                                piece.add_move(move_K)
                            else:
                                queen_side_rook.add_move(move_R)
                                piece.add_move(move_K)

                # Short castle (O-O)
                king_side_rook = self.squares[row][7].piece
                if isinstance(king_side_rook, Rook) and not king_side_rook.moved:
                    # Squares between king and rook must be empty
                    if all(not self.squares[row][c].has_piece() for c in range(5, 7)):
                        # Squares king passes through: col 4 (current), 5, 6
                        can_castle = True
                        for c in [4, 5, 6]:
                            test_king = copy.deepcopy(piece)
                            test_move = Move(Square(row, 4), Square(row, c))
                            if self.in_check(test_king, test_move):
                                can_castle = False
                                break
                        if can_castle:
                            piece.king_side_rook = king_side_rook
                            # Rook move
                            initial = Square(row, 7)
                            final = Square(row, 5)
                            move_R = Move(initial, final)
                            # King move
                            initial = Square(row, col)
                            final = Square(row, 6)
                            move_K = Move(initial, final)
                            if bool:
                                king_side_rook.add_move(move_R)
                                piece.add_move(move_K)
                            else:
                                king_side_rook.add_move(move_R)
                                piece.add_move(move_K)
                                
                        
        if isinstance(piece, Pawn): 
            pawn_moves()
        
        elif isinstance(piece, Knight): 
            knight_moves()
        
        elif isinstance(piece, Bishop): 
            straight_line_moves([
                (-1, 1), # up-right
                (-1, -1), # up-left
                (1, 1), # down-right
                (1, -1) # down-left
            ])
    
        elif isinstance(piece, Rook): 
            straight_line_moves([
                (-1, 0), # up
                (1, 0), # down
                (0, 1), # right
                (0, -1) # left
            ])
        
        elif isinstance(piece, Queen): 
            straight_line_moves([
                (-1, 1), # up-right
                (-1, -1), # up-left
                (1, 1), # down-right
                (1, -1), # down-left
                (-1, 0), # up
                (1, 0), # down
                (0, 1), # right
                (0, -1) # left
            ])
        
        elif isinstance(piece, King): 
            king_moves()
        
    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)
    
    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1,0)
        
        # Pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))
   
        # Knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))
        
        # Bishiops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))
       
        # Rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # Queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # King
        self.squares[row_other][4] = Square(row_other, 4, King(color))

