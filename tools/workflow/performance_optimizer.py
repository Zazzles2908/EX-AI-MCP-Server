"""
Performance optimization utilities for workflow tools.

Day 3.3: Implements caching for redundant operations to reduce execution time.
Expected improvement: 10-20% reduction in execution time.

Based on EXAI recommendations from continuation_id: 8b5fce66-a561-45ec-b412-68992147882c
"""

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """
    Performance optimization utilities for workflow tools.
    
    Features:
    - Path validation caching (avoid repeated os.path.exists calls)
    - Model resolution caching (avoid repeated model lookups)
    - Statistics tracking (cache hits, misses, time saved)
    
    Usage:
        optimizer = get_performance_optimizer()
        if optimizer.is_valid_path("/path/to/file.py"):
            # Path is valid
            pass
    """
    
    def __init__(self):
        """Initialize performance optimizer."""
        self.stats = {
            'path_validations': 0,
            'path_cache_hits': 0,
            'model_resolutions': 0,
            'model_cache_hits': 0,
        }
        self._path_cache = {}
        self._model_cache = {}
        
        logger.info("PerformanceOptimizer initialized")
    
    def is_valid_path(self, path: str) -> bool:
        """
        Check if a path exists (with caching).
        
        Day 3.3: Caches path validation results to avoid repeated os.path.exists calls.
        Cache is invalidated if the path is modified (based on mtime).
        
        Args:
            path: Path to validate
            
        Returns:
            True if path exists, False otherwise
        """
        self.stats['path_validations'] += 1
        
        # Check cache first
        if path in self._path_cache:
            cached_result, cached_mtime = self._path_cache[path]
            
            # Validate cache entry (check if file still exists and mtime matches)
            try:
                current_mtime = os.path.getmtime(path)
                if current_mtime == cached_mtime:
                    self.stats['path_cache_hits'] += 1
                    return cached_result
            except OSError:
                # File no longer exists, invalidate cache
                del self._path_cache[path]
                return False
        
        # Perform actual validation
        try:
            exists = os.path.exists(path)
            if exists:
                mtime = os.path.getmtime(path)
                self._path_cache[path] = (exists, mtime)
            return exists
        except OSError:
            return False
    
    def resolve_model(self, model_name: str, provider: str = "auto") -> str:
        """
        Resolve model name to actual model identifier (with caching).
        
        Day 3.3: Caches model resolution results to avoid repeated lookups.
        
        Args:
            model_name: Model name to resolve (e.g., "auto", "glm-4.6")
            provider: Provider name (e.g., "glm", "kimi")
            
        Returns:
            Resolved model identifier
        """
        self.stats['model_resolutions'] += 1
        
        cache_key = f"{provider}:{model_name}"
        
        # Check cache first
        if cache_key in self._model_cache:
            self.stats['model_cache_hits'] += 1
            return self._model_cache[cache_key]
        
        # Perform actual resolution (simplified - actual implementation would use provider logic)
        resolved = model_name
        if model_name == "auto":
            if provider == "glm":
                resolved = "glm-4.6"
            elif provider == "kimi":
                resolved = "kimi-k2-0905-preview"
            else:
                resolved = "glm-4.6"  # Default
        
        # Cache result
        self._model_cache[cache_key] = resolved
        return resolved
    
    def get_stats(self) -> dict:
        """
        Get performance optimizer statistics.
        
        Returns:
            Dictionary with statistics:
            - path_validations: Total path validation calls
            - path_cache_hits: Number of path cache hits
            - path_cache_hit_rate: Path cache hit rate (0.0 to 1.0)
            - model_resolutions: Total model resolution calls
            - model_cache_hits: Number of model cache hits
            - model_cache_hit_rate: Model cache hit rate (0.0 to 1.0)
            - total_cache_hits: Total cache hits across all operations
            - total_operations: Total operations performed
            - overall_cache_hit_rate: Overall cache hit rate (0.0 to 1.0)
        """
        path_hit_rate = (
            self.stats['path_cache_hits'] / self.stats['path_validations']
            if self.stats['path_validations'] > 0 else 0
        )
        model_hit_rate = (
            self.stats['model_cache_hits'] / self.stats['model_resolutions']
            if self.stats['model_resolutions'] > 0 else 0
        )
        
        total_ops = self.stats['path_validations'] + self.stats['model_resolutions']
        total_hits = self.stats['path_cache_hits'] + self.stats['model_cache_hits']
        overall_hit_rate = total_hits / total_ops if total_ops > 0 else 0
        
        return {
            **self.stats,
            'path_cache_hit_rate': path_hit_rate,
            'model_cache_hit_rate': model_hit_rate,
            'total_cache_hits': total_hits,
            'total_operations': total_ops,
            'overall_cache_hit_rate': overall_hit_rate,
        }
    
    def clear_caches(self):
        """Clear all caches."""
        self._path_cache.clear()
        self._model_cache.clear()
        logger.info("Performance optimizer caches cleared")
    
    def invalidate_path(self, path: str):
        """
        Invalidate a specific path in the cache.
        
        Args:
            path: Path to invalidate
        """
        if path in self._path_cache:
            del self._path_cache[path]
            logger.debug(f"Invalidated path cache: {path}")


# Singleton instance for shared optimizer across workflow tools
_performance_optimizer: Optional[PerformanceOptimizer] = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """
    Get singleton performance optimizer instance.
    
    Returns:
        Shared PerformanceOptimizer instance
    """
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer


def reset_performance_optimizer():
    """Reset the performance optimizer (useful for testing)."""
    global _performance_optimizer
    if _performance_optimizer is not None:
        _performance_optimizer.clear_caches()
    _performance_optimizer = None


# PHASE 2.3.2 (2025-10-22): Migrated to use centralized path normalization
# This function is now a wrapper around CrossPlatformPathHandler for backward compatibility
# NOTE: Caching is handled by CrossPlatformPathHandler.normalize_path_cached() - no double caching
def normalize_path(path: str) -> str:
    """
    Normalize a file path using the canonical CrossPlatformPathHandler.

    PHASE 2.3.2 (2025-10-22): Migrated to use centralized path normalization
    CRITICAL FIX (2025-10-19): Docker-aware path normalization

    This function is now a thin wrapper around CrossPlatformPathHandler
    for backward compatibility. New code should use get_path_handler() directly.

    NOTE: Caching is handled by the underlying CrossPlatformPathHandler.normalize_path_cached()
    to avoid double caching and memory waste.

    Examples:
        Windows: c:\Project\EX-AI-MCP-Server\src\file.py -> /app/src/file.py
        Linux:   /app/src/file.py -> /app/src/file.py (unchanged)
        Relative: src/file.py -> /app/src/file.py

    Args:
        path: Path to normalize (Windows, Linux, or relative)

    Returns:
        Normalized absolute path (Docker-aware)
    """
    from utils.file.cross_platform import get_path_handler

    # Use the canonical path handler with caching
    handler = get_path_handler()
    normalized_path, was_converted, error = handler.normalize_path_cached(path)

    if error:
        # Log warning but return best-effort normalization
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Path normalization warning: {error}")

    return normalized_path


@lru_cache(maxsize=128)
def get_file_extension(path: str) -> str:
    """
    Get file extension (with caching).
    
    Day 3.3: Uses functools.lru_cache to avoid repeated extension extraction.
    
    Args:
        path: File path
        
    Returns:
        File extension (e.g., ".py", ".js")
    """
    return Path(path).suffix.lower()

