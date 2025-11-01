"""
Centralized Supabase Connection Singleton
Date: 2025-11-01
EXAI Consultation ID: 63c00b70-364b-4351-bf6c-5a105e553dce

PHASE 1 FIX: Consolidate 4+ Supabase client initializations into 1 singleton
with proper connection pooling.

This replaces:
- src/storage/supabase_client.py (SupabaseStorageManager)
- src/daemon/warmup.py (_supabase_client)
- utils/monitoring/unified_collector.py (create_client)
- Multiple script-level create_client() calls
"""

import os
import logging
from typing import Optional
from supabase import create_client, Client
import threading

logger = logging.getLogger(__name__)

# ============================================================================
# SINGLETON PATTERN
# ============================================================================

_instance: Optional['SupabaseSingleton'] = None
_lock = threading.Lock()


class SupabaseSingleton:
    """
    Thread-safe singleton for Supabase client with connection pooling.
    
    Features:
    - Single connection pool shared across entire application
    - Thread-safe initialization
    - Lazy loading (only creates client when first accessed)
    - Automatic credential validation
    - Support for both service role and anon key
    
    Usage:
        # Get singleton instance
        supabase = SupabaseSingleton.get_instance()
        
        # Use client
        result = supabase.client.table('conversations').select('*').execute()
        
        # Get admin client (service role)
        admin_client = supabase.get_admin_client()
    """
    
    def __init__(self):
        """Initialize singleton (called only once)."""
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        # Validate credentials
        if not self.url:
            raise ValueError("SUPABASE_URL environment variable not set")
        
        if not self.service_key and not self.anon_key:
            raise ValueError("Either SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY must be set")
        
        # Initialize clients (lazy - only when accessed)
        self._client: Optional[Client] = None
        self._admin_client: Optional[Client] = None
        
        logger.info(f"[SUPABASE_SINGLETON] Initialized (URL: {self.url})")
    
    @property
    def client(self) -> Client:
        """
        Get Supabase client (uses anon key if available, otherwise service key).
        
        Returns:
            Supabase client with connection pooling
        """
        if self._client is None:
            key = self.anon_key or self.service_key
            self._client = create_client(self.url, key)
            logger.info("[SUPABASE_SINGLETON] Client initialized (anon/service key)")
        
        return self._client
    
    def get_admin_client(self) -> Client:
        """
        Get admin Supabase client (uses service role key).
        
        Returns:
            Supabase admin client with full permissions
            
        Raises:
            ValueError: If service role key not configured
        """
        if not self.service_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY not configured - cannot create admin client")
        
        if self._admin_client is None:
            self._admin_client = create_client(self.url, self.service_key)
            logger.info("[SUPABASE_SINGLETON] Admin client initialized (service role)")
        
        return self._admin_client
    
    @classmethod
    def get_instance(cls) -> 'SupabaseSingleton':
        """
        Get singleton instance (thread-safe).
        
        Returns:
            SupabaseSingleton instance
        """
        global _instance
        
        if _instance is None:
            with _lock:
                if _instance is None:
                    _instance = cls()
        
        return _instance
    
    def close(self):
        """Close all clients (cleanup)."""
        self._client = None
        self._admin_client = None
        logger.info("[SUPABASE_SINGLETON] Clients closed")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_supabase_client(use_admin: bool = False) -> Client:
    """
    Get Supabase client from singleton.
    
    Args:
        use_admin: If True, returns admin client (service role)
                   If False, returns standard client (anon key)
    
    Returns:
        Supabase client instance
        
    Example:
        # Standard client
        client = get_supabase_client()
        
        # Admin client
        admin = get_supabase_client(use_admin=True)
    """
    singleton = SupabaseSingleton.get_instance()
    return singleton.get_admin_client() if use_admin else singleton.client


def get_supabase_url() -> str:
    """Get Supabase URL from singleton."""
    return SupabaseSingleton.get_instance().url


def close_supabase_connections():
    """Close all Supabase connections (cleanup)."""
    global _instance
    if _instance is not None:
        _instance.close()
        _instance = None

