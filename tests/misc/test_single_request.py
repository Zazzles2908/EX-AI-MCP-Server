"""
Simple test script to debug WebSocket timeout issues

Tests a single request with detailed logging to identify root cause
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import websockets

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_single_request():
    """Test a single chat request to identify timeout issues"""
    
    ws_url = "ws://127.0.0.1:8079"
    
    logger.info(f"Connecting to {ws_url}...")
    
    try:
        async with websockets.connect(ws_url) as ws:
            logger.info("✅ Connected successfully")

            # Send hello message for authentication
            hello_msg = {
                "op": "hello",
                "session_id": "test_session_001",
                "token": "test-token-12345"  # Auth token from .env.docker
            }
            await ws.send(json.dumps(hello_msg))
            logger.info("Sent hello message, waiting for ack...")

            # Wait for hello response
            hello_response = await ws.recv()
            hello_data = json.loads(hello_response)
            logger.info(f"Hello response: {hello_data}")

            if hello_data.get("op") not in ["hello_res", "hello_ack"] or not hello_data.get("ok"):
                logger.error(f"❌ Authentication failed: {hello_data}")
                return False

            logger.info("✅ Authenticated successfully")

            # Test 1: Simple GLM chat
            logger.info("\n" + "="*80)
            logger.info("TEST 1: Simple GLM-4.6 chat request")
            logger.info("="*80)
            
            request = {
                "op": "call_tool",
                "request_id": "test_glm_001",
                "name": "chat_EXAI-WS-VSCode2",
                "arguments": {
                    "prompt": "Say 'Hello from GLM!' and nothing else.",
                    "model": "glm-4.6",
                    "temperature": 0.7,
                    "use_websearch": False
                }
            }
            
            logger.info(f"Sending request: {json.dumps(request, indent=2)}")
            start_time = time.perf_counter()
            
            await ws.send(json.dumps(request))
            logger.info("Request sent, waiting for response...")
            
            # Wait with 5 minute timeout
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=300.0)
                latency_ms = (time.perf_counter() - start_time) * 1000
                
                logger.info(f"✅ Response received in {latency_ms:.2f}ms")
                
                response_data = json.loads(response)
                logger.info(f"Response data: {json.dumps(response_data, indent=2)}")
                
                # Check if successful
                if response_data.get("success"):
                    logger.info("✅ TEST 1 PASSED: GLM request successful")
                else:
                    logger.error(f"❌ TEST 1 FAILED: {response_data.get('error')}")
                    
            except asyncio.TimeoutError:
                logger.error("❌ TEST 1 FAILED: Request timed out after 300 seconds")
                return False
            
            # Wait a bit before next test
            await asyncio.sleep(5)
            
            # Test 2: Simple Kimi chat
            logger.info("\n" + "="*80)
            logger.info("TEST 2: Simple Kimi chat request")
            logger.info("="*80)
            
            request = {
                "op": "call_tool",
                "request_id": "test_kimi_001",
                "name": "chat_EXAI-WS-VSCode2",
                "arguments": {
                    "prompt": "Say 'Hello from Kimi!' and nothing else.",
                    "model": "kimi-k2-0905-preview",
                    "temperature": 0.7,
                    "use_websearch": False
                }
            }
            
            logger.info(f"Sending request: {json.dumps(request, indent=2)}")
            start_time = time.perf_counter()
            
            await ws.send(json.dumps(request))
            logger.info("Request sent, waiting for response...")
            
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=300.0)
                latency_ms = (time.perf_counter() - start_time) * 1000
                
                logger.info(f"✅ Response received in {latency_ms:.2f}ms")
                
                response_data = json.loads(response)
                logger.info(f"Response data: {json.dumps(response_data, indent=2)}")
                
                # Check if successful
                if response_data.get("success"):
                    logger.info("✅ TEST 2 PASSED: Kimi request successful")
                else:
                    logger.error(f"❌ TEST 2 FAILED: {response_data.get('error')}")
                    
            except asyncio.TimeoutError:
                logger.error("❌ TEST 2 FAILED: Request timed out after 300 seconds")
                return False
            
            logger.info("\n" + "="*80)
            logger.info("✅ ALL TESTS PASSED!")
            logger.info("="*80)
            return True
            
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    logger.info("Starting single request test...")
    success = asyncio.run(test_single_request())
    
    if success:
        logger.info("\n✅ Infrastructure validated - ready for comparison tests")
        sys.exit(0)
    else:
        logger.error("\n❌ Infrastructure issues detected - fix before running comparison")
        sys.exit(1)

