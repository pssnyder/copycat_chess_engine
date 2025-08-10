#!/usr/bin/env python3
"""
Test the Copycat Chess Engine by playing a few moves and verifying functionality.
"""

import sys
import os
import time
import chess

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    # Try to import from the new structure
    from src.core.chess_game import ChessGame
    from src.core.engine import CopycatChessEngine
except ImportError:
    # Fallback to old structure
    sys.path.insert(0, os.path.join(parent_dir, 'src'))
    try:
        from core.chess_game import ChessGame
        from core.engine import CopycatChessEngine
    except ImportError:
        print("Error: Could not import required modules.")
        print("Make sure you're running this script from the tests directory or the project root.")
        sys.exit(1)

def run_basic_test():
    """Run a basic test to verify engine functionality."""
    print("Running basic engine test...")
    
    # Initialize engine
    try:
        print("Initializing engine...")
        engine = CopycatChessEngine()
        print("Engine initialized successfully.")
    except Exception as e:
        print(f"Error initializing engine: {str(e)}")
        return False
    
    # Initialize game
    try:
        print("\nInitializing game...")
        game = ChessGame(engine)
        print("Game initialized successfully.")
        print(f"Current position:\n{game.board}")
    except Exception as e:
        print(f"Error initializing game: {str(e)}")
        return False
    
    # Play a few moves
    print("\nPlaying a few standard opening moves...")
    opening_moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"]
    
    for move in opening_moves:
        print(f"\nPlaying move: {move}")
        try:
            success = game.make_move(move)
            if not success:
                print(f"Error: Failed to make move {move}")
                return False
            print(f"Current position:\n{game.board}")
        except Exception as e:
            print(f"Error making move {move}: {str(e)}")
            return False
    
    # Test engine move
    print("\nRequesting engine move...")
    try:
        start_time = time.time()
        engine_move = game.get_engine_move()
        end_time = time.time()
        
        print(f"Engine suggested move: {engine_move.uci()}")
        print(f"Think time: {end_time - start_time:.2f} seconds")
        
        # Make the suggested move
        game.make_move(engine_move)
        print(f"Current position after engine move:\n{game.board}")
    except Exception as e:
        print(f"Error getting engine move: {str(e)}")
        return False
    
    # Check game phase and opening detection
    print(f"\nCurrent game phase: {game.game_phase}")
    print(f"Detected opening: {game.opening}")
    
    return True

def run_uci_test():
    """Test UCI protocol functionality."""
    print("\nTesting UCI protocol functionality...")
    
    try:
        from src.core.uci_interface import UCIInterface
    except ImportError:
        try:
            from core.uci_interface import UCIInterface
        except ImportError:
            try:
                # Try to import from root
                sys.path.insert(0, parent_dir)
                from testing.uci_interface import CopycatUCI as UCIInterface
            except ImportError:
                print("Could not import UCI interface module.")
                return False
    
    try:
        # Initialize UCI interface
        print("Initializing UCI interface...")
        uci = UCIInterface()
        
        # Test basic UCI commands
        print("\nTesting 'uci' command...")
        if hasattr(uci, 'handle_uci'):
            uci.handle_uci()
        elif hasattr(uci, 'uci'):
            uci.uci()
        else:
            print("UCI interface does not have expected methods.")
            return False
        
        print("\nTesting 'isready' command...")
        if hasattr(uci, 'handle_isready'):
            uci.handle_isready()
        elif hasattr(uci, 'isready'):
            uci.isready()
        else:
            print("UCI interface does not have expected methods.")
            return False
        
        print("\nUCI protocol test successful.")
        return True
    
    except Exception as e:
        print(f"Error testing UCI protocol: {str(e)}")
        return False

def main():
    """Run tests to verify engine functionality."""
    print("Copycat Chess Engine - Test Suite")
    print("================================\n")
    
    # Run basic engine test
    basic_test_result = run_basic_test()
    
    # Run UCI test
    uci_test_result = run_uci_test()
    
    # Report results
    print("\nTest Results:")
    print(f"Basic Engine Test: {'PASS' if basic_test_result else 'FAIL'}")
    print(f"UCI Protocol Test: {'PASS' if uci_test_result else 'FAIL'}")
    
    if basic_test_result and uci_test_result:
        print("\nAll tests passed! The Copycat Chess Engine is working properly.")
        return 0
    else:
        print("\nSome tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
