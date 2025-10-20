"""
Correlation ID Middleware

Provides request correlation tracking across all system components.
Enables tracing of requests from entry point through all downstream operations.

Created: 2025-10-18
EXAI Consultation: 30441b5d-87d0-4f31-864e-d40e8dcbcad2
Critical Gap #3: Correlation ID Tracking (6 hours)
"""

import uuid
import logging
import contextvars
from typing import Optional

logger = logging.getLogger(__name__)

# Context variable for correlation ID (thread-safe)
_correlation_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'correlation_id',
    default=None
)


def get_correlation_id() -> Optional[str]:
    """
    Get the current correlation ID from context.
    
    Returns:
        Correlation ID or None if not set
    """
    return _correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    """
    Set the correlation ID in context.
    
    Args:
        correlation_id: Correlation ID to set
    """
    _correlation_id_var.set(correlation_id)


def generate_correlation_id() -> str:
    """
    Generate a new correlation ID.
    
    Returns:
        New UUID-based correlation ID
    """
    return str(uuid.uuid4())


def ensure_correlation_id() -> str:
    """
    Ensure a correlation ID exists, generating one if needed.
    
    Returns:
        Current or newly generated correlation ID
    """
    correlation_id = get_correlation_id()
    if not correlation_id:
        correlation_id = generate_correlation_id()
        set_correlation_id(correlation_id)
    return correlation_id


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter that adds correlation ID to log records.
    
    Usage:
        handler.addFilter(CorrelationIdFilter())
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID to log record"""
        correlation_id = get_correlation_id()
        record.correlation_id = correlation_id if correlation_id else 'N/A'
        return True


def setup_correlation_logging() -> None:
    """
    Setup correlation ID logging for all handlers.
    
    Adds correlation ID filter to all existing handlers and updates
    the logging format to include correlation ID.
    """
    # Add filter to all handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(CorrelationIdFilter())
    
    # Update format to include correlation ID
    # Note: This assumes handlers use a formatter
    for handler in root_logger.handlers:
        if handler.formatter:
            # Get current format string
            current_format = handler.formatter._fmt
            
            # Add correlation ID if not already present
            if 'correlation_id' not in current_format:
                # Insert correlation ID after timestamp
                new_format = current_format.replace(
                    '%(levelname)s',
                    '[%(correlation_id)s] %(levelname)s'
                )
                handler.setFormatter(logging.Formatter(new_format))
    
    logger.info("[CORRELATION] Correlation ID logging configured")


# ============================================================================
# WEBSOCKET INTEGRATION
# ============================================================================

async def websocket_correlation_wrapper(websocket, handler):
    """
    WebSocket middleware to add correlation ID tracking.
    
    Args:
        websocket: WebSocket connection
        handler: Handler function to wrap
    """
    # Generate correlation ID for this connection
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    
    logger.info(f"[CORRELATION] New WebSocket connection: {correlation_id}")
    
    try:
        await handler(websocket)
    finally:
        logger.info(f"[CORRELATION] WebSocket connection closed: {correlation_id}")


# ============================================================================
# HTTP INTEGRATION (for health/metrics endpoints)
# ============================================================================

async def http_correlation_middleware(request, handler):
    """
    HTTP middleware to add correlation ID tracking.
    
    Args:
        request: HTTP request
        handler: Handler function to wrap
    
    Returns:
        HTTP response with correlation ID header
    """
    # Get or generate correlation ID
    correlation_id = request.headers.get('X-Correlation-ID')
    if not correlation_id:
        correlation_id = generate_correlation_id()
    
    set_correlation_id(correlation_id)
    
    logger.debug(f"[CORRELATION] HTTP request: {correlation_id} {request.method} {request.path}")
    
    try:
        response = await handler(request)
        
        # Add correlation ID to response headers
        response.headers['X-Correlation-ID'] = correlation_id
        
        return response
        
    except Exception as e:
        logger.error(f"[CORRELATION] Request failed: {correlation_id} - {e}")
        raise


# ============================================================================
# PROVIDER INTEGRATION
# ============================================================================

def with_correlation(func):
    """
    Decorator to ensure correlation ID is propagated to provider calls.
    
    Usage:
        @with_correlation
        def api_call(...):
            ...
    """
    def wrapper(*args, **kwargs):
        # Ensure correlation ID exists
        correlation_id = ensure_correlation_id()
        
        # Add correlation ID to kwargs if not present
        if 'correlation_id' not in kwargs:
            kwargs['correlation_id'] = correlation_id
        
        # Call function
        return func(*args, **kwargs)
    
    return wrapper


async def async_with_correlation(func):
    """
    Async decorator to ensure correlation ID is propagated to provider calls.
    
    Usage:
        @async_with_correlation
        async def api_call(...):
            ...
    """
    async def wrapper(*args, **kwargs):
        # Ensure correlation ID exists
        correlation_id = ensure_correlation_id()
        
        # Add correlation ID to kwargs if not present
        if 'correlation_id' not in kwargs:
            kwargs['correlation_id'] = correlation_id
        
        # Call function
        return await func(*args, **kwargs)
    
    return wrapper


# ============================================================================
# STORAGE INTEGRATION
# ============================================================================

def add_correlation_to_metadata(metadata: dict) -> dict:
    """
    Add correlation ID to metadata dict.
    
    Args:
        metadata: Metadata dictionary
    
    Returns:
        Updated metadata with correlation ID
    """
    correlation_id = get_correlation_id()
    if correlation_id:
        metadata = metadata.copy() if metadata else {}
        metadata['correlation_id'] = correlation_id
    return metadata


# ============================================================================
# MONITORING INTEGRATION
# ============================================================================

def get_correlation_context() -> dict:
    """
    Get correlation context for monitoring events.
    
    Returns:
        Dictionary with correlation ID
    """
    correlation_id = get_correlation_id()
    return {
        'correlation_id': correlation_id if correlation_id else 'N/A'
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def log_with_correlation(level: str, message: str, **kwargs) -> None:
    """
    Log a message with correlation ID context.
    
    Args:
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **kwargs: Additional context
    """
    correlation_id = get_correlation_id()
    context = {'correlation_id': correlation_id} if correlation_id else {}
    context.update(kwargs)
    
    log_func = getattr(logger, level.lower())
    log_func(message, extra=context)

