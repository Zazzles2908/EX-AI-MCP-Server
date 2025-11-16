"""
OpenRouter Model Registry for backward compatibility.

This module provides the OpenRouterModelRegistry class that was expected
by the tool infrastructure but doesn't actually exist.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class OpenRouterModelRegistry:
    """
    Mock OpenRouter Model Registry for backward compatibility.
    
    This provides the interface that the tool infrastructure expects
    without requiring actual OpenRouter integration.
    """
    
    def __init__(self):
        """Initialize the mock registry."""
        logger.warning("OpenRouterModelRegistry is a mock implementation for backward compatibility")
        self._models = {}
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Name of the model to look up
            
        Returns:
            Model information dictionary or None if not found
        """
        # Return basic model info for common models
        common_models = {
            'gpt-3.5-turbo': {'provider': 'openai', 'type': 'chat'},
            'gpt-4': {'provider': 'openai', 'type': 'chat'},
            'claude-3-haiku': {'provider': 'anthropic', 'type': 'chat'},
            'claude-3-sonnet': {'provider': 'anthropic', 'type': 'chat'},
            'glm-4': {'provider': 'glm', 'type': 'chat'},
        }
        
        return common_models.get(model_name)
    
    def list_models(self) -> List[str]:
        """
        List all available models.
        
        Returns:
            List of model names
        """
        return ['gpt-3.5-turbo', 'gpt-4', 'claude-3-haiku', 'claude-3-sonnet', 'glm-4']
    
    def is_model_available(self, model_name: str) -> bool:
        """
        Check if a model is available.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if the model is available, False otherwise
        """
        return model_name in self.list_models()