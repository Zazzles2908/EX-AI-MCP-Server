"""
Supabase Download Utility for Universal File Hub
Date: 2025-10-30
EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9

Provides file download functionality with:
- Local caching with LRU eviction
- Progress tracking
- Metadata updates (access count)
- Error handling and retry logic
"""

import os
import hashlib
import shutil
import sqlite3
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Callable
from collections import OrderedDict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheDB:
    """SQLite database for cache metadata persistence."""
    
    def __init__(self, db_path: str):
        """Initialize cache database."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    file_id TEXT PRIMARY KEY,
                    cache_key TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    access_count INTEGER DEFAULT 1,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def add_file(self, file_id: str, cache_key: str, file_size: int):
        """Add or update cache entry."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cache_entries 
                (file_id, cache_key, file_size, access_count, last_accessed, cached_at)
                VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (file_id, cache_key, file_size))
            conn.commit()
    
    def update_access(self, file_id: str):
        """Update access statistics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE cache_entries 
                SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE file_id = ?
            """, (file_id,))
            conn.commit()
    
    def get_lru_files(self, limit: int = 10) -> list:
        """Get least recently used files."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT file_id, cache_key, file_size 
                FROM cache_entries 
                ORDER BY last_accessed ASC 
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()
    
    def remove_file(self, file_id: str):
        """Remove file from cache database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache_entries WHERE file_id = ?", (file_id,))
            conn.commit()
    
    def get_total_size(self) -> int:
        """Get total cache size."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT SUM(file_size) FROM cache_entries")
            result = cursor.fetchone()[0]
            return result if result else 0


class CacheManager:
    """Manages file caching with LRU eviction."""
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        max_size: int = 1024**3,  # 1GB default
        ttl: int = 86400  # 24 hours default
    ):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Cache directory path (defaults to temp dir)
            max_size: Maximum cache size in bytes
            ttl: Time-to-live in seconds
        """
        self.cache_dir = Path(cache_dir or os.path.join(tempfile.gettempdir(), 'exai-file-cache'))
        self.max_size = max_size
        self.ttl = ttl
        self.lru_cache = OrderedDict()
        
        # Initialize cache directory and database
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db = CacheDB(str(self.cache_dir / 'cache.db'))
        
        logger.info(f"Cache initialized: {self.cache_dir} (max: {max_size / 1024**2:.1f}MB)")
    
    def generate_cache_key(self, file_id: str) -> str:
        """Generate cache key from file_id."""
        return hashlib.sha256(file_id.encode()).hexdigest()
    
    def get(self, file_id: str) -> Optional[str]:
        """
        Get cached file path if valid.
        
        Args:
            file_id: File ID to retrieve
        
        Returns:
            Path to cached file or None if not cached/invalid
        """
        cache_key = self.generate_cache_key(file_id)
        cache_path = self.cache_dir / cache_key
        
        if cache_path.exists():
            # Update access statistics
            self.db.update_access(file_id)
            self.lru_cache[file_id] = str(cache_path)
            self.lru_cache.move_to_end(file_id)
            
            logger.debug(f"Cache hit: {file_id}")
            return str(cache_path)
        
        logger.debug(f"Cache miss: {file_id}")
        return None
    
    def add(self, file_id: str, source_path: str) -> str:
        """
        Add file to cache with LRU eviction.
        
        Args:
            file_id: File ID
            source_path: Path to source file
        
        Returns:
            Path to cached file
        """
        file_size = os.path.getsize(source_path)
        
        # Ensure space available
        self.ensure_space(file_size)
        
        # Generate cache path
        cache_key = self.generate_cache_key(file_id)
        cache_path = self.cache_dir / cache_key
        
        # Move file to cache
        shutil.move(source_path, cache_path)
        
        # Update LRU and database
        self.lru_cache[file_id] = str(cache_path)
        self.lru_cache.move_to_end(file_id)
        self.db.add_file(file_id, cache_key, file_size)
        
        logger.info(f"Cached: {file_id} ({file_size / 1024:.1f}KB)")
        return str(cache_path)
    
    def ensure_space(self, required_size: int):
        """Ensure enough space in cache, evicting if necessary."""
        current_size = self.db.get_total_size()
        
        while current_size + required_size > self.max_size:
            # Get LRU files
            lru_files = self.db.get_lru_files(limit=1)
            if not lru_files:
                break
            
            file_id, cache_key, file_size = lru_files[0]
            cache_path = self.cache_dir / cache_key
            
            # Remove file
            if cache_path.exists():
                cache_path.unlink()
            
            self.db.remove_file(file_id)
            if file_id in self.lru_cache:
                del self.lru_cache[file_id]
            
            current_size -= file_size
            logger.info(f"Evicted: {file_id} ({file_size / 1024:.1f}KB)")
    
    def cleanup_expired(self):
        """Clean up expired cache entries based on TTL."""
        cutoff_time = datetime.now() - timedelta(seconds=self.ttl)
        
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute("""
                SELECT file_id, cache_key 
                FROM cache_entries 
                WHERE last_accessed < ?
            """, (cutoff_time.isoformat(),))
            
            expired = cursor.fetchall()
            
            for file_id, cache_key in expired:
                cache_path = self.cache_dir / cache_key
                if cache_path.exists():
                    cache_path.unlink()
                self.db.remove_file(file_id)
                if file_id in self.lru_cache:
                    del self.lru_cache[file_id]
                
                logger.info(f"Expired: {file_id}")
        
        logger.info(f"Cleaned up {len(expired)} expired entries")


