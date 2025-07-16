"""
Comprehensive opening book for the chess AI.
Contains extensive opening theory and punishes early queen development.
"""

from typing import Dict, List, Optional
import random

class OpeningBook:
    """
    Comprehensive opening book implementation with deep opening knowledge.
    Emphasizes sound opening principles and punishes premature queen development.
    """
    
    def __init__(self):
        # Comprehensive opening book with deeper lines
        # Format: FEN -> list of good moves with weights
        self.book = {
            # Starting position - sound first moves for white
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": [
                ("e2e4", 30), ("d2d4", 30), ("g1f3", 25), ("c2c4", 10), ("b1c3", 5)
            ],
            
            # KING'S PAWN OPENINGS (1.e4)
            # After 1.e4 - black responses
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1": [
                ("e7e5", 35), ("c7c5", 25), ("e7e6", 15), ("c7c6", 10), ("d7d6", 8), ("g8f6", 7)
            ],
            
            # 1.e4 e5 - King's Pawn Game
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2": [
                ("g1f3", 40), ("f2f4", 20), ("b1c3", 20), ("f1c4", 15), ("d2d3", 5)
            ],
            
            # 1.e4 e5 2.Nf3 - Knight attacks pawn
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2": [
                ("b8c6", 35), ("d7d6", 25), ("g8f6", 20), ("f7f5", 15), ("f8e7", 5)
            ],
            
            # ITALIAN GAME: 1.e4 e5 2.Nf3 Nc6 3.Bc4
            "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3": [
                ("f8e7", 25), ("f7f5", 20), ("g8f6", 20), ("f8c5", 15), ("d7d6", 10), ("h7h6", 5), ("a7a6", 5)
            ],
            
            # SPANISH/RUY LOPEZ: 1.e4 e5 2.Nf3 Nc6 3.Bb5
            "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3": [
                ("a7a6", 30), ("g8f6", 25), ("f7f5", 15), ("d7d6", 15), ("f8c5", 10), ("b7b5", 5)
            ],
            
            # SICILIAN DEFENSE: 1.e4 c5
            "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2": [
                ("g1f3", 40), ("b1c3", 25), ("f2f4", 15), ("d2d4", 10), ("g2g3", 5), ("c2c3", 5)
            ],
            
            # SICILIAN: 1.e4 c5 2.Nf3
            "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2": [
                ("d7d6", 25), ("b8c6", 25), ("g8f6", 20), ("g7g6", 15), ("e7e6", 10), ("a7a6", 5)
            ],
            
            # FRENCH DEFENSE: 1.e4 e6
            "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": [
                ("d2d4", 40), ("g1f3", 25), ("b1c3", 20), ("f2f4", 10), ("d2d3", 5)
            ],
            
            # FRENCH: 1.e4 e6 2.d4 d5
            "rnbqkbnr/ppp2ppp/4p3/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq d6 0 3": [
                ("b1c3", 30), ("e4d5", 25), ("e4e5", 20), ("g1f3", 15), ("f2f3", 10)
            ],
            
            # CARO-KANN: 1.e4 c6
            "rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": [
                ("d2d4", 35), ("g1f3", 25), ("b1c3", 20), ("f2f4", 10), ("d2d3", 10)
            ],
            
            # ALEKHINE'S DEFENSE: 1.e4 Nf6
            "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 1 2": [
                ("e4e5", 40), ("b1c3", 25), ("d2d3", 20), ("f2f3", 10), ("g1f3", 5)
            ],
            
            # QUEEN'S PAWN OPENINGS (1.d4)
            # After 1.d4 - black responses
            "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1": [
                ("d7d5", 30), ("g8f6", 25), ("f7f5", 15), ("e7e6", 15), ("c7c5", 10), ("g7g6", 5)
            ],
            
            # QUEEN'S GAMBIT: 1.d4 d5 2.c4
            "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3 0 2": [
                ("e7e6", 30), ("c7c6", 25), ("d5c4", 20), ("g8f6", 15), ("e7e5", 10)
            ],
            
            # KING'S INDIAN DEFENSE: 1.d4 Nf6 2.c4 g6
            "rnbqkb1r/pppppp1p/5np1/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3": [
                ("b1c3", 30), ("g1f3", 25), ("g2g3", 20), ("f2f3", 15), ("h2h3", 10)
            ],
            
            # NIMZO-INDIAN: 1.d4 Nf6 2.c4 e6 3.Nc3 Bb4
            "rnbqk2r/pppp1ppp/4pn2/8/1bPP4/2N5/PP2PPPP/R1BQKBNR w KQkq - 2 4": [
                ("e2e3", 25), ("g1f3", 25), ("a2a3", 20), ("d1c2", 15), ("f2f3", 10), ("c1d2", 5)
            ],
            
            # ENGLISH OPENING: 1.c4
            "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq c3 0 1": [
                ("e7e5", 25), ("g8f6", 25), ("c7c5", 20), ("e7e6", 15), ("g7g6", 10), ("d7d5", 5)
            ],
            
            # RETI OPENING: 1.Nf3
            "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1": [
                ("d7d5", 25), ("g8f6", 25), ("c7c5", 20), ("e7e6", 15), ("g7g6", 10), ("f7f5", 5)
            ],
            
            # DEEPER LINES AND THEORY
            
            # Italian Game main line: 1.e4 e5 2.Nf3 Nc6 3.Bc4 Be7 4.d3
            "r1bqk1nr/ppppbppp/2n5/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 4": [
                ("g8f6", 30), ("d7d6", 25), ("f7f5", 20), ("h7h6", 15), ("a7a6", 10)
            ],
            
            # Spanish main line: 1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4
            "r1bqkbnr/1ppp1ppp/p1n5/4p3/B3P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 1 4": [
                ("g8f6", 30), ("f7f5", 20), ("d7d6", 20), ("b7b5", 15), ("f8e7", 15)
            ],
            
            # Sicilian Dragon setup: 1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 g6
            "rnbqkb1r/pp2pp1p/3p1np1/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 6": [
                ("f2f3", 25), ("f1e2", 25), ("c1e3", 20), ("h2h3", 15), ("g2g3", 15)
            ],
            
            # Queen's Gambit Declined: 1.d4 d5 2.c4 e6 3.Nc3
            "rnbqkbnr/ppp2ppp/4p3/3p4/2PP4/2N5/PP2PPPP/R1BQKBNR b KQkq - 1 3": [
                ("g8f6", 30), ("c7c6", 25), ("f8e7", 20), ("d5c4", 15), ("b8d7", 10)
            ],
            
            # MORE DEEP OPENING LINES
            
            # Scandinavian Defense: 1.e4 d5 (uncommon but sound)
            "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2": [
                ("e4d5", 40), ("b1c3", 25), ("e4e5", 20), ("d2d3", 15)
            ],
            
            # After 1.e4 d5 2.exd5 Qxd5 (Black queen comes out early - we should develop with tempo)
            "rnb1kbnr/ppp1pppp/8/3q4/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 3": [
                ("b1c3", 40), ("g1f3", 30), ("d2d4", 20), ("f1c4", 10)
            ],
            
            # King's Gambit: 1.e4 e5 2.f4 (aggressive opening)
            "rnbqkbnr/pppp1ppp/8/4p3/4PP2/8/PPPP2PP/RNBQKBNR b KQkq f3 0 2": [
                ("e5f4", 30), ("d7d6", 25), ("f8c5", 20), ("g8f6", 15), ("e5e4", 10)
            ],
            
            # Vienna Game: 1.e4 e5 2.Nc3
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/2N5/PPPP1PPP/R1BQKBNR b KQkq - 1 2": [
                ("g8f6", 30), ("b8c6", 25), ("f8c5", 20), ("d7d6", 15), ("f7f5", 10)
            ],
            
            # Dutch Defense: 1.d4 f5
            "rnbqkbnr/ppppp1pp/8/5p2/3P4/8/PPP1PPPP/RNBQKBNR w KQkq f6 0 2": [
                ("g1f3", 30), ("c2c4", 25), ("g2g3", 20), ("b1c3", 15), ("e2e3", 10)
            ],
            
            # Bird's Opening: 1.f4
            "rnbqkbnr/pppppppp/8/8/5P2/8/PPPPP1PP/RNBQKBNR b KQkq f3 0 1": [
                ("d7d5", 25), ("g8f6", 25), ("c7c5", 20), ("e7e6", 15), ("g7g6", 10), ("e7e5", 5)
            ],
            
            # MORE ANTI-EARLY QUEEN POSITIONS
            
            # After 1.d4 d5 2.Qd3 (premature queen development by white)
            "rnbqkbnr/ppp1pppp/8/3p4/3P4/3Q4/PPP1PPPP/RNB1KBNR b KQkq - 1 2": [
                ("b8c6", 30), ("g8f6", 25), ("c8f5", 20), ("e7e6", 15), ("c7c6", 10)
            ],
            
            # After 1.e4 e5 2.Nf3 Nc6 3.Bc4 f5 (premature attack)
            "r1bqkbnr/pppp1ppp/2n5/4pp2/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq f6 0 4": [
                ("d2d3", 30), ("e4f5", 25), ("b1c3", 20), ("d1e2", 15), ("h2h3", 10)
            ],
            
            # Wayward Queen Attack defense: 1.e4 e5 2.Qh5 Nc6 3.Bc4
            "r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 3 3": [
                ("g7g6", 35), ("g8f6", 25), ("f8e7", 20), ("d7d6", 15), ("h7h6", 5)
            ],
            
            # Légal's Mate setup defense: 1.e4 e5 2.Nf3 d6 3.Bc4 Bg4 4.Nc3 g6?? (bad move)
            # We give good alternatives after 3...Bg4
            "r1bqkbnr/ppp2ppp/3p4/4p3/2B1P1b1/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 1 5": [
                ("h2h3", 30), ("d1d2", 25), ("f1e2", 20), ("d2d3", 15), ("a2a3", 10)
            ]
        }
        
        # Store forbidden moves (early queen development)
        self.forbidden_moves = {
            # Starting position - no early queen moves
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": [
                "d1h5", "d1g4", "d1f3", "d1e2"
            ],
            
            # After 1.e4 - no immediate queen moves
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1": [
                "d8h4", "d8g5", "d8f6", "d8e7"
            ],
            
            # Many more positions where early queen moves are bad...
        }
    
    def get_book_move(self, fen: str) -> Optional[str]:
        """
        Get a book move for the given position using weighted selection.
        
        Args:
            fen: FEN string of current position
            
        Returns:
            Algebraic notation move string or None if not in book
        """
        if fen in self.book:
            moves_with_weights = self.book[fen]
            
            # Check for forbidden moves first
            if fen in self.forbidden_moves:
                forbidden = set(self.forbidden_moves[fen])
                # Filter out forbidden moves
                moves_with_weights = [(move, weight) for move, weight in moves_with_weights 
                                    if move not in forbidden]
            
            if not moves_with_weights:
                return None
            
            # Weighted random selection
            moves = [move for move, weight in moves_with_weights]
            weights = [weight for move, weight in moves_with_weights]
            
            # Use weighted random choice
            total_weight = sum(weights)
            if total_weight == 0:
                return random.choice(moves)
            
            r = random.uniform(0, total_weight)
            cumulative = 0
            for move, weight in moves_with_weights:
                cumulative += weight
                if r <= cumulative:
                    return move
            
            # Fallback to last move if something went wrong
            return moves[-1]
        
        return None
    
    def is_in_book(self, fen: str) -> bool:
        """Check if position is in opening book."""
        return fen in self.book
    
    def add_position(self, fen: str, moves: List[str], weights: Optional[List[int]] = None) -> None:
        """Add a position and its moves to the book."""
        if weights is None:
            weights = [1] * len(moves)  # Equal weights if not specified
        
        if len(moves) != len(weights):
            raise ValueError("Number of moves must match number of weights")
        
        self.book[fen] = list(zip(moves, weights))
    
    def get_book_size(self) -> int:
        """Get number of positions in book."""
        return len(self.book)
    
    def is_forbidden_move(self, fen: str, move: str) -> bool:
        """Check if a move is forbidden in the given position."""
        if fen in self.forbidden_moves:
            return move in self.forbidden_moves[fen]
        return False
    
    def get_opening_name(self, moves: List[str]) -> str:
        """
        Get the name of the opening based on the sequence of moves.
        Useful for educational purposes and debugging.
        """
        move_sequence = " ".join(moves)
        
        # Basic opening recognition
        openings = {
            "e2e4 e7e5 g1f3 b8c6 f1c4": "Italian Game",
            "e2e4 e7e5 g1f3 b8c6 f1b5": "Ruy Lopez (Spanish Opening)",
            "e2e4 c7c5": "Sicilian Defense",
            "e2e4 e7e6": "French Defense", 
            "e2e4 c7c6": "Caro-Kann Defense",
            "e2e4 g8f6": "Alekhine's Defense",
            "d2d4 d7d5": "Queen's Pawn Game",
            "d2d4 d7d5 c2c4": "Queen's Gambit",
            "d2d4 g8f6": "Indian Defense",
            "d2d4 g8f6 c2c4 g7g6": "King's Indian Defense",
            "d2d4 g8f6 c2c4 e7e6 b1c3 f8b4": "Nimzo-Indian Defense",
            "c2c4": "English Opening",
            "g1f3": "Reti Opening"
        }
        
        for pattern, name in openings.items():
            if move_sequence.startswith(pattern):
                return name
        
        return "Unknown Opening"
