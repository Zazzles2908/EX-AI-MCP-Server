"""
File ID Mapper for Supabase Universal File Hub
Date: 2025-10-30
EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9

Maps between Supabase file IDs and provider-specific file IDs.
Supports bidirectional lookup and session tracking for GLM.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class FileIdMapper:
    """
    Maps between Supabase file_ids and provider file_ids.
    
    Provides bidirectional lookup and tracks upload status for retry logic.
    """
    
    def __init__(self, supabase_client):
        """
        Initialize File ID Mapper.
        
        Args:
            supabase_client: Supabase client instance
        """
        self.client = supabase_client
    
    def store_mapping(
        self,
        supabase_id: str,
        provider_id: str,
        provider: str,
        user_id: str,
        session_info: Optional[Dict[str, Any]] = None,
        status: str = "completed"
    ) -> bool:
        """
        Store mapping between Supabase and provider file IDs.
        
        Args:
            supabase_id: Supabase file ID (storage path)
            provider_id: Provider-specific file ID
            provider: Provider name ('kimi' or 'glm')
            user_id: User ID
            session_info: Optional session information (for GLM)
            status: Upload status ('pending', 'completed', 'failed')
        
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'supabase_file_id': supabase_id,
                'provider_file_id': provider_id,
                'provider': provider,
                'user_id': user_id,
                'status': status,
                'retry_count': 0,
                'session_info': session_info or {}
            }
            
            self.client.table('file_id_mappings').insert(data).execute()
            logger.info(f"Stored mapping: {supabase_id} -> {provider}:{provider_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store mapping: {e}")
            return False
    
    def get_provider_id(self, supabase_id: str, provider: str) -> Optional[str]:
        """
        Get provider file_id from Supabase ID.
        
        Args:
            supabase_id: Supabase file ID
            provider: Provider name
        
        Returns:
            Provider file ID or None if not found
        """
        try:
            result = self.client.table('file_id_mappings').select('provider_file_id').eq(
                'supabase_file_id', supabase_id
            ).eq('provider', provider).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]['provider_file_id']
            return None
            
        except Exception as e:
            logger.error(f"Failed to get provider ID: {e}")
            return None
    
    def get_supabase_id(self, provider_id: str, provider: str) -> Optional[str]:
        """
        Get Supabase ID from provider file_id.
        
        Args:
            provider_id: Provider file ID
            provider: Provider name
        
        Returns:
            Supabase file ID or None if not found
        """
        try:
            result = self.client.table('file_id_mappings').select('supabase_file_id').eq(
                'provider_file_id', provider_id
            ).eq('provider', provider).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]['supabase_file_id']
            return None
            
        except Exception as e:
            logger.error(f"Failed to get Supabase ID: {e}")
            return None
    
    def get_session_info(self, supabase_id: str, provider: str) -> Optional[Dict[str, Any]]:
        """
        Get session information for a file (primarily for GLM).
        
        Args:
            supabase_id: Supabase file ID
            provider: Provider name
        
        Returns:
            Session info dictionary or None
        """
        try:
            result = self.client.table('file_id_mappings').select('session_info').eq(
                'supabase_file_id', supabase_id
            ).eq('provider', provider).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]['session_info']
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session info: {e}")
            return None
    
    def update_status(
        self,
        supabase_id: str,
        provider: str,
        status: str,
        increment_retry: bool = False
    ) -> bool:
        """
        Update upload status for retry logic.
        
        Args:
            supabase_id: Supabase file ID
            provider: Provider name
            status: New status ('pending', 'completed', 'failed')
            increment_retry: Whether to increment retry count
        
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {'status': status}
            
            if increment_retry:
                # Get current retry count
                result = self.client.table('file_id_mappings').select('retry_count').eq(
                    'supabase_file_id', supabase_id
                ).eq('provider', provider).limit(1).execute()
                
                if result.data and len(result.data) > 0:
                    current_count = result.data[0]['retry_count']
                    data['retry_count'] = current_count + 1
                    data['last_retry_at'] = datetime.utcnow().isoformat()
            
            self.client.table('file_id_mappings').update(data).eq(
                'supabase_file_id', supabase_id
            ).eq('provider', provider).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
            return False
    
    def get_failed_uploads(self, provider: Optional[str] = None, max_retries: int = 3) -> list:
        """
        Get failed uploads that can be retried.
        
        Args:
            provider: Optional provider filter
            max_retries: Maximum retry count to include
        
        Returns:
            List of failed upload records
        """
        try:
            query = self.client.table('file_id_mappings').select('*').eq('status', 'failed').lt(
                'retry_count', max_retries
            )
            
            if provider:
                query = query.eq('provider', provider)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Failed to get failed uploads: {e}")
            return []

