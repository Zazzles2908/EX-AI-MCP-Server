"""
Standardized Error Handling for File Management

Provides consistent error codes and responses across all file operations.
Replaces inconsistent error handling across providers.

CRITICAL CONSISTENCY FIX (2025-11-02): Task 2.3
- Standardizes error codes across all providers
- Provides consistent error responses
- Enables better error tracking and debugging

Author: EX-AI MCP Server
Date: 2025-11-02
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class FileUploadErrorCode(Enum):
    """Standardized error codes for file upload operations"""
    
    # Validation Errors (1xxx)
    VALIDATION_FAILED = "1001"
    INVALID_FILE_TYPE = "1002"
    FILE_TOO_LARGE = "1003"
    FILE_NOT_FOUND = "1004"
    INVALID_PATH = "1005"
    MALICIOUS_FILE = "1006"
    INVALID_EXTENSION = "1007"
    
    # Authentication/Authorization Errors (2xxx)
    UNAUTHORIZED = "2001"
    INVALID_TOKEN = "2002"
    TOKEN_EXPIRED = "2003"
    QUOTA_EXCEEDED = "2004"
    PERMISSION_DENIED = "2005"
    
    # Provider Errors (3xxx)
    PROVIDER_ERROR = "3001"
    PROVIDER_UNAVAILABLE = "3002"
    CIRCUIT_BREAKER_OPEN = "3003"
    ALL_PROVIDERS_UNAVAILABLE = "3004"
    INVALID_PURPOSE = "3005"
    UPLOAD_FAILED = "3006"
    DELETE_FAILED = "3007"
    
    # Concurrency Errors (4xxx)
    FILE_LOCKED = "4001"
    LOCK_TIMEOUT = "4002"
    CONCURRENT_UPLOAD = "4003"
    
    # Storage Errors (5xxx)
    STORAGE_ERROR = "5001"
    SUPABASE_ERROR = "5002"
    DATABASE_ERROR = "5003"
    
    # System Errors (9xxx)
    UNEXPECTED_ERROR = "9001"
    CONFIGURATION_ERROR = "9002"
    NETWORK_ERROR = "9003"


@dataclass
class ErrorDetail:
    """Detailed error information"""
    code: FileUploadErrorCode
    message: str
    provider: Optional[str] = None
    file_path: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "error_code": self.code.value,
            "error_name": self.code.name,
            "message": self.message,
            "provider": self.provider,
            "file_path": self.file_path,
            "user_id": self.user_id,
            "metadata": self.metadata or {}
        }
    
    def to_http_response(self) -> tuple[int, Dict[str, Any]]:
        """
        Convert to HTTP response (status code, body).
        
        Returns:
            Tuple of (status_code, response_body)
        """
        # Map error codes to HTTP status codes
        status_map = {
            # Validation errors -> 400 Bad Request
            FileUploadErrorCode.VALIDATION_FAILED: 400,
            FileUploadErrorCode.INVALID_FILE_TYPE: 400,
            FileUploadErrorCode.FILE_TOO_LARGE: 400,
            FileUploadErrorCode.FILE_NOT_FOUND: 404,
            FileUploadErrorCode.INVALID_PATH: 400,
            FileUploadErrorCode.MALICIOUS_FILE: 400,
            FileUploadErrorCode.INVALID_EXTENSION: 400,
            
            # Auth errors -> 401/403
            FileUploadErrorCode.UNAUTHORIZED: 401,
            FileUploadErrorCode.INVALID_TOKEN: 401,
            FileUploadErrorCode.TOKEN_EXPIRED: 401,
            FileUploadErrorCode.QUOTA_EXCEEDED: 403,
            FileUploadErrorCode.PERMISSION_DENIED: 403,
            
            # Provider errors -> 502/503
            FileUploadErrorCode.PROVIDER_ERROR: 502,
            FileUploadErrorCode.PROVIDER_UNAVAILABLE: 503,
            FileUploadErrorCode.CIRCUIT_BREAKER_OPEN: 503,
            FileUploadErrorCode.ALL_PROVIDERS_UNAVAILABLE: 503,
            FileUploadErrorCode.INVALID_PURPOSE: 400,
            FileUploadErrorCode.UPLOAD_FAILED: 502,
            FileUploadErrorCode.DELETE_FAILED: 502,
            
            # Concurrency errors -> 409/423
            FileUploadErrorCode.FILE_LOCKED: 423,
            FileUploadErrorCode.LOCK_TIMEOUT: 408,
            FileUploadErrorCode.CONCURRENT_UPLOAD: 409,
            
            # Storage errors -> 500
            FileUploadErrorCode.STORAGE_ERROR: 500,
            FileUploadErrorCode.SUPABASE_ERROR: 500,
            FileUploadErrorCode.DATABASE_ERROR: 500,
            
            # System errors -> 500
            FileUploadErrorCode.UNEXPECTED_ERROR: 500,
            FileUploadErrorCode.CONFIGURATION_ERROR: 500,
            FileUploadErrorCode.NETWORK_ERROR: 502,
        }
        
        status_code = status_map.get(self.code, 500)
        
        return status_code, {
            "success": False,
            "error": self.to_dict()
        }


class StandardizedFileUploadError(Exception):
    """
    Base exception for all file upload errors.
    
    Provides consistent error handling across all providers.
    """
    
    def __init__(
        self,
        code: FileUploadErrorCode,
        message: str,
        provider: Optional[str] = None,
        file_path: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize standardized error.
        
        Args:
            code: Error code from FileUploadErrorCode enum
            message: Human-readable error message
            provider: Provider name (kimi, glm, etc.)
            file_path: File path (if applicable)
            user_id: User ID (if applicable)
            metadata: Additional error metadata
        """
        self.detail = ErrorDetail(
            code=code,
            message=message,
            provider=provider,
            file_path=file_path,
            user_id=user_id,
            metadata=metadata
        )
        
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.detail.to_dict()
    
    def to_http_response(self) -> tuple[int, Dict[str, Any]]:
        """Convert to HTTP response"""
        return self.detail.to_http_response()


