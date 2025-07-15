from perft import PerftTest
from fen import FEN

# Quick test to see if depth 3 starting position works
test = PerftTest()
FEN.load(test.board, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

print("Testing a few moves at depth 3:")

# Just test a few key moves to see if the counts match
test_moves = [
    ("a2a3", 380),
    ("b2b3", 420), 
    ("d2d4", 560),
    ("e2e4", 600)
]

for move, expected in test_moves:
    # We'll implement a way to test individual moves
    print(f"Expected {move}: {expected}")
