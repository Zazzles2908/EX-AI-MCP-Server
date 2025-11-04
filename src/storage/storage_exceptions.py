"""
Storage Exception Classes

Custom exception types for Supabase storage operations.
These exceptions help distinguish between retryable and non-retryable errors.
"""


class RetryableError(Exception):
    """Base class for retryable errors.

    These are temporary failures that may succeed on retry:
    - Network timeouts
    - Rate limiting
    - Temporary service unavailability
    """
    pass


class NonRetryableError(Exception):
    """Base class for non-retryable errors.

    These are permanent failures that won't succeed on retry:
    - Invalid credentials
    - Schema violations
    - Permission denied
    - Resource not found
    """
    pass
