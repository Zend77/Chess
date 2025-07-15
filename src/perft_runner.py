#!/usr/bin/env python3
"""
Perft Test Runner - Run specific perft tests and compare with Stockfish results.
"""

import sys
import time
from perft import PerftTest
from perft_results import PERFT_POSITIONS

def run_position_test(position_name: str, depth: int = 3):
    """Run perft test for a specific position."""
    if position_name not in PERFT_POSITIONS:
        print(f"Unknown position: {position_name}")
        print(f"Available positions: {list(PERFT_POSITIONS.keys())}")
        return
    
    position_data = PERFT_POSITIONS[position_name]
    fen = position_data["fen"]
    description = position_data["description"]
    
    print(f"{description} at depth {depth}:")
    print(f"FEN: {fen}")
    print()
    
    test = PerftTest()
    start_time = time.time()
    
    try:
        # Load the position
        from fen import FEN
        FEN.load(test.board, fen)
        
        # Run perft divide
        results, total_nodes = test.perft_divide(depth)
        end_time = time.time()
        
        # Print results in Stockfish format
        for move, nodes in results.items():
            print(f"{move}: {nodes}")
        
        print(f"\nNodes searched: {total_nodes}")
        print(f"Time: {end_time - start_time:.3f} seconds")
        
        # Compare with expected results if available
        if depth in position_data.get("results", {}):
            expected = position_data["results"][depth]
            if total_nodes == expected:
                print(f"✓ CORRECT: Matches expected result ({expected})")
            else:
                print(f"✗ INCORRECT: Expected {expected}, got {total_nodes}")
        
        # Compare divide results if available
        expected_divide = position_data.get(f"divide_{depth}", {})
        if expected_divide:
            print(f"\n--- Move-by-move comparison ---")
            matches = 0
            total_moves = len(expected_divide)
            
            for move, expected_nodes in expected_divide.items():
                actual_nodes = results.get(move, "MISSING")
                if actual_nodes == expected_nodes:
                    print(f"✓ {move}: {actual_nodes}")
                    matches += 1
                else:
                    print(f"✗ {move}: {actual_nodes} (expected {expected_nodes})")
            
            print(f"\nMove accuracy: {matches}/{total_moves} ({(matches/total_moves)*100:.1f}%)")
    
    except Exception as e:
        print(f"Error running perft: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function to run perft tests."""
    if len(sys.argv) < 2:
        print("Usage: python perft_runner.py <position> [depth]")
        print("\nAvailable positions:")
        for name, data in PERFT_POSITIONS.items():
            print(f"  {name}: {data['description']}")
        print("\nExamples:")
        print("  python perft_runner.py starting_position 3")
        print("  python perft_runner.py en_passant_position 3")
        print("  python perft_runner.py castling_position 3")
        return
    
    position_name = sys.argv[1]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    run_position_test(position_name, depth)


if __name__ == "__main__":
    main()
