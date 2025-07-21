#!/usr/bin/env python3
"""
Setup and build script for Chess Game.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("✗ Python 3.7 or higher is required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def run_quick_test():
    """Run a quick test to verify installation."""
    print("Running quick verification test...")
    try:
        # Try importing main modules
        sys.path.append('src')
        import pygame
        from board import Board
        from game import Game
        
        # Quick functionality test
        board = Board()
        if len(board.squares) == 64:
            print("✓ Core functionality verified")
            return True
        else:
            print("✗ Core functionality test failed")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def main():
    print("=== Chess Game Setup ===")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install requirements
    if not install_requirements():
        return 1
    
    # Run verification
    if not run_quick_test():
        return 1
    
    print("\n🎉 Setup complete! You can now run the game:")
    print("   cd src")
    print("   python main.py")
    print("\nOther useful commands:")
    print("   python scripts/run_tests.py quick    # Run quick tests")
    print("   python scripts/perft_runner.py quick # Run perft verification")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
