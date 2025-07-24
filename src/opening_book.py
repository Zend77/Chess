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
            
            # EXTENSIVE D4 OPENING COVERAGE
            
            # After 1.d4 - black responses
            "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1": [
                ("d7d5", 30), ("g8f6", 25), ("f7f5", 15), ("e7e6", 15), ("c7c5", 10), ("g7g6", 5)
            ],
            
            # After 1.d4 d5 - Queen's Pawn Game main lines
            "rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq d6 0 2": [
                ("c2c4", 35), ("g1f3", 30), ("c1f4", 25), ("e2e3", 20), ("b1c3", 15), ("c1g5", 10)
            ],
            
            # London System: 1.d4 d5 2.Bf4
            "rnbqkbnr/ppp1pppp/8/3p4/3P1B2/8/PPP1PPPP/RN1QKBNR b KQkq - 1 2": [
                ("g8f6", 30), ("c7c6", 25), ("e7e6", 20), ("b8c6", 15), ("c8f5", 10)
            ],
            
            # London System: 1.d4 d5 2.Bf4 Nf6 3.e3
            "rnbqkb1r/ppp1pppp/5n2/3p4/3P1B2/4P3/PPP2PPP/RN1QKBNR b KQkq - 0 3": [
                ("e7e6", 30), ("c7c6", 25), ("c8f5", 20), ("g7g6", 15), ("b8d7", 10)
            ],
            
            # London System: 1.d4 d5 2.Bf4 Nf6 3.e3 e6 4.Nd2
            "rnbqkb1r/ppp2ppp/4pn2/3p4/3P1B2/4P3/PPPN1PPP/R2QKBNR b KQkq - 1 4": [
                ("c7c5", 30), ("f8d6", 25), ("b8d7", 20), ("c8d7", 15), ("a7a6", 10)
            ],
            
            # Queen's Gambit: 1.d4 d5 2.c4
            "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3 0 2": [
                ("e7e6", 30), ("c7c6", 25), ("d5c4", 20), ("g8f6", 15), ("e7e5", 10)
            ],
            
            # Queen's Gambit Accepted: 1.d4 d5 2.c4 dxc4
            "rnbqkbnr/ppp1pppp/8/8/2pP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3": [
                ("g1f3", 35), ("e2e3", 25), ("e2e4", 20), ("b1c3", 15), ("f1c4", 5)
            ],
            
            # Queen's Gambit Declined: 1.d4 d5 2.c4 e6
            "rnbqkbnr/ppp2ppp/4p3/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3": [
                ("b1c3", 35), ("g1f3", 30), ("c1f4", 20), ("e2e3", 15)
            ],
            
            # Queen's Gambit Declined: 1.d4 d5 2.c4 e6 3.Nc3 Nf6
            "rnbqkb1r/ppp2ppp/4pn2/3p4/2PP4/2N5/PP2PPPP/R1BQKBNR w KQkq - 1 4": [
                ("c1g5", 30), ("g1f3", 25), ("c4d5", 20), ("e2e3", 15), ("a2a3", 10)
            ],
            
            # Slav Defense: 1.d4 d5 2.c4 c6
            "rnbqkbnr/pp2pppp/2p5/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3": [
                ("g1f3", 35), ("b1c3", 25), ("e2e3", 20), ("c4d5", 15), ("c1f4", 5)
            ],
            
            # Slav Defense: 1.d4 d5 2.c4 c6 3.Nf3 Nf6
            "rnbqkb1r/pp2pppp/2p2n2/3p4/2PP4/5N2/PP2PPPP/RNBQKB1R w KQkq - 1 4": [
                ("b1c3", 30), ("e2e3", 25), ("c1f4", 20), ("g2g3", 15), ("c4d5", 10)
            ],
            
            # Caro-Kann structure in Queen's pawn: 1.d4 d5 2.c4 c6 3.Nf3 Nf6 4.Nc3
            "rnbqkb1r/pp2pppp/2p2n2/3p4/2PP4/2N2N2/PP2PPPP/R1BQKB1R b KQkq - 2 4": [
                ("d5c4", 25), ("e7e6", 25), ("c8f5", 20), ("a7a6", 15), ("g7g6", 15)
            ],
            
            # Indian Defense setups: 1.d4 Nf6
            "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 1 2": [
                ("c2c4", 40), ("g1f3", 25), ("c1g5", 15), ("b1c3", 10), ("e2e3", 10)
            ],
            
            # King's Indian Defense: 1.d4 Nf6 2.c4 g6
            "rnbqkb1r/pppppp1p/5np1/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3": [
                ("b1c3", 35), ("g1f3", 30), ("g2g3", 20), ("f2f3", 10), ("h2h3", 5)
            ],
            
            # King's Indian Defense: 1.d4 Nf6 2.c4 g6 3.Nc3 Bg7
            "rnbqk2r/ppppppbp/5np1/8/2PP4/2N5/PP2PPPP/R1BQKBNR w KQkq - 1 4": [
                ("e2e4", 40), ("g1f3", 30), ("f2f3", 15), ("g2g3", 10), ("c1g5", 5)
            ],
            
            # Nimzo-Indian Defense: 1.d4 Nf6 2.c4 e6 3.Nc3 Bb4
            "rnbqk2r/pppp1ppp/4pn2/8/1bPP4/2N5/PP2PPPP/R1BQKBNR w KQkq - 2 4": [
                ("e2e3", 30), ("g1f3", 25), ("a2a3", 20), ("d1c2", 15), ("f2f3", 10)
            ],
            
            # Queen's Indian Defense: 1.d4 Nf6 2.c4 e6 3.Nf3 b6
            "rnbqkb1r/p1pp1ppp/1p2pn2/8/2PP4/5N2/PP2PPPP/RNBQKB1R w KQkq - 0 4": [
                ("g2g3", 30), ("e2e3", 25), ("a2a3", 20), ("b1c3", 15), ("c1g5", 10)
            ],
            
            # Bogo-Indian Defense: 1.d4 Nf6 2.c4 e6 3.Nf3 Bb4+
            "rnbqk2r/pppp1ppp/4pn2/8/1bPP4/5N2/PP2PPPP/RNBQKB1R w KQkq - 2 4": [
                ("c1d2", 30), ("b1d2", 25), ("b1c3", 20), ("a2a3", 15), ("d1c2", 10)
            ],
            
            # Dutch Defense: 1.d4 f5
            "rnbqkbnr/ppppp1pp/8/5p2/3P4/8/PPP1PPPP/RNBQKBNR w KQkq f6 0 2": [
                ("g1f3", 30), ("c2c4", 25), ("g2g3", 20), ("b1c3", 15), ("e2e3", 10)
            ],
            
            # Dutch Defense: 1.d4 f5 2.c4 Nf6
            "rnbqkb1r/ppppp1pp/5n2/5p2/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 1 3": [
                ("g1f3", 30), ("b1c3", 25), ("g2g3", 20), ("f2f3", 15), ("e2e3", 10)
            ],
            
            # Benoni Defense: 1.d4 Nf6 2.c4 c5
            "rnbqkb1r/pp1ppppp/5n2/2p5/2PP4/8/PP2PPPP/RNBQKBNR w KQkq c6 0 3": [
                ("d4d5", 35), ("g1f3", 25), ("b1c3", 20), ("e2e3", 15), ("d4c5", 5)
            ],
            
            # Modern Benoni: 1.d4 Nf6 2.c4 c5 3.d5 e6
            "rnbqkb1r/pp1p1ppp/4pn2/2pP4/2P5/8/PP2PPPP/RNBQKBNR w KQkq - 0 4": [
                ("b1c3", 35), ("g1f3", 25), ("e2e4", 20), ("d5e6", 15), ("f2f4", 5)
            ],
            
            # English Opening: 1.c4
            "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq c3 0 1": [
                ("e7e5", 25), ("g8f6", 25), ("c7c5", 20), ("e7e6", 15), ("g7g6", 10), ("d7d5", 5)
            ],
            
            # English Opening: 1.c4 e5 (Reversed Sicilian)
            "rnbqkbnr/pppp1ppp/8/4p3/2P5/8/PP1PPPPP/RNBQKBNR w KQkq e6 0 2": [
                ("b1c3", 30), ("g1f3", 25), ("g2g3", 20), ("d2d3", 15), ("e2e3", 10)
            ],
            
            # Reti Opening: 1.Nf3
            "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1": [
                ("d7d5", 25), ("g8f6", 25), ("c7c5", 20), ("e7e6", 15), ("g7g6", 10), ("f7f5", 5)
            ],
            
            # Reti: 1.Nf3 d5 - White should develop, not move knight again
            "rnbqkbnr/ppp1pppp/8/3p4/8/5N2/PPPPPPPP/RNBQKB1R w KQkq d6 0 2": [
                ("c2c4", 35), ("d2d4", 30), ("g2g3", 20), ("e2e3", 10), ("b2b3", 5)
            ],
            
            # Reti: 1.Nf3 Nf6 - White should NOT play Ng5
            "rnbqkb1r/pppppppp/5n2/8/8/5N2/PPPPPPPP/RNBQKB1R w KQkq - 2 2": [
                ("c2c4", 35), ("d2d4", 30), ("g2g3", 20), ("e2e3", 10), ("b2b3", 5)
            ],
            
            # After 1.Nf3 Nc6 - Absolutely NO knight moves, develop other pieces
            "r1bqkbnr/pppppppp/2n5/8/8/5N2/PPPPPPPP/RNBQKB1R w KQkq - 2 2": [
                ("d2d4", 35), ("c2c4", 30), ("e2e4", 25), ("g2g3", 10)
            ],
            
            # Reti: 1.Nf3 d5 2.c4
            "rnbqkbnr/ppp1pppp/8/3p4/2P5/5N2/PP1PPPPP/RNBQKB1R b KQkq c3 0 2": [
                ("e7e6", 25), ("c7c6", 25), ("g8f6", 20), ("d5c4", 15), ("c8g4", 15)
            ],
            
            # Reti: 1.Nf3 Nf6 2.c4
            "rnbqkb1r/pppppppp/5n2/8/2P5/5N2/PP1PPPPP/RNBQKB1R b KQkq c3 0 2": [
                ("g7g6", 25), ("e7e6", 25), ("c7c5", 20), ("d7d5", 15), ("b7b6", 15)
            ],
            
            # Catalan Opening: 1.d4 Nf6 2.c4 e6 3.g3
            "rnbqkb1r/pppp1ppp/4pn2/8/2PP4/6P1/PP2PP1P/RNBQKBNR b KQkq - 0 3": [
                ("d7d5", 35), ("f8e7", 25), ("c7c5", 20), ("b7b6", 15), ("f8b4", 5)
            ],
            
            # Catalan: 1.d4 Nf6 2.c4 e6 3.g3 d5
            "rnbqkb1r/ppp2ppp/4pn2/3p4/2PP4/6P1/PP2PP1P/RNBQKBNR w KQkq d6 0 4": [
                ("f1g2", 35), ("c4d5", 25), ("g1f3", 20), ("b1c3", 15), ("c1g5", 5)
            ],
            
            # Bird's Opening: 1.f4
            "rnbqkbnr/pppppppp/8/8/5P2/8/PPPPP1PP/RNBQKBNR b KQkq f3 0 1": [
                ("d7d5", 25), ("g8f6", 25), ("c7c5", 20), ("e7e6", 15), ("g7g6", 10), ("e7e5", 5)
            ],
            
            # EXPANDED COVERAGE FOR COMMON POSITIONS
            
            # After 1.d4 d5 2.Nf3 (Quiet development)
            "rnbqkbnr/ppp1pppp/8/3p4/3P4/5N2/PPP1PPPP/RNBQKB1R b KQkq - 1 2": [
                ("g8f6", 30), ("c8f5", 25), ("e7e6", 20), ("c7c6", 15), ("b8c6", 10)
            ],
            
            # After 1.d4 d5 2.Nf3 Nf6 3.e3
            "rnbqkb1r/ppp1pppp/5n2/3p4/3P4/4PN2/PPP2PPP/RNBQKB1R b KQkq - 0 3": [
                ("e7e6", 30), ("c8f5", 25), ("c7c6", 20), ("g7g6", 15), ("b8d7", 10)
            ],
            
            # After 1.d4 d5 2.e3 (Stonewall setup)
            "rnbqkbnr/ppp1pppp/8/3p4/3P4/4P3/PPP2PPP/RNBQKBNR b KQkq - 0 2": [
                ("g8f6", 30), ("c8f5", 25), ("e7e6", 20), ("c7c5", 15), ("f7f5", 10)
            ],
            
            # After 1.d4 d5 2.g3 (Fianchetto setup)
            "rnbqkbnr/ppp1pppp/8/3p4/3P4/6P1/PPP1PP1P/RNBQKBNR b KQkq - 0 2": [
                ("g8f6", 30), ("c8f5", 25), ("e7e6", 20), ("c7c6", 15), ("f7f5", 10)
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
            
            # ADDITIONAL COMPREHENSIVE D4 COVERAGE
            
            # After 1.d4 d5 2.Nf3 (Quiet development)
            "rnbqkbnr/ppp1pppp/8/3p4/3P4/5N2/PPP1PPPP/RNBQKB1R b KQkq - 1 2": [
                ("g8f6", 30), ("c8f5", 25), ("e7e6", 20), ("c7c6", 15), ("b8c6", 10)
            ],
            
            # After 1.d4 d5 2.Nf3 Nf6 3.e3
            "rnbqkb1r/ppp1pppp/5n2/3p4/3P4/4PN2/PPP2PPP/RNBQKB1R b KQkq - 0 3": [
                ("e7e6", 30), ("c8f5", 25), ("c7c6", 20), ("g7g6", 15), ("b8d7", 10)
            ],
            
            # After 1.d4 d5 2.e3 (Stonewall setup)
            "rnbqkbnr/ppp1pppp/8/3p4/3P4/4P3/PPP2PPP/RNBQKBNR b KQkq - 0 2": [
                ("g8f6", 30), ("c8f5", 25), ("e7e6", 20), ("c7c5", 15), ("f7f5", 10)
            ],
            
            # After 1.d4 d5 2.g3 (Fianchetto setup)
            "rnbqkbnr/ppp1pppp/8/3p4/3P4/6P1/PPP1PP1P/RNBQKBNR b KQkq - 0 2": [
                ("g8f6", 30), ("c8f5", 25), ("e7e6", 20), ("c7c6", 15), ("f7f5", 10)
            ],
            
            # Queen's Gambit Accepted: 1.d4 d5 2.c4 dxc4 3.Nf3
            "rnbqkbnr/ppp1pppp/8/8/2pP4/5N2/PP2PPPP/RNBQKB1R b KQkq - 1 3": [
                ("g8f6", 30), ("a7a6", 25), ("e7e6", 20), ("b7b5", 15), ("c8g4", 10)
            ],
            
            # Queen's Gambit Accepted: 1.d4 d5 2.c4 dxc4 3.Nf3 Nf6 4.e3
            "rnbqkb1r/ppp1pppp/5n2/8/2pP4/4PN2/PP3PPP/RNBQKB1R b KQkq - 0 4": [
                ("e7e6", 30), ("a7a6", 25), ("b7b5", 20), ("c8g4", 15), ("c7c5", 10)
            ],
            
            # Queen's Gambit Declined: 1.d4 d5 2.c4 e6 3.Nc3
            "rnbqkbnr/ppp2ppp/4p3/3p4/2PP4/2N5/PP2PPPP/R1BQKBNR b KQkq - 1 3": [
                ("g8f6", 35), ("c7c6", 20), ("f8e7", 20), ("d5c4", 15), ("f7f5", 10)
            ],
            
            # Queen's Gambit Declined: 1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Bg5
            "rnbqkb1r/ppp2ppp/4pn2/3p2B1/2PP4/2N5/PP2PPPP/R2QKBNR b KQkq - 2 4": [
                ("f8e7", 30), ("b8d7", 25), ("h7h6", 20), ("f8b4", 15), ("c7c6", 10)
            ],
            
            # Queen's Gambit Declined: 1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Bg5 Be7 5.e3
            "rnbqk2r/ppp1bppp/4pn2/3p2B1/2PP4/2N1P3/PP3PPP/R2QKBNR b KQkq - 0 5": [
                ("e8g8", 30), ("h7h6", 25), ("b8d7", 20), ("c7c6", 15), ("a7a6", 10)
            ],
            
            # Slav Defense: 1.d4 d5 2.c4 c6 3.Nf3
            "rnbqkbnr/pp2pppp/2p5/3p4/2PP4/5N2/PP2PPPP/RNBQKB1R b KQkq - 1 3": [
                ("g8f6", 35), ("d5c4", 25), ("e7e6", 20), ("c8f5", 15), ("a7a6", 5)
            ],
            
            # Slav Defense: 1.d4 d5 2.c4 c6 3.Nf3 Nf6 4.Nc3
            "rnbqkb1r/pp2pppp/2p2n2/3p4/2PP4/2N2N2/PP2PPPP/R1BQKB1R b KQkq - 2 4": [
                ("d5c4", 25), ("e7e6", 25), ("c8f5", 20), ("a7a6", 15), ("g7g6", 15)
            ],
            
            # Slav Defense: 1.d4 d5 2.c4 c6 3.Nf3 Nf6 4.Nc3 e6 5.e3
            "rnbqkb1r/pp3ppp/2p1pn2/3p4/2PP4/2N1PN2/PP3PPP/R1BQKB1R b KQkq - 0 5": [
                ("b8d7", 30), ("c8d7", 25), ("f8e7", 20), ("d5c4", 15), ("a7a6", 10)
            ],
            
            # Semi-Slav: 1.d4 d5 2.c4 c6 3.Nf3 Nf6 4.Nc3 e6 5.Bg5
            "rnbqkb1r/pp3ppp/2p1pn2/3p2B1/2PP4/2N2N2/PP2PPPP/R2QKB1R b KQkq - 2 5": [
                ("h7h6", 30), ("d5c4", 25), ("f8e7", 20), ("b8d7", 15), ("d8b6", 10)
            ],
            
            # London System: 1.d4 d5 2.Bf4 Nf6 3.e3 c6 
            "rnbqkb1r/pp2pppp/2p2n2/3p4/3P1B2/4P3/PPP2PPP/RN1QKBNR w KQkq - 0 4": [
                ("b1d2", 30), ("f1d3", 25), ("g1f3", 20), ("h2h3", 15), ("c2c3", 10)
            ],
            
            # London System: 1.d4 d5 2.Bf4 Nf6 3.e3 e6 4.Nd2 Be7
            "rnbqk2r/ppp1bppp/4pn2/3p4/3P1B2/4P3/PPPN1PPP/R2QKBNR w KQkq - 1 5": [
                ("g1f3", 35), ("f1d3", 25), ("h2h3", 20), ("c2c3", 15), ("g2g3", 5)
            ],
            
            # London System: 1.d4 d5 2.Bf4 Nf6 3.e3 c5 (fighting the center)
            "rnbqkb1r/pp2pppp/5n2/2pp4/3P1B2/4P3/PPP2PPP/RN1QKBNR w KQkq c6 0 4": [
                ("c2c3", 30), ("d4c5", 25), ("g1f3", 20), ("b1d2", 15), ("f1d3", 10)
            ],
            
            # London System deeper: 1.d4 d5 2.Bf4 Nf6 3.e3 e6 4.Nd2 c5
            "rnbqkb1r/pp3ppp/4pn2/2pp4/3P1B2/4P3/PPPN1PPP/R2QKBNR w KQkq c6 0 5": [
                ("c2c3", 35), ("d4c5", 25), ("f1d3", 20), ("g1f3", 15), ("a2a4", 5)
            ],
            
            # Indian Defense setups: 1.d4 Nf6 2.c4
            "rnbqkb1r/pppppppp/5n2/8/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3 0 2": [
                ("g7g6", 30), ("e7e6", 30), ("c7c5", 20), ("d7d5", 15), ("b7b6", 5)
            ],
            
            # King's Indian Defense: 1.d4 Nf6 2.c4 g6 3.Nc3 Bg7
            "rnbqk2r/ppppppbp/5np1/8/2PP4/2N5/PP2PPPP/R1BQKBNR w KQkq - 1 4": [
                ("e2e4", 40), ("g1f3", 30), ("f2f3", 15), ("g2g3", 10), ("c1g5", 5)
            ],
            
            # King's Indian Defense: 1.d4 Nf6 2.c4 g6 3.Nc3 Bg7 4.e4 d6
            "rnbqk2r/ppp1ppbp/3p1np1/8/2PPP3/2N5/PP3PPP/R1BQKBNR w KQkq - 0 5": [
                ("g1f3", 35), ("f2f3", 25), ("c1g5", 20), ("f1e2", 15), ("h2h3", 5)
            ],
            
            # King's Indian Defense: 1.d4 Nf6 2.c4 g6 3.Nc3 Bg7 4.e4 d6 5.Nf3 O-O
            "rnbq1rk1/ppp1ppbp/3p1np1/8/2PPP3/2N2N2/PP3PPP/R1BQKB1R w KQ - 1 6": [
                ("f1e2", 30), ("c1g5", 25), ("h2h3", 20), ("f1d3", 15), ("a2a4", 10)
            ],
            
            # Grünfeld Defense: 1.d4 Nf6 2.c4 g6 3.Nc3 d5
            "rnbqkb1r/ppp1pp1p/5np1/3p4/2PP4/2N5/PP2PPPP/R1BQKBNR w KQkq d6 0 4": [
                ("c4d5", 30), ("e2e3", 25), ("g1f3", 20), ("c1f4", 15), ("d1b3", 10)
            ],
            
            # Grünfeld Defense: 1.d4 Nf6 2.c4 g6 3.Nc3 d5 4.cxd5 Nxd5
            "rnbqkb1r/ppp1pp1p/6p1/3n4/3P4/2N5/PP2PPPP/R1BQKBNR w KQkq - 0 5": [
                ("e2e4", 35), ("g1f3", 25), ("d1b3", 20), ("c1d2", 15), ("a2a3", 5)
            ],
            
            # Nimzo-Indian Defense: 1.d4 Nf6 2.c4 e6 3.Nc3 Bb4 4.e3
            "rnbqk2r/pppp1ppp/4pn2/8/1bPP4/2N1P3/PP3PPP/R1BQKBNR b KQkq - 0 4": [
                ("e8g8", 25), ("c7c5", 25), ("b7b6", 20), ("d7d5", 15), ("f6e4", 15)
            ],
            
            # Nimzo-Indian Defense: 1.d4 Nf6 2.c4 e6 3.Nc3 Bb4 4.e3 O-O 5.Bd3
            "rnbq1rk1/pppp1ppp/4pn2/8/1bPP4/2NBP3/PP3PPP/R1BQK1NR b KQ - 1 5": [
                ("d7d5", 30), ("c7c5", 25), ("b4c3", 20), ("b7b6", 15), ("f6e4", 10)
            ],
            
            # Queen's Indian Defense: 1.d4 Nf6 2.c4 e6 3.Nf3 b6 4.g3
            "rnbqkb1r/p1pp1ppp/1p2pn2/8/2PP4/5NP1/PP2PP1P/RNBQKB1R b KQkq - 0 4": [
                ("c8a6", 30), ("c8b7", 25), ("f8e7", 20), ("d7d5", 15), ("c7c5", 10)
            ],
            
            # Queen's Indian Defense: 1.d4 Nf6 2.c4 e6 3.Nf3 b6 4.g3 Ba6
            "rn1qkb1r/p1pp1ppp/bp2pn2/8/2PP4/5NP1/PP2PP1P/RNBQKB1R w KQkq - 1 5": [
                ("b2b3", 30), ("d1c2", 25), ("f1g2", 20), ("b1d2", 15), ("c1d2", 10)
            ],
            
            # Bogo-Indian Defense: 1.d4 Nf6 2.c4 e6 3.Nf3 Bb4+ 4.Bd2
            "rnbqk2r/pppp1ppp/4pn2/8/1bPP4/5N2/PPBB1PPP/RN1QK2R b KQkq - 2 4": [
                ("b4d2", 30), ("d8e7", 25), ("a7a5", 20), ("e8g8", 15), ("d7d6", 10)
            ],
            
            # Catalan Opening: 1.d4 Nf6 2.c4 e6 3.g3 d5 4.Bg2
            "rnbqkb1r/ppp2ppp/4pn2/3p4/2PP4/6P1/PP2PPBP/RNBQK1NR b KQkq - 1 4": [
                ("f8e7", 30), ("d5c4", 25), ("c7c6", 20), ("b8d7", 15), ("a7a6", 10)
            ],
            
            # Catalan Opening: 1.d4 Nf6 2.c4 e6 3.g3 d5 4.Bg2 dxc4
            "rnbqkb1r/ppp2ppp/4pn2/8/2pP4/6P1/PP2PPBP/RNBQK1NR w KQkq - 0 5": [
                ("g1f3", 35), ("d1a4", 25), ("f2f3", 20), ("e2e3", 15), ("b1c3", 5)
            ],
            
            # Dutch Defense: 1.d4 f5 2.g3
            "rnbqkbnr/ppppp1pp/8/5p2/3P4/6P1/PPP1PP1P/RNBQKBNR b KQkq - 0 2": [
                ("g8f6", 30), ("e7e6", 25), ("d7d6", 20), ("c7c6", 15), ("g7g6", 10)
            ],
            
            # Dutch Defense: 1.d4 f5 2.c4 Nf6 3.g3
            "rnbqkb1r/ppppp1pp/5n2/5p2/2PP4/6P1/PP2PP1P/RNBQKBNR b KQkq - 0 3": [
                ("e7e6", 30), ("g7g6", 25), ("d7d6", 20), ("c7c6", 15), ("b8c6", 10)
            ],
            
            # Modern Benoni: 1.d4 Nf6 2.c4 c5 3.d5 e6 4.Nc3
            "rnbqkb1r/pp1p1ppp/4pn2/2pP4/2P5/2N5/PP2PPPP/R1BQKBNR b KQkq - 1 4": [
                ("e6d5", 30), ("d7d6", 25), ("f8e7", 20), ("b7b5", 15), ("a7a6", 10)
            ],
            
            # Modern Benoni: 1.d4 Nf6 2.c4 c5 3.d5 e6 4.Nc3 exd5 5.cxd5 d6
            "rnbqkb1r/pp3ppp/3p1n2/2pP4/8/2N5/PP2PPPP/R1BQKBNR w KQkq - 0 6": [
                ("e2e4", 35), ("g1f3", 25), ("f2f4", 20), ("c1g5", 15), ("h2h3", 5)
            ],
            
            # Pirc Defense: 1.d4 Nf6 2.c4 g6 3.Nc3 d6
            "rnbqkb1r/ppp1pp1p/3p1np1/8/2PP4/2N5/PP2PPPP/R1BQKBNR w KQkq - 0 4": [
                ("e2e4", 35), ("g1f3", 25), ("f2f3", 20), ("c1g5", 15), ("h2h3", 5)
            ],
            
            # English Opening: 1.c4 e5 2.Nc3 
            "rnbqkbnr/pppp1ppp/8/4p3/2P5/2N5/PP1PPPPP/R1BQKBNR b KQkq - 1 2": [
                ("g8f6", 30), ("b8c6", 25), ("f7f5", 20), ("f8b4", 15), ("d7d6", 10)
            ],
            
            # English Opening: 1.c4 e5 2.Nc3 Nf6 3.Nf3
            "rnbqkb1r/pppp1ppp/5n2/4p3/2P5/2N2N2/PP1PPPPP/R1BQKB1R b KQkq - 2 3": [
                ("b8c6", 30), ("d7d6", 25), ("f8b4", 20), ("e5e4", 15), ("g7g6", 10)
            ],
            
            # English Opening: 1.c4 Nf6 2.Nc3
            "rnbqkb1r/pppppppp/5n2/8/2P5/2N5/PP1PPPPP/R1BQKBNR b KQkq - 1 2": [
                ("g7g6", 25), ("e7e6", 25), ("c7c5", 20), ("d7d5", 15), ("e7e5", 15)
            ],
            
            # English Opening: 1.c4 c5 (Symmetrical English)
            "rnbqkbnr/pp1ppppp/8/2p5/2P5/8/PP1PPPPP/RNBQKBNR w KQkq c6 0 2": [
                ("g1f3", 30), ("b1c3", 25), ("g2g3", 20), ("e2e3", 15), ("d2d4", 10)
            ],
            
            # Reti Opening: 1.Nf3 d5 2.c4
            "rnbqkbnr/ppp1pppp/8/3p4/2P5/5N2/PP1PPPPP/RNBQKB1R b KQkq c3 0 2": [
                ("e7e6", 25), ("c7c6", 25), ("g8f6", 20), ("d5c4", 15), ("c8g4", 15)
            ],
            
            # Reti Opening: 1.Nf3 Nf6 2.c4 g6
            "rnbqkb1r/pppppp1p/5np1/8/2P5/5N2/PP1PPPPP/RNBQKB1R w KQkq - 0 3": [
                ("g2g3", 30), ("b1c3", 25), ("d2d4", 20), ("e2e3", 15), ("d2d3", 10)
            ],
            
            # Bird's Opening: 1.f4 d5
            "rnbqkbnr/ppp1pppp/8/3p4/5P2/8/PPPPP1PP/RNBQKBNR w KQkq d6 0 2": [
                ("g1f3", 30), ("e2e3", 25), ("b1c3", 20), ("f1b5", 15), ("d2d3", 10)
            ],
            
            # Bird's Opening: 1.f4 d5 2.Nf3 Nf6
            "rnbqkb1r/ppp1pppp/5n2/3p4/5P2/5N2/PPPPP1PP/RNBQKB1R w KQkq - 1 3": [
                ("e2e3", 30), ("b1c3", 25), ("d2d3", 20), ("c1b2", 15), ("g2g3", 10)
            ],
            
            # Advanced theoretical positions for major openings
            
            # Scandinavian Defense: 1.e4 d5 2.exd5 Qxd5 3.Nc3 Qa5
            "rnb1kbnr/ppp1pppp/8/q7/8/2N5/PPPPPPPP/R1BQKBNR w KQkq - 2 4": [
                ("d2d4", 35), ("g1f3", 25), ("c1d2", 20), ("a2a3", 15), ("b2b4", 5)
            ],
            
            # Owen's Defense: 1.e4 b6 
            "rnbqkbnr/p1pppppp/1p6/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": [
                ("d2d4", 35), ("g1f3", 25), ("f1c4", 20), ("b1c3", 15), ("c2c3", 5)
            ],
            
            # St. George Defense: 1.e4 a6
            "rnbqkbnr/1ppppppp/p7/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": [
                ("d2d4", 35), ("g1f3", 25), ("f1c4", 20), ("b1c3", 15), ("c2c3", 5)
            ],
            
            # Nimzowitsch Defense: 1.e4 Nc6
            "r1bqkbnr/pppppppp/2n5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 1 2": [
                ("g1f3", 30), ("d2d4", 25), ("f1c4", 20), ("b1c3", 15), ("f2f4", 10)
            ],
            
            # Center Game: 1.e4 e5 2.d4 exd4 3.Qxd4
            "rnbqkbnr/pppp1ppp/8/8/3QP3/8/PPP2PPP/RNB1KBNR b KQkq - 0 3": [
                ("b8c6", 35), ("g8f6", 25), ("d7d6", 20), ("f8e7", 15), ("c7c6", 5)
            ],
            
            # King's Gambit: 1.e4 e5 2.f4
            "rnbqkbnr/pppp1ppp/8/4p3/4PP2/8/PPPP2PP/RNBQKBNR b KQkq f3 0 2": [
                ("e5f4", 35), ("d7d6", 25), ("f8c5", 20), ("g8f6", 15), ("b8c6", 5)
            ],
            
            # Vienna Game: 1.e4 e5 2.Nc3
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/2N5/PPPP1PPP/R1BQKBNR b KQkq - 1 2": [
                ("g8f6", 30), ("b8c6", 25), ("f8c5", 20), ("d7d6", 15), ("f7f5", 10)
            ],
            
            # Ponziani Opening: 1.e4 e5 2.Nf3 Nc6 3.c3
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/2P2N2/PP1P1PPP/RNBQKB1R b KQkq - 0 3": [
                ("d7d5", 30), ("g8f6", 25), ("f7f5", 20), ("f8e7", 15), ("d8f6", 10)
            ],
            
            # Scotch Game: 1.e4 e5 2.Nf3 Nc6 3.d4
            "r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq d3 0 3": [
                ("e5d4", 35), ("f7f5", 25), ("f8b4", 20), ("g8f6", 15), ("d8h4", 5)
            ],
            
            # Four Knights Game: 1.e4 e5 2.Nf3 Nc6 3.Nc3 Nf6
            "r1bqkb1r/pppp1ppp/2n2n2/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 2 4": [
                ("f1b5", 30), ("f1c4", 25), ("d2d3", 20), ("a2a3", 15), ("h2h3", 10)
            ],
            
            # Petroff Defense: 1.e4 e5 2.Nf3 Nf6
            "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 1 3": [
                ("f3e5", 30), ("d2d3", 25), ("b1c3", 20), ("f1c4", 15), ("e4e5", 10)
            ],
            
            # Philidor Defense: 1.e4 e5 2.Nf3 d6
            "rnbqkbnr/ppp2ppp/3p4/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3": [
                ("d2d4", 35), ("f1c4", 25), ("b1c3", 20), ("c2c3", 15), ("h2h3", 5)
            ]
        }
        
        # Forbidden moves that should never be played
        # Format: FEN -> list of bad moves to avoid
        self.forbidden_moves = {
            # Never play early queen moves in most openings
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": [
                "d1h5", "d1g4", "d1f3"
            ],
            
            # Don't bring queen out early in Sicilian
            "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2": [
                "d1h5", "d1g4", "d1f3"
            ],
            
            # Don't weaken kingside in opening
            "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1": [
                "h7h6", "h7h5", "g7g5", "f7f6", "f7f5"
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
