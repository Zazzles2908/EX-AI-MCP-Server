"""
Supabase Storage Manager - Core Module

Main storage operations for EXAI MCP Server.
Handles conversations, messages, files, and provider file management.

This is part of the Phase 3 refactoring that split the large supabase_client.py
into focused modules:
- storage_exceptions.py: Custom exception types
- storage_progress.py: Progress tracking utilities
- storage_circuit_breaker.py: Circuit breaker and retry logic
- storage_telemetry.py: Performance tracking
- storage_manager.py: Main storage operations (this file)
"""

import os
import logging
import time
import hashlib
import io
import random
from typing import Optional, Dict, Any, List, Tuple

# Import Supabase client
from supabase import create_client, Client

# Import local modules
from src.storage.storage_exceptions import RetryableError, NonRetryableError
from src.storage.storage_progress import ProgressTracker
from src.storage.storage_circuit_breaker import with_circuit_breaker, with_retry
from src.storage.storage_telemetry import track_storage_performance

# Import other utilities
from datetime import datetime

logger = logging.getLogger(__name__)


class SupabaseStorageManager:
    """
    Manages all Supabase operations for EXAI MCP Server

    Features:
    - Conversation persistence
    - Message history storage
    - File upload/download
    - Performance tracking with circuit breakers
    - Connection pre-warming
    - Error handling with retries
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

        # Use centralized singleton instead of creating new client
        from src.storage.supabase_singleton import get_supabase_client
        return get_supabase_client(use_admin=True)

    def close(self):
        """Close the Supabase client"""
        self._client = None
        logger.debug("Supabase client closed")

    # ========================================================================
    # CONVERSATION OPERATIONS
    # ========================================================================

    @track_storage_performance(operation_type="write")
    def save_conversation(
        self,
        session_id: str,
        title: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Save or update a conversation

        Args:
            session_id: Unique conversation identifier
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
                "session_id": session_id,
                "title": title or f"Conversation {session_id[:8]}",
                "metadata": metadata or {}
            }

            result = client.table("conversations").upsert(data).execute()

            if result.data:
                conversation_id = result.data[0]["id"]
                logger.debug(f"Saved conversation: {session_id} -> {conversation_id}")
                return conversation_id

            return None

        except Exception as e:
            logger.error(f"Failed to save conversation {session_id}: {e}")
            return None

    @track_storage_performance(operation_type="query")
    def get_conversation_by_session_id(self, session_id: str) -> Optional[Dict]:
        """
        Get conversation by session_id

        Args:
            session_id: Unique conversation identifier

        Returns:
            Conversation record dict or None if not found
        """
        if not self._enabled:
            return None

        try:
            client = self.get_client()
            result = client.table("conversations").select("*").eq(
                "session_id", session_id
            ).execute()

            if result.data:
                logger.debug(f"Retrieved conversation: {session_id}")
                return result.data[0]

            return None

        except Exception as e:
            logger.error(f"Failed to get conversation {session_id}: {e}")
            return None

    def _generate_idempotency_key(self, data: Dict[str, Any]) -> str:
        """
        Generate idempotency key for message deduplication

        Args:
            data: Message data to hash

        Returns:
            SHA256 hash as hex string
        """
        # Create stable string representation
        content = f"{data.get('role', '')}:{data.get('content', '')}:{data.get('timestamp', '')}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @track_storage_performance(operation_type="write")
    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
        timestamp: Optional[str] = None
    ) -> Optional[str]:
        """
        Save a message to conversation with idempotency

        Args:
            conversation_id: Conversation UUID
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
            timestamp: Optional ISO timestamp

        Returns:
            Message UUID or None on error
        """
        if not self._enabled:
            return None

        try:
            client = self.get_client()
            ts = timestamp or datetime.now().isoformat()

            # Create message data
            message_data = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "metadata": metadata or {},
                "timestamp": ts
            }

            # Generate idempotency key
            idempotency_key = self._generate_idempotency_key(message_data)
            message_data["idempotency_key"] = idempotency_key

            # Try to insert with upsert (ignores duplicates)
            result = client.table("messages").upsert(
                message_data,
                on_conflict="idempotency_key",
                ignore_duplicates=True
            ).execute()

            if result.data:
                message_id = result.data[0]["id"]
                logger.debug(f"Saved message: {conversation_id}/{message_id}")
                return message_id

            # Message already exists (duplicate)
            logger.debug(f"Message already exists (idempotency): {conversation_id}")
            return None

        except Exception as e:
            logger.error(f"Failed to save message to {conversation_id}: {e}")
            return None

    @track_storage_performance(operation_type="query")
    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get all messages for a conversation

        Args:
            conversation_id: Conversation UUID
            limit: Optional maximum number of messages

        Returns:
            List of message records ordered by timestamp
        """
        if not self._enabled:
            return []

        try:
            client = self.get_client()
            query = client.table("messages").select("*").eq(
                "conversation_id", conversation_id
            ).order("timestamp", desc=False)

            if limit:
                query = query.limit(limit)

            result = query.execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Failed to get messages for {conversation_id}: {e}")
            return []

    # ========================================================================
    # FILE CHECK AND UTILITY METHODS
    # ========================================================================

    def _check_file_exists(self, file_path: str, original_name: str, file_type: str) -> Optional[str]:
        """Check if file already exists and return its ID"""
        if not self._enabled:
            return None

        try:
            client = self.get_client()
            result = client.table("files").select("id").eq(
                "storage_path", file_path
            ).eq("file_type", file_type).execute()

            if result.data:
                return result.data[0]["id"]

            return None

        except Exception as e:
            logger.error(f"Failed to check file existence: {e}")
            return None

    # ========================================================================
    # FILE OPERATIONS (upload, download, delete)
    # ========================================================================

    @track_storage_performance(operation_type="write")
    @with_retry(max_retries=3)
    def upload_file(
        self,
        file_data: bytes,
        original_name: str,
        file_path: str,
        mime_type: str,
        file_type: str,
        progress_callback: Optional[callable] = None,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Upload file to Supabase Storage with progress tracking

        Args:
            file_data: File content as bytes
            original_name: Original filename
            file_path: Storage path (within bucket)
            mime_type: MIME type
            file_type: File type category
            progress_callback: Optional callback for progress updates
            max_retries: Maximum retry attempts

        Returns:
            File UUID or None on error
        """
        if not self._enabled:
            return None

        file_obj = io.BytesIO(file_data)
        file_size = len(file_data)

        try:
            # Initialize progress tracker
            progress_tracker = ProgressTracker(
                progress_callback,
                throttle_interval=float(os.getenv("SUPABASE_PROGRESS_INTERVAL", "0.5"))
            )

            # Check for existing file
            existing_file_id = self._check_file_exists(file_path, original_name, file_type)
            if existing_file_id:
                logger.info(f"File already exists: {original_name} -> {existing_file_id}")
                # Report 100% progress for existing file
                if progress_callback:
                    progress_callback(file_size, file_size, 100.0)
                return existing_file_id

            # Determine bucket
            bucket = "user-files" if file_type == "user_upload" else "generated-files"

            # Report initial progress
            progress_tracker.update(0, file_size)

            # Upload to storage
            client = self.get_client()

            try:
                # Read file data for upload
                file_obj.seek(0)
                upload_data = file_obj.read()

                # Upload with progress simulation
                storage_result = client.storage.from_(bucket).upload(
                    file_path,
                    upload_data
                )

                # Report completion
                progress_tracker.update(file_size, file_size)

            except Exception as e:
                # Handle race condition - file might exist from another process
                if "Duplicate" in str(e) or "already exists" in str(e).lower() or "409" in str(e):
                    logger.warning(f"Upload race condition detected: {original_name}")
                    existing_file_id = self._check_file_exists(file_path, original_name, file_type)
                    if existing_file_id:
                        logger.info(f"Found existing file after race condition: {original_name} -> {existing_file_id}")
                        progress_tracker.update(file_size, file_size)
                        return existing_file_id
                raise

            # Save metadata to database
            file_metadata = {
                "storage_path": file_path,
                "original_name": original_name,
                "mime_type": mime_type,
                "size_bytes": file_size,
                "file_type": file_type
            }

            db_result = client.table("files").insert(file_metadata).execute()

            if not db_result.data:
                raise Exception("Failed to save file metadata")

            file_id = db_result.data[0]["id"]
            logger.info(f"Uploaded file: {original_name} -> {file_id}")
            return file_id

        except NonRetryableError as e:
            logger.error(f"Upload failed (non-retryable): {e}")
            return None

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return None

        finally:
            # Clean up file object if we created it
            file_obj.close()

    @track_storage_performance(operation_type="query")
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

    @track_storage_performance(operation_type="write")
    @with_retry(max_retries=3)
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Supabase Storage with retry logic

        Deletes both the file from storage bucket and the file record from database.

        Args:
            file_id: UUID of the file to delete

        Returns:
            True if deletion successful, False otherwise
        """
        if not self._enabled:
            return False

        try:
            client = self.get_client()

            # Get file metadata with race condition protection
            file_record = client.table("files").select("*").eq("id", file_id).execute()

            if not file_record.data:
                logger.warning(f"File {file_id} not found in database - considering already deleted")
                return True  # Consider file already deleted as success

            storage_path = file_record.data[0]["storage_path"]
            file_type = file_record.data[0]["file_type"]

            # Determine bucket
            bucket = "user-files" if file_type == "user_upload" else "generated-files"

            # Delete from storage first (prevents orphaned files)
            try:
                client.storage.from_(bucket).remove([storage_path])
                logger.debug(f"Deleted file from storage: {storage_path}")
            except Exception as storage_error:
                # Continue to delete database record to prevent orphaned records
                logger.warning(f"Storage deletion warning: {storage_error}")

            # Delete from database
            delete_result = client.table("files").delete().eq("id", file_id).execute()

            if delete_result.data:
                logger.debug(f"Deleted file record: {file_id}")
                return True
            else:
                logger.error(f"Failed to delete file record: {file_id}")
                return False

        except NonRetryableError as e:
            logger.error(f"Delete failed (non-retryable): {e}")
            return False

        except RetryableError as e:
            logger.error(f"Delete failed after retries: {e}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error deleting file {file_id}: {e}")
            return False

    # ========================================================================
    # CONVERSATION-FILE LINKING
    # ========================================================================

    @track_storage_performance(operation_type="write")
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

            # Use upsert to handle duplicates
            result = client.table("conversation_files").upsert(data).execute()

            if result.data:
                logger.debug(f"Linked file {file_id} to conversation {conversation_id}")
                return True

            return False

        except Exception as e:
            # Don't log duplicate key errors as errors
            if "duplicate key" in str(e).lower():
                logger.debug(f"File {file_id} already linked to conversation {conversation_id}")
                return True
            logger.error(f"Failed to link file to conversation: {e}")
            return False

    @track_storage_performance(operation_type="write")
    def link_files_to_conversation_batch(
        self,
        conversation_id: str,
        file_ids: List[str]
    ) -> dict:
        """
        Batch link multiple files to a conversation

        Reduces N+1 queries by batching file linking operations.

        Args:
            conversation_id: UUID of the conversation
            file_ids: List of file UUIDs to link

        Returns:
            Dictionary with success count and errors
        """
        if not self._enabled or not file_ids:
            return {"success": 0, "errors": []}

        try:
            client = self.get_client()

            # Build batch data with unique constraint handling
            batch_data = [
                {"conversation_id": conversation_id, "file_id": file_id}
                for file_id in file_ids
            ]

            # Use upsert with explicit on_conflict to prevent errors
            result = client.table("conversation_files").upsert(
                batch_data,
                on_conflict='conversation_id,file_id',
                ignore_duplicates=True
            ).execute()

            success_count = len(result.data) if result.data else 0
            logger.info(f"Linked {success_count}/{len(file_ids)} files to conversation {conversation_id}")

            return {"success": success_count, "errors": []}

        except Exception as e:
            logger.error(f"Failed to batch link files: {e}")
            return {"success": 0, "errors": [str(e)]}

    # ========================================================================
    # PROVIDER FILE OPERATIONS
    # ========================================================================

    @track_storage_performance(operation_type="write")
    def save_provider_file_upload(
        self,
        provider: str,
        provider_file_id: str,
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Save provider file upload record

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
            provider_file_id: Provider's file identifier
            purpose: File purpose (e.g., 'assistants', 'fine_tuning')
            metadata: Optional metadata

        Returns:
            File record UUID or None on error
        """
        if not self._enabled:
            return None

        try:
            client = self.get_client()
            data = {
                "provider": provider,
                "provider_file_id": provider_file_id,
                "purpose": purpose,
                "metadata": metadata or {}
            }

            result = client.table("provider_file_uploads").insert(data).execute()

            if result.data:
                file_id = result.data[0]["id"]
                logger.info(f"Saved provider file: {provider}/{provider_file_id}")
                return file_id

            return None

        except Exception as e:
            # Handle duplicate key violations
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                logger.warning(f"Duplicate provider file: {provider}/{provider_file_id}")
                # Try to get existing record
                existing = self.get_provider_file_by_id(provider, provider_file_id)
                return existing.get("id") if existing else None

            logger.error(f"Failed to save provider file upload {provider}/{provider_file_id}: {e}")
            return None

    @track_storage_performance(operation_type="query")
    def get_provider_file_by_id(
        self,
        provider: str,
        provider_file_id: str
    ) -> Optional[Dict]:
        """
        Get provider file upload record

        Args:
            provider: Provider name
            provider_file_id: Provider's file identifier

        Returns:
            File record dict or None if not found
        """
        if not self._enabled:
            return None

        try:
            client = self.get_client()
            result = client.table("provider_file_uploads").select("*").eq(
                "provider", provider
            ).eq("provider_file_id", provider_file_id).execute()

            if result.data:
                logger.debug(f"Retrieved provider file: {provider}/{provider_file_id}")
                return result.data[0]

            return None

        except Exception as e:
            logger.error(f"Failed to get provider file {provider}/{provider_file_id}: {e}")
            return None

    @track_storage_performance(operation_type="write")
    def update_provider_file_last_used(
        self,
        provider: str,
        provider_file_id: str
    ) -> bool:
        """
        Update last_used timestamp for provider file

        Args:
            provider: Provider name
            provider_file_id: Provider's file identifier

        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            return False

        try:
            client = self.get_client()
            result = client.table("provider_file_uploads").update({
                "last_used": datetime.now().isoformat()
            }).eq("provider", provider).eq("provider_file_id", provider_file_id).execute()

            if result.data:
                logger.debug(f"Updated last_used for {provider}/{provider_file_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to update last_used for {provider}/{provider_file_id}: {e}")
            return False

    @track_storage_performance(operation_type="query")
    def get_provider_files_by_purpose(
        self,
        provider: str,
        purpose: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get provider files filtered by purpose

        Args:
            provider: Provider name
            purpose: File purpose
            limit: Maximum number of results

        Returns:
            List of file records
        """
        if not self._enabled:
            return []

        try:
            client = self.get_client()
            result = client.table("provider_file_uploads").select("*").eq(
                "provider", provider
            ).eq("purpose", purpose).limit(limit).execute()

            return result.data or []

        except Exception as e:
            logger.error(f"Failed to get provider files by purpose: {e}")
            return []

    # ========================================================================
    # FILE EMBEDDINGS
    # ========================================================================

    @track_storage_performance(operation_type="write")
    def save_file_embedding(
        self,
        provider_file_id: str,
        embedding_model: str,
        embedding_data: List[float],
        chunk_index: int = 0,
        text_content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Save file embedding for caching

        Args:
            provider_file_id: Provider file UUID
            embedding_model: Model used for embedding
            embedding_data: Embedding vector as list of floats
            chunk_index: Chunk index for multi-chunk embeddings
            text_content: Optional text content that was embedded
            metadata: Optional metadata

        Returns:
            Embedding UUID or None on error
        """
        if not self._enabled:
            return None

        try:
            client = self.get_client()
            data = {
                "provider_file_id": provider_file_id,
                "embedding_model": embedding_model,
                "embedding_dimension": len(embedding_data),
                "embedding_data": embedding_data,
                "chunk_index": chunk_index,
                "text_content": text_content,
                "metadata": metadata
            }

            result = client.table("file_embeddings").insert(data).execute()

            if result.data:
                embedding_id = result.data[0]["id"]
                logger.info(f"Saved file embedding: {provider_file_id} (model: {embedding_model})")
                return embedding_id

            return None

        except Exception as e:
            logger.error(f"Failed to save file embedding: {e}")
            return None

    @track_storage_performance(operation_type="query")
    def get_file_embeddings(
        self,
        provider_file_id: str,
        embedding_model: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve cached embeddings for a file

        Args:
            provider_file_id: Provider file UUID
            embedding_model: Optional model filter

        Returns:
            List of embedding records
        """
        if not self._enabled:
            return []

        try:
            client = self.get_client()
            query = client.table("file_embeddings").select("*").eq(
                "provider_file_id", provider_file_id
            )

            if embedding_model:
                query = query.eq("embedding_model", embedding_model)

            result = query.order("chunk_index").execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Failed to get file embeddings: {e}")
            return []

    # ========================================================================
    # FILE ACCESS LOGGING
    # ========================================================================

    def log_file_access(
        self,
        provider_file_id: str,
        operation: str,
        provider: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        status_code: Optional[int] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log file access for monitoring and analytics

        Args:
            provider_file_id: Provider file UUID
            operation: Operation type (upload, download, delete, list, metadata)
            provider: Provider name
            user_id: Optional user identifier
            ip_address: Optional IP address
            user_agent: Optional user agent string
            response_time_ms: Optional response time in milliseconds
            status_code: Optional HTTP status code
            error_message: Optional error message
            metadata: Optional metadata

        Returns:
            True if successful, False otherwise

        Note: This method does NOT use @track_storage_performance to avoid circular logging
        """
        if not self._enabled:
            return False

        # Validate operation
        valid_operations = ['upload', 'download', 'delete', 'list', 'metadata']
        if operation not in valid_operations:
            logger.warning(f"Invalid operation for file access log: {operation}")
            return False

        try:
            client = self.get_client()
            data = {
                "provider_file_id": provider_file_id,
                "operation": operation,
                "provider": provider,
                "user_id": user_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "response_time_ms": response_time_ms,
                "status_code": status_code,
                "error_message": error_message,
                "metadata": metadata
            }

            # Fire and forget - don't wait for response
            client.table("file_access_log").insert(data).execute()
            return True

        except Exception as e:
            # Don't log errors for logging failures to avoid recursion
            logger.debug(f"Failed to log file access: {e}")
            return False


# Global instance (initialized on first import)
_storage_manager: Optional[SupabaseStorageManager] = None


def get_storage_manager() -> SupabaseStorageManager:
    """Get global Supabase storage manager instance"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = SupabaseStorageManager()
    return _storage_manager
