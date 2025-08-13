# Copycat Chess Engine

A neural network-based chess engine with evaluation capabilities, combining deep learning and traditional chess evaluation techniques.

## Engine Versions

The engine has several versions with different capabilities:
- **v0.5.31_copycat_enhanced_ai**: Latest version with improved evaluation
- **v0.5.31_copycat_genetic_ai**: Version using genetic algorithms for move selection
- **v0.5.30_copycat_eval_ai**: Version focused on evaluation capabilities

## UCI Support

This engine can now be used with any UCI-compatible chess GUI, such as Arena, Fritz, or Cutechess.

### Using with Arena Chess GUI

1. Download and install [Arena Chess GUI](http://www.playwitharena.de/)
2. In Arena, go to Engines > Install New Engine
3. Navigate to the copycat_chess_engine directory
4. Select `Copycat_UCI.bat`
5. Click "OK" to confirm the engine installation
6. The engine should now be available in Arena's engine list

### Technical Details

The UCI interface implements the following commands:
- `uci`: Identifies the engine
- `isready`: Initializes the engine and responds when ready
- `position [fen/startpos] moves ...`: Sets up the position
- `go [depth/movetime/wtime/btime/...]`: Starts engine analysis
- `stop`: Stops analysis (if supported)
- `quit`: Exits the engine

## Features

- Neural network-based move prediction
- Sophisticated evaluation engine with multiple factors:
  - Material evaluation
  - Positional understanding
  - King safety
  - Center control
  - Development assessment
  - Hanging piece detection
- Multiple engine versions (enhanced, genetic, evaluation)
- Time management for tournament play

## Architecture

The engine combines neural network prediction with classical evaluation:
1. The neural network suggests candidate moves based on patterns learned from games
2. The evaluation engine scores each candidate position
3. The best scoring move is selected

In the genetic algorithm version:
1. Multiple move sequences are generated
2. They are evolved over generations using genetic operators
3. The best performing sequence is selected for the first move

## Development

The engine is in active development with various improvements:
- Enhanced position evaluation
- Better search algorithms
- Material and positional understanding
- Time management techniques

## Technical Requirements

- Python 3.8+
- PyTorch
- python-chess
- numpy

### Installation

The required dependencies can be installed with pip:

```bash
# Install all required packages
pip install -r requirements.txt

# Or install them individually
pip install torch
pip install numpy
pip install python-chess
```

PyTorch is already installed on most systems. You can verify your installation with:

```bash
python -c "import torch; print(f'PyTorch version: {torch.__version__}, CUDA available: {torch.cuda.is_available()}')"
```

### Verifying Your Installation

You can verify that all required dependencies are correctly installed by running:

```bash
python check_dependencies.py
```

This script checks:
- If PyTorch, NumPy, and python-chess are installed
- Whether CUDA is available for GPU acceleration
- If model files and vocabulary files are present

### Troubleshooting Import Errors in VS Code

If you see "Import 'torch' could not be resolved" errors in VS Code even though PyTorch is installed:

1. Run `test_environment.bat` to diagnose Python environment issues
2. Try selecting a different Python interpreter in VS Code:
   - Press `Ctrl+Shift+P` and type "Python: Select Interpreter"
   - Choose the Python installation where PyTorch is installed
3. Make sure the VS Code Python and Pylance extensions are up to date
4. Reload the VS Code window (`Ctrl+Shift+P` → "Developer: Reload Window")

### Fixing Terminal Interpreter Issues

If your VS Code terminal shows a different Python version than your editor:

1. Run `fix_terminal_interpreter.bat` to update VS Code settings
2. Close all terminal windows
3. Reload VS Code (`Ctrl+Shift+P` → "Developer: Reload Window")
4. Open a new terminal with the correct interpreter:
   - `Ctrl+Shift+P` → "Python: Create Terminal"

Alternatively, use `CopycatUCI_VSCode.bat` which attempts to use the VS Code selected Python interpreter.

## Tournament Usage

When using in a tournament:
1. Set appropriate time controls in Arena
2. The engine will automatically manage its time based on the position complexity
3. For best performance, use a machine with CUDA-compatible GPU

## Acknowledgements

The engine's neural network was trained on a dataset of high-quality chess games, including games from strong engines and human masters.