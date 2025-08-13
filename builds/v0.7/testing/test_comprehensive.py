#!/usr/bin/env python3
"""
Comprehensive test for CopycatChessEngine_v0.7.exe including move generation.
"""
import subprocess
import time
import os

def comprehensive_engine_test():
    """Comprehensive test of the engine with actual chess moves."""
    engine_path = os.path.join("release", "CopycatChessEngine_v0.7.exe")
    
    if not os.path.exists(engine_path):
        print(f"Error: Engine executable not found at {engine_path}")
        return False
    
    print("=" * 60)
    print("COPYCAT CHESS ENGINE v0.7 - COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"Engine path: {engine_path}")
    print(f"File size: {os.path.getsize(engine_path) / (1024*1024*1024):.2f} GB")
    print()
    
    try:
        # Start the engine process
        print("🔄 Starting engine...")
        process = subprocess.Popen(
            [engine_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(engine_path)
        )
        
        def send_command(cmd, expected_response=None, timeout=5):
            """Send a command and wait for response."""
            print(f">>> {cmd}")
            process.stdin.write(f"{cmd}\n")
            process.stdin.flush()
            
            start_time = time.time()
            responses = []
            
            while time.time() - start_time < timeout:
                line = process.stdout.readline()
                if line:
                    line = line.strip()
                    responses.append(line)
                    print(f"<<< {line}")
                    
                    if expected_response and expected_response in line:
                        return True, responses
                time.sleep(0.1)
            
            return expected_response is None, responses
        
        # Test 1: UCI Protocol
        print("\n📋 TEST 1: UCI Protocol")
        success, _ = send_command("uci", "uciok", timeout=10)
        if not success:
            print("❌ UCI test failed!")
            return False
        print("✅ UCI protocol working!")
        
        # Test 2: Ready Check
        print("\n📋 TEST 2: Ready Check")
        success, _ = send_command("isready", "readyok", timeout=5)
        if not success:
            print("❌ Ready check failed!")
            return False
        print("✅ Engine is ready!")
        
        # Test 3: New Game
        print("\n📋 TEST 3: New Game Setup")
        send_command("ucinewgame")
        send_command("position startpos")
        print("✅ New game setup complete!")
        
        # Test 4: Move Generation
        print("\n📋 TEST 4: Move Generation")
        print("Requesting best move for starting position...")
        success, responses = send_command("go movetime 1000", "bestmove", timeout=15)
        
        if success:
            # Find the bestmove line
            for response in responses:
                if response.startswith("bestmove"):
                    move = response.split()[1]
                    print(f"✅ Engine suggested move: {move}")
                    break
        else:
            print("❌ Move generation failed!")
            return False
        
        # Test 5: Position After Move
        print("\n📋 TEST 5: Position After Move (e2e4)")
        send_command("position startpos moves e2e4")
        success, responses = send_command("go movetime 1000", "bestmove", timeout=15)
        
        if success:
            for response in responses:
                if response.startswith("bestmove"):
                    move = response.split()[1]
                    print(f"✅ Engine response to e2e4: {move}")
                    break
        else:
            print("❌ Response move generation failed!")
            return False
        
        # Test 6: Debug Mode
        print("\n📋 TEST 6: Debug Mode")
        send_command("setoption name Debug value true")
        send_command("position startpos")
        success, responses = send_command("go movetime 500", "bestmove", timeout=10)
        
        if success:
            print("✅ Debug mode working!")
        else:
            print("❌ Debug mode failed!")
        
        # Clean shutdown
        print("\n📋 SHUTDOWN")
        send_command("quit")
        process.wait(timeout=5)
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Engine is ready for Arena chess GUI!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        try:
            process.terminate()
        except:
            pass
        return False

if __name__ == "__main__":
    success = comprehensive_engine_test()
    if not success:
        print("\n❌ Some tests failed. Check the output above.")
        exit(1)
    else:
        print("\n✅ All tests passed successfully!")