class SupabaseDownloadManager:
    """Manages file downloads from Supabase Storage with caching."""
    
    def __init__(
        self,
        supabase_client,
        cache_manager: Optional[CacheManager] = None,
        default_bucket: str = "user-files"
    ):
        """
        Initialize download manager.
        
        Args:
            supabase_client: Supabase client instance
            cache_manager: Optional cache manager (creates default if None)
            default_bucket: Default storage bucket name
        """
        self.client = supabase_client
        self.cache = cache_manager or CacheManager()
        self.default_bucket = default_bucket
        self.max_retries = 3
    
    def download_file(
        self,
        file_id: str,
        bucket: Optional[str] = None,
        force_download: bool = False,
        progress_callback: Optional[Callable[[int, float], None]] = None
    ) -> str:
        """
        Download file from Supabase Storage with caching.
        
        Args:
            file_id: File ID or storage path
            bucket: Optional bucket name (defaults to default_bucket)
            force_download: Force download even if cached
            progress_callback: Optional progress callback (bytes_downloaded, percent)
        
        Returns:
            Path to downloaded file (cached or fresh)
        
        Raises:
            DownloadError: If download fails
        """
        bucket = bucket or self.default_bucket
        
        # Check cache first (unless force_download)
        if not force_download:
            cached_path = self.cache.get(file_id)
            if cached_path and os.path.exists(cached_path):
                logger.info(f"Using cached file: {file_id}")
                self._update_metadata_access(file_id)
                return cached_path
        
        # Download file
        logger.info(f"Downloading file: {file_id}")
        try:
            temp_path = self._download_with_retry(file_id, bucket, progress_callback)
            
            # Add to cache
            final_path = self.cache.add(file_id, temp_path)
            
            # Update metadata
            self._update_metadata_access(file_id)
            
            return final_path
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise DownloadError(f"Download failed: {str(e)}") from e
    
    def _download_with_retry(
        self,
        file_id: str,
        bucket: str,
        progress_callback: Optional[Callable[[int, float], None]] = None
    ) -> str:
        """Download file with retry logic."""
        for attempt in range(self.max_retries):
            try:
                return self._download_to_temp(file_id, bucket, progress_callback)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Retry {attempt + 1}/{self.max_retries} for {file_id}: {e}")
    
    def _download_to_temp(
        self,
        file_id: str,
        bucket: str,
        progress_callback: Optional[Callable[[int, float], None]] = None
    ) -> str:
        """Download file to temporary location."""
        # Download from Supabase Storage
        response = self.client.storage.from_(bucket).download(file_id)
        
        # Write to temporary file
        temp_fd, temp_path = tempfile.mkstemp(prefix='exai_download_')
        try:
            with os.fdopen(temp_fd, 'wb') as f:
                f.write(response)
            
            # Call progress callback with 100%
            if progress_callback:
                file_size = os.path.getsize(temp_path)
                progress_callback(file_size, 100.0)
            
            return temp_path
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    
    def _update_metadata_access(self, file_id: str):
        """Update file metadata access statistics."""
        try:
            # Call Supabase function to increment access count
            self.client.rpc('increment_file_access_count', {'p_file_id': file_id}).execute()
        except Exception as e:
            logger.warning(f"Failed to update metadata for {file_id}: {e}")


class DownloadError(Exception):
    """Custom exception for download errors."""
    pass

