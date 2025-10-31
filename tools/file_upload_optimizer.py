"""
File Upload Optimizer - EXAI-Recommended Fixes
Implements adaptive provider selection, timeout handling, and query optimization
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class QueryComplexity(Enum):
    """Query complexity levels"""
    SIMPLE = 1
    MODERATE = 2
    COMPLEX = 3


class FileSize(Enum):
    """File size categories"""
    SMALL = 1      # < 1 MB
    MEDIUM = 2     # 1-10 MB
    LARGE = 3      # 10-100 MB


@dataclass
class UploadMetrics:
    """Metrics for upload operations"""
    file_size_bytes: int
    query_complexity: int
    provider: str
    upload_time_ms: float
    analysis_time_ms: float
    timeout_occurred: bool
    fallback_used: bool
    timestamp: datetime


class FileUploadOptimizer:
    """
    Optimizes file uploads based on EXAI recommendations
    
    Features:
    - Adaptive provider selection
    - Timeout prediction and handling
    - Query optimization
    - Intelligent caching
    - Metrics collection
    """
    
    # Configuration constants
    KIMI_TIMEOUT_THRESHOLD = 180  # seconds
    COMPLEXITY_THRESHOLD = 200    # characters
    LARGE_FILE_THRESHOLD = 10 * 1024 * 1024  # 10 MB
    
    def __init__(self):
        self.metrics: list[UploadMetrics] = []
        self.kimi_cache: Dict[str, str] = {}  # Persistent cache
        self.glm_cache: Dict[str, str] = {}   # Per-session cache
        self.timeout_history: Dict[str, int] = {}  # Track timeouts per provider
    
    def estimate_query_complexity(self, query: str) -> QueryComplexity:
        """
        Estimate query complexity based on length and structure
        
        Args:
            query: The query string
            
        Returns:
            QueryComplexity level
        """
        query_len = len(query)
        
        if query_len < 50:
            return QueryComplexity.SIMPLE
        elif query_len < 200:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.COMPLEX
    
    def categorize_file_size(self, file_size_bytes: int) -> FileSize:
        """
        Categorize file size
        
        Args:
            file_size_bytes: File size in bytes
            
        Returns:
            FileSize category
        """
        if file_size_bytes < 1024 * 1024:
            return FileSize.SMALL
        elif file_size_bytes < 10 * 1024 * 1024:
            return FileSize.MEDIUM
        else:
            return FileSize.LARGE
    
    def select_provider(
        self,
        query_complexity: QueryComplexity,
        file_size: FileSize,
        user_preference: str = "auto"
    ) -> str:
        """
        Select optimal provider based on query complexity and file size
        
        EXAI Recommendation: Adaptive provider selection
        
        Args:
            query_complexity: Estimated query complexity
            file_size: File size category
            user_preference: User's provider preference
            
        Returns:
            Selected provider ("kimi" or "glm")
        """
        # Rule 1: Complex queries on large files → use GLM to avoid timeout
        if (query_complexity == QueryComplexity.COMPLEX and 
            file_size == FileSize.LARGE):
            logger.info("Selecting GLM for complex query on large file (timeout risk)")
            return "glm"
        
        # Rule 2: Complex queries → use GLM
        if query_complexity == QueryComplexity.COMPLEX:
            logger.info("Selecting GLM for complex query")
            return "glm"
        
        # Rule 3: Default to Kimi for simple/moderate queries
        logger.info("Selecting Kimi for simple/moderate query")
        return "kimi"
    
    def estimate_processing_time(
        self,
        query_complexity: QueryComplexity,
        file_size: FileSize
    ) -> float:
        """
        Estimate processing time in seconds
        
        Args:
            query_complexity: Query complexity level
            file_size: File size category
            
        Returns:
            Estimated processing time in seconds
        """
        # Base times (in seconds)
        base_times = {
            QueryComplexity.SIMPLE: 5,
            QueryComplexity.MODERATE: 15,
            QueryComplexity.COMPLEX: 45,
        }
        
        # File size multipliers
        size_multipliers = {
            FileSize.SMALL: 1.0,
            FileSize.MEDIUM: 2.0,
            FileSize.LARGE: 4.0,
        }
        
        base_time = base_times[query_complexity]
        multiplier = size_multipliers[file_size]
        
        estimated_time = base_time * multiplier
        logger.info(f"Estimated processing time: {estimated_time}s")
        
        return estimated_time
    
    def will_timeout(
        self,
        query_complexity: QueryComplexity,
        file_size: FileSize,
        provider: str
    ) -> bool:
        """
        Predict if operation will timeout

        Args:
            query_complexity: Query complexity level
            file_size: File size category
            provider: Target provider

        Returns:
            True if timeout is likely
        """
        estimated_time = self.estimate_processing_time(query_complexity, file_size)

        if provider == "kimi":
            # Add safety margin (80% of timeout threshold)
            timeout_threshold = self.KIMI_TIMEOUT_THRESHOLD * 0.8
            will_timeout = estimated_time > timeout_threshold
            if will_timeout:
                logger.warning(f"Timeout risk detected: {estimated_time}s > {timeout_threshold}s (80% of {self.KIMI_TIMEOUT_THRESHOLD}s limit)")
            return will_timeout

        return False
    
    def optimize_query(self, query: str, file_size: FileSize) -> str:
        """
        Optimize query to reduce processing time

        EXAI Recommendation: Query optimization and chunking

        Args:
            query: Original query
            file_size: File size category

        Returns:
            Optimized query
        """
        complexity = self.estimate_query_complexity(query)

        # If complex query on large file, simplify
        if complexity == QueryComplexity.COMPLEX and file_size == FileSize.LARGE:
            logger.info("Simplifying complex query for large file")

            # Extract main question (first sentence or first 100 chars)
            sentences = query.split(".")
            if len(sentences) > 1:
                # Use first sentence
                simplified = sentences[0] + "."
            else:
                # Use first 100 characters
                simplified = query[:100] + "..."

            reduction = ((len(query) - len(simplified)) / len(query) * 100)
            logger.info(f"Original: {len(query)} chars")
            logger.info(f"Simplified: {len(simplified)} chars ({reduction:.1f}% reduction)")

            return simplified

        # For moderate complexity on large files, also optimize
        if complexity == QueryComplexity.MODERATE and file_size == FileSize.LARGE:
            logger.info("Optimizing moderate query for large file")

            # Keep first 150 characters
            if len(query) > 150:
                optimized = query[:150] + "..."
                reduction = ((len(query) - len(optimized)) / len(query) * 100)
                logger.info(f"Optimized from {len(query)} to {len(optimized)} chars ({reduction:.1f}% reduction)")
                return optimized

        return query
    
    def create_analysis_prompt(
        self,
        task: str,
        files: list[str],
        provider: str
    ) -> str:
        """
        Create optimized analysis prompt
        
        EXAI Recommendation: Enhanced prompt engineering
        
        Args:
            task: The analysis task
            files: List of files being analyzed
            provider: Target provider
            
        Returns:
            Optimized prompt
        """
        file_list = "\n".join([f"- {f}" for f in files])
        
        prompt = f"""You are an AI assistant tasked with: {task}

