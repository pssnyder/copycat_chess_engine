# Copycat Chess Engine

A data-driven chess engine that learns and mimics a player's style from their game history.

## Project Overview

This engine analyzes historical chess games to understand and replicate a player's:
- Move preferences
- Piece placement patterns
- Time management style
- Opening choices
- Tactical patterns

## Key Features

- **Pattern-Based Play**: Uses frequency analysis and pattern matching instead of traditional engine evaluation
- **Style Mimicking**: Replicates the target player's characteristic moves and positions
- **Dynamic Time Management**: Adapts search depth based on remaining time
- **UCI Compatible**: Works with standard chess GUIs like Arena
- **Visual Analytics**: Generate insights about playing patterns

## Project Structure

```
copycat_chess_engine/
├── analysis/                # Analysis tools
│   ├── game_analyzer.py    # PGN analysis and metadata extraction
│   └── visualize_results.py # Visualization generators
├── results/                # Analysis results and visualizations
│   ├── piece_heatmaps.json
│   ├── move_patterns.json
│   ├── position_transitions.json
│   └── visual_reports/
├── training_positions/     # Training data
│   └── games.pgn          # Historical games
├── engine.py              # Main engine
├── search.py              # Move search implementation
└── move_library.json      # Compiled move database
```

## Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Place your PGN file in `training_positions/games.pgn`

4. Generate move library:
   ```bash
   python analysis/game_analyzer.py
   ```

5. Generate visual reports:
   ```bash
   python analysis/visualize_results.py
   ```

## Analysis Pipeline

1. **Game Analysis**
   - Parse PGN files
   - Extract moves, positions, and timing
   - Calculate frequencies and patterns
   - Generate metadata

2. **Data Visualization**
   - Piece movement heatmaps
   - Timing distributions
   - Success rate analysis
   - Move sequence graphs

3. **Move Library Generation**
   - Compile analyzed data
   - Index positions and patterns
   - Calculate weights
   - Optimize for query speed

## Using the Engine

1. **Arena Chess GUI Setup**
   - Add as UCI engine
   - Configure time controls
   - Set player name to match PGN

2. **Engine Commands**
   - `uci`: Initialize UCI mode
   - `setoption name PlayerName value v7p3r`: Set target player
   - `go movetime 1000`: Calculate move with 1 second
   - `go wtime 300000 btime 300000`: Tournament time control

## Understanding Results

The `results/visual_reports/` directory contains:
- `heatmap_*.png`: Piece movement preferences
- `timing_distribution.png`: Move timing patterns
- `move_success_rates.png`: Win rates by move
- `phase_distribution.png`: Piece usage by game phase
- `move_sequences.png`: Common move sequences

## Development Notes

1. **Data Collection**
   - Clean PGN files
   - Verify move timestamps
   - Check game completeness

2. **Analysis Tuning**
   - Adjust frequency thresholds
   - Calibrate timing categories
   - Fine-tune pattern matching

3. **Performance Optimization**
   - Index common positions
   - Cache frequent patterns
   - Optimize query paths

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - See LICENSE file for details
