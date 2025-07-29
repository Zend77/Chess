# Chess Game

A Python chess game built with Pygame featuring AI opponents, AI vs AI mode, move validation, and comprehensive testing.

## Features

- Interactive chess game with drag-and-drop pieces
- AI opponents with multiple difficulty levels (Easy to Grandmaster)
- **AI vs AI mode**: Watch two AI opponents play against each other
- Complete chess rules implementation including:
  - Castling
  - En passant
  - Pawn promotion
  - Check and checkmate detection
  - Stalemate and draw conditions
- Visual themes and sound effects
- FEN notation support for custom positions
- Move history with undo/redo functionality
- Opening book integration
- Debug mode for AI analysis

## AI Difficulty Levels

The game offers 6 difficulty levels:

- **Easy** (Depth 2, 40s): Basic evaluation
- **Medium** (Depth 3, 40s): Enhanced position evaluation
- **Hard** (Depth 4, 50s): Advanced search algorithms
- **Expert** (Depth 5, 80s): Deep tactical analysis
- **Master** (Depth 6, 120s): Strong positional play
- **Grandmaster** (Depth 10, 600s): Maximum strength

## Getting Started

### Prerequisites

- Python 3.7+
- Pygame

### Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Game

```bash
python src/main.py
```

When you start the game, you'll be prompted to choose:
- **W**: AI plays as White
- **B**: AI plays as Black  
- **A**: AI vs AI mode (both sides controlled by AI)
- **N**: No AI (human vs human)

## Controls

### Game Controls
- **Mouse**: Click and drag pieces to move
- **R**: Reset game
- **G**: Toggle AI opponent on/off
- **← →**: Undo/Redo moves
- **T**: Change visual theme
- **D**: Offer draw (press twice to accept)
- **F**: Load position from FEN notation
- **H**: Show help/controls

### AI Debug Mode
- **V**: Toggle AI evaluation debug mode
  - See all moves the AI considers
  - Breakdown by evaluation components
  - Understand AI decision making

## Project Structure

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
│   ├── opening_book.py    # Opening book database
│   └── ...
├── scripts/               # Utility scripts (perft testing, etc.)
├── assets/                # Game assets (images, sounds)
│   ├── images/           # Piece images (standard and Hello Kitty themes)
│   └── sounds/           # Game sounds
└── README.md             # This file
```

## Testing

The project includes comprehensive testing and verification:

### Perft Testing
Move generation verification using perft (performance test):
```bash
python scripts/perft_runner.py quick
```

### Running Tests
```bash
python scripts/run_tests.py
```

## Technical Features

This chess engine includes:

### Core Engine
- **Minimax search** with alpha-beta pruning
- **Position evaluation** with piece-square tables
- **Opening book** for common openings
- **Move generation** with full rule validation
- **Transposition tables** for performance optimization

### Game Features
- **Multiple AI modes**: Single AI vs Human, AI vs AI
- **Visual feedback**: Move highlights, check indicators
- **Sound effects**: Move and capture sounds
- **Theme support**: Multiple visual themes including Hello Kitty
- **Position management**: FEN import/export, move history
- **Draw detection**: Stalemate, threefold repetition, 50-move rule

### Performance
- **Efficient move generation** verified by perft testing
- **Optimized evaluation** for fast AI response
- **Memory management** with proper cleanup
- **Scalable difficulty** from casual to engine-strength play

## Development Notes

- Built with modern Python practices
- Modular architecture for easy extension
- Comprehensive error handling
- Performance optimized for real-time play
- Extensible AI framework for custom evaluations

## License

This project is open source and available under the MIT License.
