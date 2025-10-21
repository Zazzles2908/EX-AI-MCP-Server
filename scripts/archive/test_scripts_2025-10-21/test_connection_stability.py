"""
Test WebSocket connection stability and error handling.
"""
import asyncio
import json
import sys
import uuid
from datetime import datetime

try:
    import websockets
except ImportError:
    print("ERROR: websockets module not installed")
    sys.exit(1)

from dotenv import load_dotenv
import os

load_dotenv()

WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
WS_URI = f"ws://{WS_HOST}:{WS_PORT}"


async def test_normal_connection():
    """Test normal connection flow"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Test 1: Normal connection...")
    
    try:
        async with websockets.connect(WS_URI, max_size=20 * 1024 * 1024) as websocket:
            # Send hello
            await websocket.send(json.dumps({
                "op": "hello",
                "session_id": f"test-{uuid.uuid4().hex[:6]}",
                "token": WS_TOKEN
            }))
            
            # Wait for ack
            ack = json.loads(await websocket.recv())
            if ack.get("ok"):
                print("  ✅ Normal connection successful")
                return True
            else:
                print(f"  ❌ Auth failed: {ack}")
                return False
                
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False


async def test_immediate_disconnect():
    """Test connecting and immediately disconnecting (before hello)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Test 2: Immediate disconnect...")
    
    try:
        websocket = await websockets.connect(WS_URI, max_size=20 * 1024 * 1024)
        # Close immediately without sending hello
        await websocket.close()
        print("  ✅ Immediate disconnect handled")
        return True
                
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False


async def test_slow_hello():
    """Test slow hello (within timeout)"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Test 3: Slow hello (5s delay)...")
    
    try:
        async with websockets.connect(WS_URI, max_size=20 * 1024 * 1024) as websocket:
            # Wait 5 seconds before sending hello (should be OK, timeout is 15s)
            await asyncio.sleep(5)
            
            await websocket.send(json.dumps({
                "op": "hello",
                "session_id": f"test-{uuid.uuid4().hex[:6]}",
                "token": WS_TOKEN
            }))
            
            ack = json.loads(await websocket.recv())
            if ack.get("ok"):
                print("  ✅ Slow hello successful")
                return True
            else:
                print(f"  ❌ Auth failed: {ack}")
                return False
                
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False


async def test_disconnect_after_hello():
    """Test disconnecting after hello but before tool call"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Test 4: Disconnect after hello...")
    
    try:
        websocket = await websockets.connect(WS_URI, max_size=20 * 1024 * 1024)
        
        # Send hello
        await websocket.send(json.dumps({
            "op": "hello",
            "session_id": f"test-{uuid.uuid4().hex[:6]}",
            "token": WS_TOKEN
        }))
        
        # Wait for ack
        ack = json.loads(await websocket.recv())
        if not ack.get("ok"):
            print(f"  ❌ Auth failed: {ack}")
            return False
        
        # Close after hello
        await websocket.close()
        print("  ✅ Disconnect after hello handled")
        return True
                
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False


async def test_multiple_rapid_connections():
    """Test multiple rapid connections"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Test 5: Multiple rapid connections (10x)...")
    
    success_count = 0
    for i in range(10):
        try:
            async with websockets.connect(WS_URI, max_size=20 * 1024 * 1024) as websocket:
                await websocket.send(json.dumps({
                    "op": "hello",
                    "session_id": f"test-{i}",
                    "token": WS_TOKEN
                }))
                
                ack = json.loads(await websocket.recv())
                if ack.get("ok"):
                    success_count += 1
                    
        except Exception as e:
            print(f"  ❌ Connection {i} failed: {e}")
    
    print(f"  ✅ {success_count}/10 connections successful")
    return success_count == 10


async def main():
    print("="*60)
    print("WebSocket Connection Stability Tests")
    print("="*60)
    
    tests = [
        ("Normal Connection", test_normal_connection),
        ("Immediate Disconnect", test_immediate_disconnect),
        ("Slow Hello", test_slow_hello),
        ("Disconnect After Hello", test_disconnect_after_hello),
        ("Multiple Rapid Connections", test_multiple_rapid_connections),
    ]
    
    results = []
    for name, test_func in tests:
        result = await test_func()
        results.append((name, result))
        await asyncio.sleep(0.5)  # Small delay between tests
    
    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("\nCheck server logs for any ERROR messages.")
        print("ConnectionClosedOK is normal and expected.")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

