#!/usr/bin/env python3
"""
Run UCI Chess Engine

This script launches the Copycat chess engine with UCI protocol support.
It is designed to be called from chess GUIs like Arena, Cutechess, etc.
"""

import os
import sys
import subprocess

def main():
    """Run the UCI chess engine."""
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the UCI interface script
    uci_script = os.path.join(script_dir, "copycat_uci.py")
    
    # Run the UCI interface script
    print(f"Starting Copycat Chess Engine from {uci_script}")
    
    try:
        # Use sys.executable to ensure we're using the right Python
        process = subprocess.Popen([sys.executable, uci_script],
                                  stdin=sys.stdin,
                                  stdout=sys.stdout,
                                  stderr=sys.stderr)
        
        # Wait for the process to complete
        process.wait()
        
        # Return the exit code
        return process.returncode
    
    except Exception as e:
        print(f"Error running UCI engine: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
