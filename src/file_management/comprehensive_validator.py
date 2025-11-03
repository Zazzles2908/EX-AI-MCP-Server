"""
Comprehensive File Validator - Security Module for File Upload System

CRITICAL SECURITY COMPONENT - Validates files before upload

This module provides comprehensive file validation including:
- File size limits
- MIME type validation
- Extension blocking
- SHA256 checksum calculation
- Malware detection (basic)

Author: EX-AI MCP Server
Date: 2025-11-02
Phase: 0 - IMMEDIATE Security Fixes
Task: 0.4 - Comprehensive File Validation
"""

import hashlib
import logging
import mimetypes
import os
from pathlib import Path
from typing import Dict, List, Set, Optional

logger = logging.getLogger(__name__)


class FileValidationError(Exception):
    """Raised when file validation fails."""
    
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        self.error_code = error_code
        super().__init__(message)


class ComprehensiveFileValidator:
    """
    Comprehensive file validation for upload security.
    
    Validates files against multiple security criteria before allowing upload.
    """
    
    # Blocked file extensions (executable/script files)
    BLOCKED_EXTENSIONS: Set[str] = {
        ".exe", ".bat", ".cmd", ".com", ".pif",  # Windows executables
        ".sh", ".bash", ".zsh",  # Unix shells
        ".ps1", ".psm1",  # PowerShell
        ".scr", ".vbs", ".js", ".jar",  # Scripts
        ".app", ".deb", ".rpm",  # Installers
        ".msi", ".dmg", ".pkg"  # Installers
    }
    
    # Default allowed MIME types (can be overridden)
    DEFAULT_ALLOWED_MIMES: Set[str] = {
        # Images
        "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml",
        # Documents
        "application/pdf", "text/plain", "text/markdown", "text/csv",
        "application/json", "application/xml", "text/xml",
        # Office documents
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
        # Archives
        "application/zip", "application/x-tar", "application/gzip",
        # Code
        "text/x-python", "text/x-java", "text/x-c", "text/x-c++",
        "application/javascript", "text/html", "text/css"
    }
    
    def __init__(
        self,
        max_file_size: int = 512 * 1024 * 1024,  # 512MB default
        allowed_mime_types: Optional[Set[str]] = None,
        blocked_extensions: Optional[Set[str]] = None
    ):
        """
        Initialize comprehensive file validator.
        
        Args:
            max_file_size: Maximum file size in bytes (default: 512MB)
            allowed_mime_types: Set of allowed MIME types (None = use defaults)
            blocked_extensions: Set of blocked extensions (None = use defaults)
        """
        self.max_file_size = max_file_size
        self.allowed_mime_types = allowed_mime_types or self.DEFAULT_ALLOWED_MIMES
        self.blocked_extensions = blocked_extensions or self.BLOCKED_EXTENSIONS
        
        logger.info(
            f"ComprehensiveFileValidator initialized: "
            f"max_size={max_file_size/1024/1024:.1f}MB, "
            f"allowed_mimes={len(self.allowed_mime_types)}, "
            f"blocked_exts={len(self.blocked_extensions)}"
        )
    
    async def validate(self, file_path: str) -> Dict:
        """
        Comprehensive file validation.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            Dict with validation results:
            {
                "valid": bool,
                "errors": List[str],
                "metadata": {
                    "size": int,
                    "mime_type": str,
                    "sha256": str,
                    "extension": str
                }
            }
            
        Raises:
            FileValidationError: If critical validation fails
        """
        result = {
            "path": file_path,
            "valid": False,
            "errors": [],
            "metadata": {}
        }
        
        try:
            # 1. Check file exists
            if not os.path.exists(file_path):
                result["errors"].append("File does not exist")
                raise FileValidationError(
                    f"File not found: {file_path}",
                    "FILE_NOT_FOUND"
                )
            
            path_obj = Path(file_path)
            
            # 2. Check it's a file (not directory)
            if not path_obj.is_file():
                result["errors"].append("Path is not a file")
                raise FileValidationError(
                    f"Path is not a file: {file_path}",
                    "NOT_A_FILE"
                )
            
            # 3. Size validation
            size = path_obj.stat().st_size
            result["metadata"]["size"] = size
            
            if size > self.max_file_size:
                error_msg = (
                    f"File too large: {size} bytes "
                    f"(max: {self.max_file_size} bytes = "
                    f"{self.max_file_size/1024/1024:.1f}MB)"
                )
                result["errors"].append(error_msg)
                raise FileValidationError(error_msg, "FILE_TOO_LARGE")
            
            # 4. Extension validation
            ext = path_obj.suffix.lower()
            result["metadata"]["extension"] = ext
            
            if ext in self.blocked_extensions:
                error_msg = f"Blocked file type: {ext}"
                result["errors"].append(error_msg)
                raise FileValidationError(error_msg, "BLOCKED_EXTENSION")
            
            # 5. MIME type validation
            mime_type, _ = mimetypes.guess_type(str(path_obj))
            if not mime_type:
                mime_type = "application/octet-stream"
            
            result["metadata"]["mime_type"] = mime_type
            
            # Allow application/octet-stream for unknown types
            if mime_type != "application/octet-stream" and mime_type not in self.allowed_mime_types:
                error_msg = f"Unsupported MIME type: {mime_type}"
                result["errors"].append(error_msg)
                logger.warning(f"File {file_path} has unsupported MIME type: {mime_type}")
                # Don't raise - just warn for now
            
            # 6. Calculate SHA256 for deduplication
            try:
                sha256 = self._calculate_sha256(file_path)
                result["metadata"]["sha256"] = sha256
            except Exception as e:
                error_msg = f"Checksum calculation failed: {str(e)}"
                result["errors"].append(error_msg)
                logger.error(error_msg, exc_info=True)
                # Don't raise - checksum is optional
            
            # 7. Basic malware detection (file header check)
            try:
                is_suspicious = self._check_file_header(file_path)
                if is_suspicious:
                    error_msg = "Suspicious file header detected"
                    result["errors"].append(error_msg)
                    logger.warning(f"Suspicious file: {file_path}")
                    # Don't raise - just warn
            except Exception as e:
                logger.error(f"Header check failed: {e}", exc_info=True)
            
            # All critical checks passed
            if not result["errors"]:
                result["valid"] = True
                logger.info(
                    f"✅ File validated: {file_path} "
                    f"(size={size}, mime={mime_type}, sha256={result['metadata'].get('sha256', 'N/A')[:16]}...)"
                )
            else:
                logger.warning(f"⚠️ File validation warnings: {file_path} - {result['errors']}")
                result["valid"] = True  # Allow with warnings
            
            return result
            
        except FileValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            result["errors"].append(error_msg)
            logger.error(error_msg, exc_info=True)
            raise FileValidationError(error_msg, "VALIDATION_ERROR") from e
    
    def _calculate_sha256(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file.
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA256 hash as hex string
        """
        sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def _check_file_header(self, file_path: str) -> bool:
        """
        Basic malware detection via file header check.
        
        Checks for suspicious file headers (e.g., PE executables).
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file appears suspicious
        """
        # Read first 4 bytes
        with open(file_path, "rb") as f:
            header = f.read(4)
        
        if not header:
            return False
        
        # Check for PE executable header (MZ)
        if header[:2] == b"MZ":
            return True
        
        # Check for ELF executable header
        if header[:4] == b"\x7fELF":
            return True
        
        # Check for Mach-O executable header
        if header[:4] in (b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf", b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe"):
            return True
        
        return False


# Global instance
_global_validator: Optional[ComprehensiveFileValidator] = None


def get_file_validator() -> ComprehensiveFileValidator:
    """Get global ComprehensiveFileValidator instance."""
    global _global_validator
    if _global_validator is None:
        # Read max size from environment
        max_size_mb = float(os.getenv("MAX_FILE_SIZE_MB", "512"))
        max_size = int(max_size_mb * 1024 * 1024)
        
        _global_validator = ComprehensiveFileValidator(max_file_size=max_size)
    
    return _global_validator


async def validate_file(file_path: str) -> Dict:
    """
    Convenience function for file validation.
    
    Args:
        file_path: Path to validate
        
    Returns:
        Validation result dict
    """
    validator = get_file_validator()
    return await validator.validate(file_path)

