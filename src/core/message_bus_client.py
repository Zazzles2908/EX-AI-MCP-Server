"""
Supabase Message Bus Client for EX-AI MCP Server

Handles large message payloads (up to 100MB) with guaranteed integrity.
Provides automatic fallback to WebSocket for small messages (<1MB).

Phase 2B: Core message bus implementation
Created: 2025-10-07
Based on: Expert guidance from GLM-4.6 with web search
"""

import hashlib
import gzip
import json
import logging
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from src.core.config import get_config

logger = logging.getLogger(__name__)


class MessageStatus(str, Enum):
    """Message status enum matching database type."""
    PENDING = "pending"
    COMPLETE = "complete"
    ERROR = "error"
    EXPIRED = "expired"


class CompressionType(str, Enum):
    """Compression type enum matching database type."""
    NONE = "none"
    GZIP = "gzip"
    ZSTD = "zstd"


@dataclass
class MessageBusRecord:
    """Represents a message bus record."""
    id: str
    transaction_id: str
    session_id: str
    tool_name: str
    provider_name: str
    payload: Dict[str, Any]
    payload_size_bytes: int
    compression_type: CompressionType
    compressed_size_bytes: Optional[int]
    checksum: str
    status: MessageStatus
    error_message: Optional[str]
    created_at: datetime
    accessed_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any]


class CircuitBreaker:
    """
    Circuit breaker for Supabase message bus.
    
    Automatically falls back to WebSocket when Supabase is slow/unavailable.
    """
    
    def __init__(self, threshold: int = 5, timeout_secs: int = 60):
        """
        Initialize circuit breaker.
        
        Args:
            threshold: Number of failures before opening circuit
            timeout_secs: Seconds to wait before attempting to close circuit
        """
        self.threshold = threshold
        self.timeout_secs = timeout_secs
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.is_open = False
    
    def record_success(self):
        """Record a successful operation."""
        self.failure_count = 0
        self.is_open = False
        self.last_failure_time = None
    
    def record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.threshold:
            self.is_open = True
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures. "
                f"Falling back to WebSocket for {self.timeout_secs} seconds."
            )
    
    def should_allow_request(self) -> bool:
        """
        Check if request should be allowed.
        
        Returns:
            True if request should proceed, False if circuit is open
        """
        if not self.is_open:
            return True
        
        # Check if timeout has elapsed
        if self.last_failure_time and (time.time() - self.last_failure_time) > self.timeout_secs:
            logger.info("Circuit breaker timeout elapsed, attempting to close circuit")
            self.is_open = False
            self.failure_count = 0
            return True
        
        return False


