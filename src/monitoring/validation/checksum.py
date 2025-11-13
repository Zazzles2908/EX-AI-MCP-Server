"""
Checksum validation for dual-write consistency.

Provides CRC32 and SHA256 checksum generation and validation for monitoring events.
Ensures data integrity across WebSocket and Supabase Realtime adapters.
"""

import hashlib
import zlib
import json
import hmac
import threading
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class ChecksumAlgorithm(Enum):
    """Supported checksum algorithms."""
    CRC32 = "crc32"
    SHA256 = "sha256"


@dataclass
class ChecksumResult:
    """Result of checksum generation or validation."""
    
    algorithm: ChecksumAlgorithm
    checksum: str
    timestamp: datetime
    event_type: str
    sequence_id: Optional[int] = None
    is_valid: Optional[bool] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'algorithm': self.algorithm.value,
            'checksum': self.checksum,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'sequence_id': self.sequence_id,
            'is_valid': self.is_valid,
            'error_message': self.error_message,
        }


class ChecksumManager:
    """Manages checksum generation and validation for events.

    REFACTORED: Removed singleton pattern - now uses dependency injection
    for better testability and maintainability.
    """

    def __init__(self):
        """Initialize ChecksumManager."""
        self._lock = threading.Lock()
        self._default_algorithm = ChecksumAlgorithm.CRC32
        self._critical_algorithm = ChecksumAlgorithm.SHA256

        # Metrics
        self._checksums_generated: int = 0
        self._checksums_validated: int = 0
        self._validation_failures: int = 0
        self._algorithm_distribution: Dict[str, int] = {}
        self._secret_key: Optional[str] = None

    def reset_metrics(self):
        """Reset metrics (for testing)."""
        with self._lock:
            self._checksums_generated = 0
            self._checksums_validated = 0
            self._validation_failures = 0
            self._algorithm_distribution = {}
    
    def _serialize_event_data(self, data: Dict[str, Any]) -> str:
        """
        Serialize event data for checksum calculation.
        
        Uses JSON serialization with sorted keys for consistency.
        """
        try:
            return json.dumps(data, sort_keys=True, separators=(',', ':'))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Failed to serialize event data: {e}")
    
    def _calculate_crc32(self, data: str) -> str:
        """Calculate CRC32 checksum."""
        crc = zlib.crc32(data.encode('utf-8')) & 0xffffffff
        return f"{crc:08x}"
    
    def _calculate_sha256(self, data: str) -> str:
        """Calculate SHA256 checksum."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def _calculate_hmac_sha256(self, data: str, secret_key: str) -> str:
        """Calculate HMAC-SHA256 checksum for critical events."""
        return hmac.new(
            secret_key.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def set_secret_key(self, secret_key: str) -> None:
        """Set secret key for HMAC-SHA256 (for critical events)."""
        with self._lock:
            self._secret_key = secret_key
    
    def generate_checksum(
        self,
        event_data: Dict[str, Any],
        event_type: str,
        algorithm: Optional[ChecksumAlgorithm] = None,
        sequence_id: Optional[int] = None,
    ) -> ChecksumResult:
        """
        Generate checksum for event data.
        
        Args:
            event_data: Event data to checksum
            event_type: Type of event
            algorithm: Checksum algorithm (defaults to CRC32)
            sequence_id: Optional sequence ID for tracking
            
        Returns:
            ChecksumResult with generated checksum
        """
        if algorithm is None:
            algorithm = self._default_algorithm
        
        try:
            serialized = self._serialize_event_data(event_data)

            if algorithm == ChecksumAlgorithm.CRC32:
                checksum = self._calculate_crc32(serialized)
            elif algorithm == ChecksumAlgorithm.SHA256:
                # Use HMAC-SHA256 if secret key is set, otherwise use regular SHA256
                if self._secret_key:
                    checksum = self._calculate_hmac_sha256(serialized, self._secret_key)
                else:
                    checksum = self._calculate_sha256(serialized)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            self._checksums_generated += 1
            self._algorithm_distribution[algorithm.value] = \
                self._algorithm_distribution.get(algorithm.value, 0) + 1
            
            return ChecksumResult(
                algorithm=algorithm,
                checksum=checksum,
                timestamp=datetime.utcnow(),
                event_type=event_type,
                sequence_id=sequence_id,
            )
        except Exception as e:
            raise ValueError(f"Checksum generation failed: {e}")
    
    def validate_checksum(
        self,
        event_data: Dict[str, Any],
        expected_checksum: str,
        algorithm: ChecksumAlgorithm,
        event_type: str,
        sequence_id: Optional[int] = None,
    ) -> ChecksumResult:
        """
        Validate event data against expected checksum.
        
        Args:
            event_data: Event data to validate
            expected_checksum: Expected checksum value
            algorithm: Checksum algorithm used
            event_type: Type of event
            sequence_id: Optional sequence ID for tracking
            
        Returns:
            ChecksumResult with validation outcome
        """
        try:
            result = self.generate_checksum(
                event_data,
                event_type,
                algorithm,
                sequence_id,
            )
            
            self._checksums_validated += 1

            # Use constant-time comparison to prevent timing attacks
            if hmac.compare_digest(result.checksum, expected_checksum):
                result.is_valid = True
                return result
            else:
                result.is_valid = False
                result.error_message = (
                    f"Checksum mismatch: expected {expected_checksum}, "
                    f"got {result.checksum}"
                )
                self._validation_failures += 1
                return result
        except Exception as e:
            self._validation_failures += 1
            return ChecksumResult(
                algorithm=algorithm,
                checksum="",
                timestamp=datetime.utcnow(),
                event_type=event_type,
                sequence_id=sequence_id,
                is_valid=False,
                error_message=f"Validation error: {e}",
            )
    
    def get_algorithm_for_category(self, category: str) -> ChecksumAlgorithm:
        """
        Get recommended checksum algorithm for event category.
        
        Args:
            category: Event category (critical, performance, etc.)
            
        Returns:
            ChecksumAlgorithm for the category
        """
        # Use SHA256 for critical events, CRC32 for others
        if category == 'critical':
            return ChecksumAlgorithm.SHA256
        return ChecksumAlgorithm.CRC32
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get checksum metrics."""
        with self._lock:
            total_checksums = self._checksums_generated
            total_validations = self._checksums_validated

            return {
                'checksums_generated': total_checksums,
                'checksums_validated': total_validations,
                'validation_failures': self._validation_failures,
                'validation_failure_rate': (
                    self._validation_failures / total_validations
                    if total_validations > 0 else 0
                ),
                'algorithm_distribution': self._algorithm_distribution.copy(),
            }

    def flush_metrics(self) -> Dict[str, Any]:
        """Get and reset metrics."""
        with self._lock:
            metrics = self.get_metrics()
            self.reset_metrics()
            return metrics


# DEPRECATED: Factory function replaced with direct instantiation
# Use: checksum_manager = ChecksumManager() instead of get_checksum_manager()

