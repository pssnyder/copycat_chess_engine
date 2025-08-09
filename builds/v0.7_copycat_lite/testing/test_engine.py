#!/usr/bin/env python3
"""
Quick test script to verify the engine executable works correctly.
"""
import subprocess
import time
import os

def test_engine():
    """Test the CopycatChessEngine_v0.7.exe executable."""
    engine_path = os.path.join("release", "CopycatChessEngine_v0.7.exe")
    
    if not os.path.exists(engine_path):
        print(f"Error: Engine executable not found at {engine_path}")
        return False
    
    print(f"Testing engine at: {engine_path}")
    print(f"File size: {os.path.getsize(engine_path) / (1024*1024*1024):.2f} GB")
    
    try:
        # Start the engine process
        print("Starting engine...")
        process = subprocess.Popen(
            [engine_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(engine_path)
        )
        
        # Send UCI command
        print("Sending 'uci' command...")
        process.stdin.write("uci\n")
        process.stdin.flush()
        
        # Wait for response with timeout
        start_time = time.time()
        output_lines = []
        
        while time.time() - start_time < 10:  # 10 second timeout
            line = process.stdout.readline()
            if line:
                output_lines.append(line.strip())
                print(f"Engine: {line.strip()}")
                if "uciok" in line:
                    print("✓ Engine responded with uciok!")
                    break
            time.sleep(0.1)
        
        # Send quit command
        print("Sending 'quit' command...")
        process.stdin.write("quit\n")
        process.stdin.flush()
        
        # Wait for process to terminate
        process.wait(timeout=5)
        
        if "uciok" in " ".join(output_lines):
            print("✓ Test PASSED - Engine is working correctly!")
            return True
        else:
            print("✗ Test FAILED - Engine did not respond properly")
            return False
            
    except Exception as e:
        print(f"✗ Test FAILED - Exception: {e}")
        try:
            process.terminate()
        except:
            pass
        return False

if __name__ == "__main__":
    test_engine()
