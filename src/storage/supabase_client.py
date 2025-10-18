"""
Supabase Storage Manager for EXAI MCP Server
Handles persistent storage for conversations, messages, and files
"""

import os
import logging
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from functools import wraps
from supabase import create_client, Client

# PHASE 3 (2025-10-18): Import monitoring utilities
from utils.monitoring import record_supabase_event
from utils.timezone_helper import log_timestamp

# PHASE 1 (2025-10-18): Import circuit breaker for resilience
from src.resilience.circuit_breaker_manager import circuit_breaker_manager
import pybreaker

logger = logging.getLogger(__name__)


def track_performance(func):
    """
    Decorator to track performance of storage operations with circuit breaker protection

    PHASE 1 (2025-10-18): Added circuit breaker protection for all Supabase operations
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start = time.time()
        error = None
        result = None

        # PHASE 1 (2025-10-18): Apply circuit breaker protection
        breaker = circuit_breaker_manager.get_breaker('supabase')

        try:
            # Wrap Supabase call with circuit breaker
            @breaker
            def _call_with_breaker():
                return func(self, *args, **kwargs)

            result = _call_with_breaker()
            duration = time.time() - start

            # Log performance metrics
            logger.debug(f"{func.__name__} completed in {duration:.3f}s")

            # Alert on slow operations (> 500ms)
            if duration > 0.5:
                logger.warning(f"Slow operation: {func.__name__} took {duration:.3f}s")

            # PHASE 3 (2025-10-18): Monitor Supabase operations
            # Determine operation type from function name
            operation_type = "query" if "get" in func.__name__ or "fetch" in func.__name__ else "write"

            # Estimate data size (rough approximation)
            data_size = 0
            if result:
                if isinstance(result, (list, dict)):
                    data_size = len(str(result).encode('utf-8'))

            record_supabase_event(
                direction="receive" if operation_type == "query" else "send",
                function_name=f"SupabaseStorageManager.{func.__name__}",
                data_size=data_size,
                response_time_ms=duration * 1000,
                metadata={
                    "operation": operation_type,
                    "slow": duration > 0.5,
                    "timestamp": log_timestamp()
                }
            )

            return result

        except pybreaker.CircuitBreakerError:
            # Circuit breaker is OPEN - Supabase is unavailable
            logger.error(f"Supabase circuit breaker OPEN - cannot execute {func.__name__}")
            duration = time.time() - start

            record_supabase_event(
                direction="error",
                function_name=f"SupabaseStorageManager.{func.__name__}",
                data_size=0,
                error="Circuit breaker OPEN",
                metadata={"timestamp": log_timestamp()}
            )

            # Graceful degradation: Return None (operation failed but service continues)
            return None

        except Exception as e:
            error = str(e)
            duration = time.time() - start

            # PHASE 3 (2025-10-18): Monitor errors
            record_supabase_event(
                direction="error",
                function_name=f"SupabaseStorageManager.{func.__name__}",
                data_size=0,
                error=error,
                metadata={"timestamp": log_timestamp()}
            )

            raise

    return wrapper


class SupabaseStorageManager:
    """
    Manages all Supabase operations for EXAI MCP Server

    Features:
    - Conversation persistence
    - Message history storage
    - File upload/download
    - Performance tracking
    - Connection pre-warming
    - Error handling with retries

    Note: Uses supabase-py 2.15.3 which internally uses httpx with default connection pooling.
    Application-level optimizations (caching, batching) provide better performance gains.
    """
    
    def __init__(self):
        """Initialize Supabase client with environment configuration"""
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self._client: Optional[Client] = None

        # DEBUG: Log environment variable status
        logger.info(f"[SUPABASE_INIT] SUPABASE_URL={'SET' if self.url else 'NOT SET'}")
        logger.info(f"[SUPABASE_INIT] SUPABASE_SERVICE_ROLE_KEY={'SET' if self.service_key else 'NOT SET'}")

        # Validate configuration
        if not self.url or not self.service_key:
            logger.warning("Supabase credentials not configured. Storage features disabled.")
            self._enabled = False
        else:
            self._enabled = True
            logger.info(f"Supabase storage initialized: {self.url}")
            self._prewarm_connections()
    
    @property
    def enabled(self) -> bool:
        """Check if Supabase storage is enabled"""
        return self._enabled
    
    def _prewarm_connections(self):
        """Pre-warm HTTP connections to reduce first-request latency"""
        try:
            client = self.get_client()
            client.table('schema_version').select('version').limit(1).execute()
            logger.debug("HTTP connections pre-warmed successfully")
        except Exception as e:
            logger.debug(f"Connection pre-warming failed (non-critical): {e}")

    def get_client(self) -> Client:
        """
        Get Supabase client instance

        Returns:
            Supabase client instance (uses httpx internally with default connection pooling)
        """
        if not self._enabled:
            raise RuntimeError("Supabase storage not configured")

        if self._client is None:
            # Create client - supabase-py uses httpx internally with default connection pooling
            self._client = create_client(
                self.url,
                self.service_key  # Use service key for server operations
            )
            logger.debug("Supabase client created")

        return self._client

    def close(self):
        """Close the Supabase client"""
        self._client = None
        logger.debug("Supabase client closed")
    
    # ========================================================================
    # CONVERSATION OPERATIONS
    # ========================================================================
    
    @track_performance
    def save_conversation(
        self,
        continuation_id: str,
        title: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Save or update a conversation
        
        Args:
            continuation_id: Unique conversation identifier
            title: Optional conversation title
            metadata: Optional metadata (tool usage, model info, etc.)
        
        Returns:
            Conversation UUID or None on error
        """
        if not self._enabled:
            return None
        
        try:
            client = self.get_client()
            data = {
                "continuation_id": continuation_id,
                "title": title or f"Conversation {continuation_id[:8]}",
                "metadata": metadata or {}
            }
            
            result = client.table("conversations").upsert(data).execute()
            
            if result.data:
                conv_id = result.data[0]["id"]
                logger.info(f"Saved conversation: {continuation_id} -> {conv_id}")
                return conv_id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to save conversation {continuation_id}: {e}")
            return None
    
    @track_performance
    def get_conversation_by_continuation_id(
        self,
        continuation_id: str
    ) -> Optional[Dict]:
        """
        Retrieve a conversation by its continuation_id
        
        Args:
            continuation_id: Unique conversation identifier
        
        Returns:
            Conversation dict or None if not found
        """
        if not self._enabled:
            return None
        
        try:
            client = self.get_client()
            result = client.table("conversations").select("*").eq(
                "continuation_id", continuation_id
            ).execute()
            
            if result.data:
                logger.debug(f"Retrieved conversation: {continuation_id}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get conversation {continuation_id}: {e}")
            return None
    
    # ========================================================================
    # MESSAGE OPERATIONS
    # ========================================================================
    
    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Save a message to a conversation
        
        Args:
            conversation_id: UUID of the conversation
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata (model, tokens, etc.)
        
        Returns:
            Message UUID or None on error
        """
        if not self._enabled:
            return None
        
        try:
            client = self.get_client()
            data = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "metadata": metadata or {}
            }
            
            result = client.table("messages").insert(data).execute()
            
            if result.data:
                msg_id = result.data[0]["id"]
                logger.debug(f"Saved message: {msg_id} ({role})")
                return msg_id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return None
    
    @track_performance
    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get all messages for a conversation
        
        Args:
            conversation_id: UUID of the conversation
            limit: Maximum number of messages to retrieve
        
        Returns:
            List of message dicts (ordered by timestamp)
        """
        if not self._enabled:
            return []
        
        try:
            client = self.get_client()
            result = client.table("messages").select("*").eq(
                "conversation_id", conversation_id
            ).order("created_at").limit(limit).execute()
            
            messages = result.data if result.data else []
            logger.debug(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get messages for {conversation_id}: {e}")
            return []
    
    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================

    def _check_file_exists(
        self,
        storage_path: str,
        original_name: str,
        file_type: str
    ) -> Optional[str]:
        """
        Check if file already exists in database by storage path and original name

        Args:
            storage_path: Storage path to check
            original_name: Original filename
            file_type: File type (user_upload, generated, cache)

        Returns:
            file_id if exists, None otherwise
        """
        try:
            client = self.get_client()

            # Query database for existing file
            result = client.table("files").select("id").eq(
                "storage_path", storage_path
            ).eq("original_name", original_name).eq(
                "file_type", file_type
            ).execute()

            if result.data and len(result.data) > 0:
                return result.data[0]["id"]

            return None

        except Exception as e:
            logger.warning(f"Failed to check file existence: {e}")
            # Don't fail the upload if check fails
            return None

    def upload_file(
        self,
        file_path: str,
        file_data: bytes,
        original_name: str,
        mime_type: Optional[str] = None,
        file_type: str = "user_upload"
    ) -> Optional[str]:
        """
        Upload a file to Supabase Storage with duplicate detection

        Args:
            file_path: Storage path (unique identifier)
            file_data: File content as bytes
            original_name: Original filename
            mime_type: Optional MIME type
            file_type: Type (user_upload, generated, cache)

        Returns:
            File UUID or None on error
        """
        if not self._enabled:
            return None

        try:
            client = self.get_client()

            # Determine bucket based on file type
            bucket = "user-files" if file_type == "user_upload" else "generated-files"

            # CRITICAL FIX (2025-10-17): Check for existing file first to prevent 409 Duplicate errors
            existing_file_id = self._check_file_exists(file_path, original_name, file_type)
            if existing_file_id:
                logger.info(f"File already exists: {original_name} -> {existing_file_id}")
                return existing_file_id

            # Upload to storage
            try:
                storage_result = client.storage.from_(bucket).upload(
                    file_path,
                    file_data
                )
            except Exception as e:
                # Handle race condition - file might exist from another process
                if "Duplicate" in str(e) or "already exists" in str(e).lower() or "409" in str(e):
                    logger.warning(f"Upload race condition detected: {original_name}")
                    # Retry check to get the file_id
                    existing_file_id = self._check_file_exists(file_path, original_name, file_type)
                    if existing_file_id:
                        logger.info(f"Found existing file after race condition: {original_name} -> {existing_file_id}")
                        return existing_file_id
                raise

            # Save metadata to database
            file_metadata = {
                "storage_path": file_path,
                "original_name": original_name,
                "mime_type": mime_type,
                "size_bytes": len(file_data),
                "file_type": file_type
            }

            db_result = client.table("files").insert(file_metadata).execute()

            if db_result.data:
                file_id = db_result.data[0]["id"]
                logger.info(f"Uploaded file: {original_name} -> {file_id}")
                return file_id

            return None

        except Exception as e:
            logger.error(f"Failed to upload file {original_name}: {e}")
            return None
    
    def download_file(self, file_id: str) -> Optional[bytes]:
        """
        Download a file from Supabase Storage
        
        Args:
            file_id: UUID of the file
        
        Returns:
            File content as bytes or None on error
        """
        if not self._enabled:
            return None
        
        try:
            client = self.get_client()
            
            # Get file metadata
            file_record = client.table("files").select("*").eq("id", file_id).execute()
            
            if not file_record.data:
                logger.error(f"File {file_id} not found in database")
                return None
            
            storage_path = file_record.data[0]["storage_path"]
            file_type = file_record.data[0]["file_type"]
            
            # Determine bucket
            bucket = "user-files" if file_type == "user_upload" else "generated-files"
            
            # Download from storage
            result = client.storage.from_(bucket).download(storage_path)
            
            logger.debug(f"Downloaded file: {file_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to download file {file_id}: {e}")
            return None
    
    # ========================================================================
    # CONVERSATION-FILE LINKING
    # ========================================================================
    
    def link_file_to_conversation(
        self,
        conversation_id: str,
        file_id: str
    ) -> bool:
        """
        Link a file to a conversation
        
        Args:
            conversation_id: UUID of the conversation
            file_id: UUID of the file
        
        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            return False
        
        try:
            client = self.get_client()
            data = {
                "conversation_id": conversation_id,
                "file_id": file_id
            }
            
            result = client.table("conversation_files").insert(data).execute()
            
            if result.data:
                logger.debug(f"Linked file {file_id} to conversation {conversation_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to link file to conversation: {e}")
            return False


# Global instance (initialized on first import)
_storage_manager: Optional[SupabaseStorageManager] = None


def get_storage_manager() -> SupabaseStorageManager:
    """Get global Supabase storage manager instance"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = SupabaseStorageManager()
    return _storage_manager

