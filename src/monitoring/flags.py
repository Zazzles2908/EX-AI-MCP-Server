"""
Monitoring Flags - Stub Implementation
Provides flag manager singleton for monitoring endpoint
"""
import logging

logger = logging.getLogger(__name__)

class FlagManager:
    """Stub flag manager for feature flags"""
    
    def __init__(self):
        self.flags = {}
        logger.debug("[FLAG_MANAGER] Initialized")
    
    def is_enabled(self, flag_name):
        """Check if flag is enabled"""
        return self.flags.get(flag_name, False)

_flag_manager = None

def get_flag_manager():
    """Get flag manager singleton"""
    global _flag_manager
    if _flag_manager is None:
        _flag_manager = FlagManager()
    return _flag_manager

