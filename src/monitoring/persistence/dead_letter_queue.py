"""
Dead Letter Queue (DLQ) for Failed Metrics Operations

Stores failed metrics operations for later retry and recovery.
Provides persistence, retry logic, and recovery mechanisms.

EXAI Consultation: ac40c717-09db-4b0a-b943-6e38730a1300
Date: 2025-11-01
Phase: Phase 2.4.6 - MetricsPersister Resilience
"""

import logging
import json
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class DLQItem:
    """Represents a failed operation in the DLQ"""
    id: Optional[int] = None
    original_payload: Dict[str, Any] = None
    failure_reason: str = ""
    retry_count: int = 0
    max_retries: int = 5
    created_at: Optional[datetime] = None
    last_retry_at: Optional[datetime] = None
    recovered_at: Optional[datetime] = None
    status: str = "pending"  # pending, retrying, recovered, failed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'original_payload': self.original_payload,
            'failure_reason': self.failure_reason,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_retry_at': self.last_retry_at.isoformat() if self.last_retry_at else None,
            'recovered_at': self.recovered_at.isoformat() if self.recovered_at else None,
            'status': self.status,
        }


class DeadLetterQueue:
    """
    Dead Letter Queue for storing and recovering failed metrics operations.
    
    Features:
    - Store failed operations with metadata
    - Retry mechanism with configurable limits
    - Recovery tracking
    - Metrics and statistics
    - Cleanup of old items
    """
    
    def __init__(self, supabase_client: Any, max_retries: int = 5):
        """
        Initialize Dead Letter Queue.
        
        Args:
            supabase_client: Supabase client instance
            max_retries: Maximum retry attempts per item (default: 5)
        """
        self.supabase = supabase_client
        self.max_retries = max_retries
        self._stats = {
            'total_stored': 0,
            'total_recovered': 0,
            'total_failed': 0,
            'current_pending': 0,
        }
    
    def store_failed_operation(
        self,
        payload: Dict[str, Any],
        failure_reason: str,
        max_retries: Optional[int] = None
    ) -> bool:
        """
        Store a failed operation in the DLQ.
        
        Args:
            payload: Original operation payload
            failure_reason: Reason for failure
            max_retries: Override default max retries
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            item = DLQItem(
                original_payload=payload,
                failure_reason=failure_reason,
                max_retries=max_retries or self.max_retries,
                created_at=datetime.now(),
                status='pending'
            )
            
            # Store in database
            data = item.to_dict()
            self.supabase.table('monitoring.dead_letter_queue').insert(data).execute()
            
            self._stats['total_stored'] += 1
            self._stats['current_pending'] += 1
            
            logger.info(f"Stored failed operation in DLQ: {failure_reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store operation in DLQ: {e}")
            return False
    
    def get_pending_items(self, limit: int = 100) -> List[DLQItem]:
        """
        Get pending items from DLQ for retry.
        
        Args:
            limit: Maximum items to retrieve
            
        Returns:
            List of pending DLQ items
        """
        try:
            result = self.supabase.table('monitoring.dead_letter_queue').select(
                '*'
            ).eq('status', 'pending').limit(limit).execute()
            
            items = []
            for row in result.data:
                item = DLQItem(
                    id=row.get('id'),
                    original_payload=row.get('original_payload'),
                    failure_reason=row.get('failure_reason'),
                    retry_count=row.get('retry_count', 0),
                    max_retries=row.get('max_retries', self.max_retries),
                    created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else None,
                    last_retry_at=datetime.fromisoformat(row['last_retry_at']) if row.get('last_retry_at') else None,
                    recovered_at=datetime.fromisoformat(row['recovered_at']) if row.get('recovered_at') else None,
                    status=row.get('status', 'pending')
                )
                items.append(item)
            
            return items
            
        except Exception as e:
            logger.error(f"Failed to get pending DLQ items: {e}")
            return []
    
    def mark_recovered(self, item_id: int) -> bool:
        """
        Mark a DLQ item as recovered.
        
        Args:
            item_id: ID of the DLQ item
            
        Returns:
            True if marked successfully, False otherwise
        """
        try:
            self.supabase.table('monitoring.dead_letter_queue').update({
                'status': 'recovered',
                'recovered_at': datetime.now().isoformat()
            }).eq('id', item_id).execute()
            
            self._stats['total_recovered'] += 1
            self._stats['current_pending'] -= 1
            
            logger.info(f"Marked DLQ item {item_id} as recovered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark DLQ item as recovered: {e}")
            return False
    
    def mark_failed(self, item_id: int) -> bool:
        """
        Mark a DLQ item as permanently failed.
        
        Args:
            item_id: ID of the DLQ item
            
        Returns:
            True if marked successfully, False otherwise
        """
        try:
            self.supabase.table('monitoring.dead_letter_queue').update({
                'status': 'failed'
            }).eq('id', item_id).execute()
            
            self._stats['total_failed'] += 1
            self._stats['current_pending'] -= 1
            
            logger.warning(f"Marked DLQ item {item_id} as permanently failed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark DLQ item as failed: {e}")
            return False
    
    def increment_retry_count(self, item_id: int) -> bool:
        """
        Increment retry count for a DLQ item.
        
        Args:
            item_id: ID of the DLQ item
            
        Returns:
            True if incremented successfully, False otherwise
        """
        try:
            self.supabase.table('monitoring.dead_letter_queue').update({
                'retry_count': self.supabase.rpc('increment_retry_count', {'item_id': item_id}),
                'last_retry_at': datetime.now().isoformat()
            }).eq('id', item_id).execute()
            
            logger.debug(f"Incremented retry count for DLQ item {item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to increment retry count: {e}")
            return False
    
    def cleanup_old_items(self, days: int = 30) -> int:
        """
        Clean up old recovered/failed items from DLQ.
        
        Args:
            days: Remove items older than this many days
            
        Returns:
            Number of items deleted
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            result = self.supabase.table('monitoring.dead_letter_queue').delete().lt(
                'created_at', cutoff_date
            ).in_('status', ['recovered', 'failed']).execute()
            
            deleted_count = len(result.data) if result.data else 0
            logger.info(f"Cleaned up {deleted_count} old DLQ items")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old DLQ items: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get DLQ statistics"""
        return self._stats.copy()
    
    def get_size(self) -> int:
        """Get current number of pending items in DLQ"""
        try:
            result = self.supabase.table('monitoring.dead_letter_queue').select(
                'count', count='exact'
            ).eq('status', 'pending').execute()
            
            return result.count or 0
            
        except Exception as e:
            logger.error(f"Failed to get DLQ size: {e}")
            return 0


# Global DLQ instance
_dlq_instance: Optional[DeadLetterQueue] = None


def get_dlq(supabase_client: Optional[Any] = None) -> DeadLetterQueue:
    """
    Get or create global DLQ instance.
    
    Args:
        supabase_client: Supabase client (required for first call)
        
    Returns:
        DeadLetterQueue instance
    """
    global _dlq_instance
    
    if _dlq_instance is None:
        if supabase_client is None:
            raise ValueError("supabase_client required for first initialization")
        _dlq_instance = DeadLetterQueue(supabase_client)
    
    return _dlq_instance

