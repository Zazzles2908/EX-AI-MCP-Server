"""
Continuation Manager for handling truncated API responses.

This module provides automatic continuation logic when API responses are truncated
due to max_tokens limits. It manages continuation sessions, tracks cumulative tokens,
prevents infinite loops, and merges response chunks.

Phase: 2.1.3 - Automatic Continuation
Created: 2025-10-21
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class ContinuationResult:
    """
    Result of a continuation operation.
    
    Contains the complete merged response, metadata about the continuation process,
    and any errors that occurred.
    """
    
    def __init__(self):
        self.complete_response: str = ""
        self.is_complete: bool = False
        self.attempts_made: int = 0
        self.total_tokens_used: int = 0
        self.error_message: Optional[str] = None
        self.was_truncated: bool = False
        self.response_chunks: List[str] = []
        self.continuation_metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for logging/debugging."""
        return {
            'complete_response_length': len(self.complete_response),
            'is_complete': self.is_complete,
            'attempts_made': self.attempts_made,
            'total_tokens_used': self.total_tokens_used,
            'error_message': self.error_message,
            'was_truncated': self.was_truncated,
            'chunks_count': len(self.response_chunks),
            'metadata': self.continuation_metadata
        }


class ContinuationSession:
    """
    Manages a single continuation session.
    
    Tracks cumulative tokens, attempt count, response chunks, and provides
    logic for determining when to continue and when to stop.
    """
    
    def __init__(
        self,
        session_id: str,
        max_total_tokens: int = 32000,
        max_attempts: int = 3,
        backoff_delays: Optional[List[float]] = None
    ):
        """
        Initialize a continuation session.
        
        Args:
            session_id: Unique identifier for this session
            max_total_tokens: Maximum cumulative tokens across all continuations
            max_attempts: Maximum number of continuation attempts
            backoff_delays: Delays between attempts (default: [0, 1, 2] seconds)
        """
        self.session_id = session_id
        self.max_total_tokens = max_total_tokens
        self.max_attempts = max_attempts
        self.backoff_delays = backoff_delays or [0, 1.0, 2.0]
        
        # State tracking
        self.cumulative_tokens = 0
        self.attempt_count = 0
        self.response_chunks: List[str] = []
        self.created_at = datetime.utcnow()
        self.last_attempt_at: Optional[datetime] = None
    
    def should_continue(self, new_response: str, new_tokens: int) -> tuple[bool, Optional[str]]:
        """
        Determine if continuation should proceed.
        
        Args:
            new_response: The latest response chunk
            new_tokens: Tokens used in the latest response
        
        Returns:
            Tuple of (should_continue, reason_if_not)
        """
        # Check max attempts
        if self.attempt_count >= self.max_attempts:
            return False, f"Max attempts reached ({self.max_attempts})"
        
        # Check cumulative tokens
        if self.cumulative_tokens + new_tokens >= self.max_total_tokens:
            return False, f"Max total tokens reached ({self.max_total_tokens})"
        
        # Check for duplicate response (no progress)
        if self.response_chunks and new_response.strip() == self.response_chunks[-1].strip():
            return False, "No progress detected (duplicate response)"
        
        # Check for empty response
        if not new_response.strip():
            return False, "Empty response received"
        
        return True, None
    
    def add_response_chunk(self, chunk: str, tokens_used: int):
        """Add a response chunk and update tracking."""
        self.response_chunks.append(chunk)
        self.cumulative_tokens += tokens_used
        self.attempt_count += 1
        self.last_attempt_at = datetime.utcnow()
    
    def get_backoff_delay(self) -> float:
        """Get the backoff delay for the current attempt."""
        if self.attempt_count < len(self.backoff_delays):
            return self.backoff_delays[self.attempt_count]
        return self.backoff_delays[-1]  # Use last delay for any additional attempts
    
    def merge_responses(self) -> str:
        """Merge all response chunks into a single response."""
        return ''.join(self.response_chunks)


