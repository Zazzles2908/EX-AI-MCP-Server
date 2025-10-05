"""
MCP Client - Call EX-AI MCP Server tools through daemon

This module provides a client for calling MCP server tools through
the WebSocket daemon, testing the actual server implementation.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import websocket
from dotenv import load_dotenv

# Add parent directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils.prompt_counter import PromptCounter
else:
    from .prompt_counter import PromptCounter

# Load environment variables
load_dotenv("tool_validation_suite/.env.testing")
load_dotenv(".env.testing")
load_dotenv(".env")

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP client for calling server tools through WebSocket daemon.
    
    This client connects to the EX-AI MCP Server daemon and calls
    tools through the MCP protocol, testing the actual server implementation.
    """
    
    def __init__(self, prompt_counter: Optional[PromptCounter] = None):
        """Initialize the MCP client."""
        # WebSocket configuration
        self.ws_host = os.getenv("EXAI_WS_HOST", "127.0.0.1")
        self.ws_port = int(os.getenv("EXAI_WS_PORT", "8765"))
        self.ws_url = f"ws://{self.ws_host}:{self.ws_port}"
        
        # Prompt counter
        self.prompt_counter = prompt_counter or PromptCounter()
        
        # Logging configuration
        self.save_requests = os.getenv("SAVE_API_REQUESTS", "true").lower() == "true"
        self.save_responses = os.getenv("SAVE_API_RESPONSES", "true").lower() == "true"
        self.api_debug_dir = Path(os.getenv("API_DEBUG_DIR", "./tool_validation_suite/results/latest/api_responses"))
        
        # Create debug directories
        if self.save_requests or self.save_responses:
            (self.api_debug_dir / "mcp").mkdir(parents=True, exist_ok=True)
        
        logger.info(f"MCP client initialized (daemon: {self.ws_url})")
    
    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        test_name: str = "unknown",
        variation: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Call an MCP tool through the daemon.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            test_name: Name of test being run
            variation: Test variation name

        Returns:
            Tool response dictionary
        """
        # Build tool call request
        request_id = f"{test_name}_{variation}_{int(time.time() * 1000)}"
        tool_request = {
            "op": "call_tool",
            "request_id": request_id,
            "name": tool_name,
            "arguments": arguments
        }

        # Save request
        if self.save_requests:
            self._save_request(tool_name, test_name, variation, tool_request)

        # Make WebSocket call
        start_time = time.time()

        try:
            # Connect to daemon
            ws = websocket.create_connection(
                self.ws_url,
                timeout=int(os.getenv("TEST_TIMEOUT_SECS", "300"))
            )

            # Send hello handshake
            session_id = f"test_{test_name}_{int(time.time())}"
            hello_msg = {
                "op": "hello",
                "session_id": session_id,
                "token": os.getenv("EXAI_WS_TOKEN", "")
            }
            ws.send(json.dumps(hello_msg))

            # Wait for hello_ack
            hello_ack_str = ws.recv()
            hello_ack = json.loads(hello_ack_str)

            if not hello_ack.get("ok"):
                error = hello_ack.get("error", "unknown")
                raise Exception(f"Hello handshake failed: {error}")

            logger.debug(f"Hello handshake successful, session: {hello_ack.get('session_id')}")

            # Send tool call request
            ws.send(json.dumps(tool_request))

            # Receive response (may get ack and progress messages first)
            while True:
                response_str = ws.recv()
                logger.debug(f"Raw response: {response_str[:500]}")

                # Parse response
                try:
                    response = json.loads(response_str)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.error(f"Response was: {response_str[:500]}")
                    raise Exception(f"Invalid JSON response: {response_str[:200]}")

                op = response.get("op")

                # Check if this is the final response
                if op == "call_tool_res" and response.get("request_id") == request_id:
                    break
                elif op == "call_tool_ack":
                    # Acknowledgment that tool call was received
                    logger.debug(f"Tool call acknowledged")
                    continue
                elif op == "progress":
                    # Progress message, keep waiting
                    logger.debug(f"Progress: {response.get('message', 'working...')}")
                    continue
                else:
                    logger.debug(f"Received message type: {op}")

            # Close connection
            ws.close()

            duration = time.time() - start_time

            # Save response
            if self.save_responses:
                self._save_response(tool_name, test_name, variation, response)

            # Check for error
            if isinstance(response, dict) and "error" in response:
                error_msg = response["error"] if isinstance(response["error"], str) else str(response["error"])
                logger.error(f"MCP tool call failed: {tool_name} - {error_msg}")
                logger.error(f"Full response: {json.dumps(response, indent=2)}")
                raise Exception(f"MCP error: {error_msg}")
            
            # Extract outputs from response
            # Response format: {"op": "call_tool_res", "request_id": "...", "outputs": [...]}
            outputs = response.get("outputs", [])

            # Build result dictionary
            result = {
                "outputs": outputs,
                "request_id": response.get("request_id"),
                "_metadata": {
                    "provider": "mcp",
                    "tool": tool_name,
                    "duration_secs": duration,
                    "daemon_url": self.ws_url
                }
            }

            # Record prompt (estimate tokens based on content length)
            estimated_output_tokens = 0
            if isinstance(outputs, list) and len(outputs) > 0:
                for output in outputs:
                    if isinstance(output, dict):
                        text = output.get("text", "")
                        estimated_output_tokens += len(text.split()) * 1.3  # Rough estimate
            
            self.prompt_counter.record_prompt(
                provider="mcp",
                model="server",
                tool_name=tool_name,
                variation=variation,
                input_tokens=0,  # MCP doesn't expose token counts
                output_tokens=int(estimated_output_tokens),
                features={}
            )
            
            logger.info(f"MCP tool call successful: {tool_name} ({duration:.2f}s)")
            
            return result
        
        except Exception as e:
            logger.error(f"MCP tool call failed: {e}")
            raise
    
    def _save_request(self, tool_name: str, test_name: str, variation: str, request: Dict[str, Any]):
        """Save request to file."""
        timestamp = int(time.time() * 1000)
        filename = f"{tool_name}_{test_name}_{variation}_{timestamp}_request.json"
        filepath = self.api_debug_dir / "mcp" / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(request, f, indent=2, ensure_ascii=False)
    
    def _save_response(self, tool_name: str, test_name: str, variation: str, response: Dict[str, Any]):
        """Save response to file."""
        timestamp = int(time.time() * 1000)
        filename = f"{tool_name}_{test_name}_{variation}_{timestamp}_response.json"
        filepath = self.api_debug_dir / "mcp" / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=2, ensure_ascii=False)


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test MCP client
    client = MCPClient()
    
    try:
        # Call chat tool
        result = client.call_tool(
            tool_name="chat",
            arguments={
                "prompt": "Say hello in 5 words",
                "model": "glm-4.5-flash"
            },
            test_name="mcp_client_test",
            variation="basic"
        )
        
        print("\n✅ MCP tool call successful!")
        print(f"Result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"\n❌ MCP tool call failed: {e}")