class MessageBusClient:
    """
    Client for interacting with Supabase message bus.
    
    Handles large message payloads with compression, checksums, and circuit breaker.
    """
    
    def __init__(self):
        """Initialize message bus client."""
        self.config = get_config()
        self.client: Optional[Client] = None
        self.circuit_breaker: Optional[CircuitBreaker] = None
        
        # Initialize if message bus is enabled
        if self.config.message_bus_enabled:
            self._initialize()
    
    def _initialize(self):
        """Initialize Supabase client and circuit breaker."""
        if not SUPABASE_AVAILABLE:
            logger.error("Supabase library not available. Install with: pip install supabase")
            raise ImportError("supabase library is required for message bus")
        
        if not self.config.supabase_url or not self.config.supabase_key:
            logger.error("SUPABASE_URL and SUPABASE_KEY are required when MESSAGE_BUS_ENABLED=true")
            raise ValueError("Supabase configuration is incomplete")
        
        try:
            self.client = create_client(
                self.config.supabase_url,
                self.config.supabase_key
            )
            logger.info(f"Supabase message bus client initialized: {self.config.supabase_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}", exc_info=True)
            raise
        
        # Initialize circuit breaker if enabled
        if self.config.circuit_breaker_enabled:
            self.circuit_breaker = CircuitBreaker(
                threshold=self.config.circuit_breaker_threshold,
                timeout_secs=self.config.circuit_breaker_timeout_secs
            )
            logger.info(
                f"Circuit breaker enabled: threshold={self.config.circuit_breaker_threshold}, "
                f"timeout={self.config.circuit_breaker_timeout_secs}s"
            )
    
    def _calculate_checksum(self, data: str) -> str:
        """
        Calculate SHA-256 checksum of data.
        
        Args:
            data: String data to checksum
            
        Returns:
            Hex-encoded SHA-256 checksum
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _compress_payload(self, payload: Dict[str, Any]) -> tuple[bytes, CompressionType, int]:
        """
        Compress payload if configured.
        
        Args:
            payload: Payload dictionary to compress
            
        Returns:
            Tuple of (compressed_data, compression_type, compressed_size)
        """
        payload_json = json.dumps(payload, ensure_ascii=False)
        payload_bytes = payload_json.encode('utf-8')
        
        compression = self.config.message_bus_compression.lower()
        
        if compression == "none":
            return payload_bytes, CompressionType.NONE, len(payload_bytes)
        
        elif compression == "gzip":
            compressed = gzip.compress(payload_bytes)
            return compressed, CompressionType.GZIP, len(compressed)
        
        elif compression == "zstd":
            try:
                import zstandard as zstd
                compressor = zstd.ZstdCompressor()
                compressed = compressor.compress(payload_bytes)
                return compressed, CompressionType.ZSTD, len(compressed)
            except ImportError:
                logger.warning("zstandard library not available, falling back to gzip")
                compressed = gzip.compress(payload_bytes)
                return compressed, CompressionType.GZIP, len(compressed)
        
        else:
            logger.warning(f"Unknown compression type: {compression}, using none")
            return payload_bytes, CompressionType.NONE, len(payload_bytes)
    
    def _decompress_payload(self, data: bytes, compression_type: CompressionType) -> Dict[str, Any]:
        """
        Decompress payload.
        
        Args:
            data: Compressed data bytes
            compression_type: Type of compression used
            
        Returns:
            Decompressed payload dictionary
        """
        if compression_type == CompressionType.NONE:
            payload_json = data.decode('utf-8')
        
        elif compression_type == CompressionType.GZIP:
            decompressed = gzip.decompress(data)
            payload_json = decompressed.decode('utf-8')
        
        elif compression_type == CompressionType.ZSTD:
            try:
                import zstandard as zstd
                decompressor = zstd.ZstdDecompressor()
                decompressed = decompressor.decompress(data)
                payload_json = decompressed.decode('utf-8')
            except ImportError:
                raise ValueError("zstandard library required for zstd decompression")
        
        else:
            raise ValueError(f"Unknown compression type: {compression_type}")
        
        return json.loads(payload_json)
    
    def should_use_message_bus(self, payload_size_bytes: int) -> bool:
        """
        Determine if message bus should be used based on payload size and circuit breaker.
        
        Args:
            payload_size_bytes: Size of payload in bytes
            
        Returns:
            True if message bus should be used, False to use WebSocket
        """
        # Check if message bus is enabled
        if not self.config.message_bus_enabled:
            return False
        
        # Check circuit breaker
        if self.circuit_breaker and not self.circuit_breaker.should_allow_request():
            logger.debug("Circuit breaker open, using WebSocket fallback")
            return False
        
        # Check payload size (use message bus for large payloads)
        # Default threshold: 1MB
        threshold_bytes = 1024 * 1024  # 1MB
        return payload_size_bytes > threshold_bytes

    async def store_message(
        self,
        transaction_id: str,
        session_id: str,
        tool_name: str,
        provider_name: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a message in the message bus.

        Args:
            transaction_id: Unique transaction ID
            session_id: Session ID
            tool_name: Name of the tool
            provider_name: Name of the provider
            payload: Message payload
            metadata: Optional metadata

        Returns:
            True if stored successfully, False otherwise
        """
        if not self.client:
            logger.error("Message bus client not initialized")
            return False

        try:
            # Calculate payload size
            payload_json = json.dumps(payload, ensure_ascii=False)
            payload_size = len(payload_json.encode('utf-8'))

            # Compress if needed
            compressed_data, compression_type, compressed_size = self._compress_payload(payload)

            # Calculate checksum
            checksum = self._calculate_checksum(payload_json)

            # Calculate expiration
            ttl_hours = self.config.message_bus_ttl_hours
            expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

            # Prepare record
            record = {
                "transaction_id": transaction_id,
                "session_id": session_id,
                "tool_name": tool_name,
                "provider_name": provider_name,
                "payload": payload,  # Supabase handles JSONB automatically
                "payload_size_bytes": payload_size,
                "compression_type": compression_type.value,
                "compressed_size_bytes": compressed_size if compression_type != CompressionType.NONE else None,
                "checksum": checksum,
                "status": MessageStatus.COMPLETE.value,
                "expires_at": expires_at.isoformat(),
                "metadata": metadata or {}
            }

            # Insert into Supabase
            result = self.client.table("message_bus").insert(record).execute()

            if self.circuit_breaker:
                self.circuit_breaker.record_success()

            logger.info(
                f"Stored message in bus: transaction_id={transaction_id}, "
                f"size={payload_size} bytes, compression={compression_type.value}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to store message in bus: {e}", exc_info=True)

            if self.circuit_breaker:
                self.circuit_breaker.record_failure()

            return False

    async def retrieve_message(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a message from the message bus.

        Args:
            transaction_id: Transaction ID to retrieve

        Returns:
            Message payload if found, None otherwise
        """
        if not self.client:
            logger.error("Message bus client not initialized")
            return None

        try:
            # Query by transaction_id
            result = self.client.table("message_bus").select("*").eq("transaction_id", transaction_id).execute()

            if not result.data or len(result.data) == 0:
                logger.warning(f"Message not found: transaction_id={transaction_id}")
                return None

            record = result.data[0]

            # Update accessed_at timestamp
            self.client.table("message_bus").update({
                "accessed_at": datetime.utcnow().isoformat()
            }).eq("transaction_id", transaction_id).execute()

            # Verify checksum if enabled
            if self.config.message_bus_checksum_enabled:
                payload_json = json.dumps(record["payload"], ensure_ascii=False)
                calculated_checksum = self._calculate_checksum(payload_json)

                if calculated_checksum != record["checksum"]:
                    logger.error(
                        f"Checksum mismatch for transaction_id={transaction_id}: "
                        f"expected={record['checksum']}, calculated={calculated_checksum}"
                    )
                    return None

            if self.circuit_breaker:
                self.circuit_breaker.record_success()

            logger.info(f"Retrieved message from bus: transaction_id={transaction_id}")
            return record["payload"]

        except Exception as e:
            logger.error(f"Failed to retrieve message from bus: {e}", exc_info=True)

            if self.circuit_breaker:
                self.circuit_breaker.record_failure()

            return None

    async def delete_message(self, transaction_id: str) -> bool:
        """
        Delete a message from the message bus.

        Args:
            transaction_id: Transaction ID to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.client:
            logger.error("Message bus client not initialized")
            return False

        try:
            self.client.table("message_bus").delete().eq("transaction_id", transaction_id).execute()
            logger.info(f"Deleted message from bus: transaction_id={transaction_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete message from bus: {e}", exc_info=True)
            return False


# Singleton instance
_message_bus_client: Optional[MessageBusClient] = None


def get_message_bus_client() -> MessageBusClient:
    """
    Get the singleton message bus client instance.

    Returns:
        MessageBusClient instance
    """
    global _message_bus_client
    if _message_bus_client is None:
        _message_bus_client = MessageBusClient()
    return _message_bus_client

