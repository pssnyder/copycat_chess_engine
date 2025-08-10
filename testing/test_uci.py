#!/usr/bin/env python3
"""
Test script for the UCI interface of the Copycat Chess Engine.
This script simulates a UCI GUI interacting with the engine.
"""

import subprocess
import time
import sys
import os

def main():
    """Run a test sequence of UCI commands."""
    print("Starting UCI test for Copycat Chess Engine")
    
    # Start the engine process
    try:
        # Get Python executable path
        python_executable = sys.executable
        
        # Run the UCI interface
        process = subprocess.Popen(
            [python_executable, "copycat_uci.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
    except Exception as e:
        print(f"Error starting engine: {e}")
        return

    # Function to send a command and get response
    def send_command(command, wait_time=0.5):
        """
        Send a command to the engine and return the response.
        
        Args:
            command: The command to send
            wait_time: Time to wait for response
        """
        print(f"\nSending: {command}")
        process.stdin.write(command + "\n")
        process.stdin.flush()
        
        # Wait for response
        time.sleep(wait_time)
        
        # Read all available output
        output = []
        while True:
            # Check if there's data to read
            try:
                line = process.stdout.readline().strip()
                if not line:
                    break
                output.append(line)
                print(f"< {line}")
            except:
                break
            
            # Break after a few lines to avoid blocking
            if len(output) > 50:
                print("(output truncated)")
                break
        
        return output

    # Send UCI init commands
    send_command("uci", 1.0)
    send_command("isready", 0.5)
    
    # Start a new game
    send_command("ucinewgame", 0.5)
    
    # Set up the starting position and make some moves
    send_command("position startpos", 0.5)
    send_command("go movetime 1000", 2.0)  # Think for 1 second
    
    # Set up a position with some moves already played
    send_command("position startpos moves e2e4 e7e5 g1f3", 0.5)
    send_command("go movetime 1000", 2.0)
    
    # Set up a middlegame position
    # This is the Ruy Lopez, Berlin Defense after 9 moves
    fen = "r1bqk2r/ppp2ppp/2p2n2/b3p3/3PP3/5N2/PPP2PPP/RNBQ1RK1 b kq - 0 9"
    send_command(f"position fen {fen}", 0.5)
    send_command("go movetime 2000", 3.0)
    
    # Set up an endgame position
    # This is a king and pawn endgame
    fen = "4k3/8/8/4P3/8/8/8/4K3 w - - 0 1"
    send_command(f"position fen {fen}", 0.5)
    send_command("go movetime 1000", 2.0)
    
    # Test time control commands
    send_command("position startpos", 0.5)
    send_command("go wtime 300000 btime 300000 winc 1000 binc 1000", 2.0)
    
    # Quit the engine
    send_command("quit", 0.5)
    
    # Cleanup
    try:
        process.terminate()
    except:
        pass
    
    print("\nUCI test completed")

if __name__ == "__main__":
    main()