class ContinuationManager:
    """
    Manages automatic continuation for truncated API responses.
    
    Provides centralized logic for detecting truncation, generating continuation
    prompts, tracking tokens, and merging responses.
    """
    
    def __init__(self):
        """Initialize the continuation manager."""
        self.active_sessions: Dict[str, ContinuationSession] = {}
    
    def create_session(
        self,
        session_id: str,
        max_total_tokens: int = 32000,
        max_attempts: int = 3
    ) -> ContinuationSession:
        """
        Create a new continuation session.
        
        Args:
            session_id: Unique identifier for this session
            max_total_tokens: Maximum cumulative tokens
            max_attempts: Maximum continuation attempts
        
        Returns:
            ContinuationSession instance
        """
        session = ContinuationSession(
            session_id=session_id,
            max_total_tokens=max_total_tokens,
            max_attempts=max_attempts
        )
        self.active_sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ContinuationSession]:
        """Get an existing session by ID."""
        return self.active_sessions.get(session_id)
    
    def cleanup_session(self, session_id: str):
        """Remove a session from active sessions."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def generate_continuation_prompt(
        self,
        original_request: str,
        last_response_chunk: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a context-aware continuation prompt.
        
        Args:
            original_request: The original user request
            last_response_chunk: The last response chunk (truncated)
            context: Additional context for the continuation
        
        Returns:
            Continuation prompt string
        """
        # Truncate original request for context (first 200 chars)
        request_preview = original_request[:200]
        if len(original_request) > 200:
            request_preview += "..."
        
        # Get last 100 chars of previous response for context
        response_preview = last_response_chunk[-100:] if len(last_response_chunk) > 100 else last_response_chunk
        
        continuation_prompt = f"""Please continue your previous response.

Context:
- You were responding to: "{request_preview}"
- Your last response was truncated at: "...{response_preview}"
- Please continue from where you left off, maintaining the same tone and context.

Continue:"""
        
        return continuation_prompt
    
    def extract_response_content(self, response: Dict[str, Any]) -> str:
        """
        Extract text content from API response.
        
        Handles different response formats from various providers.
        
        Args:
            response: API response dictionary
        
        Returns:
            Extracted text content
        """
        # Try common response formats
        if 'choices' in response and len(response['choices']) > 0:
            choice = response['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                return choice['message']['content']
            if 'text' in choice:
                return choice['text']
        
        if 'content' in response:
            return response['content']
        
        if 'text' in response:
            return response['text']
        
        logger.warning(f"Could not extract content from response: {response.keys()}")
        return ""
    
    def extract_token_usage(self, response: Dict[str, Any]) -> int:
        """
        Extract token usage from API response.
        
        Args:
            response: API response dictionary
        
        Returns:
            Total tokens used (0 if not available)
        """
        if 'usage' in response:
            usage = response['usage']
            if 'total_tokens' in usage:
                return usage['total_tokens']
            # Fallback: sum prompt + completion tokens
            return usage.get('prompt_tokens', 0) + usage.get('completion_tokens', 0)
        
        return 0

    async def continue_response_async(
        self,
        original_messages: List[Dict[str, Any]],
        initial_response: Dict[str, Any],
        provider_callable: Callable,
        session_id: Optional[str] = None,
        **kwargs
    ) -> ContinuationResult:
        """
        Automatically continue a truncated response (async version).

        Args:
            original_messages: Original conversation messages
            initial_response: Initial (truncated) response
            provider_callable: Async function to call for continuation
            session_id: Optional session ID (generated if not provided)
            **kwargs: Additional arguments to pass to provider_callable

        Returns:
            ContinuationResult with merged response and metadata
        """
        result = ContinuationResult()

        # Generate session ID if not provided
        if session_id is None:
            session_id = f"cont_{int(time.time() * 1000)}"

        # Create continuation session
        max_total_tokens = kwargs.get('max_total_tokens', 32000)
        max_attempts = kwargs.get('max_continuation_attempts', 3)
        session = self.create_session(session_id, max_total_tokens, max_attempts)

        try:
            # Extract initial response content and tokens
            initial_content = self.extract_response_content(initial_response)
            initial_tokens = self.extract_token_usage(initial_response)

            # Add initial response to session
            session.add_response_chunk(initial_content, initial_tokens)
            result.was_truncated = True

            logger.info(f"🔄 Starting continuation session {session_id} (attempt 1/{max_attempts})")

            # Check if we should continue
            from src.utils.truncation_detector import check_truncation
            truncation_info = check_truncation(initial_response, kwargs.get('model', 'unknown'))

            if not truncation_info.get('is_truncated'):
                # Not actually truncated, return as-is
                result.complete_response = initial_content
                result.is_complete = True
                result.attempts_made = 1
                result.total_tokens_used = initial_tokens
                return result

            # Continue until complete or max attempts reached
            current_messages = original_messages.copy()

            while session.attempt_count < max_attempts:
                # Apply backoff delay
                delay = session.get_backoff_delay()
                if delay > 0:
                    logger.debug(f"Applying backoff delay: {delay}s")
                    await asyncio.sleep(delay)

                # Generate continuation prompt
                original_request = current_messages[-1].get('content', '') if current_messages else ''
                last_chunk = session.response_chunks[-1]
                continuation_prompt = self.generate_continuation_prompt(
                    original_request,
                    last_chunk
                )

                # Add continuation prompt to messages
                continuation_messages = current_messages + [
                    {'role': 'assistant', 'content': last_chunk},
                    {'role': 'user', 'content': continuation_prompt}
                ]

                # Call provider for continuation
                logger.info(f"🔄 Continuation attempt {session.attempt_count + 1}/{max_attempts}")
                continuation_response = await provider_callable(continuation_messages, **kwargs)

                # Extract content and tokens
                continuation_content = self.extract_response_content(continuation_response)
                continuation_tokens = self.extract_token_usage(continuation_response)

                # Check if we should continue
                should_continue, reason = session.should_continue(continuation_content, continuation_tokens)

                if not should_continue:
                    logger.info(f"⏹️ Stopping continuation: {reason}")
                    break

                # Add to session
                session.add_response_chunk(continuation_content, continuation_tokens)

                # Check if this response is also truncated
                truncation_info = check_truncation(continuation_response, kwargs.get('model', 'unknown'))
                if not truncation_info.get('is_truncated'):
                    logger.info(f"✅ Continuation complete (not truncated)")
                    result.is_complete = True
                    break

            # Merge all response chunks
            result.complete_response = session.merge_responses()
            result.attempts_made = session.attempt_count
            result.total_tokens_used = session.cumulative_tokens
            result.response_chunks = session.response_chunks.copy()
            result.continuation_metadata = {
                'session_id': session_id,
                'max_attempts': max_attempts,
                'max_total_tokens': max_total_tokens,
                'created_at': session.created_at.isoformat(),
                'last_attempt_at': session.last_attempt_at.isoformat() if session.last_attempt_at else None
            }

            logger.info(
                f"✅ Continuation session {session_id} complete: "
                f"{result.attempts_made} attempts, {result.total_tokens_used} tokens, "
                f"{len(result.complete_response)} chars"
            )

        except Exception as e:
            logger.error(f"❌ Continuation session {session_id} failed: {e}", exc_info=True)
            result.error_message = str(e)
            # Return partial results if available
            if session.response_chunks:
                result.complete_response = session.merge_responses()
                result.attempts_made = session.attempt_count
                result.total_tokens_used = session.cumulative_tokens

        finally:
            # Cleanup session
            self.cleanup_session(session_id)

        return result

    def continue_response_sync(
        self,
        original_messages: List[Dict[str, Any]],
        initial_response: Dict[str, Any],
        provider_callable: Callable,
        session_id: Optional[str] = None,
        **kwargs
    ) -> ContinuationResult:
        """
        Automatically continue a truncated response (sync version).

        This is a synchronous wrapper that should NOT be used in async contexts.
        For async contexts, use continue_response_async instead.

        Args:
            original_messages: Original conversation messages
            initial_response: Initial (truncated) response
            provider_callable: Sync function to call for continuation
            session_id: Optional session ID (generated if not provided)
            **kwargs: Additional arguments to pass to provider_callable

        Returns:
            ContinuationResult with merged response and metadata
        """
        result = ContinuationResult()

        # Generate session ID if not provided
        if session_id is None:
            session_id = f"cont_{int(time.time() * 1000)}"

        # Create continuation session
        max_total_tokens = kwargs.get('max_total_tokens', 32000)
        max_attempts = kwargs.get('max_continuation_attempts', 3)
        session = self.create_session(session_id, max_total_tokens, max_attempts)

        try:
            # Extract initial response content and tokens
            initial_content = self.extract_response_content(initial_response)
            initial_tokens = self.extract_token_usage(initial_response)

            # Add initial response to session
            session.add_response_chunk(initial_content, initial_tokens)
            result.was_truncated = True

            logger.info(f"🔄 Starting continuation session {session_id} (attempt 1/{max_attempts})")

            # Check if we should continue
            from src.utils.truncation_detector import check_truncation
            truncation_info = check_truncation(initial_response, kwargs.get('model', 'unknown'))

            if not truncation_info.get('is_truncated'):
                # Not actually truncated, return as-is
                result.complete_response = initial_content
                result.is_complete = True
                result.attempts_made = 1
                result.total_tokens_used = initial_tokens
                return result

            # Continue until complete or max attempts reached
            current_messages = original_messages.copy()

            while session.attempt_count < max_attempts:
                # Apply backoff delay
                delay = session.get_backoff_delay()
                if delay > 0:
                    logger.debug(f"Applying backoff delay: {delay}s")
                    time.sleep(delay)

                # Generate continuation prompt
                original_request = current_messages[-1].get('content', '') if current_messages else ''
                last_chunk = session.response_chunks[-1]
                continuation_prompt = self.generate_continuation_prompt(
                    original_request,
                    last_chunk
                )

                # Add continuation prompt to messages
                continuation_messages = current_messages + [
                    {'role': 'assistant', 'content': last_chunk},
                    {'role': 'user', 'content': continuation_prompt}
                ]

                # Call provider for continuation
                logger.info(f"🔄 Continuation attempt {session.attempt_count + 1}/{max_attempts}")
                continuation_response = provider_callable(continuation_messages, **kwargs)

                # Extract content and tokens
                continuation_content = self.extract_response_content(continuation_response)
                continuation_tokens = self.extract_token_usage(continuation_response)

                # Check if we should continue
                should_continue, reason = session.should_continue(continuation_content, continuation_tokens)

                if not should_continue:
                    logger.info(f"⏹️ Stopping continuation: {reason}")
                    break

                # Add to session
                session.add_response_chunk(continuation_content, continuation_tokens)

                # Check if this response is also truncated
                truncation_info = check_truncation(continuation_response, kwargs.get('model', 'unknown'))
                if not truncation_info.get('is_truncated'):
                    logger.info(f"✅ Continuation complete (not truncated)")
                    result.is_complete = True
                    break

            # Merge all response chunks
            result.complete_response = session.merge_responses()
            result.attempts_made = session.attempt_count
            result.total_tokens_used = session.cumulative_tokens
            result.response_chunks = session.response_chunks.copy()
            result.continuation_metadata = {
                'session_id': session_id,
                'max_attempts': max_attempts,
                'max_total_tokens': max_total_tokens,
                'created_at': session.created_at.isoformat(),
                'last_attempt_at': session.last_attempt_at.isoformat() if session.last_attempt_at else None
            }

            logger.info(
                f"✅ Continuation session {session_id} complete: "
                f"{result.attempts_made} attempts, {result.total_tokens_used} tokens, "
                f"{len(result.complete_response)} chars"
            )

        except Exception as e:
            logger.error(f"❌ Continuation session {session_id} failed: {e}", exc_info=True)
            result.error_message = str(e)
            # Return partial results if available
            if session.response_chunks:
                result.complete_response = session.merge_responses()
                result.attempts_made = session.attempt_count
                result.total_tokens_used = session.cumulative_tokens

        finally:
            # Cleanup session
            self.cleanup_session(session_id)

        return result


# Global continuation manager instance
_continuation_manager = None


def get_continuation_manager() -> ContinuationManager:
    """Get the global continuation manager instance."""
    global _continuation_manager
    if _continuation_manager is None:
        _continuation_manager = ContinuationManager()
    return _continuation_manager