# Convenience exception classes for common errors

class FileValidationError(StandardizedFileUploadError):
    """File validation failed"""
    def __init__(self, message: str, provider: str = None, file_path: str = None):
        super().__init__(
            code=FileUploadErrorCode.VALIDATION_FAILED,
            message=message,
            provider=provider,
            file_path=file_path
        )


class QuotaExceededError(StandardizedFileUploadError):
    """User quota exceeded"""
    def __init__(self, message: str, user_id: str = None):
        super().__init__(
            code=FileUploadErrorCode.QUOTA_EXCEEDED,
            message=message,
            user_id=user_id
        )


class ProviderUnavailableError(StandardizedFileUploadError):
    """Provider unavailable"""
    def __init__(self, message: str, provider: str = None):
        super().__init__(
            code=FileUploadErrorCode.PROVIDER_UNAVAILABLE,
            message=message,
            provider=provider
        )


class FileLockError(StandardizedFileUploadError):
    """File is locked"""
    def __init__(self, message: str, file_path: str = None):
        super().__init__(
            code=FileUploadErrorCode.FILE_LOCKED,
            message=message,
            file_path=file_path
        )


class InvalidPurposeError(StandardizedFileUploadError):
    """Invalid upload purpose"""
    def __init__(self, message: str, provider: str = None):
        super().__init__(
            code=FileUploadErrorCode.INVALID_PURPOSE,
            message=message,
            provider=provider
        )


# Error code to exception class mapping
ERROR_CODE_TO_EXCEPTION = {
    FileUploadErrorCode.VALIDATION_FAILED: FileValidationError,
    FileUploadErrorCode.QUOTA_EXCEEDED: QuotaExceededError,
    FileUploadErrorCode.PROVIDER_UNAVAILABLE: ProviderUnavailableError,
    FileUploadErrorCode.FILE_LOCKED: FileLockError,
    FileUploadErrorCode.INVALID_PURPOSE: InvalidPurposeError,
}


def create_error_from_code(
    code: FileUploadErrorCode,
    message: str,
    **kwargs
) -> StandardizedFileUploadError:
    """
    Create appropriate exception from error code.
    
    Args:
        code: Error code
        message: Error message
        **kwargs: Additional error details
        
    Returns:
        Appropriate exception instance
    """
    exception_class = ERROR_CODE_TO_EXCEPTION.get(code, StandardizedFileUploadError)
    return exception_class(message, **kwargs)

