#!/usr/bin/env python3
"""
Perft Test Runner - Comprehensive test suite for chess engine verification.
"""

import sys
import time
import argparse
from typing import Dict, List, Optional
from perft import PerftTest
from perft_results import PERFT_POSITIONS, run_perft_verification, print_perft_summary

def run_position_test(position_name: str, depth: int = 3, show_divide: bool = False):
    """Run perft test for a specific position."""
    if position_name not in PERFT_POSITIONS:
        print(f"Unknown position: {position_name}")
        print(f"Available positions: {list(PERFT_POSITIONS.keys())}")
        return False
    
    position_data = PERFT_POSITIONS[position_name]
    fen = position_data["fen"]
    description = position_data["description"]
    
    print(f"=== {description} ===")
    print(f"FEN: {fen}")
    print(f"Testing at depth {depth}")
    print()
    
    test = PerftTest()
    start_time = time.time()
    
    try:
        # Load the position
        from fen import FEN
        FEN.load(test.board, fen)
        
        # Run perft divide if requested or just perft
        if show_divide:
            results, total_nodes = test.perft_divide(depth)
            end_time = time.time()
            
            # Print results in Stockfish format
            for move, nodes in results.items():
                print(f"{move}: {nodes}")
            
            print(f"\nNodes searched: {total_nodes}")
        else:
            total_nodes = test.perft(depth)
            end_time = time.time()
            print(f"Nodes searched: {total_nodes}")
        
        print(f"Time: {end_time - start_time:.3f} seconds")
        
        # Compare with expected results if available
        expected_results = position_data.get("results", {})
        if depth in expected_results:
            expected = expected_results[depth]
            if total_nodes == expected:
                print(f"✓ CORRECT: Matches expected result ({expected})")
                success = True
            else:
                print(f"✗ INCORRECT: Expected {expected}, got {total_nodes}")
                diff = total_nodes - expected
                print(f"  Difference: {diff:+d} nodes")
                success = False
        else:
            print(f"⚠ No expected result available for depth {depth}")
            success = True
        
        # Compare divide results if available and requested
        if show_divide:
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
        
        return success
    
    except Exception as e:
        print(f"Error running perft: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_test_suite(max_depth: int = 3, positions: Optional[List[str]] = None):
    """Run the complete perft test suite."""
    print("=== PERFT TEST SUITE ===")
    print(f"Running tests up to depth {max_depth}")
    print()
    
    if positions is None:
        positions = list(PERFT_POSITIONS.keys())
    
    total_tests = 0
    passed_tests = 0
    failed_positions = []
    
    for position_name in positions:
        if position_name not in PERFT_POSITIONS:
            print(f"⚠ Unknown position: {position_name}")
            continue
        
        position_data = PERFT_POSITIONS[position_name]
        available_depths = [d for d in position_data.get("results", {}).keys() if d <= max_depth]
        
        if not available_depths:
            print(f"⚠ No test data for {position_name} at depth <= {max_depth}")
            continue
        
        print(f"\n--- {position_data['description']} ---")
        position_passed = True
        
        for depth in sorted(available_depths):
            total_tests += 1
            print(f"  Depth {depth}: ", end="", flush=True)
            
            start_time = time.time()
            test = PerftTest()
            
            try:
                from fen import FEN
                FEN.load(test.board, position_data["fen"])
                actual_nodes = test.perft(depth)
                end_time = time.time()
                
                expected_nodes = position_data["results"][depth]
                
                if actual_nodes == expected_nodes:
                    print(f"{actual_nodes} nodes ✓ ({end_time - start_time:.3f}s)")
                    passed_tests += 1
                else:
                    print(f"{actual_nodes} nodes ✗ (expected {expected_nodes}) ({end_time - start_time:.3f}s)")
                    position_passed = False
            
            except Exception as e:
                print(f"ERROR - {e}")
                position_passed = False
        
        if not position_passed:
            failed_positions.append(position_name)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Passed: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
    
    if failed_positions:
        print(f"\nFailed positions:")
        for pos in failed_positions:
            print(f"  - {pos}")
    else:
        print(f"\n🎉 All tests passed!")
    
    return passed_tests == total_tests


def run_quick_suite():
    """Run a quick test suite for basic verification."""
    print("=== QUICK PERFT VERIFICATION ===")
    quick_positions = ["starting_position", "en_passant_position", "castling_position", "position_5"]
    return run_test_suite(max_depth=3, positions=quick_positions)


def run_comprehensive_suite():
    """Run the full comprehensive test suite."""
    print("=== COMPREHENSIVE PERFT TEST SUITE ===")
    return run_test_suite(max_depth=5)


def run_benchmark(position_name: str = "starting_position", depth: int = 5):
    """Run a performance benchmark on a specific position."""
    if position_name not in PERFT_POSITIONS:
        print(f"Unknown position: {position_name}")
        return
    
    position_data = PERFT_POSITIONS[position_name]
    print(f"=== PERFT BENCHMARK ===")
    print(f"Position: {position_data['description']}")
    print(f"Depth: {depth}")
    print()
    
    test = PerftTest()
    from fen import FEN
    FEN.load(test.board, position_data["fen"])
    
    # Warm up
    test.perft(1)
    
    # Actual benchmark
    start_time = time.time()
    nodes = test.perft(depth)
    end_time = time.time()
    
    elapsed = end_time - start_time
    nps = nodes / elapsed if elapsed > 0 else 0
    
    print(f"Nodes: {nodes:,}")
    print(f"Time: {elapsed:.3f} seconds")
    print(f"Speed: {nps:,.0f} nodes/second")
    
    # Compare with expected if available
    expected = position_data.get("results", {}).get(depth)
    if expected:
        if nodes == expected:
            print(f"✓ Result matches expected ({expected:,})")
        else:
            print(f"✗ Result differs from expected ({expected:,})")


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description="Chess Engine Perft Test Suite")
    parser.add_argument("command", nargs="?", default="help", 
                       choices=["test", "suite", "quick", "comprehensive", "benchmark", "list", "help"],
                       help="Command to run")
    parser.add_argument("position", nargs="?", help="Position name for test/benchmark")
    parser.add_argument("-d", "--depth", type=int, default=3, help="Search depth")
    parser.add_argument("--divide", action="store_true", help="Show move-by-move breakdown")
    
    args = parser.parse_args()
    
    if args.command == "help" or (args.command == "test" and not args.position):
        print("Chess Engine Perft Test Suite")
        print("\nCommands:")
        print("  test <position> [-d depth] [--divide]  - Test specific position")
        print("  suite [-d max_depth]                   - Run full test suite")
        print("  quick                                  - Run quick verification suite")
        print("  comprehensive                          - Run comprehensive test suite")
        print("  benchmark <position> [-d depth]       - Run performance benchmark")
        print("  list                                   - List available positions")
        print("\nExamples:")
        print("  python perft_runner.py test starting_position -d 4")
        print("  python perft_runner.py test position_5 -d 5 --divide")
        print("  python perft_runner.py quick")
        print("  python perft_runner.py benchmark starting_position -d 6")
        return
    
    if args.command == "list":
        print("Available test positions:")
        for name, data in PERFT_POSITIONS.items():
            depths = list(data.get("results", {}).keys())
            max_depth = max(depths) if depths else "unknown"
            print(f"  {name:<20} - {data['description']} (max depth: {max_depth})")
        return
    
    if args.command == "test":
        if not args.position:
            print("Error: Position name required for test command")
            return
        run_position_test(args.position, args.depth, args.divide)
    
    elif args.command == "suite":
        run_test_suite(args.depth)
    
    elif args.command == "quick":
        run_quick_suite()
    
    elif args.command == "comprehensive":
        run_comprehensive_suite()
    
    elif args.command == "benchmark":
        position = args.position or "starting_position"
        run_benchmark(position, args.depth)


if __name__ == "__main__":
    main()
