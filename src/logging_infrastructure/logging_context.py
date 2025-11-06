"""
Logging Context Management for EXAI-MCP Server
===============================================

Provides context propagation for structured logging using contextvars.
Works correctly across async boundaries.

Date: 2025-10-22
Reference: EXAI consultation (Continuation: 32864286-932c-4b84-aefa-e5bd19c208bd)
"""

import uuid
from contextlib import contextmanager
from typing import Optional, Generator
from .logging_manager import request_id_var, session_id_var, user_id_var


class LoggingContext:
    """
    Context manager for setting logging context variables.
    
    Uses contextvars for proper async support and automatic propagation
    across async boundaries.
    
    Example:
        with LoggingContext.request_context(request_id="123", user_id="user456"):
            logger.info("Operation completed")  # Automatically includes request_id and user_id
    """
    
    @staticmethod
    @contextmanager
    def request_context(
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Generator[None, None, None]:
        """
        Context manager for setting logging context.
        
        Args:
            request_id: Optional request identifier (generated if not provided)
            session_id: Optional session identifier
            user_id: Optional user identifier
            
        Yields:
            None
            
        Example:
            with LoggingContext.request_context(request_id="req-123"):
                logger.info("Processing request")  # Includes request_id
        """
        token_request = None
        token_session = None
        token_user = None
        
        try:
            # Generate request_id if not provided
            if request_id is None:
                request_id = LoggingContext.generate_request_id()
            
            # Set context variables
            if request_id:
                token_request = request_id_var.set(request_id)
            if session_id:
                token_session = session_id_var.set(session_id)
            if user_id:
                token_user = user_id_var.set(user_id)
            
            yield
            
        finally:
            # Reset context variables
            if token_request:
                request_id_var.reset(token_request)
            if token_session:
                session_id_var.reset(token_session)
            if token_user:
                user_id_var.reset(token_user)
    
    @staticmethod
    @contextmanager
    def session_context(session_id: str, user_id: Optional[str] = None) -> Generator[None, None, None]:
        """
        Context manager for session-level logging context.
        
        Args:
            session_id: Session identifier
            user_id: Optional user identifier
            
        Yields:
            None
            
        Example:
            with LoggingContext.session_context(session_id="sess-456"):
                logger.info("Session started")  # Includes session_id
        """
        token_session = None
        token_user = None
        
        try:
            if session_id:
                token_session = session_id_var.set(session_id)
            if user_id:
                token_user = user_id_var.set(user_id)
            
            yield
            
        finally:
            if token_session:
                session_id_var.reset(token_session)
            if token_user:
                user_id_var.reset(token_user)
    
    @staticmethod
    def set_request_id(request_id: str):
        """
        Set request_id in current context.
        
        Args:
            request_id: Request identifier
        """
        request_id_var.set(request_id)
    
    @staticmethod
    def set_session_id(session_id: str):
        """
        Set session_id in current context.
        
        Args:
            session_id: Session identifier
        """
        session_id_var.set(session_id)
    
    @staticmethod
    def set_user_id(user_id: str):
        """
        Set user_id in current context.
        
        Args:
            user_id: User identifier
        """
        user_id_var.set(user_id)
    
    @staticmethod
    def get_request_id() -> Optional[str]:
        """
        Get current request_id from context.
        
        Returns:
            Current request_id or None
        """
        return request_id_var.get()
    
    @staticmethod
    def get_session_id() -> Optional[str]:
        """
        Get current session_id from context.
        
        Returns:
            Current session_id or None
        """
        return session_id_var.get()
    
    @staticmethod
    def get_user_id() -> Optional[str]:
        """
        Get current user_id from context.
        
        Returns:
            Current user_id or None
        """
        return user_id_var.get()
    
    @staticmethod
    def generate_request_id() -> str:
        """
        Generate a unique request ID.
        
        Returns:
            UUID-based request identifier
        """
        return f"req-{uuid.uuid4()}"
    
    @staticmethod
    def generate_session_id() -> str:
        """
        Generate a unique session ID.
        
        Returns:
            UUID-based session identifier
        """
        return f"sess-{uuid.uuid4()}"
    
    @staticmethod
    def clear_context():
        """
        Clear all logging context variables.
        
        Useful for cleanup or testing.
        """
        request_id_var.set(None)
        session_id_var.set(None)
        user_id_var.set(None)

