#!/usr/bin/env python3
"""
Test runner for chess engine tests.
Run all tests or specific test categories.
"""

import os
import sys
import subprocess
import argparse

def run_test_file(filepath):
    """Run a single test file."""
    print(f"\n=== Running {os.path.basename(filepath)} ===")
    try:
        result = subprocess.run([sys.executable, filepath], 
                              capture_output=True, text=True, cwd=os.path.dirname(filepath))
        
        if result.returncode == 0:
            print(f"✓ {os.path.basename(filepath)} PASSED")
            if result.stdout.strip():
                print(result.stdout)
        else:
            print(f"✗ {os.path.basename(filepath)} FAILED")
            if result.stderr.strip():
                print("STDERR:", result.stderr)
            if result.stdout.strip():
                print("STDOUT:", result.stdout)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"✗ Error running {os.path.basename(filepath)}: {e}")
        return False

def run_tests_in_directory(directory, pattern=None):
    """Run all test files in a directory."""
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist")
        return 0, 0
    
    test_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.py') and filename != '__init__.py':
            if pattern is None or pattern in filename:
                test_files.append(os.path.join(directory, filename))
    
    test_files.sort()
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        if run_test_file(test_file):
            passed += 1
    
    return passed, total

def main():
    parser = argparse.ArgumentParser(description="Chess Engine Test Runner")
    parser.add_argument("category", nargs="?", default="all", 
                       choices=["all", "tests", "debug", "quick"],
                       help="Test category to run")
    parser.add_argument("--pattern", help="Filter tests by name pattern")
    
    args = parser.parse_args()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    chess_dir = os.path.dirname(base_dir)
    
    total_passed = 0
    total_tests = 0
    
    print("=== CHESS ENGINE TEST RUNNER ===")
    
    if args.category in ["all", "tests"]:
        print(f"\n--- Running Tests ---")
        tests_dir = os.path.join(chess_dir, 'tests')
        passed, count = run_tests_in_directory(tests_dir, args.pattern)
        total_passed += passed
        total_tests += count
        print(f"\nTests: {passed}/{count} passed")
    
    if args.category in ["all", "debug"]:
        print(f"\n--- Running Debug Scripts ---")
        debug_dir = os.path.join(chess_dir, 'debug')
        passed, count = run_tests_in_directory(debug_dir, args.pattern)
        total_passed += passed
        total_tests += count
        print(f"\nDebug: {passed}/{count} passed")
    
    if args.category == "quick":
        print(f"\n--- Running Quick Tests ---")
        # Run only essential tests
        tests_dir = os.path.join(chess_dir, 'tests')
        quick_tests = ['minimal_test.py', 'basic_test.py']
        
        for test_name in quick_tests:
            test_path = os.path.join(tests_dir, test_name)
            if os.path.exists(test_path):
                if run_test_file(test_path):
                    total_passed += 1
                total_tests += 1
        
        print(f"\nQuick tests: {total_passed}/{total_tests} passed")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"❌ {total_tests - total_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
