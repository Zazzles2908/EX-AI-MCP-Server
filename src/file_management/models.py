"""
Data models for file management

Provides Pydantic models for file references and metadata with
validation, serialization, and type safety.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import re


class FileReference(BaseModel):
    """
    Provider-agnostic file reference
    
    Represents a file that may be stored across multiple providers
    with a single internal ID for tracking and deduplication.
    
    Attributes:
        internal_id: Internal UUID for this file
        provider_id: Provider-specific file ID
        provider: Provider name (kimi, glm, local, etc.)
        file_hash: SHA256 hash of file content
        size: File size in bytes
        mime_type: MIME type of the file
        original_name: Original filename
        created_at: When the file was first uploaded
        accessed_at: Last access timestamp
        metadata: Additional provider-specific metadata
    """
    
    internal_id: str = Field(
        ...,
        description="Internal UUID for this file",
        min_length=36,
        max_length=36
    )
    
    provider_id: str = Field(
        ...,
        description="Provider-specific file ID"
    )
    
    provider: str = Field(
        ...,
        pattern="^(kimi|glm|local|supabase)$",
        description="Provider name"
    )
    
    file_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="SHA256 hash of file content"
    )
    
    size: int = Field(
        ...,
        gt=0,
        description="File size in bytes"
    )
    
    mime_type: str = Field(
        ...,
        description="MIME type of the file"
    )
    
    original_name: str = Field(
        ...,
        description="Original filename"
    )
    
    created_at: Optional[datetime] = Field(
        default=None,
        description="When the file was first uploaded"
    )
    
    accessed_at: Optional[datetime] = Field(
        default=None,
        description="Last access timestamp"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional provider-specific metadata"
    )
    
    @validator('file_hash')
    def validate_sha256(cls, v):
        """Validate SHA256 hash format"""
        if not re.match(r'^[a-f0-9]{64}$', v.lower()):
            raise ValueError('Invalid SHA256 hash format. Must be 64 hexadecimal characters.')
        return v.lower()
    
    @validator('internal_id')
    def validate_uuid(cls, v):
        """Validate UUID format"""
        # Basic UUID format validation
        if not re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', v.lower()):
            raise ValueError('Invalid UUID format')
        return v.lower()
    
    @validator('mime_type')
    def validate_mime_type(cls, v):
        """Validate MIME type format"""
        if not re.match(r'^[a-z]+/[a-z0-9\-\+\.]+$', v.lower()):
            raise ValueError('Invalid MIME type format')
        return v.lower()
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        validate_assignment = True
    
    def to_supabase_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for Supabase storage
        
        Returns:
            Dictionary with snake_case keys for database storage
        """
        return {
            "id": self.internal_id,
            "provider_file_id": self.provider_id,
            "provider": self.provider,
            "sha256": self.file_hash,
            "size_bytes": self.size,
            "mime_type": self.mime_type,
            "original_name": self.original_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "accessed_at": self.accessed_at.isoformat() if self.accessed_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_supabase_dict(cls, data: Dict[str, Any]) -> "FileReference":
        """
        Create FileReference from Supabase data
        
        Args:
            data: Dictionary from Supabase query
            
        Returns:
            FileReference instance
        """
        return cls(
            internal_id=data["id"],
            provider_id=data["provider_file_id"],
            provider=data["provider"],
            file_hash=data["sha256"],
            size=data["size_bytes"],
            mime_type=data["mime_type"],
            original_name=data["original_name"],
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            accessed_at=datetime.fromisoformat(data["accessed_at"]) if data.get("accessed_at") else None,
            metadata=data.get("metadata", {})
        )


class FileUploadMetadata(BaseModel):
    """
    Metadata for file upload operations
    
    Attributes:
        purpose: Purpose of the upload (file-extract, assistants, etc.)
        context_id: Optional context/session ID
        user_id: Optional user ID
        tags: Optional tags for categorization
        custom_metadata: Additional custom metadata
    """
    
    purpose: str = Field(
        default="file-extract",
        description="Purpose of the upload"
    )
    
    context_id: Optional[str] = Field(
        default=None,
        description="Context or session ID"
    )
    
    user_id: Optional[str] = Field(
        default=None,
        description="User ID"
    )
    
    tags: Optional[list] = Field(
        default_factory=list,
        description="Tags for categorization"
    )
    
    custom_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional custom metadata"
    )
    
    class Config:
        """Pydantic configuration"""
        validate_assignment = True


class FileOperationResult(BaseModel):
    """
    Result of a file operation
    
    Attributes:
        success: Whether the operation succeeded
        file_reference: File reference if successful
        error: Error message if failed
        operation_id: Unique operation ID for tracking
        duration_ms: Operation duration in milliseconds
    """
    
    success: bool = Field(
        ...,
        description="Whether the operation succeeded"
    )
    
    file_reference: Optional[FileReference] = Field(
        default=None,
        description="File reference if successful"
    )
    
    error: Optional[str] = Field(
        default=None,
        description="Error message if failed"
    )
    
    operation_id: Optional[str] = Field(
        default=None,
        description="Unique operation ID for tracking"
    )
    
    duration_ms: Optional[float] = Field(
        default=None,
        description="Operation duration in milliseconds"
    )
    
    class Config:
        """Pydantic configuration"""
        validate_assignment = True

