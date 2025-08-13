#!/usr/bin/env python
"""
check_dependencies.py - Script to check if all dependencies for Copycat Chess Engine are installed
"""

import sys
import os

def check_dependencies():
    """Check if all required dependencies are installed and working correctly"""
    print("Checking Copycat Chess Engine dependencies...\n")
    
    # Dictionary to track dependency status
    dependencies = {
        "torch": {"installed": False, "version": None, "cuda": False},
        "numpy": {"installed": False, "version": None},
        "chess": {"installed": False, "version": None}
    }
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python version: {python_version}")
    
    # Check PyTorch
    try:
        import torch
        dependencies["torch"]["installed"] = True
        dependencies["torch"]["version"] = torch.__version__
        dependencies["torch"]["cuda"] = torch.cuda.is_available()
        cuda_version = torch.version.cuda if torch.cuda.is_available() else "N/A"
        print(f"PyTorch: Installed (version {torch.__version__})")
        print(f"CUDA available: {torch.cuda.is_available()}")
        print(f"CUDA version: {cuda_version}")
        if torch.cuda.is_available():
            print(f"GPU device: {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("PyTorch: Not installed")
    
    # Check numpy
    try:
        import numpy
        dependencies["numpy"]["installed"] = True
        dependencies["numpy"]["version"] = numpy.__version__
        print(f"NumPy: Installed (version {numpy.__version__})")
    except ImportError:
        print("NumPy: Not installed")
    
    # Check python-chess
    try:
        import chess
        dependencies["chess"]["installed"] = True
        dependencies["chess"]["version"] = chess.__version__
        print(f"python-chess: Installed (version {chess.__version__})")
    except ImportError:
        print("python-chess: Not installed")
    
    # Check model files
    print("\nChecking model files...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    model_paths = [
        os.path.join(script_dir, "rl_actor_model.pth"),
        os.path.join(script_dir, "builds", "v0.5.31_copycat_enhanced_ai", "v7p3r_chess_ai_model.pth"),
        os.path.join(script_dir, "builds", "v0.5.31_copycat_genetic_ai", "v7p3r_chess_ai_model.pth"),
        os.path.join(script_dir, "builds", "v0.5.30_copycat_eval_ai", "v7p3r_chess_ai_model.pth")
    ]
    
    vocab_paths = [
        os.path.join(script_dir, "builds", "v0.5.31_copycat_enhanced_ai", "move_vocab.pkl"),
        os.path.join(script_dir, "builds", "v0.5.31_copycat_genetic_ai", "move_vocab.pkl"),
        os.path.join(script_dir, "builds", "v0.5.30_copycat_eval_ai", "move_vocab.pkl")
    ]
    
    found_model = False
    for path in model_paths:
        if os.path.exists(path):
            print(f"Found model: {os.path.basename(path)}")
            found_model = True
    
    if not found_model:
        print("No model files found!")
    
    found_vocab = False
    for path in vocab_paths:
        if os.path.exists(path):
            print(f"Found vocabulary: {os.path.basename(path)}")
            found_vocab = True
    
    if not found_vocab:
        print("No vocabulary files found!")
    
    # Overall status
    print("\nOverall Status:")
    all_installed = all(dep["installed"] for dep in dependencies.values())
    
    if all_installed and found_model and found_vocab:
        print("✅ All dependencies and model files are installed correctly.")
        return True
    else:
        print("❌ Some dependencies or model files are missing.")
        
        # Print installation instructions for missing dependencies
        if not dependencies["torch"]["installed"]:
            print("\nTo install PyTorch:")
            print("pip install torch")
        
        if not dependencies["numpy"]["installed"]:
            print("\nTo install NumPy:")
            print("pip install numpy")
        
        if not dependencies["chess"]["installed"]:
            print("\nTo install python-chess:")
            print("pip install python-chess")
            
        if not found_model or not found_vocab:
            print("\nModel files are missing. Please check the builds directory.")
        
        return False

if __name__ == "__main__":
    check_dependencies()
