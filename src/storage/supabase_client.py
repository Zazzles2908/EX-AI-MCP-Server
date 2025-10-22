"""
Supabase Storage Manager for EXAI MCP Server
Handles persistent storage for conversations, messages, and files
"""

import os
import logging
import time
import hashlib
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

    @staticmethod
    def generate_idempotency_key(
        conversation_id: str,
        role: str,
        content: str,
        client_timestamp: Optional[str] = None
    ) -> str:
        """
        Generate a deterministic idempotency key for a message.

        DEDUPLICATION FIX (2025-10-22): Added idempotency key generation
        to prevent duplicate message insertion.

        Args:
            conversation_id: UUID of the conversation
            role: Message role (user, assistant, system)
            content: Message content
            client_timestamp: ISO string from client when message was created

        Returns:
            SHA-256 hash as hex string
        """
        # Use current timestamp if not provided
        if not client_timestamp:
            client_timestamp = datetime.utcnow().isoformat()

        # Normalize content to reduce false duplicates
        normalized_content = content.strip()

        # Create deterministic string to hash
        key_string = f"{conversation_id}:{role}:{normalized_content}:{client_timestamp}"

        # Generate SHA-256 hash (more reliable than MD5)
        return hashlib.sha256(key_string.encode('utf-8')).hexdigest()

    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
        client_timestamp: Optional[str] = None
    ) -> Optional[str]:
        """
        Save a message to a conversation with idempotency key.

        DEDUPLICATION FIX (2025-10-22): Added idempotency key to prevent
        duplicate message insertion. If a duplicate is detected, returns
        the existing message ID instead of creating a new one.

        Args:
            conversation_id: UUID of the conversation
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata (model, tokens, etc.)
            client_timestamp: Optional timestamp for idempotency key generation

        Returns:
            Message UUID or None on error
        """
        if not self._enabled:
            return None

        try:
            client = self.get_client()

            # Generate idempotency key
            idempotency_key = self.generate_idempotency_key(
                conversation_id, role, content, client_timestamp
            )

            data = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "metadata": metadata or {},
                "idempotency_key": idempotency_key
            }

            result = client.table("messages").insert(data).execute()

            if result.data:
                msg_id = result.data[0]["id"]
                logger.debug(f"Saved message: {msg_id} ({role})")
                return msg_id

            return None

        except Exception as e:
            # Check if this is a duplicate key error
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                logger.debug(f"Duplicate message detected (idempotency key: {idempotency_key[:16]}...)")

                # Fetch existing message ID
                try:
                    existing = client.table("messages").select("id").eq(
                        "idempotency_key", idempotency_key
                    ).execute()

                    if existing.data:
                        existing_id = existing.data[0]["id"]
                        logger.debug(f"Returning existing message: {existing_id}")
                        return existing_id
                except Exception as fetch_error:
                    logger.error(f"Failed to fetch existing message: {fetch_error}")

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

    # ========================================================================
    # PROVIDER FILE UPLOAD TRACKING (Phase 2.3.2)
    # ========================================================================

    @track_performance
    def save_provider_file_upload(
        self,
        provider: str,
        provider_file_id: str,
        filename: str,
        file_size_bytes: int,
        purpose: str = "file-extract",
        supabase_file_id: Optional[str] = None,
        checksum_sha256: Optional[str] = None,
        mime_type: Optional[str] = None,
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Save provider file upload metadata with validation

        Args:
            provider: Provider name (kimi, glm, openai, anthropic)
            provider_file_id: Provider's file identifier
            filename: Original filename
            file_size_bytes: File size in bytes
            purpose: File purpose (file-extract, agent, assistants, training, custom)
            supabase_file_id: Optional Supabase file UUID
            checksum_sha256: Optional SHA-256 checksum
            mime_type: Optional MIME type
            custom_metadata: Optional custom metadata

        Returns:
            Record UUID or None on error
        """
        if not self._enabled:
            return None

        # Validate file size (2GB max)
        if file_size_bytes > 2 * 1024 * 1024 * 1024:
            logger.error(f"File too large: {file_size_bytes} bytes (max 2GB)")
            return None

        # Validate purpose
        valid_purposes = ['file-extract', 'agent', 'assistants', 'training', 'custom']
        if purpose not in valid_purposes:
            logger.error(f"Invalid purpose: {purpose}. Must be one of {valid_purposes}")
            return None

        # Validate provider
        valid_providers = ['kimi', 'glm', 'openai', 'anthropic']
        if provider not in valid_providers:
            logger.error(f"Invalid provider: {provider}. Must be one of {valid_providers}")
            return None

        try:
            client = self.get_client()
            data = {
                "provider": provider,
                "provider_file_id": provider_file_id,
                "filename": filename,
                "file_size_bytes": file_size_bytes,
                "purpose": purpose,
                "supabase_file_id": supabase_file_id,
                "checksum_sha256": checksum_sha256,
                "mime_type": mime_type,
                "custom_metadata": custom_metadata,  # Let JSONB handle None
                "upload_status": "completed"
            }

            result = client.table("provider_file_uploads").upsert(data).execute()

            if result.data:
                record_id = result.data[0]["id"]
                logger.info(f"Saved provider file upload: {provider}/{provider_file_id} -> {record_id}")
                return record_id

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

    @track_performance
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

    @track_performance
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

    @track_performance
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
    # FILE EMBEDDINGS (Phase 2.3.2)
    # ========================================================================

    @track_performance
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
            embedding_model: Model used for embedding (e.g., 'text-embedding-ada-002')
            embedding_data: Embedding vector as list of floats
            chunk_index: Chunk index for multi-chunk embeddings (default 0)
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
                "embedding_data": embedding_data,  # Stored as JSONB array
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

    @track_performance
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
    # FILE ACCESS LOGGING (Phase 2.3.2)
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

        Note: This method does NOT use @track_performance to avoid circular logging
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

