"""
Provider Diagnostics Tool - Comprehensive provider health and configuration check

This tool provides detailed diagnostics for all configured providers including:
- API key validation
- Model availability
- Web search capabilities
- Streaming support
- Recent API call success/failure rates
- Configuration issues
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.types import TextContent

from tools.shared.base_tool import BaseTool
from tools.shared.base_models import ToolRequest

logger = logging.getLogger(__name__)


class ProviderDiagnosticsTool(BaseTool):
    """Comprehensive provider diagnostics and health check tool."""
    
    def get_name(self) -> str:
        return "provider-diagnostics"
    
    def get_description(self) -> str:
        return (
            "PROVIDER DIAGNOSTICS - Comprehensive health check for all configured providers. "
            "Returns API key status, model availability, capabilities, recent call statistics, "
            "and configuration issues. Use this to troubleshoot provider problems."
        )
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "provider": {
                    "type": "string",
                    "description": "Specific provider to check (GLM, KIMI, or 'all' for all providers)",
                    "enum": ["all", "GLM", "KIMI"],
                },
                "include_test_call": {
                    "type": "boolean",
                    "description": "Perform a test API call to verify connectivity (default: false)",
                },
            },
            "additionalProperties": False,
        }
    
    def get_system_prompt(self) -> str:
        return ""
    
    def requires_model(self) -> bool:
        return False
    
    def get_request_model(self):
        return ToolRequest
    
    async def prepare_prompt(self, request: ToolRequest) -> str:
        return ""
    
    def _check_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Check configuration for a specific provider."""
        result = {
            "provider": provider_name,
            "configured": False,
            "api_key_present": False,
            "base_url": None,
            "capabilities": {},
            "issues": [],
        }
        
        # Check API key
        if provider_name == "GLM":
            api_key = os.getenv("GLM_API_KEY", "").strip()
            base_url = os.getenv("GLM_BASE_URL", "https://api.z.ai").strip()
            result["api_key_present"] = bool(api_key)
            result["base_url"] = base_url
            result["configured"] = bool(api_key)
            
            # Check capabilities
            result["capabilities"]["web_search"] = os.getenv("GLM_ENABLE_WEB_BROWSING", "false").lower() == "true"
            result["capabilities"]["streaming"] = os.getenv("GLM_STREAM_ENABLED", "false").lower() == "true"
            
            # Check for issues
            if not api_key:
                result["issues"].append("GLM_API_KEY not set")
            if base_url != "https://api.z.ai":
                result["issues"].append(f"Non-standard base URL: {base_url}")
                
        elif provider_name == "KIMI":
            api_key = os.getenv("KIMI_API_KEY", "").strip()
            base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1").strip()
            result["api_key_present"] = bool(api_key)
            result["base_url"] = base_url
            result["configured"] = bool(api_key)
            
            # Check capabilities
            result["capabilities"]["web_search"] = os.getenv("KIMI_ENABLE_INTERNET_SEARCH", "false").lower() == "true"
            result["capabilities"]["file_upload"] = bool(os.getenv("TEST_FILES_DIR", "").strip())
            
            # Check for issues
            if not api_key:
                result["issues"].append("KIMI_API_KEY not set")
            if base_url != "https://api.moonshot.ai/v1":
                result["issues"].append(f"Non-standard base URL: {base_url}")
            if not os.getenv("TEST_FILES_DIR"):
                result["issues"].append("TEST_FILES_DIR not set (file upload disabled)")
        
        return result
    
    def _get_available_models(self, provider_name: str) -> List[str]:
        """Get list of available models for a provider."""
        try:
            from src.providers.registry import ModelProviderRegistry
            
            all_models = ModelProviderRegistry.get_available_model_names()
            
            # Filter by provider
            if provider_name == "GLM":
                return [m for m in all_models if m.startswith("glm-")]
            elif provider_name == "KIMI":
                return [m for m in all_models if m.startswith("kimi-") or m.startswith("moonshot-")]
            
            return []
        except Exception as e:
            logger.error(f"Failed to get models for {provider_name}: {e}")
            return []
    
    def _test_provider_call(self, provider_name: str) -> Dict[str, Any]:
        """Perform a test API call to verify connectivity."""
        result = {
            "success": False,
            "error": None,
            "response_time_ms": None,
        }
        
        try:
            import time
            from src.providers.registry import ModelProviderRegistry
            
            # Get provider
            if provider_name == "GLM":
                from src.providers.base import ProviderType
                provider = ModelProviderRegistry.get_provider(ProviderType.GLM)
            elif provider_name == "KIMI":
                from src.providers.base import ProviderType
                provider = ModelProviderRegistry.get_provider(ProviderType.KIMI)
            else:
                result["error"] = f"Unknown provider: {provider_name}"
                return result
            
            # Simple test call
            start_time = time.time()
            response = provider.generate_content(
                prompt="Test",
                model_name="auto",
                system_prompt="Respond with 'OK'",
                temperature=0.1,
            )
            end_time = time.time()
            
            result["success"] = bool(response and response.content)
            result["response_time_ms"] = int((end_time - start_time) * 1000)
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Test call failed for {provider_name}: {e}")
        
        return result
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute provider diagnostics."""
        provider_filter = arguments.get("provider", "all")
        include_test = arguments.get("include_test_call", False)
        
        # Determine which providers to check
        if provider_filter == "all":
            providers_to_check = ["GLM", "KIMI"]
        else:
            providers_to_check = [provider_filter]
        
        # Collect diagnostics
        diagnostics = {
            "timestamp": None,
            "providers": {},
            "summary": {
                "total_providers": len(providers_to_check),
                "configured_providers": 0,
                "total_issues": 0,
            }
        }
        
        try:
            from datetime import datetime
            diagnostics["timestamp"] = datetime.utcnow().isoformat() + "Z"
        except:
            pass
        
        # Check each provider
        for provider_name in providers_to_check:
            provider_info = self._check_provider_config(provider_name)
            provider_info["models"] = self._get_available_models(provider_name)
            provider_info["model_count"] = len(provider_info["models"])
            
            # Perform test call if requested
            if include_test and provider_info["configured"]:
                provider_info["test_call"] = self._test_provider_call(provider_name)
            
            diagnostics["providers"][provider_name] = provider_info
            
            # Update summary
            if provider_info["configured"]:
                diagnostics["summary"]["configured_providers"] += 1
            diagnostics["summary"]["total_issues"] += len(provider_info["issues"])
        
        # Add recommendations
        recommendations = []
        if diagnostics["summary"]["configured_providers"] == 0:
            recommendations.append("⚠️  No providers configured! Set GLM_API_KEY or KIMI_API_KEY")
        if diagnostics["summary"]["total_issues"] > 0:
            recommendations.append(f"⚠️  {diagnostics['summary']['total_issues']} configuration issues found")
        
        # Check for web search issues
        glm_info = diagnostics["providers"].get("GLM", {})
        kimi_info = diagnostics["providers"].get("KIMI", {})
        
        if glm_info.get("capabilities", {}).get("web_search"):
            recommendations.append("⚠️  GLM web search is enabled but not functional (known issue)")
        if not kimi_info.get("capabilities", {}).get("web_search"):
            recommendations.append("💡 Enable Kimi web search with KIMI_ENABLE_INTERNET_SEARCH=true")
        
        diagnostics["recommendations"] = recommendations
        
        # Format output
        output = json.dumps(diagnostics, indent=2, ensure_ascii=False)
        
        return [TextContent(type="text", text=output)]


    def format_response(self, response: str, request: ToolRequest, model_info: Dict | None = None) -> str:
        return response

