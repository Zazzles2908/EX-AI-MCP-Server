#!/usr/bin/env python3
"""
Streaming Implementation Test Script
Tests progressive chunk delivery for both GLM and Moonshot providers

Created: 2025-10-24
"""

import asyncio
import json
import websockets
import time
from datetime import datetime

# Test configuration
WS_URL = "ws://localhost:8079"
TEST_TIMEOUT = 60  # seconds


class StreamingTester:
    """Test progressive streaming functionality"""
    
    def __init__(self):
        self.chunks_received = []
        self.start_time = None
        self.first_chunk_time = None
        self.completion_time = None
        
    async def test_glm_streaming(self):
        """Test GLM provider streaming"""
        print("\n" + "="*80)
        print("TEST 1: GLM Provider Streaming")
        print("="*80)
        
        self.chunks_received = []
        self.start_time = time.time()
        
        async with websockets.connect(WS_URL) as ws:
            # Send chat request with GLM model
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "chat_EXAI-WS",
                    "arguments": {
                        "prompt": "Count from 1 to 10 slowly, one number per line.",
                        "model": "glm-4.5-flash",
                        "stream": True  # Request streaming
                    }
                }
            }
            
            await ws.send(json.dumps(request))
            print(f"✓ Sent request at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
            
            # Collect responses
            while True:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=TEST_TIMEOUT)
                    data = json.loads(response)
                    
                    # Check for stream chunks
                    if "op" in data:
                        if data["op"] == "stream_chunk":
                            chunk_time = time.time()
                            if self.first_chunk_time is None:
                                self.first_chunk_time = chunk_time
                                ttfc = (chunk_time - self.start_time) * 1000
                                print(f"✓ First chunk received! TTFC: {ttfc:.0f}ms")
                            
                            chunk = data.get("chunk", "")
                            self.chunks_received.append(chunk)
                            print(f"  Chunk {len(self.chunks_received)}: {repr(chunk[:50])}")
                            
                        elif data["op"] == "stream_complete":
                            self.completion_time = time.time()
                            print(f"✓ Stream complete at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
                            
                    # Check for final result
                    if "result" in data:
                        total_time = (time.time() - self.start_time) * 1000
                        print(f"\n✓ Final result received! Total time: {total_time:.0f}ms")
                        break
                        
                except asyncio.TimeoutError:
                    print(f"✗ Timeout waiting for response")
                    break
                except Exception as e:
                    print(f"✗ Error: {e}")
                    break
        
        # Report results
        self._report_results("GLM")
        
    async def test_moonshot_streaming(self):
        """Test Moonshot provider streaming"""
        print("\n" + "="*80)
        print("TEST 2: Moonshot Provider Streaming")
        print("="*80)
        
        self.chunks_received = []
        self.start_time = time.time()
        self.first_chunk_time = None
        self.completion_time = None
        
        async with websockets.connect(WS_URL) as ws:
            # Send chat request with Moonshot model
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "chat_EXAI-WS",
                    "arguments": {
                        "prompt": "List 5 programming languages, one per line.",
                        "model": "kimi-k2-turbo-preview",
                        "stream": True  # Request streaming
                    }
                }
            }
            
            await ws.send(json.dumps(request))
            print(f"✓ Sent request at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
            
            # Collect responses
            while True:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=TEST_TIMEOUT)
                    data = json.loads(response)
                    
                    # Check for stream chunks
                    if "op" in data:
                        if data["op"] == "stream_chunk":
                            chunk_time = time.time()
                            if self.first_chunk_time is None:
                                self.first_chunk_time = chunk_time
                                ttfc = (chunk_time - self.start_time) * 1000
                                print(f"✓ First chunk received! TTFC: {ttfc:.0f}ms")
                            
                            chunk = data.get("chunk", "")
                            self.chunks_received.append(chunk)
                            print(f"  Chunk {len(self.chunks_received)}: {repr(chunk[:50])}")
                            
                        elif data["op"] == "stream_complete":
                            self.completion_time = time.time()
                            print(f"✓ Stream complete at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
                            
                    # Check for final result
                    if "result" in data:
                        total_time = (time.time() - self.start_time) * 1000
                        print(f"\n✓ Final result received! Total time: {total_time:.0f}ms")
                        break
                        
                except asyncio.TimeoutError:
                    print(f"✗ Timeout waiting for response")
                    break
                except Exception as e:
                    print(f"✗ Error: {e}")
                    break
        
        # Report results
        self._report_results("Moonshot")
        
    def _report_results(self, provider_name):
        """Report test results"""
        print("\n" + "-"*80)
        print(f"RESULTS: {provider_name} Provider")
        print("-"*80)
        
        if self.first_chunk_time:
            ttfc = (self.first_chunk_time - self.start_time) * 1000
            print(f"✓ Time to First Chunk (TTFC): {ttfc:.0f}ms")
        else:
            print(f"✗ No chunks received!")
            
        print(f"✓ Total chunks received: {len(self.chunks_received)}")
        
        if self.completion_time:
            total_time = (self.completion_time - self.start_time) * 1000
            print(f"✓ Total streaming time: {total_time:.0f}ms")
            
        if self.chunks_received:
            full_response = "".join(self.chunks_received)
            print(f"✓ Full response length: {len(full_response)} characters")
            print(f"\nFull response preview:")
            print(full_response[:200] + ("..." if len(full_response) > 200 else ""))
        
        print("-"*80)


async def main():
    """Run all streaming tests"""
    print("\n" + "="*80)
    print("STREAMING IMPLEMENTATION TEST SUITE")
    print("="*80)
    print(f"WebSocket URL: {WS_URL}")
    print(f"Test timeout: {TEST_TIMEOUT}s")
    print("="*80)
    
    tester = StreamingTester()
    
    try:
        # Test GLM streaming
        await tester.test_glm_streaming()
        
        # Wait between tests
        await asyncio.sleep(2)
        
        # Test Moonshot streaming
        await tester.test_moonshot_streaming()
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETE!")
        print("="*80)
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

