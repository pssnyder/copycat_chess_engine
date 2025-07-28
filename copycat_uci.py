#!/usr/bin/env python
# copycat_uci.py - UCI launcher for Copycat Chess Engine

import sys
import os
from uci_interface import UCIEngine

def main():
    """Launch the Copycat Chess Engine in UCI mode"""
    try:
        # Initialize and run the UCI engine
        engine = UCIEngine()
        engine.run()
    except Exception as e:
        sys.stderr.write(f"Fatal error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
