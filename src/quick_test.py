"""
Quick validation script to test specific moves against expected results.
"""

from perft import PerftTest
from fen import FEN

def test_single_move(fen, move_str, depth):
    """Test a single move and return node count."""
    test = PerftTest()
    FEN.load(test.board, fen)
    
    # Find the move in our generated moves
    moves = test.generate_legal_moves(test.board)
    target_move = None
    
    for move in moves:
        if test.move_to_algebraic(move) == move_str:
            target_move = move
            break
    
    if not target_move:
        print(f"Move {move_str} not found!")
        return None
    
    # Make the move and run perft
    board_copy = test.copy_board(test.board)
    test.make_move(board_copy, target_move)
    
    if depth <= 1:
        return 1
    else:
        return test.perft(depth - 1, board_copy)

# Test a few key moves from starting position at depth 3
print("Testing individual moves from starting position:")
starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

test_cases = [
    ("a2a3", 380),
    ("d2d4", 560),
    ("e2e4", 600),
    ("g1f3", 440)
]

for move, expected in test_cases:
    try:
        result = test_single_move(starting_fen, move, 3)
        status = "✓" if result == expected else "✗"
        print(f"{status} {move}: {result} (expected {expected})")
    except Exception as e:
        print(f"✗ {move}: ERROR - {e}")
