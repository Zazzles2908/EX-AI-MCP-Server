"""
Performance Timing Utilities for EXAI MCP Server

Provides decorators and utilities for measuring execution time of operations.
Used to identify bottlenecks and validate performance improvements.

Created: 2025-10-19 (Bug #11 investigation)
"""

import time
import logging
from functools import wraps
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)


def timing_decorator(operation_name: Optional[str] = None):
    """
    Decorator to measure execution time of functions
    
    Args:
        operation_name: Optional custom name for the operation (defaults to module.function)
    
    Example:
        @timing_decorator("MyOperation")
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"[TIMING] {op_name} completed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"[TIMING] {op_name} failed after {execution_time:.3f}s: {str(e)}")
                raise
        return wrapper
    return decorator


def log_operation_time(operation_name: str, start_time: float) -> float:
    """
    Log operation time given a start time
    
    Args:
        operation_name: Name of the operation
        start_time: Start time from time.time()
    
    Returns:
        Execution time in seconds
    
    Example:
        start = time.time()
        # ... do work ...
        log_operation_time("MyOperation", start)
    """
    execution_time = time.time() - start_time
    logger.info(f"[TIMING] {operation_name} took {execution_time:.3f}s")
    return execution_time


class TimingContext:
    """
    Context manager for timing code blocks
    
    Example:
        with TimingContext("MyOperation"):
            # ... do work ...
    """
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time: Optional[float] = None
        self.execution_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.execution_time = time.time() - self.start_time
        
        if exc_type is None:
            logger.info(f"[TIMING] {self.operation_name} completed in {self.execution_time:.3f}s")
        else:
            logger.error(f"[TIMING] {self.operation_name} failed after {self.execution_time:.3f}s: {exc_val}")
        
        return False  # Don't suppress exceptions

