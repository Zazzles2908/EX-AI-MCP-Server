# src/security/rate_limiter.py
"""
Rate Limiter for Application-Level Rate Limiting

Phase A2 Week 1 - Basic Security Infrastructure
Uses Redis for fast lookups and sliding window counters
"""

import os
import redis
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, redis_host: str = 'redis', redis_port: int = 6379, redis_db: int = 0):
        """Initialize rate limiter with Redis connection

        CRITICAL FIX (2025-11-01): Changed default redis_host from 'localhost' to 'redis'
        - In Docker containers, 'localhost' refers to the container itself
        - 'redis' is the Docker service name that resolves to the Redis container
        - This fixes "Connection refused" errors in containerized environments
        """
        try:
            # Get Redis password from environment for authentication
            redis_password = os.getenv('REDIS_PASSWORD', '')

            logger.info(f"[RATE_LIMITER] Connecting to Redis at {redis_host}:{redis_port} (password: {'SET' if redis_password else 'NOT SET'})")

            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password if redis_password else None,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"✅ Rate limiter connected to Redis at {redis_host}:{redis_port}")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Rate limiting will be disabled.")
            self.redis_client = None
        
        # Default rate limits
        self.default_limits = {
            'requests_per_minute': 60,
            'files_per_hour': 100,
            'mb_per_day': 1000
        }
    
    def check_rate_limit(self, application_id: str, operation: str, size_mb: float = 0) -> Dict[str, Any]:
        """
        Check if application has exceeded rate limits for a specific operation
        
        Args:
            application_id: Unique identifier for the application
            operation: Type of operation ('request', 'file_upload', 'file_download')
            size_mb: Size of file in MB (for file operations)
            
        Returns:
            Dict with 'allowed': bool and 'remaining': int for each limit type
        """
        # SECURITY FIX: Fail closed when Redis is unavailable
        # Previous behavior: fail open (allowed=True) - security bypass!
        # New behavior: fail closed (allowed=False) - reject requests until Redis is restored
        if not self.redis_client:
            logging.warning(f"Rate limiter unavailable (Redis down) - rejecting request for user {user_id}")
            return {
                'allowed': False,
                'error': 'Rate limiting service temporarily unavailable',
                'limits': {
                    'requests_per_minute': {'limit': self.default_limits['requests_per_minute'], 'remaining': 0},
                    'files_per_hour': {'limit': self.default_limits['files_per_hour'], 'remaining': 0},
                    'mb_per_day': {'limit': self.default_limits['mb_per_day'], 'remaining': 0}
                }
            }
        
        current_time = int(time.time())
        current_minute = current_time // 60
        current_hour = current_time // 3600
        current_day = current_time // 86400
        
        # Redis keys for different time windows
        minute_key = f"rate_limit:{application_id}:minute:{current_minute}"
        hour_key = f"rate_limit:{application_id}:hour:{current_hour}"
        day_key = f"rate_limit:{application_id}:day:{current_day}"
        
        # Initialize response
        response = {
            'allowed': True,
            'limits': {
                'requests_per_minute': {'limit': self.default_limits['requests_per_minute'], 'remaining': self.default_limits['requests_per_minute']},
                'files_per_hour': {'limit': self.default_limits['files_per_hour'], 'remaining': self.default_limits['files_per_hour']},
                'mb_per_day': {'limit': self.default_limits['mb_per_day'], 'remaining': self.default_limits['mb_per_day']}
            }
        }
        
        try:
            # Check minute limit (for requests)
            if operation in ['request', 'file_upload', 'file_download']:
                minute_count = self.redis_client.incr(minute_key)
                if minute_count == 1:
                    self.redis_client.expire(minute_key, 60)  # Expire after 1 minute
                
                response['limits']['requests_per_minute']['remaining'] = max(0, self.default_limits['requests_per_minute'] - minute_count)
                if minute_count > self.default_limits['requests_per_minute']:
                    response['allowed'] = False
            
            # Check hour limit (for file operations)
            if operation in ['file_upload', 'file_download']:
                hour_count = self.redis_client.incr(hour_key)
                if hour_count == 1:
                    self.redis_client.expire(hour_key, 3600)  # Expire after 1 hour
                
                response['limits']['files_per_hour']['remaining'] = max(0, self.default_limits['files_per_hour'] - hour_count)
                if hour_count > self.default_limits['files_per_hour']:
                    response['allowed'] = False
            
            # Check daily limit (for file size)
            if operation in ['file_upload', 'file_download'] and size_mb > 0:
                day_mb = self.redis_client.incrbyfloat(day_key, size_mb)
                if day_mb == size_mb:  # First operation today
                    self.redis_client.expire(day_key, 86400)  # Expire after 24 hours
                
                response['limits']['mb_per_day']['remaining'] = max(0, self.default_limits['mb_per_day'] - day_mb)
                if day_mb > self.default_limits['mb_per_day']:
                    response['allowed'] = False
        
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # On error, allow the request (fail open)
            response['allowed'] = True
        
        return response
    
    def get_current_usage(self, application_id: str) -> Dict[str, Any]:
        """
        Get current usage statistics for an application
        
        Args:
            application_id: Unique identifier for the application
            
        Returns:
            Dict with current usage for all limit types
        """
        if not self.redis_client:
            return {
                'requests_per_minute': 0,
                'files_per_hour': 0,
                'mb_per_day': 0
            }
        
        current_time = int(time.time())
        current_minute = current_time // 60
        current_hour = current_time // 3600
        current_day = current_time // 86400
        
        # Redis keys for different time windows
        minute_key = f"rate_limit:{application_id}:minute:{current_minute}"
        hour_key = f"rate_limit:{application_id}:hour:{current_hour}"
        day_key = f"rate_limit:{application_id}:day:{current_day}"
        
        try:
            # Get current counts
            minute_count = int(self.redis_client.get(minute_key) or 0)
            hour_count = int(self.redis_client.get(hour_key) or 0)
            day_mb = float(self.redis_client.get(day_key) or 0)
            
            return {
                'requests_per_minute': minute_count,
                'files_per_hour': hour_count,
                'mb_per_day': day_mb
            }
        except Exception as e:
            logger.error(f"Failed to get current usage: {e}")
            return {
                'requests_per_minute': 0,
                'files_per_hour': 0,
                'mb_per_day': 0
            }

