"""
Custom exceptions for file management operations

Provides structured error handling with provider context, error codes,
and retry information for debugging and monitoring.
"""

from typing import Optional
from src.file_management.models import FileReference


class FileManagementError(Exception):
    """Base exception for all file management operations"""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        error_code: Optional[str] = None
    ):
        self.provider = provider
        self.error_code = error_code
        super().__init__(message)
    
    def to_dict(self):
        """Convert exception to dictionary for logging"""
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "provider": self.provider,
            "error_code": self.error_code
        }


class FileUploadError(FileManagementError):
    """Exception raised when file upload fails"""
    
    def __init__(
        self,
        message: str,
        provider: str,
        error_code: str,
        retryable: bool = True,
        file_path: Optional[str] = None
    ):
        self.retryable = retryable
        self.file_path = file_path
        super().__init__(message, provider, error_code)
    
    def to_dict(self):
        """Convert exception to dictionary for logging"""
        data = super().to_dict()
        data.update({
            "retryable": self.retryable,
            "file_path": self.file_path
        })
        return data


class FileDownloadError(FileManagementError):
    """Exception raised when file download fails"""
    
    def __init__(
        self,
        message: str,
        provider: str,
        error_code: str,
        file_ref: Optional[FileReference] = None
    ):
        self.file_ref = file_ref
        super().__init__(message, provider, error_code)
    
    def to_dict(self):
        """Convert exception to dictionary for logging"""
        data = super().to_dict()
        if self.file_ref:
            data["file_reference"] = self.file_ref.dict()
        return data


class FileDeleteError(FileManagementError):
    """Exception raised when file deletion fails"""
    
    def __init__(
        self,
        message: str,
        provider: str,
        error_code: str,
        file_ref: Optional[FileReference] = None
    ):
        self.file_ref = file_ref
        super().__init__(message, provider, error_code)
    
    def to_dict(self):
        """Convert exception to dictionary for logging"""
        data = super().to_dict()
        if self.file_ref:
            data["file_reference"] = self.file_ref.dict()
        return data


class FileDuplicateError(FileManagementError):
    """Exception raised when attempting to upload a duplicate file"""
    
    def __init__(
        self,
        message: str,
        existing_file: FileReference
    ):
        self.existing_file = existing_file
        super().__init__(message)
    
    def to_dict(self):
        """Convert exception to dictionary for logging"""
        data = super().to_dict()
        data["existing_file"] = self.existing_file.dict()
        return data


class FileNotFoundError(FileManagementError):
    """Exception raised when file is not found"""
    
    def __init__(
        self,
        file_ref: Optional[FileReference] = None,
        file_path: Optional[str] = None,
        provider: Optional[str] = None
    ):
        self.file_ref = file_ref
        self.file_path = file_path
        
        if file_ref:
            message = f"File not found: {file_ref.internal_id}"
            provider = file_ref.provider
        elif file_path:
            message = f"File not found: {file_path}"
        else:
            message = "File not found"
        
        super().__init__(message, provider)
    
    def to_dict(self):
        """Convert exception to dictionary for logging"""
        data = super().to_dict()
        if self.file_ref:
            data["file_reference"] = self.file_ref.dict()
        if self.file_path:
            data["file_path"] = self.file_path
        return data


class FileValidationError(FileManagementError):
    """Exception raised when file validation fails"""
    
    def __init__(
        self,
        message: str,
        file_path: str,
        validation_errors: Optional[dict] = None
    ):
        self.file_path = file_path
        self.validation_errors = validation_errors or {}
        super().__init__(message)
    
    def to_dict(self):
        """Convert exception to dictionary for logging"""
        data = super().to_dict()
        data.update({
            "file_path": self.file_path,
            "validation_errors": self.validation_errors
        })
        return data


class ProviderNotFoundError(FileManagementError):
    """Exception raised when requested provider is not available"""
    
    def __init__(
        self,
        provider: str,
        available_providers: Optional[list] = None
    ):
        self.available_providers = available_providers or []
        message = f"Provider not found: {provider}"
        if self.available_providers:
            message += f". Available providers: {', '.join(self.available_providers)}"
        super().__init__(message, provider)
    
    def to_dict(self):
        """Convert exception to dictionary for logging"""
        data = super().to_dict()
        data["available_providers"] = self.available_providers
        return data

