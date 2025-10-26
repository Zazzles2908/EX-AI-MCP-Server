"""
Rollout Manager for Gradual Migration

Manages percentage-based rollout of the UnifiedFileManager with consistent
user-level routing and random sampling for request-level decisions.

Architecture: Canary Deployment with Consistent Hashing
Date: 2025-10-22
Reference: EXAI consultation (Continuation: 9222d725-b6cd-44f1-8406-274e5a3b3389)
"""

import hashlib
import random
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class RolloutManager:
    """
    Manages gradual rollout of unified file management implementation.
    
    This class determines whether a given request should use the new unified
    implementation or fall back to legacy handlers based on:
    - Global feature flags
    - Per-tool migration flags
    - Rollout percentages (0-100)
    - Consistent user-level routing (same user always gets same implementation)
    - Random sampling for request-level decisions
    
    Rollout Strategy:
    - 1%: Initial validation, monitor for errors
    - 10%: Expand to more users, gather performance data
    - 50%: Majority rollout, focus on edge cases
    - 100%: Full migration, decommission legacy
    """
    
    def __init__(self, config: Any):
        """
        Initialize the rollout manager.
        
        Args:
            config: Configuration object with rollout settings
        """
        self.config = config
        
        logger.info(
            "RolloutManager initialized",
            extra={
                "unified_enabled": config.ENABLE_UNIFIED_MANAGER,
                "kimi_rollout": getattr(config, "KIMI_ROLLOUT_PERCENTAGE", 0),
                "smart_handler_rollout": getattr(config, "SMART_HANDLER_ROLLOUT_PERCENTAGE", 0),
                "supabase_rollout": getattr(config, "SUPABASE_ROLLOUT_PERCENTAGE", 0)
            }
        )
    
    def should_use_unified(self, tool_name: str, user_id: Optional[str] = None) -> bool:
        """
        Determine if request should use unified implementation.
        
        This method implements the core rollout logic:
        1. Check if unified manager is globally enabled
        2. Get rollout percentage for the specific tool
        3. Use consistent hashing for user-level routing (if user_id provided)
        4. Use random sampling for request-level routing (if no user_id)
        
        Args:
            tool_name: Name of the tool/operation (e.g., 'kimi_upload', 'download')
            user_id: Optional user ID for consistent routing
            
        Returns:
            True if should use unified implementation, False for legacy
            
        Examples:
            >>> manager.should_use_unified('kimi_upload', 'user123')
            True  # User 123 is in the 10% rollout
            
            >>> manager.should_use_unified('kimi_upload', 'user456')
            False  # User 456 is not in the 10% rollout
            
            >>> manager.should_use_unified('download')
            True  # Random sampling returned True for this request
        """
        # Global kill switch
        if not self.config.ENABLE_UNIFIED_MANAGER:
            logger.debug(
                "Unified manager globally disabled",
                extra={"tool_name": tool_name}
            )
            return False
        
        # Get rollout percentage for this tool
        rollout_percentage = self._get_rollout_percentage(tool_name)
        
        if rollout_percentage == 0:
            logger.debug(
                f"Tool not in rollout (0%)",
                extra={"tool_name": tool_name}
            )
            return False
        
        if rollout_percentage == 100:
            logger.debug(
                f"Tool fully rolled out (100%)",
                extra={"tool_name": tool_name}
            )
            return True
        
        # Use consistent hashing for user-level rollout
        if user_id:
            use_unified = self._consistent_hash_decision(tool_name, user_id, rollout_percentage)
            logger.debug(
                f"User-level routing decision",
                extra={
                    "tool_name": tool_name,
                    "user_id": user_id,
                    "rollout_percentage": rollout_percentage,
                    "use_unified": use_unified
                }
            )
            return use_unified
        
        # Use random sampling for request-level rollout
        use_unified = self._random_sample_decision(rollout_percentage)
        logger.debug(
            f"Request-level routing decision",
            extra={
                "tool_name": tool_name,
                "rollout_percentage": rollout_percentage,
                "use_unified": use_unified
            }
        )
        return use_unified
    
    def _get_rollout_percentage(self, tool_name: str) -> int:
        """
        Get rollout percentage for a specific tool.
        
        Args:
            tool_name: Name of the tool (e.g., 'kimi_upload', 'smart_handler')
            
        Returns:
            Rollout percentage (0-100)
        """
        # Map tool names to config attributes
        tool_mapping = {
            "kimi_upload": "KIMI_ROLLOUT_PERCENTAGE",
            "kimi": "KIMI_ROLLOUT_PERCENTAGE",
            "smart_handler": "SMART_HANDLER_ROLLOUT_PERCENTAGE",
            "smart": "SMART_HANDLER_ROLLOUT_PERCENTAGE",
            "supabase": "SUPABASE_ROLLOUT_PERCENTAGE",
            "download": "KIMI_ROLLOUT_PERCENTAGE",  # Default to kimi for generic operations
            "delete": "KIMI_ROLLOUT_PERCENTAGE"
        }
        
        config_attr = tool_mapping.get(tool_name.lower(), "KIMI_ROLLOUT_PERCENTAGE")
        return getattr(self.config, config_attr, 0)
    
    def _consistent_hash_decision(
        self,
        tool_name: str,
        user_id: str,
        rollout_percentage: int
    ) -> bool:
        """
        Make routing decision using consistent hashing.
        
        This ensures the same user always gets the same implementation
        for a given tool, which is important for:
        - Consistent user experience
        - Easier debugging (user always in same group)
        - Gradual rollout without user confusion
        
        Args:
            tool_name: Name of the tool
            user_id: User identifier
            rollout_percentage: Target rollout percentage (0-100)
            
        Returns:
            True if user should use unified implementation
        """
        # Create a stable hash from tool_name + user_id
        hash_input = f"{tool_name}:{user_id}".encode('utf-8')
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
        
        # Map hash to 0-99 range and compare with rollout percentage
        bucket = hash_value % 100
        return bucket < rollout_percentage
    
    def _random_sample_decision(self, rollout_percentage: int) -> bool:
        """
        Make routing decision using random sampling.
        
        Used when no user_id is available. Each request is independently
        sampled, which means:
        - No consistency guarantees
        - Simpler implementation
        - Good for stateless operations
        
        Args:
            rollout_percentage: Target rollout percentage (0-100)
            
        Returns:
            True if request should use unified implementation
        """
        return random.random() < (rollout_percentage / 100.0)
    
    def get_rollout_status(self) -> dict:
        """
        Get current rollout status for all tools.
        
        Returns:
            Dictionary with rollout percentages for each tool
        """
        return {
            "unified_enabled": self.config.ENABLE_UNIFIED_MANAGER,
            "kimi_rollout": getattr(self.config, "KIMI_ROLLOUT_PERCENTAGE", 0),
            "smart_handler_rollout": getattr(self.config, "SMART_HANDLER_ROLLOUT_PERCENTAGE", 0),
            "supabase_rollout": getattr(self.config, "SUPABASE_ROLLOUT_PERCENTAGE", 0),
            "fallback_enabled": getattr(self.config, "ENABLE_FALLBACK_TO_LEGACY", True)
        }

