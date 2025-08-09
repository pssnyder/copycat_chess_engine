# Arena Chess GUI Setup Guide for Copycat Chess Engine v0.7

## Engine Information
- **Name**: Copycat Chess Engine v0.7
- **Version**: 0.7 (Based on v0.2 with hybrid AI architecture)
- **File**: `CopycatChessEngine_v0.7.exe` (Located in `release/` folder)
- **Size**: ~2.4 GB
- **Protocol**: UCI (Universal Chess Interface)
- **Author**: Copycat Chess AI

## Installation in Arena

### Step 1: Locate the Engine
1. Navigate to the `release/` folder in your chess engine directory
2. Find `CopycatChessEngine_v0.7.exe`
3. Note the full path (e.g., `S:\Maker Stuff\Programming\Chess Engines\Copycat Chess AI\copycat_chess_engine\release\CopycatChessEngine_v0.7.exe`)

### Step 2: Install in Arena
1. Open Arena Chess GUI
2. Go to `Engines` → `Install New Engine...`
3. Browse to the `release/` folder
4. Select `CopycatChessEngine_v0.7.exe`
5. Choose "UCI" as the engine type
6. Click "OK"

### Step 3: Engine Configuration
The engine supports the following options:
- **Debug**: Enable/disable debug output (default: false)

To configure:
1. Go to `Engines` → `Manage...`
2. Select "Copycat Chess Engine v0.7"
3. Click "Configure"
4. Adjust settings as needed

### Step 4: Test the Engine
1. Create a new game: `Game` → `New`
2. Select "Copycat Chess Engine v0.7" as one of the players
3. Set thinking time (recommended: 5-30 seconds per move)
4. Start the game

## Engine Features

### Hybrid AI Architecture
- **Neural Network**: Deep learning model for position evaluation
- **Classical Evaluation**: Traditional chess evaluation functions
- **Intelligent Fallback**: Automatically switches to classical evaluation if neural network fails

### Performance Characteristics
- **Startup Time**: ~10-15 seconds (loading neural network model)
- **Move Time**: 1-30 seconds depending on position complexity
- **Search Depth**: Variable based on time allocation
- **Playing Strength**: Intermediate to advanced level

### Technical Details
- **Model**: v7p3r_chess_ai_model.pth (PyTorch neural network)
- **Vocabulary**: move_vocab.pkl (move encoding dictionary)
- **Dependencies**: PyTorch, python-chess, numpy
- **Platform**: Windows x64

## Troubleshooting

### Engine Won't Start
- **Issue**: Engine doesn't appear in Arena or fails to load
- **Solution**: 
  1. Ensure all files are in the same directory as the executable
  2. Check that you have sufficient RAM (4+ GB recommended)
  3. Verify Windows is x64 architecture

### Slow Performance
- **Issue**: Engine takes too long to make moves
- **Solution**:
  1. Reduce thinking time in Arena
  2. Enable debug mode to see what the engine is doing
  3. Ensure no other heavy programs are running

### Engine Crashes
- **Issue**: Engine stops responding during game
- **Solution**:
  1. Restart Arena and the engine
  2. Check Windows Event Viewer for error details
  3. Try enabling debug mode to identify issues

### No Moves Generated
- **Issue**: Engine doesn't make any moves
- **Solution**:
  1. Check that the game position is legal
  2. Ensure sufficient thinking time is allocated
  3. Enable debug mode to see engine output

## Recommended Arena Settings

### Time Controls
- **Blitz**: 3+2 (3 minutes + 2 second increment)
- **Rapid**: 15+10 (15 minutes + 10 second increment)
- **Classical**: 30+30 (30 minutes + 30 second increment)

### Engine Settings
- **Hash Size**: 128-512 MB (if available)
- **Threads**: 1 (engine is single-threaded)
- **Debug**: Enable for troubleshooting

## Files Required
The following files must be in the same directory as the executable:
- `CopycatChessEngine_v0.7.exe` (main executable)
- `v7p3r_chess_ai_model.pth` (neural network model)
- `move_vocab.pkl` (move vocabulary)
- `config.yaml` (configuration file)

## Tournament Play
The engine is suitable for:
- **Casual games** against human players
- **Engine tournaments** (intermediate level)
- **Analysis** of chess positions
- **Training** for developing players

**Note**: Due to startup time, avoid very fast time controls (under 1 minute total).

## Support
For issues or questions:
1. Check the debug output in Arena
2. Review this guide for common solutions
3. Ensure all required files are present
4. Verify system meets minimum requirements

---
*Copycat Chess Engine v0.7 - Ready for Arena Chess GUI*
