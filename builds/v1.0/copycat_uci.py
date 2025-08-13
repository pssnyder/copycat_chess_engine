#!/usr/bin/env python3
"""
Copycat Chess Engine - UCI Interface

This is the main entry point for the Copycat Chess Engine, implementing the UCI protocol
for compatibility with chess GUIs.

Usage:
  python copycat_uci.py
"""

import sys
import os
import importlib.util
import logging

# Version (can be overridden by environment variable set in build/spec)
ENGINE_VERSION = os.environ.get("COPYCAT_VERSION", "0.5.0-dev")

# Configure logging
logging.basicConfig(
    filename="copycat_chess.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if os.path.exists(src_dir):
    sys.path.insert(0, src_dir)
    logging.info(f"Added {src_dir} to Python path")

def load_module(module_path):
    """
    Dynamically load a module from a file path.
    
    Args:
        module_path: Path to the Python module
        
    Returns:
        The loaded module, or None if not found
    """
    try:
        if os.path.exists(module_path):
            module_name = os.path.basename(module_path).replace(".py", "")
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is None:
                logging.error(f"Could not load spec for {module_path}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        else:
            logging.error(f"Module file not found: {module_path}")
            return None
    except Exception as e:
        logging.error(f"Error loading module {module_path}: {str(e)}")
        return None

def main():
    """Main entry point for the Copycat Chess Engine UCI interface."""
    # Top-level exception guard
    try:
        print(f"Copycat Chess Engine v{ENGINE_VERSION}")
        print("Analytics-based chess engine that mimics a player's style")

        # Attempt primary import path
        try:
            from core.uci_interface import CopycatUCI  # type: ignore
            logging.info("Imported UCI interface from core.uci_interface")
            uci_class = CopycatUCI
        except ImportError:
            # Fallback: dynamic module load
            search_paths = [
                os.path.join(current_dir, 'src', 'core', 'uci_interface.py'),
                os.path.join(current_dir, 'uci_interface.py')
            ]
            uci_class = None  # type: ignore
            for candidate in search_paths:
                if os.path.exists(candidate):
                    uci_module = load_module(candidate)
                    if uci_module and hasattr(uci_module, 'CopycatUCI'):
                        uci_class = getattr(uci_module, 'CopycatUCI')
                        logging.info(f"Loaded UCI interface from {candidate}")
                        break
            if uci_class is None:  # type: ignore
                raise ImportError("Could not locate CopycatUCI implementation")

        # Instantiate and enter protocol loop
        logging.info("Starting UCI interface main loop")
        uci = uci_class()  # type: ignore
        loop = getattr(uci, 'run', None) or getattr(uci, 'main_loop', None)
        if loop is None:
            raise RuntimeError("UCI interface has no run() or main_loop() method")
        loop()
    except Exception as exc:  # noqa: BLE001
        logging.error(f"Fatal startup error: {exc}")
        print(f"Error starting UCI interface: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
