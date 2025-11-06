"""
Timeout Configuration

Centralized timeout management for EX-AI MCP Server.
This module provides all timeout values in one place for easy maintenance.

Groups timeouts by category:
- WebSocket timeouts
- Tool execution timeouts  
- API call timeouts
- Database timeouts
- File operation timeouts

Updated: 2025-11-06 - Extracted from 906 timeout operations across 116 files
"""

import os
from typing import Dict, Any


class TimeoutConfig:
    """Centralized timeout configuration"""
    
    # WebSocket Timeouts (in seconds)
    WEBSOCKET = {
        'connect': 30.0,           # Initial WebSocket connection
        'handshake': 10.0,         # WebSocket handshake
        'idle': 300.0,             # Idle connection timeout
        'heartbeat': 30.0,         # Heartbeat/ping interval
        'receive': 3600.0,         # Receive timeout for long connections
        'overall': 3600.0,         # Overall connection timeout
    }
    
    # Tool Execution Timeouts (in seconds)
    TOOL_EXECUTION = {
        'kimi_simple': 180.0,           # Simple Kimi tool execution
        'kimi_file': 300.0,             # Kimi file operation
        'kimi_download': 600.0,         # Kimi file download
        'glm_streaming': 300.0,         # GLM streaming operation
        'file_deduplication': 120.0,    # File deduplication
        'smart_file_query': 240.0,      # Smart file query
        'supabase_upload': 600.0,       # Supabase upload
        'supabase_download': 600.0,     # Supabase download
        'semaphore_acquire': 60.0,      # Semaphore acquire
        'workflow_expert': 180.0,       # Workflow expert analysis
    }
    
    # API Call Timeouts (in seconds)
    API_CALLS = {
        'kimi_chat': 180.0,         # Kimi chat completion
        'kimi_estimate': 5.0,       # Kimi estimate API
        'glm_chat': 120.0,          # GLM chat completion
        'openai_chat': 120.0,       # OpenAI chat completion
        'moonshot_chat': 180.0,     # Moonshot chat completion
        'adaptive_timeout': 180.0,  # Adaptive timeout engine
        'http_request': 30.0,       # Generic HTTP request
        'external_api': 60.0,       # External API call
    }
    
    # Database Timeouts (in seconds)
    DATABASE = {
        'supabase_query': 30.0,          # Supabase query execution
        'supabase_connection': 10.0,     # Supabase connection
        'redis_query': 5.0,              # Redis query
        'metrics_flush': 60.0,           # Metrics flush to database
        'auditor_save': 30.0,            # Save auditor observation
        'cache_lookup': 2.0,             # Cache lookup
        'cache_update': 5.0,             # Cache update
    }
    
    # File Operation Timeouts (in seconds)
    FILE_OPS = {
        'read_small': 10.0,         # Read small file (< 1MB)
        'read_medium': 30.0,        # Read medium file (1-10MB)
        'read_large': 60.0,         # Read large file (> 10MB)
        'write_small': 10.0,        # Write small file
        'write_large': 60.0,        # Write large file
        'copy': 30.0,               # File copy operation
        'delete': 10.0,             # File delete operation
        'hash_calculation': 30.0,   # File hash calculation
    }
    
    # Monitoring Timeouts (in seconds)
    MONITORING = {
        'health_check': 5.0,        # Health check
        'metrics_broadcast': 5.0,   # Metrics broadcast interval
        'cleanup': 300.0,           # Cleanup operation
        'session_cleanup': 86400.0, # Session cleanup (24 hours)
    }
    
    @classmethod
    def get_timeout(cls, category: str, key: str, default: float = None) -> float:
        """
        Get timeout value from configuration.
        
        Args:
            category: Timeout category (websocket, tool_execution, etc.)
            key: Timeout key within category
            default: Default value if not found
            
        Returns:
            Timeout value in seconds
        """
        category_map = {
            'websocket': cls.WEBSOCKET,
            'tool_execution': cls.TOOL_EXECUTION,
            'api_call': cls.API_CALLS,
            'api': cls.API_CALLS,
            'database': cls.DATABASE,
            'file': cls.FILE_OPS,
            'monitoring': cls.MONITORING,
        }
        
        if category.lower() in category_map:
            return category_map[category.lower()].get(key, default or 30.0)
        
        return default or 30.0
    
    @classmethod
    def get_all_timeouts(cls) -> Dict[str, Dict[str, float]]:
        """
        Get all timeout configurations.
        
        Returns:
            Dictionary with all timeout categories and values
        """
        return {
            'websocket': cls.WEBSOCKET,
            'tool_execution': cls.TOOL_EXECUTION,
            'api_call': cls.API_CALLS,
            'database': cls.DATABASE,
            'file_operation': cls.FILE_OPS,
            'monitoring': cls.MONITORING,
        }
    
    @classmethod
    def get_env_override(cls, category: str, key: str) -> float:
        """
        Get timeout with environment variable override.
        
        Environment variable format: EXAI_TIMEOUT_{CATEGORY}_{KEY}
        Example: EXAI_TIMEOUT_WEBSOCKET_CONNECT=60.0
        
        Args:
            category: Timeout category
            key: Timeout key
            
        Returns:
            Timeout value (env var if set, otherwise config value)
        """
        env_key = f"EXAI_TIMEOUT_{category.upper()}_{key.upper()}"
        env_value = os.getenv(env_key)
        
        if env_value:
            try:
                return float(env_value)
            except ValueError:
                pass
        
        return cls.get_timeout(category, key)
    
    @classmethod
    def validate_timeouts(cls) -> Dict[str, Any]:
        """
        Validate timeout configurations.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'timeouts': cls.get_all_timeouts(),
        }
        
        # Check for reasonable timeout values
        for category, timeouts in results['timeouts'].items():
            for key, value in timeouts.items():
                if value <= 0:
                    results['errors'].append(f"{category}.{key}: invalid value {value}")
                    results['valid'] = False
                elif value > 3600:  # > 1 hour
                    results['warnings'].append(f"{category}.{key}: very long timeout {value}s")
        
        return results


# Global instance for convenience
timeout_config = TimeoutConfig()

# Convenience functions for common timeouts
def get_websocket_timeout(timeout_type: str) -> float:
    """Get WebSocket timeout value"""
    return timeout_config.get_timeout('websocket', timeout_type)


def get_tool_timeout(tool_name: str) -> float:
    """Get tool execution timeout"""
    return timeout_config.get_timeout('tool_execution', tool_name)


def get_api_timeout(api_name: str) -> float:
    """Get API call timeout"""
    return timeout_config.get_timeout('api', api_name)


def get_file_timeout(operation: str) -> float:
    """Get file operation timeout"""
    return timeout_config.get_timeout('file', operation)


# Export commonly used timeouts
DEFAULT_TIMEOUT = 30.0
LONG_TIMEOUT = 300.0
SHORT_TIMEOUT = 5.0
