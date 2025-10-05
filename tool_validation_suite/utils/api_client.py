"""
API Client - Unified client for Kimi and GLM APIs

This module provides a unified interface for calling Kimi and GLM APIs
with automatic feature detection, cost tracking, and prompt counting.

Features:
- Unified interface for both providers
- Automatic web search activation
- File upload support
- Thinking mode support (Kimi only)
- Tool use support
- Cost tracking
- Prompt counting
- Request/response logging

Created: 2025-10-05
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

from .prompt_counter import PromptCounter

# Load environment variables
load_dotenv(".env.testing")

logger = logging.getLogger(__name__)


class APIClient:
    """
    Unified API client for Kimi and GLM providers.
    
    Handles:
    - API calls to both providers
    - Feature activation (web search, file upload, thinking mode, tools)
    - Cost tracking
    - Prompt counting
    - Request/response logging
    """
    
    def __init__(self, prompt_counter: Optional[PromptCounter] = None):
        """Initialize the API client."""
        # API configuration
        self.kimi_api_key = os.getenv("KIMI_API_KEY")
        self.kimi_base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1")
        
        self.glm_api_key = os.getenv("GLM_API_KEY")
        self.glm_base_url = os.getenv("GLM_BASE_URL", "https://api.z.ai/api/paas/v4")
        
        # Prompt counter
        self.prompt_counter = prompt_counter or PromptCounter()
        
        # Logging configuration
        self.save_requests = os.getenv("SAVE_API_REQUESTS", "true").lower() == "true"
        self.save_responses = os.getenv("SAVE_API_RESPONSES", "true").lower() == "true"
        self.api_debug_dir = Path(os.getenv("API_DEBUG_DIR", "./tool_validation_suite/results/latest/api_responses"))
        
        # Create debug directories
        if self.save_requests or self.save_responses:
            (self.api_debug_dir / "kimi").mkdir(parents=True, exist_ok=True)
            (self.api_debug_dir / "glm").mkdir(parents=True, exist_ok=True)
        
        logger.info("API client initialized")
    
    def call_kimi(
        self,
        model: str,
        messages: List[Dict[str, str]],
        tool_name: str = "unknown",
        variation: str = "unknown",
        enable_search: bool = False,
        thinking_mode: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call Kimi API.
        
        Args:
            model: Model name (e.g., "kimi-k2-0905-preview")
            messages: List of message dictionaries
            tool_name: Name of tool being tested
            variation: Test variation name
            enable_search: Enable web search
            thinking_mode: Thinking mode level (basic/deep/expert)
            tools: Tool definitions for tool use
            **kwargs: Additional parameters
        
        Returns:
            API response dictionary
        """
        url = f"{self.kimi_base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.kimi_api_key}"
        }
        
        # Build payload
        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        
        # Add features
        if enable_search:
            payload["enable_search"] = True
        
        if thinking_mode:
            payload["thinking_mode"] = thinking_mode
        
        if tools:
            payload["tools"] = tools
        
        # Save request
        if self.save_requests:
            self._save_request("kimi", tool_name, variation, payload)
        
        # Make API call
        start_time = time.time()
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=int(os.getenv("TEST_TIMEOUT_SECS", "300"))
            )
            response.raise_for_status()
            
            result = response.json()
            duration = time.time() - start_time
            
            # Extract token usage
            usage = result.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            
            # Track features
            features = {
                "web_search": enable_search,
                "thinking_mode": thinking_mode is not None,
                "thinking_mode_level": thinking_mode,
                "tool_use": tools is not None
            }
            
            # Record prompt
            self.prompt_counter.record_prompt(
                provider="kimi",
                model=model,
                tool_name=tool_name,
                variation=variation,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                features=features
            )
            
            # Save response
            if self.save_responses:
                self._save_response("kimi", tool_name, variation, result)
            
            # Add metadata
            result["_metadata"] = {
                "provider": "kimi",
                "model": model,
                "duration_secs": duration,
                "features": features,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens
                }
            }
            
            logger.info(f"Kimi API call successful: {model} ({duration:.2f}s, {input_tokens + output_tokens} tokens)")
            
            return result
        
        except Exception as e:
            logger.error(f"Kimi API call failed: {e}")
            raise
    
    def call_glm(
        self,
        model: str,
        messages: List[Dict[str, str]],
        tool_name: str = "unknown",
        variation: str = "unknown",
        enable_search: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call GLM API.

        Args:
            model: Model name (e.g., "glm-4.5-flash", "glm-4.6")
            messages: List of message dictionaries
            tool_name: Name of tool being tested
            variation: Test variation name
            enable_search: Enable web search
            tools: Tool definitions for tool use
            **kwargs: Additional parameters
        
        Returns:
            API response dictionary
        """
        url = f"{self.glm_base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.glm_api_key}"
        }
        
        # Build payload
        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        
        # Add web search tool if enabled
        if enable_search:
            if tools is None:
                tools = []
            tools.append({"type": "web_search"})
        
        if tools:
            payload["tools"] = tools
        
        # Save request
        if self.save_requests:
            self._save_request("glm", tool_name, variation, payload)
        
        # Make API call
        start_time = time.time()
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=int(os.getenv("TEST_TIMEOUT_SECS", "300"))
            )
            response.raise_for_status()
            
            result = response.json()
            duration = time.time() - start_time
            
            # Extract token usage
            usage = result.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            
            # Track features
            features = {
                "web_search": enable_search,
                "tool_use": tools is not None
            }
            
            # Record prompt
            self.prompt_counter.record_prompt(
                provider="glm",
                model=model,
                tool_name=tool_name,
                variation=variation,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                features=features
            )
            
            # Save response
            if self.save_responses:
                self._save_response("glm", tool_name, variation, result)
            
            # Add metadata
            result["_metadata"] = {
                "provider": "glm",
                "model": model,
                "duration_secs": duration,
                "features": features,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens
                }
            }
            
            logger.info(f"GLM API call successful: {model} ({duration:.2f}s, {input_tokens + output_tokens} tokens)")
            
            return result
        
        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            raise
    
    def _save_request(self, provider: str, tool_name: str, variation: str, payload: Dict[str, Any]):
        """Save API request to file."""
        try:
            filename = f"{tool_name}_{variation}_request.json"
            filepath = self.api_debug_dir / provider / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved request: {filepath}")
        
        except Exception as e:
            logger.error(f"Failed to save request: {e}")
    
    def _save_response(self, provider: str, tool_name: str, variation: str, response: Dict[str, Any]):
        """Save API response to file."""
        try:
            filename = f"{tool_name}_{variation}_response.json"
            filepath = self.api_debug_dir / provider / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(response, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved response: {filepath}")
        
        except Exception as e:
            logger.error(f"Failed to save response: {e}")


# Example usage
if __name__ == "__main__":
    client = APIClient()
    
    # Test Kimi API with web search and thinking mode
    result = client.call_kimi(
        model="kimi-k2-0905-preview",
        messages=[{"role": "user", "content": "What's the latest AI news?"}],
        tool_name="chat",
        variation="web_search",
        enable_search=True,
        thinking_mode="deep"
    )
    
    print(json.dumps(result.get("_metadata"), indent=2))
    
    # Test GLM API with web search
    result = client.call_glm(
        model="glm-4.5-flash",
        messages=[{"role": "user", "content": "What's the latest AI news?"}],
        tool_name="chat",
        variation="web_search",
        enable_search=True
    )
    
    print(json.dumps(result.get("_metadata"), indent=2))

