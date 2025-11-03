"""
Duplicate File Detector

Detects duplicate files using content-based hashing and Supabase tracking.
Integrates with Redis for caching and Prometheus for metrics.
"""

import logging
import os
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import redis
import json

from .hashing_service import HashingService
from src.storage.supabase_client import SupabaseStorageManager
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# Prometheus metrics
deduplication_checks_total = Counter(
    'deduplication_checks_total',
    'Total deduplication checks performed',
    ['result']  # 'duplicate', 'unique', 'error'
)
deduplication_hits_total = Counter(
    'deduplication_hits_total',
    'Total duplicate files detected'
)
deduplication_cache_hits = Counter(
    'deduplication_cache_hits_total',
    'Cache hits for deduplication checks'
)
deduplication_cache_size = Gauge(
    'deduplication_cache_size',
    'Number of hashes in deduplication cache'
)
deduplication_check_duration = Histogram(
    'deduplication_check_duration_seconds',
    'Time spent checking for duplicates'
)


class DuplicateDetector:
    """Detects duplicate files using content hashing"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize duplicate detector
        
        Args:
            redis_client: Optional Redis client for caching
        """
        self.supabase = SupabaseStorageManager()
        self.redis = redis_client or self._get_redis_client()
        self.cache_ttl = int(os.getenv('DEDUPLICATION_CACHE_TTL', '3600'))
        self.enabled = os.getenv('DEDUPLICATION_ENABLED', 'true').lower() == 'true'
        
        logger.info(f"DuplicateDetector initialized (enabled={self.enabled})")
    
    def _get_redis_client(self) -> Optional[redis.Redis]:
        """Get Redis client from environment"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            return client
        except Exception as e:
            logger.warning(f"Redis not available for deduplication cache: {e}")
            return None
    
    @deduplication_check_duration.time()
    async def check_duplicate(
        self,
        file_path: str,
        file_size: int,
        content_type: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if file is a duplicate
        
        Args:
            file_path: Path to file to check
            file_size: File size in bytes
            content_type: Optional MIME type
            
        Returns:
            Tuple of (is_duplicate, original_file_info)
            - is_duplicate: True if duplicate found
            - original_file_info: Dict with original file details if duplicate
        """
        if not self.enabled:
            deduplication_checks_total.labels(result='disabled').inc()
            return False, None
        
        try:
            # Compute file hash
            file_hash = HashingService.compute_file_hash(file_path)
            logger.debug(f"Computed hash for {file_path}: {file_hash[:16]}...")
            
            # Check Redis cache first
            cached_result = await self._check_cache(file_hash)
            if cached_result is not None:
                deduplication_cache_hits.inc()
                is_duplicate = cached_result.get('is_duplicate', False)
                result_label = 'duplicate' if is_duplicate else 'unique'
                deduplication_checks_total.labels(result=result_label).inc()
                
                if is_duplicate:
                    deduplication_hits_total.inc()
                    return True, cached_result.get('original_file')
                return False, None
            
            # Check Supabase for existing hash
            original_file = await self._check_supabase(file_hash, file_size, content_type)
            
            if original_file:
                # Duplicate found
                deduplication_checks_total.labels(result='duplicate').inc()
                deduplication_hits_total.inc()
                
                # Cache the result
                await self._cache_result(file_hash, True, original_file)
                
                logger.info(
                    f"Duplicate detected: {file_path} matches "
                    f"file_id={original_file.get('id')}"
                )
                return True, original_file
            else:
                # Unique file
                deduplication_checks_total.labels(result='unique').inc()
                
                # Cache the result
                await self._cache_result(file_hash, False, None)
                
                logger.debug(f"Unique file: {file_path}")
                return False, None
        
        except Exception as e:
            logger.error(f"Deduplication check failed: {e}")
            deduplication_checks_total.labels(result='error').inc()
            # On error, assume unique to allow upload
            return False, None
    
    async def _check_cache(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Check Redis cache for hash"""
        if not self.redis:
            return None
        
        try:
            cache_key = f"dedup:{file_hash}"
            cached_data = self.redis.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            return None
        
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
            return None
    
    async def _cache_result(
        self,
        file_hash: str,
        is_duplicate: bool,
        original_file: Optional[Dict[str, Any]]
    ):
        """Cache deduplication result in Redis"""
        if not self.redis:
            return
        
        try:
            cache_key = f"dedup:{file_hash}"
            cache_data = {
                'is_duplicate': is_duplicate,
                'original_file': original_file,
                'cached_at': datetime.utcnow().isoformat()
            }
            
            self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(cache_data)
            )
            
            # Update cache size metric
            try:
                cache_size = self.redis.dbsize()
                deduplication_cache_size.set(cache_size)
            except:
                pass
        
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")
    
    async def _check_supabase(
        self,
        file_hash: str,
        file_size: int,
        content_type: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Check Supabase for existing file with same hash"""
        try:
            # Query file_hashes table
            result = self.supabase.client.table('file_hashes') \
                .select('*') \
                .eq('file_hash', file_hash) \
                .execute()
            
            if result.data and len(result.data) > 0:
                hash_record = result.data[0]
                
                # Get original file details
                file_result = self.supabase.client.table('file_uploads') \
                    .select('*') \
                    .eq('id', hash_record['original_file_id']) \
                    .execute()
                
                if file_result.data and len(file_result.data) > 0:
                    return file_result.data[0]
            
            return None
        
        except Exception as e:
            logger.error(f"Supabase deduplication check failed: {e}")
            return None
    
    async def register_file_hash(
        self,
        file_id: str,
        file_hash: str,
        file_size: int,
        content_type: Optional[str] = None,
        is_duplicate: bool = False,
        original_file_id: Optional[str] = None
    ):
        """
        Register file hash in Supabase
        
        Args:
            file_id: File upload ID
            file_hash: SHA256 hash
            file_size: File size in bytes
            content_type: MIME type
            is_duplicate: Whether this is a duplicate
            original_file_id: ID of original file if duplicate
        """
        try:
            if not is_duplicate:
                # Register new unique file hash
                self.supabase.client.table('file_hashes').insert({
                    'file_hash': file_hash,
                    'original_file_id': file_id,
                    'file_size': file_size,
                    'content_type': content_type,
                    'duplicate_count': 0
                }).execute()
            else:
                # Increment duplicate count for original
                self.supabase.client.rpc(
                    'increment_duplicate_count',
                    {'hash_value': file_hash}
                ).execute()
            
            # Update file_uploads table
            self.supabase.client.table('file_uploads').update({
                'file_hash': file_hash,
                'is_duplicate': is_duplicate,
                'original_file_id': original_file_id,
                'deduplication_checked': True
            }).eq('id', file_id).execute()
            
            logger.info(f"Registered file hash for file_id={file_id}")
        
        except Exception as e:
            logger.error(f"Failed to register file hash: {e}")

