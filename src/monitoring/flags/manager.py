"""
Feature Flag Manager

Centralized management of monitoring system feature flags.
Loads flags from environment, validates them, and provides access interface.
"""

import logging
import os
from typing import Any, Dict, Optional
from threading import Lock

from .schema import FlagSchema, FlagDefinition, FlagType

logger = logging.getLogger(__name__)


class FlagManager:
    """
    Manages feature flags for the monitoring system.
    
    Thread-safe flag access with validation and defaults.
    """
    
    def __init__(self):
        """Initialize flag manager"""
        self._flags: Dict[str, Any] = {}
        self._lock = Lock()
        self._load_flags()
        self._log_configuration()
    
    def _load_flags(self) -> None:
        """Load and validate all flags from environment"""
        all_flags = FlagSchema.get_all_flags()
        
        for flag_name, flag_def in all_flags.items():
            try:
                # Get value from environment or use default
                env_value = os.getenv(flag_def.env_var)
                
                if env_value is None:
                    value = flag_def.default
                else:
                    # Convert string to appropriate type
                    value = self._convert_value(env_value, flag_def.flag_type)
                
                # Validate
                if not flag_def.validate(value):
                    logger.warning(
                        f"Invalid flag value for {flag_name}: {value}, "
                        f"using default: {flag_def.default}"
                    )
                    value = flag_def.default
                
                self._flags[flag_name] = value
                
            except Exception as e:
                logger.error(f"Error loading flag {flag_name}: {e}, using default")
                flag_def = FlagSchema.get_flag(flag_name)
                if flag_def:
                    self._flags[flag_name] = flag_def.default
    
    def _convert_value(self, value: str, flag_type: FlagType) -> Any:
        """Convert string environment value to appropriate type"""
        if flag_type == FlagType.BOOL:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif flag_type == FlagType.INT:
            return int(value)
        elif flag_type == FlagType.FLOAT:
            return float(value)
        else:  # STRING
            return value
    
    def _log_configuration(self) -> None:
        """Log current flag configuration"""
        logger.info("=" * 60)
        logger.info("Feature Flags Configuration")
        logger.info("=" * 60)
        
        for flag_name, value in sorted(self._flags.items()):
            flag_def = FlagSchema.get_flag(flag_name)
            if flag_def:
                logger.info(f"  {flag_name}: {value} ({flag_def.description})")
        
        logger.info("=" * 60)
    
    def get(self, flag_name: str, default: Optional[Any] = None) -> Any:
        """
        Get flag value.
        
        Args:
            flag_name: Name of the flag
            default: Default value if flag not found
            
        Returns:
            Flag value or default
        """
        with self._lock:
            return self._flags.get(flag_name, default)
    
    def get_bool(self, flag_name: str, default: bool = False) -> bool:
        """Get boolean flag value"""
        value = self.get(flag_name)
        return value if isinstance(value, bool) else default
    
    def get_string(self, flag_name: str, default: str = '') -> str:
        """Get string flag value"""
        value = self.get(flag_name)
        return value if isinstance(value, str) else default
    
    def get_int(self, flag_name: str, default: int = 0) -> int:
        """Get integer flag value"""
        value = self.get(flag_name)
        return value if isinstance(value, int) else default
    
    def get_float(self, flag_name: str, default: float = 0.0) -> float:
        """Get float flag value"""
        value = self.get(flag_name)
        return value if isinstance(value, float) else default
    
    def get_all(self) -> Dict[str, Any]:
        """Get all flags"""
        with self._lock:
            return dict(self._flags)
    
    def set(self, flag_name: str, value: Any) -> bool:
        """
        Set flag value (for testing/runtime updates).
        
        Args:
            flag_name: Name of the flag
            value: New value
            
        Returns:
            True if set successfully, False if validation failed
        """
        flag_def = FlagSchema.get_flag(flag_name)
        if not flag_def:
            logger.warning(f"Unknown flag: {flag_name}")
            return False
        
        if not flag_def.validate(value):
            logger.warning(f"Invalid value for flag {flag_name}: {value}")
            return False
        
        with self._lock:
            self._flags[flag_name] = value
            logger.info(f"Flag updated: {flag_name} = {value}")
        
        return True
    
    def reset(self) -> None:
        """Reset all flags to defaults"""
        with self._lock:
            all_flags = FlagSchema.get_all_flags()
            self._flags = {
                name: flag_def.default
                for name, flag_def in all_flags.items()
            }
            logger.info("All flags reset to defaults")


# Global flag manager instance
_flag_manager: Optional[FlagManager] = None


def get_flag_manager() -> FlagManager:
    """Get or create global flag manager instance"""
    global _flag_manager
    if _flag_manager is None:
        _flag_manager = FlagManager()
    return _flag_manager

