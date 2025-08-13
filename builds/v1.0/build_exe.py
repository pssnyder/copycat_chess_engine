#!/usr/bin/env python3
"""
Build script for creating an executable of the Copycat Chess Engine.
Uses PyInstaller to bundle all dependencies into a standalone executable.
"""

import os
import sys
import shutil
import subprocess
import argparse

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Build Copycat Chess Engine executable')
    parser.add_argument('--onefile', action='store_true', help='Create a single executable file')
    parser.add_argument('--noconsole', action='store_true', help='Hide console window when running the executable')
    parser.add_argument('--name', default='CopycatChessEngine', help='Name for the output executable')
    parser.add_argument('--icon', help='Path to .ico file for the executable')
    return parser.parse_args()

def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def build_executable(args):
    """Build the executable using PyInstaller."""
    # Get the path to the main script
    script_path = os.path.join(os.getcwd(), "copycat_uci.py")
    
    if not os.path.exists(script_path):
        print(f"Error: Main script not found at {script_path}")
        return False
    
    # Build command
    cmd = ["pyinstaller"]
    
    # Add options based on arguments
    if args.onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")
    
    if args.noconsole:
        cmd.append("--noconsole")
    
    if args.icon and os.path.exists(args.icon):
        cmd.extend(["--icon", args.icon])
    
    # Add name for the executable
    cmd.extend(["--name", args.name])
    
    # Add data files
    results_dir = os.path.join(os.getcwd(), "results")
    if os.path.exists(results_dir):
        cmd.extend(["--add-data", f"{results_dir}{os.pathsep}results"])
    
    # Add main script
    cmd.append(script_path)
    
    # Run PyInstaller
    print("Building executable with command:")
    print(" ".join(cmd))
    print("\nThis may take a few minutes...\n")
    
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        return False

def copy_additional_files():
    """Copy additional files needed for the executable."""
    dist_dir = os.path.join(os.getcwd(), "dist")
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    
    # Copy README
    readme_path = os.path.join(os.getcwd(), "README.md")
    if os.path.exists(readme_path):
        shutil.copy2(readme_path, os.path.join(dist_dir, "README.md"))
    
    # Copy example batch file for running the engine
    batch_content = '@echo off\necho Running Copycat Chess Engine...\n%~dp0CopycatChessEngine.exe\n'
    with open(os.path.join(dist_dir, "Run_Engine.bat"), "w") as f:
        f.write(batch_content)
    
    return True

def main():
    """Main function to build the executable."""
    print("Copycat Chess Engine - Build Script")
    print("==================================\n")
    
    # Parse arguments
    args = parse_args()
    
    # Check if PyInstaller is installed
    if not check_pyinstaller():
        print("Error: PyInstaller is not installed.")
        print("Please install it with: pip install pyinstaller")
        return 1
    
    # Build the executable
    print("Building executable...")
    if not build_executable(args):
        print("\nBuild failed. Please check the errors above.")
        return 1
    
    # Copy additional files
    print("\nCopying additional files...")
    if not copy_additional_files():
        print("Failed to copy additional files.")
        return 1
    
    print("\nBuild completed successfully!")
    print(f"The executable has been created in the 'dist' directory as '{args.name}'.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
