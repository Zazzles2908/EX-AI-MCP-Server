"""
File caching system for workflow tools.

Day 3.1: Implements LRU cache with size limits to eliminate redundant file I/O operations.
Expected improvement: 30-50% reduction in I/O time for workflows with repeated file access.

Based on EXAI recommendations from continuation_id: 8b5fce66-a561-45ec-b412-68992147882c
"""

import hashlib
import logging
import os
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# EXAI QA Fix: Add fallback for ThreadPoolExecutor
try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    PARALLEL_READING_AVAILABLE = True
except ImportError:
    PARALLEL_READING_AVAILABLE = False
    logger.warning("ThreadPoolExecutor not available, parallel reading disabled")

logger = logging.getLogger(__name__)


class FileCache:
    """
    LRU cache for file contents with size limits.

    Features:
    - LRU eviction when cache is full
    - File modification time tracking (invalidates cache on file changes)
    - Size limits (max files and max file size)
    - Cache statistics (hits, misses, hit rate)
    - Automatic encoding detection (UTF-8 with latin-1 fallback)

    Usage:
        cache = FileCache(max_size=128, max_file_size_mb=10)
        content = cache.read_file("/path/to/file.py")
        stats = cache.get_stats()
    """

    def __init__(self, max_size: int = 128, max_file_size_mb: int = 10):
        """
        Initialize file cache.

        Args:
            max_size: Maximum number of files to cache (default: 128)
            max_file_size_mb: Maximum file size to cache in MB (default: 10)
        """
        self.max_size = max_size
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convert to bytes
        self._cache: Dict[str, Dict] = {}
        self._cache_keys: list = []  # LRU tracking
        self.stats = {
            'hits': 0,
            'misses': 0,
            'files_skipped': 0,  # Files too large to cache
            'evictions': 0,  # Files evicted due to cache size limit
            'invalidations': 0,  # Files invalidated due to modification
        }

        logger.info(f"FileCache initialized: max_size={max_size}, max_file_size={max_file_size_mb}MB")

    def _generate_key(self, file_path: str) -> str:
        """
        Generate a cache key based on file path and modification time.

        The key includes:
        - File path (absolute)
        - Modification time (to detect changes)
        - File size (to detect changes)

        Args:
            file_path: Path to the file

        Returns:
            MD5 hash of the key data
        """
        try:
            stat = os.stat(file_path)
            mtime = stat.st_mtime
            size = stat.st_size
            # Include path, mtime, and size to detect changes
            key_data = f"{file_path}:{mtime}:{size}"
            return hashlib.md5(key_data.encode()).hexdigest()
        except OSError:
            # If stat fails, just use the path
            return hashlib.md5(file_path.encode()).hexdigest()

    def read_file(self, file_path: str) -> str:
        """
        Read file with caching.

        Process:
        1. Normalize path (CRITICAL: Convert Windows paths to Docker paths)
        2. Check file size BEFORE reading (EXAI QA recommendation)
        3. Generate cache key (includes mtime for invalidation)
        4. Check cache for existing entry
        5. If hit, return cached content
        6. If miss, read file from disk
        7. Add to cache (if file size is within limits)

        Args:
            file_path: Path to the file to read (Windows, Linux, or relative)

        Returns:
            File contents as string

        Raises:
            Exception: If file cannot be read
        """
        # CRITICAL FIX (2025-10-19): Normalize path for Docker compatibility
        from tools.workflow.performance_optimizer import normalize_path
        file_path = normalize_path(file_path)
        # EXAI QA Fix: Check file size BEFORE reading to avoid loading large files
        try:
            stat = os.stat(file_path)
            if stat.st_size > self.max_file_size:
                self.stats['files_skipped'] += 1
                logger.debug(f"File too large to cache: {file_path} ({stat.st_size / 1024 / 1024:.1f}MB)")
                # Read and return directly without caching
                try:
                    return Path(file_path).read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    return Path(file_path).read_text(encoding='latin-1')
        except OSError:
            pass  # Continue with normal flow if stat fails

        cache_key = self._generate_key(file_path)

        # Check cache first
        if cache_key in self._cache:
            self.stats['hits'] += 1
            # Move to end of LRU list (most recently used)
            self._cache_keys.remove(cache_key)
            self._cache_keys.append(cache_key)
            logger.debug(f"Cache HIT: {file_path}")
            return self._cache[cache_key]['content']

        self.stats['misses'] += 1
        logger.debug(f"Cache MISS: {file_path}")

        # Read file from disk
        try:
            path = Path(file_path)
            content = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                content = path.read_text(encoding='latin-1')
                logger.debug(f"Used latin-1 encoding for {file_path}")
            except Exception as e:
                raise Exception(f"Failed to read file with any encoding: {e}")
        except Exception as e:
            raise Exception(f"Failed to read file: {e}")

        # Add to cache (size already checked above)
        self._add_to_cache(cache_key, content, file_path)

        # CRITICAL FIX (2025-10-23): Return the content!
        # BUG: Method was missing return statement, causing NoneType errors
        return content

    def read_files_parallel(self, file_paths: List[str], max_workers: int = 4) -> Dict[str, str]:
        """
        Day 3.2: Read multiple files in parallel using ThreadPoolExecutor.

        This method provides significant performance improvements for workflows
        that need to read many files (>5 files). For small file counts, the
        overhead of thread management may outweigh the benefits.

        Expected improvement: 40-60% faster for workflows with 10+ files.

        Args:
            file_paths: List of file paths to read
            max_workers: Maximum number of parallel workers (default: 4)

        Returns:
            Dictionary mapping file paths to their contents

        Example:
            cache = get_file_cache()
            files = ["/path/to/file1.py", "/path/to/file2.py", "/path/to/file3.py"]
            contents = cache.read_files_parallel(files)
        """
        if not file_paths:
            return {}

        # EXAI QA Fix: Fallback to sequential if ThreadPoolExecutor not available
        if not PARALLEL_READING_AVAILABLE:
            logger.debug(f"Reading {len(file_paths)} files sequentially (ThreadPoolExecutor not available)")
            return {path: self.read_file(path) for path in file_paths}

        # For small file counts, parallel reading may not be beneficial
        if len(file_paths) <= 2:
            logger.debug(f"Reading {len(file_paths)} files sequentially (too few for parallel)")
            return {path: self.read_file(path) for path in file_paths}

        logger.debug(f"Reading {len(file_paths)} files in parallel with {max_workers} workers")
        start_time = time.time()

        results = {}
        errors = {}

        # EXAI QA Fix: Use ThreadPoolExecutor with proper resource cleanup
        executor = ThreadPoolExecutor(max_workers=max_workers)
        try:
            # Submit all read tasks
            future_to_path = {
                executor.submit(self.read_file, path): path
                for path in file_paths
            }

            # Collect results as they complete
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    content = future.result()
                    results[path] = content
                except Exception as e:
                    logger.warning(f"Failed to read {path} in parallel: {e}")
                    errors[path] = f"Error reading file: {str(e)}"
                    results[path] = errors[path]
        finally:
            # Ensure executor is properly shut down even if exception occurs
            executor.shutdown(wait=False)

        elapsed = time.time() - start_time
        logger.debug(f"Parallel read completed: {len(results)} files in {elapsed:.2f}s ({len(results)/elapsed:.1f} files/sec)")

        return results

    def _add_to_cache(self, key: str, content: str, file_path: str):
        """
        Add item to cache with LRU eviction.

        Args:
            key: Cache key
            content: File content
            file_path: Original file path (for logging)
        """
        # Evict oldest if cache is full
        if len(self._cache) >= self.max_size and key not in self._cache:
            oldest_key = self._cache_keys.pop(0)
            evicted_path = self._cache[oldest_key].get('file_path', 'unknown')
            del self._cache[oldest_key]
            self.stats['evictions'] += 1
            logger.debug(f"Evicted from cache: {evicted_path}")

        # Add new item (or update existing)
        if key in self._cache:
            # Update existing entry (file was modified)
            self._cache_keys.remove(key)
            self.stats['invalidations'] += 1
            logger.debug(f"Invalidated cache entry: {file_path}")

        self._cache_keys.append(key)
        self._cache[key] = {
            'content': content,
            'file_path': file_path,
            'timestamp': time.time(),
            'size': len(content.encode('utf-8'))
        }
        logger.debug(f"Added to cache: {file_path}")

    def get_stats(self) -> Dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics:
            - hits: Number of cache hits
            - misses: Number of cache misses
            - files_skipped: Number of files too large to cache
            - evictions: Number of files evicted due to size limit
            - invalidations: Number of files invalidated due to modification
            - total_requests: Total number of read requests
            - hit_rate: Cache hit rate (0.0 to 1.0)
            - cache_size: Current number of files in cache
            - total_cached_mb: Total size of cached files in MB
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0

        # Calculate total cached size
        total_size = sum(entry['size'] for entry in self._cache.values())
        total_size_mb = total_size / 1024 / 1024

        return {
            **self.stats,
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'cache_size': len(self._cache),
            'total_cached_mb': total_size_mb
        }

    def clear(self):
        """Clear the cache."""
        self._cache.clear()
        self._cache_keys.clear()
        logger.info("Cache cleared")

    def invalidate(self, file_path: str):
        """
        Invalidate a specific file in the cache.

        Args:
            file_path: Path to the file to invalidate
        """
        key = self._generate_key(file_path)
        if key in self._cache:
            del self._cache[key]
            self._cache_keys.remove(key)
            self.stats['invalidations'] += 1
            logger.debug(f"Invalidated: {file_path}")


# Singleton instance for shared cache across workflow tools
_file_cache: Optional[FileCache] = None
_file_cache_lock = threading.Lock()


def get_file_cache() -> FileCache:
    """
    Get singleton file cache instance (thread-safe).

    EXAI QA Fix: Added double-checked locking for thread safety.

    Returns:
        Shared FileCache instance
    """
    global _file_cache
    if _file_cache is None:
        with _file_cache_lock:
            if _file_cache is None:
                _file_cache = FileCache()
    return _file_cache


def reset_file_cache():
    """Reset the file cache (useful for testing)."""
    global _file_cache
    if _file_cache is not None:
        _file_cache.clear()
    _file_cache = None

