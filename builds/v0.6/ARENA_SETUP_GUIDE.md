# Setting Up Copycat Chess Engine in Arena

## Step 1: Prepare the Engine

Ensure you have Python installed with the required packages:
```
pip install torch numpy python-chess
```

## Step 2: Install Arena Chess GUI

1. Download Arena Chess GUI from [http://www.playwitharena.de/](http://www.playwitharena.de/)
2. Install Arena following the on-screen instructions

## Step 3: Add Copycat Chess Engine to Arena

1. Open Arena Chess GUI
2. Go to **Engines** → **Install New Engine**
3. In the file dialog, navigate to your Copycat engine directory
4. Select `CopycatUCI.cmd` or `Copycat_UCI.bat`
5. In the engine dialog:
   - Set **Name**: `Copycat v0.5.31`
   - Set **Type**: `UCI`
   - Other settings can be left as default
6. Click **OK** to finish adding the engine

## Step 4: Test the Engine

1. Go to **Engines** → **Load Engine**
2. Select `Copycat v0.5.31` from the list
3. Click **OK**
4. Make a move or select **Engines** → **Go**
5. The engine should start calculating and make a move

## Step 5: Set Up a Tournament

1. Go to **Engines** → **Tournament**
2. Click **Add** to add Copycat and other engines
3. Configure tournament settings:
   - **Time Control**: Set appropriate time per move or game
   - **Number of Games**: Set the desired number of games
   - **Start Position**: Choose starting positions
4. Click **Start** to begin the tournament

## Troubleshooting

If the engine doesn't work:

1. **Engine doesn't load**: 
   - Check if Python is in your PATH
   - Run the cmd file manually to see error messages

2. **Engine loads but doesn't make moves**:
   - Check the model paths in uci_interface.py
   - Ensure all required packages are installed

3. **Engine crashes**:
   - Check console for error messages
   - Try using a different build version (v0.5.30 instead of v0.5.31)

## Engine Versions

Different versions of the engine are available in the builds directory:
- `v0.5.31_copycat_enhanced_ai`: Latest version with improved evaluation
- `v0.5.31_copycat_genetic_ai`: Version using genetic algorithms
- `v0.5.30_copycat_eval_ai`: Version focused on evaluation