Files provided for analysis:
{file_list}

IMPORTANT INSTRUCTIONS:
1. Focus on completing the specified task, not on file management
2. The files are already uploaded and available for analysis
3. Provide direct, actionable analysis
4. Do not discuss file upload/management procedures

Task: {task}

Please proceed with the analysis."""
        
        return prompt
    
    def get_cache_status(self, file_path: str, provider: str) -> Optional[str]:
        """
        Check if file is in cache
        
        Args:
            file_path: Path to file
            provider: Target provider
            
        Returns:
            Cached file ID if available, None otherwise
        """
        if provider == "kimi":
            return self.kimi_cache.get(file_path)
        elif provider == "glm":
            return self.glm_cache.get(file_path)
        
        return None
    
    def cache_file_id(self, file_path: str, file_id: str, provider: str) -> None:
        """
        Cache file ID for future use
        
        Args:
            file_path: Path to file
            file_id: File ID from provider
            provider: Provider name
        """
        if provider == "kimi":
            self.kimi_cache[file_path] = file_id
            logger.info(f"Cached Kimi file ID: {file_path} → {file_id}")
        elif provider == "glm":
            self.glm_cache[file_path] = file_id
            logger.info(f"Cached GLM file ID: {file_path} → {file_id}")
    
    def record_metrics(
        self,
        file_size_bytes: int,
        query_complexity: int,
        provider: str,
        upload_time_ms: float,
        analysis_time_ms: float,
        timeout_occurred: bool = False,
        fallback_used: bool = False
    ) -> None:
        """
        Record metrics for analysis
        
        Args:
            file_size_bytes: File size in bytes
            query_complexity: Query complexity score
            provider: Provider used
            upload_time_ms: Upload time in milliseconds
            analysis_time_ms: Analysis time in milliseconds
            timeout_occurred: Whether timeout occurred
            fallback_used: Whether fallback provider was used
        """
        metric = UploadMetrics(
            file_size_bytes=file_size_bytes,
            query_complexity=query_complexity,
            provider=provider,
            upload_time_ms=upload_time_ms,
            analysis_time_ms=analysis_time_ms,
            timeout_occurred=timeout_occurred,
            fallback_used=fallback_used,
            timestamp=datetime.now()
        )
        
        self.metrics.append(metric)
        
        if timeout_occurred:
            self.timeout_history[provider] = self.timeout_history.get(provider, 0) + 1
            logger.warning(f"Timeout recorded for {provider}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of collected metrics
        
        Returns:
            Metrics summary
        """
        if not self.metrics:
            return {"message": "No metrics collected yet"}
        
        total_uploads = len(self.metrics)
        total_timeouts = sum(1 for m in self.metrics if m.timeout_occurred)
        total_fallbacks = sum(1 for m in self.metrics if m.fallback_used)
        
        avg_upload_time = sum(m.upload_time_ms for m in self.metrics) / total_uploads
        avg_analysis_time = sum(m.analysis_time_ms for m in self.metrics) / total_uploads
        
        return {
            "total_uploads": total_uploads,
            "total_timeouts": total_timeouts,
            "timeout_rate": f"{(total_timeouts / total_uploads * 100):.1f}%",
            "total_fallbacks": total_fallbacks,
            "fallback_rate": f"{(total_fallbacks / total_uploads * 100):.1f}%",
            "avg_upload_time_ms": f"{avg_upload_time:.1f}",
            "avg_analysis_time_ms": f"{avg_analysis_time:.1f}",
            "timeout_history": self.timeout_history,
        }


# Global optimizer instance
_optimizer: Optional[FileUploadOptimizer] = None


def get_optimizer() -> FileUploadOptimizer:
    """Get or create global optimizer instance"""
    global _optimizer
    if _optimizer is None:
        _optimizer = FileUploadOptimizer()
    return _optimizer

