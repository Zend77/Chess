import pygame as p

from piece import *
from const import *
from square import Square
from move import Move

class Board:
    def __init__(self):
        # Create an empty 8x8 list of squares, initially None
        self.squares: list[list[Square | None]] = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')
        
    def move(self, piece, move):
        initial = move.initial
        final = move.final

        # Move the piece within the square structure
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece
        
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
        pass
        
    
    def calc_moves(self, piece, row, col):
        '''
            Calculate all possible (valid) moves of a specific piece in a specific position
        '''
        piece.clear_moves()
        
        def pawn_moves():
            # Steps
            steps = 1 if piece.moved else 2
            
            # Vertical moves
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].is_empty():
                        # Create initial and final move squares
                        initial = Square(row, col)
                        final = Square(possible_move_row, col)
                        # Create a new move
                        move = Move(initial, final)
                        # Append new move
                        piece.add_move(move)
                    # Blocked
                    else: break
                # Not in range
                else: break
            
            # Diagonal moves
            possible_move_row = row + piece.dir
            possible_move_cols = [col-1, col+1]
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                        # Create initial and final move squares
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        # Create a new move
                        move = Move(initial, final)
                        # Append new move
                        piece.add_move(move)
                        
        def knight_moves():
            possible_moves = [
                (row-2, col+1), # 2 Up, 1 Right
                (row-1, col+2), # 1 Up, 2 Right
                (row+1, col+2), # 1 Down, 2 Right
                (row+2, col+1), # 2 Down, 1 Right
                (row+2, col-1), # 2 Down, 1 Left
                (row+1, col-2), # 1 Down, 2 Left
                (row-1, col-2), # 1 Up, 2 Left
                (row-2, col-1) # 2 Up, 1 Left
            ]
            
            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move
                
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].is_empty_or_enemy(piece.color):
                        # Create squares of the new move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col) # piece=piece
                        # Create new move
                        move = Move(initial, final)
                        # Append new valid move
                        piece.add_move(move)
                         
        def straight_line_moves(increments):
            for increment in increments:
                row_increment, col_increment = increment
                possible_move_row = row + row_increment
                possible_move_col = col + col_increment
                
                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        # Create squares of the possible new move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        # Create new possible move
                        move = Move(initial, final)
                        
                        # Empty
                        if self.squares[possible_move_row][possible_move_col].is_empty():
                            # Append new move
                            piece.add_move(move)
                        
                        # Has enemy piece = add move then break
                        if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            # Append new move
                            piece.add_move(move)
                            break
                    
                        # Has team piece = break
                        if self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break
                            
                    # Not in range
                    else: break
                            
                    # Increment the increments
                    possible_move_row = possible_move_row + row_increment
                    possible_move_col = possible_move_col + col_increment
                        
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
                        # Create squares of the new move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col) # piece=piece
                        # Create new move
                        move = Move(initial, final)
                        # Append new valid move
                        piece.add_move(move)
            # Castleing moves
            
                # Long castle (O-O-O)
                
                # Short castle (O-O)
                        
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
        
        