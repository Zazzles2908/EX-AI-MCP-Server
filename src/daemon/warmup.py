"""
Connection Pre-warming Module

BUG FIX #11 (2025-10-20): Implement connection pre-warming to reduce first-call latency
Based on EXAI guidance from Phase 1 implementation plan.

This module warms up external connections during server startup to eliminate
cold start latency on the first request after container rebuild.

Expected improvements:
- Faster first request after server startup
- Verified connections before accepting requests
- Better error handling during initialization
"""

import asyncio
import logging
import os
from typing import Optional
from supabase import create_client, Client
import redis.asyncio as redis

logger = logging.getLogger(__name__)

# BUG FIX #11 (2025-10-20): Get config from environment variables directly
# This avoids import issues with config modules
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or os.getenv("SUPABASE_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "")

# Global connection instances
_supabase_client: Optional[Client] = None
_redis_client: Optional[redis.Redis] = None


async def warmup_supabase() -> Client:
    """
    Initialize and verify Supabase connection.
    
    Returns:
        Initialized Supabase client
        
    Raises:
        Exception if connection fails
    """
    global _supabase_client
    
    try:
        logger.info("[WARMUP] Initializing Supabase connection...")
        start_time = asyncio.get_event_loop().time()
        
        # Create Supabase client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Run a lightweight query to verify connection
        # Using conversations table as it's guaranteed to exist
        result = _supabase_client.table("conversations").select("id").limit(1).execute()
        
        elapsed = asyncio.get_event_loop().time() - start_time
        logger.info(f"[WARMUP] ✅ Supabase connection warmed up successfully ({elapsed:.3f}s)")
        
        return _supabase_client
        
    except Exception as e:
        logger.error(f"[WARMUP] ❌ Failed to warm up Supabase: {e}")
        raise


async def warmup_redis() -> redis.Redis:
    """
    Initialize and verify Redis connection.

    Returns:
        Initialized Redis client

    Raises:
        Exception if connection fails
    """
    global _redis_client

    try:
        logger.info("[WARMUP] Initializing Redis connection...")
        start_time = asyncio.get_event_loop().time()

        # Use REDIS_URL from environment
        if not REDIS_URL:
            logger.warning("[WARMUP] REDIS_URL not set, skipping Redis warmup")
            return None

        # Create Redis client
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True)

        # Verify connection with PING
        await _redis_client.ping()

        elapsed = asyncio.get_event_loop().time() - start_time
        logger.info(f"[WARMUP] ✅ Redis connection warmed up successfully ({elapsed:.3f}s)")

        return _redis_client

    except Exception as e:
        logger.error(f"[WARMUP] ❌ Failed to warm up Redis: {e}")
        raise


async def warmup_all() -> bool:
    """
    Warm up all external connections in parallel.
    
    Returns:
        True if all connections warmed up successfully
        
    Raises:
        Exception if any connection fails
    """
    logger.info("[WARMUP] ========================================")
    logger.info("[WARMUP] Starting connection warmup...")
    logger.info("[WARMUP] ========================================")
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Warm up connections in parallel for faster startup
        supabase_task = asyncio.create_task(warmup_supabase())
        redis_task = asyncio.create_task(warmup_redis())
        
        # Wait for all to complete
        await asyncio.gather(supabase_task, redis_task)
        
        elapsed = asyncio.get_event_loop().time() - start_time
        logger.info("[WARMUP] ========================================")
        logger.info(f"[WARMUP] ✅ All connections warmed up successfully ({elapsed:.3f}s)")
        logger.info("[WARMUP] ========================================")
        
        return True
        
    except Exception as e:
        elapsed = asyncio.get_event_loop().time() - start_time
        logger.error("[WARMUP] ========================================")
        logger.error(f"[WARMUP] ❌ Connection warmup failed ({elapsed:.3f}s): {e}")
        logger.error("[WARMUP] ========================================")
        raise


def get_warmed_supabase() -> Optional[Client]:
    """Get the pre-warmed Supabase client."""
    return _supabase_client


def get_warmed_redis() -> Optional[redis.Redis]:
    """Get the pre-warmed Redis client."""
    return _redis_client

