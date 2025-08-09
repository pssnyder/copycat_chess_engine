#!/usr/bin/env python
"""
test_imports.py - Tests imports to help diagnose any issues with the Python environment
"""

import sys
import os

def print_separator():
    print("-" * 60)

def main():
    """Print detailed information about the Python environment and package imports"""
    print_separator()
    print("PYTHON ENVIRONMENT INFORMATION")
    print_separator()
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path}")
    print_separator()
    
    print("TESTING IMPORTS")
    print_separator()
    
    # Test torch import
    print("Attempting to import torch...")
    try:
        import torch
        print(f"✅ Successfully imported torch {torch.__version__}")
        print(f"Torch path: {torch.__file__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"GPU device: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        print(f"❌ Failed to import torch: {e}")
        # Try to get pip info about torch
        try:
            import subprocess
            result = subprocess.run([sys.executable, "-m", "pip", "show", "torch"], 
                                    capture_output=True, text=True)
            print("\nPip information about torch:")
            print(result.stdout)
        except Exception as e:
            print(f"Could not get pip information: {e}")
    
    print_separator()
    
    # Test numpy import
    print("Attempting to import numpy...")
    try:
        import numpy
        print(f"✅ Successfully imported numpy {numpy.__version__}")
        print(f"NumPy path: {numpy.__file__}")
    except ImportError as e:
        print(f"❌ Failed to import numpy: {e}")
    
    print_separator()
    
    # Test chess import
    print("Attempting to import chess...")
    try:
        import chess
        print(f"✅ Successfully imported chess {chess.__version__}")
        print(f"Chess path: {chess.__file__}")
    except ImportError as e:
        print(f"❌ Failed to import chess: {e}")
    
    print_separator()
    print("SYSTEM PATHS")
    print_separator()
    
    # Print current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # Print PATH environment variable
    print("\nPATH environment variable:")
    path_entries = os.environ.get('PATH', '').split(os.pathsep)
    for i, entry in enumerate(path_entries):
        print(f"  {i+1}. {entry}")
    
    print_separator()
    print("VS CODE INTERPRETER INFO")
    print_separator()
    
    # Check if we're in VS Code
    if 'VSCODE' in os.environ or 'VSCODE_PID' in os.environ:
        print("Running in VS Code environment")
        print(f"VS Code process ID: {os.environ.get('VSCODE_PID', 'Not available')}")
        
        # Try to get pylance info
        try:
            # Check if .vscode directory exists
            vscode_dir = os.path.join(os.getcwd(), '.vscode')
            if os.path.exists(vscode_dir):
                print("\nFound .vscode directory:")
                for file in os.listdir(vscode_dir):
                    print(f"  - {file}")
                
                # Check for settings.json
                settings_path = os.path.join(vscode_dir, 'settings.json')
                if os.path.exists(settings_path):
                    print("\nContents of settings.json:")
                    with open(settings_path, 'r') as f:
                        print(f.read())
        except Exception as e:
            print(f"Error reading VS Code config: {e}")
    else:
        print("Not running in VS Code environment")
    
    print_separator()
    print("COMPLETED ENVIRONMENT TESTS")
    print_separator()

if __name__ == "__main__":
    main()
