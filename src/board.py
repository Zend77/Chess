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
        self.squares = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move, surface=None, promotion_piece=None):
        initial = move.initial
        final = move.final

        # En passant capture
        en_passant_empty = self.squares[final.row][final.col].is_empty()
        if isinstance(piece, Pawn):
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                self.squares[initial.row][initial.col + diff].piece = None

        # Move piece
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece
        piece.moved = True

        # Handle castling
        if isinstance(piece, King) and abs(initial.col - final.col) == 2:
            rook_col = 0 if final.col < initial.col else 7
            rook = self.squares[initial.row][rook_col].piece
            rook_final_col = 3 if final.col < initial.col else 5
            self.squares[initial.row][rook_col].piece = None
            self.squares[initial.row][rook_final_col].piece = rook
            rook.moved = True

        # Handle pawn promotion
        if isinstance(piece, Pawn) and (final.row == 0 or final.row == 7) and promotion_piece:
            promotion_piece.moved = True
            self.squares[final.row][final.col].piece = promotion_piece

        # Clear valid moves
        piece.clear_moves()

        # Update last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves

    def in_check(self, piece, move):
        initial_square = self.squares[move.initial.row][move.initial.col]
        final_square = self.squares[move.final.row][move.final.col]
        captured_piece = final_square.piece

        final_square.piece = piece
        initial_square.piece = None

        king_in_check = self.in_check_king(piece.color)

        initial_square.piece = piece
        final_square.piece = captured_piece

        return king_in_check

    def in_check_king(self, color):
        king_row, king_col = -1, -1
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece() and square.piece.name == 'king' and square.piece.color == color:
                    king_row, king_col = row, col

        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_enemy_piece(color):
                    enemy_piece = square.piece
                    self.calc_moves(enemy_piece, row, col, filter_checks=False)
                    for move in enemy_piece.moves:
                        if move.final.row == king_row and move.final.col == king_col:
                            return True
        return False

    def is_checkmate(self, color):
        if not self.in_check_king(color):
            return False
        return not self.player_has_moves(color)

    def is_stalemate(self, color):
        if self.in_check_king(color):
            return False
        return not self.player_has_moves(color)

    def player_has_moves(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece() and square.piece.color == color:
                    self.calc_moves(square.piece, row, col, filter_checks=True)
                    if square.piece.moves:
                        return True
        return False

    def calc_moves(self, piece, row, col, filter_checks=True):
        piece.clear_moves()

        # Get possible directions from the piece
        directions = piece.get_directions(row, col, self)

        # Add moves, filtering out illegal ones if filter_checks is True
        for move in directions:
            if filter_checks and self.in_check(piece, move):
                continue
            piece.add_move(move)


    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        placements = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_class in enumerate(placements):
            self.squares[row_other][col] = Square(row_other, col, piece_class(color))
