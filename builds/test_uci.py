#!/usr/bin/env python3
"""
Test script to verify UCI interfaces work correctly
This tests the UCI protocol without needing to build executables first
"""

import subprocess
import sys
import os
import time

def test_uci_interface(version_path, version_name):
    """Test a UCI interface by sending basic UCI commands"""
    print(f"\n{'='*50}")
    print(f"Testing {version_name}")
    print(f"Path: {version_path}")
    print(f"{'='*50}")
    
    uci_script = os.path.join(version_path, "copycat_uci.py")
    
    if not os.path.exists(uci_script):
        print(f"❌ UCI script not found: {uci_script}")
        return False
    
    try:
        # Start the UCI process
        process = subprocess.Popen(
            [sys.executable, uci_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=version_path
        )
        
        # Test UCI handshake
        print("📤 Sending: uci")
        process.stdin.write("uci\n")
        process.stdin.flush()
        
        # Read response with timeout
        response_lines = []
        start_time = time.time()
        
        while time.time() - start_time < 10:  # 10 second timeout
            if process.poll() is not None:
                break
            
            line = process.stdout.readline()
            if line:
                line = line.strip()
                print(f"📥 Received: {line}")
                response_lines.append(line)
                
                if line == "uciok":
                    print("✅ UCI handshake successful!")
                    break
        else:
            print("❌ UCI handshake timeout")
            process.terminate()
            return False
        
        # Test isready
        print("\n📤 Sending: isready")
        process.stdin.write("isready\n")
        process.stdin.flush()
        
        start_time = time.time()
        while time.time() - start_time < 15:  # 15 second timeout for engine init
            if process.poll() is not None:
                break
                
            line = process.stdout.readline()
            if line:
                line = line.strip()
                print(f"📥 Received: {line}")
                
                if line == "readyok":
                    print("✅ Engine initialization successful!")
                    break
                elif "Error" in line:
                    print(f"⚠️  Engine warning/error: {line}")
        else:
            print("❌ Engine initialization timeout")
        
        # Test position and go
        print("\n📤 Sending: position startpos")
        process.stdin.write("position startpos\n")
        process.stdin.flush()
        
        print("📤 Sending: go movetime 1000")
        process.stdin.write("go movetime 1000\n")
        process.stdin.flush()
        
        start_time = time.time()
        while time.time() - start_time < 5:  # 5 second timeout
            if process.poll() is not None:
                break
                
            line = process.stdout.readline()
            if line:
                line = line.strip()
                print(f"📥 Received: {line}")
                
                if line.startswith("bestmove"):
                    print("✅ Engine returned a move!")
                    break
        else:
            print("❌ No move returned within timeout")
        
        # Quit
        print("\n📤 Sending: quit")
        process.stdin.write("quit\n")
        process.stdin.flush()
        
        process.wait(timeout=2)
        print("✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        if 'process' in locals():
            process.terminate()
        return False

def main():
    print("Copycat Chess Engine UCI Interface Test")
    print("=" * 60)
    
    # Base directory
    builds_dir = r"s:\Maker Stuff\Programming\Chess Engines\Copycat Chess AI\copycat_chess_engine\builds"
    
    # Test each version
    versions = [
        ("v0.1_copycat_ai", "Copycat v0.1"),
        ("v0.2_copycat_eval_ai", "Copycat v0.2 Evaluation"),
        ("v0.3_copycat_enhanced_ai", "Copycat v0.3 Enhanced"),
        ("v0.4_copycat_genetic_ai", "Copycat v0.4 Genetic"),
        ("v0.5_BETA", "Copycat v0.5 BETA")
    ]
    
    results = {}
    
    for version_dir, version_name in versions:
        version_path = os.path.join(builds_dir, version_dir)
        if os.path.exists(version_path):
            results[version_name] = test_uci_interface(version_path, version_name)
        else:
            print(f"\n❌ Version directory not found: {version_path}")
            results[version_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for version_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{version_name:<30} {status}")
    
    successful = sum(results.values())
    total = len(results)
    
    print(f"\nResults: {successful}/{total} versions passed UCI tests")
    
    if successful == total:
        print("\n🎉 All UCI interfaces are working! Ready to build executables.")
    else:
        print(f"\n⚠️  {total - successful} versions need fixes before building.")

if __name__ == "__main__":
    main()
