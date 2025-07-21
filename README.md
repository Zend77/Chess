# Chess Game

A Python chess game built with Pygame featuring AI opponents, move validation, and comprehensive testing.

## Features

- Interactive chess game with drag-and-drop pieces
- AI opponents with multiple difficulty levels
- Complete chess rules implementation including:
  - Castling
  - En passant
  - Pawn promotion
  - Check and checkmate detection
- Visual themes and sound effects
- FEN notation support for custom positions

## Recent Cleanup (2025)

The codebase has been recently cleaned and reorganized:

### What was cleaned up:
- ✅ Removed empty test files (`ai_behavior_test.py`, `quick_test.py`, `optimization_success_report.py`)
- ✅ Organized files into logical directories:
  - `tests/` - All test files with fixed import paths
  - `debug/` - Debug utilities and analysis tools  
  - `scripts/` - Utility scripts (perft testing, test runner, etc.)
  - `src/` - Clean core game files only
- ✅ Removed `__pycache__` directories
- ✅ Added proper `__init__.py` files for better module organization
- ✅ Created utility scripts for running tests and fixing imports
- ✅ Added comprehensive `.gitignore` file
- ✅ Created `requirements.txt` for easy dependency management
- ✅ Added `setup.py` for easy project setup

### Project Structure

```
Chess/
├── src/                    # Core game source code
│   ├── main.py            # Main game entry point
│   ├── game.py            # Game logic and state management
│   ├── board.py           # Chess board representation
│   ├── piece.py           # Chess piece classes
│   ├── rules.py           # Chess rules validation
│   ├── AI.py              # AI player implementation
│   ├── search.py          # AI search algorithms
│   ├── evaluation.py      # Position evaluation
│   └── ...
├── tests/                 # Test files
├── debug/                 # Debug utilities
├── scripts/               # Utility scripts (perft testing, etc.)
├── assets/                # Game assets (images, sounds)
│   ├── images/           # Piece images
│   └── sounds/           # Game sounds
└── README.md             # This file
```

## Getting Started

### Prerequisites

- Python 3.7+
- Pygame

### Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install pygame
   ```

### Running the Game

```bash
cd src
python main.py
```

## Controls

- **Mouse**: Click and drag pieces to move
- **R**: Reset game
- **T**: Change theme
- **A**: Toggle AI mode
- **ESC**: Quit game

## AI Difficulty Levels

- **Easy**: Basic move evaluation
- **Medium**: Enhanced position evaluation with piece tables
- **Hard**: Advanced search with deeper lookahead

## Testing

The project includes comprehensive testing:

- **Unit Tests**: Located in `tests/` directory
- **Perft Testing**: Move generation verification in `scripts/`
- **Debug Tools**: Debugging utilities in `debug/`

To run perft tests:
```bash
cd scripts
python perft_runner.py quick
```

## Development

This chess engine includes:
- Minimax search with alpha-beta pruning
- Position evaluation with piece-square tables
- Opening book for common openings
- Comprehensive move generation and validation
- Performance testing and verification tools

## License

This project is open source and available under the MIT License.
