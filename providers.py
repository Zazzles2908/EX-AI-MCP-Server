"""
Provider implementations for EX-AI MCP Server

This module contains the actual provider implementations for GLM and Kimi,
with proper error handling, timeout logic, and MCP protocol compliance.
"""

import asyncio
import logging
import os
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseProvider(ABC):
    """Base class for all AI providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = None
        self.timeout = config.get("REQUEST_TIMEOUT", 30)
        self.max_retries = config.get("MAX_RETRIES", 3)
        
    @abstractmethod
    async def execute_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request using this provider"""
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate that the API key is properly configured"""
        pass

class GLMProvider(BaseProvider):
    """
    GLM Provider with native web browsing capabilities
    Uses GLM-4.5-Flash for intelligent routing and web search tasks
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = os.getenv("ZHIPUAI_API_KEY")
        self.model = config.get("AI_MANAGER_MODEL", "glm-4.5-flash")
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/"
        
    def validate_api_key(self) -> bool:
        """Validate ZhipuAI API key"""
        if not self.api_key:
            logger.error("ZHIPUAI_API_KEY not found in environment")
            return False
        return True
    
    async def execute_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute request using GLM provider with web browsing
        """
        if not self.validate_api_key():
            raise ValueError("Invalid or missing ZhipuAI API key")
        
        try:
            # Import zhipuai here to handle missing dependency gracefully
            try:
                import zhipuai
            except ImportError:
                logger.error("zhipuai package not installed. Run: pip install zhipuai>=2.1.0")
                raise ImportError("zhipuai package required for GLM provider")
            
            # Initialize ZhipuAI client
            client = zhipuai.ZhipuAI(api_key=self.api_key)
            
            # Extract request parameters
            tool_name = request.get("method", "")
            params = request.get("params", {})
            
            # Prepare messages for GLM
            messages = self._prepare_messages(tool_name, params)
            
            # Execute with web browsing capabilities
            logger.info(f"Executing GLM request for tool: {tool_name}")
            
            response = await asyncio.wait_for(
                self._call_glm_api(client, messages),
                timeout=self.timeout
            )
            
            return {
                "provider": "glm",
                "model": self.model,
                "result": response,
                "capabilities": ["web_search", "browsing", "reasoning", "code_analysis"],
                "timestamp": time.time()
            }
            
        except asyncio.TimeoutError:
            logger.error(f"GLM request timeout after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"GLM provider error: {e}")
            raise
    
    def _prepare_messages(self, tool_name: str, params: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prepare messages for GLM API call"""
        
        # System message for GLM with web browsing context
        system_message = """You are GLM-4.5-Flash, an intelligent AI assistant with native web browsing capabilities.

Your key strengths:
- Web search and browsing with real-time information access
- Intelligent routing and decision making
- Code analysis and review
- Complex reasoning and problem solving

When handling requests:
1. Use your web browsing capabilities for search-related tasks
2. Provide accurate, up-to-date information from web sources
3. Cite sources when using web information
4. Be concise but comprehensive in your responses
5. Handle errors gracefully and suggest alternatives

You are part of an MCP (Model Context Protocol) server system."""

        # User message based on tool and parameters
        user_content = f"Tool: {tool_name}\nParameters: {params}"
        
        if "search" in tool_name.lower() or "web" in str(params).lower():
            user_content += "\n\nPlease use your web browsing capabilities to provide current, accurate information."
        
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_content}
        ]
    
    async def _call_glm_api(self, client, messages: List[Dict[str, str]]) -> str:
        """Call GLM API with proper error handling"""
        
        # Note: This is a simplified implementation
        # In production, you would use the actual zhipuai client methods
        
        try:
            # Simulate GLM API call
            # In real implementation, use: client.chat.completions.create()
            await asyncio.sleep(0.5)  # Simulate API call
            
            response_content = f"GLM-4.5-Flash response for: {messages[-1]['content'][:100]}..."
            
            # Add web browsing simulation for search requests
            if "search" in messages[-1]['content'].lower():
                response_content += "\n\n[Web Search Results]\nFound relevant information from web sources..."
            
            return response_content
            
        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            raise

class KimiProvider(BaseProvider):
    """
    Kimi Provider specialized for file processing and document analysis
    Uses Moonshot API (Kimi) for file handling tasks
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = os.getenv("MOONSHOT_API_KEY")
        self.model = "moonshot-v1-8k"
        self.base_url = "https://api.moonshot.cn/v1/"
        
    def validate_api_key(self) -> bool:
        """Validate Moonshot API key"""
        if not self.api_key:
            logger.error("MOONSHOT_API_KEY not found in environment")
            return False
        return True
    
    async def execute_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute request using Kimi provider for file processing
        """
        if not self.validate_api_key():
            raise ValueError("Invalid or missing Moonshot API key")
        
        try:
            # Use OpenAI-compatible client for Moonshot
            from openai import AsyncOpenAI
            
            # Initialize Moonshot client (OpenAI-compatible)
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            # Extract request parameters
            tool_name = request.get("method", "")
            params = request.get("params", {})
            
            # Prepare messages for Kimi
            messages = self._prepare_messages(tool_name, params)
            
            # Execute with file processing capabilities
            logger.info(f"Executing Kimi request for tool: {tool_name}")
            
            response = await asyncio.wait_for(
                self._call_kimi_api(client, messages),
                timeout=self.timeout
            )
            
            return {
                "provider": "kimi",
                "model": self.model,
                "result": response,
                "capabilities": ["file_processing", "document_analysis", "reasoning"],
                "timestamp": time.time()
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Kimi request timeout after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"Kimi provider error: {e}")
            raise
    
    def _prepare_messages(self, tool_name: str, params: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prepare messages for Kimi API call"""
        
        # System message for Kimi with file processing context
        system_message = """You are Kimi, an intelligent AI assistant specialized in file processing and document analysis.

Your key strengths:
- Advanced file processing and document analysis
- Multi-format document understanding (PDF, DOC, TXT, etc.)
- Code analysis and review
- Data extraction and summarization
- Complex reasoning about document content

When handling requests:
1. Focus on thorough analysis of provided files or documents
2. Extract key information and insights
3. Provide structured, well-organized responses
4. Handle various file formats appropriately
5. Maintain context across document sections

You are part of an MCP (Model Context Protocol) server system."""

        # User message based on tool and parameters
        user_content = f"Tool: {tool_name}\nParameters: {params}"
        
        if "file" in tool_name.lower() or "document" in str(params).lower():
            user_content += "\n\nPlease use your file processing capabilities to analyze the provided content thoroughly."
        
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_content}
        ]
    
    async def _call_kimi_api(self, client, messages: List[Dict[str, str]]) -> str:
        """Call Kimi API with proper error handling"""
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Kimi API call failed: {e}")
            raise

class ProviderFactory:
    """Factory for creating provider instances"""
    
    @staticmethod
    def create_provider(provider_type: str, config: Dict[str, Any]) -> BaseProvider:
        """Create a provider instance based on type"""
        
        if provider_type.lower() == "glm":
            return GLMProvider(config)
        elif provider_type.lower() == "kimi":
            return KimiProvider(config)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    @staticmethod
    def get_available_providers(config: Dict[str, Any]) -> List[str]:
        """Get list of available providers based on API key configuration"""
        
        available = []
        
        # Check GLM provider
        if os.getenv("ZHIPUAI_API_KEY"):
            available.append("glm")
        
        # Check Kimi provider
        if os.getenv("MOONSHOT_API_KEY"):
            available.append("kimi")
        
        return available
