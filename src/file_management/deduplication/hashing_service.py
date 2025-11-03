"""
File Hashing Service for Deduplication

Provides SHA256 content-based hashing for file deduplication.
Supports both file paths and file-like objects.
"""

import hashlib
import logging
from typing import Union, BinaryIO
from pathlib import Path

logger = logging.getLogger(__name__)


class HashingService:
    """Service for computing file content hashes"""
    
    CHUNK_SIZE = 65536  # 64KB chunks for memory efficiency
    HASH_ALGORITHM = 'sha256'
    
    @classmethod
    def compute_file_hash(cls, file_source: Union[str, Path, BinaryIO]) -> str:
        """
        Compute SHA256 hash of file content
        
        Args:
            file_source: File path or file-like object
            
        Returns:
            Hexadecimal hash string
            
        Raises:
            FileNotFoundError: If file path doesn't exist
            IOError: If file cannot be read
        """
        try:
            hasher = hashlib.sha256()
            
            if isinstance(file_source, (str, Path)):
                # File path provided
                file_path = Path(file_source)
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
                
                with open(file_path, 'rb') as f:
                    cls._hash_file_object(f, hasher)
            else:
                # File-like object provided
                cls._hash_file_object(file_source, hasher)
            
            hash_value = hasher.hexdigest()
            logger.debug(f"Computed hash: {hash_value[:16]}...")
            return hash_value
            
        except Exception as e:
            logger.error(f"Failed to compute file hash: {e}")
            raise
    
    @classmethod
    def _hash_file_object(cls, file_obj: BinaryIO, hasher: hashlib._Hash):
        """
        Hash file object in chunks
        
        Args:
            file_obj: File-like object to hash
            hasher: Hash object to update
        """
        # Save current position
        original_position = file_obj.tell() if hasattr(file_obj, 'tell') else None
        
        try:
            # Seek to beginning if possible
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            
            # Read and hash in chunks
            while True:
                chunk = file_obj.read(cls.CHUNK_SIZE)
                if not chunk:
                    break
                hasher.update(chunk)
        
        finally:
            # Restore original position if possible
            if original_position is not None and hasattr(file_obj, 'seek'):
                try:
                    file_obj.seek(original_position)
                except Exception as e:
                    logger.warning(f"Could not restore file position: {e}")
    
    @classmethod
    def verify_hash(cls, file_source: Union[str, Path, BinaryIO], expected_hash: str) -> bool:
        """
        Verify file hash matches expected value
        
        Args:
            file_source: File path or file-like object
            expected_hash: Expected hash value
            
        Returns:
            True if hash matches, False otherwise
        """
        try:
            actual_hash = cls.compute_file_hash(file_source)
            matches = actual_hash == expected_hash
            
            if not matches:
                logger.warning(
                    f"Hash mismatch: expected {expected_hash[:16]}..., "
                    f"got {actual_hash[:16]}..."
                )
            
            return matches
            
        except Exception as e:
            logger.error(f"Hash verification failed: {e}")
            return False
    
    @classmethod
    def compute_hash_from_bytes(cls, data: bytes) -> str:
        """
        Compute hash from bytes directly
        
        Args:
            data: Bytes to hash
            
        Returns:
            Hexadecimal hash string
        """
        hasher = hashlib.sha256()
        hasher.update(data)
        return hasher.hexdigest()

