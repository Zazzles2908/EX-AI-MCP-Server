# src/security/audit_logger.py
"""
Audit Logger for File Access Tracking

Phase A2 Week 1 - Basic Security Infrastructure
Logs all file operations to Supabase for security auditing
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class AuditLogger:
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize audit logger with Supabase connection
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase service key (should be stored securely)
        """
        # Get credentials from environment if not provided
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_SERVICE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("⚠️ Supabase credentials not found. Audit logging will be disabled.")
            self.supabase = None
        else:
            try:
                self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
                logger.info("✅ Audit logger connected to Supabase")
            except Exception as e:
                logger.error(f"Failed to connect to Supabase: {e}")
                self.supabase = None
        
        self.table_name = 'audit_logs'
    
    def log_file_access(self, 
                       application_id: str, 
                       user_id: str, 
                       file_path: str, 
                       operation: str, 
                       provider: str,
                       additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log file access to Supabase audit_logs table
        
        Args:
            application_id: ID of the application making the request
            user_id: ID of the user performing the operation
            file_path: Path to the file being accessed
            operation: Type of operation (upload, download, delete, etc.)
            provider: Storage provider used (kimi, glm, etc.)
            additional_data: Optional additional metadata
            
        Returns:
            True if logging was successful, False otherwise
        """
        if not self.supabase:
            logger.debug("Audit logging skipped (Supabase not configured)")
            return False
        
        try:
            # Prepare log entry
            log_entry = {
                'application_id': application_id,
                'user_id': user_id,
                'file_path': file_path,
                'operation': operation,
                'provider': provider,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Add additional data if provided
            if additional_data:
                log_entry['additional_data'] = additional_data
            
            # Insert into Supabase
            result = self.supabase.table(self.table_name).insert(log_entry).execute()
            
            # Check if insertion was successful
            if result.data:
                logger.debug(f"✅ Logged audit entry: {operation} on {file_path}")
                return True
            else:
                logger.warning(f"Failed to log audit entry: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error logging audit entry: {str(e)}")
            return False
    
    def get_access_logs(self, 
                       application_id: Optional[str] = None,
                       user_id: Optional[str] = None,
                       file_path: Optional[str] = None,
                       operation: Optional[str] = None,
                       provider: Optional[str] = None,
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None,
                       limit: int = 100) -> list:
        """
        Retrieve access logs from Supabase with optional filters
        
        Args:
            application_id: Filter by application ID
            user_id: Filter by user ID
            file_path: Filter by file path
            operation: Filter by operation type
            provider: Filter by storage provider
            start_time: Filter logs after this time
            end_time: Filter logs before this time
            limit: Maximum number of records to return
            
        Returns:
            List of matching log entries
        """
        if not self.supabase:
            logger.debug("Cannot retrieve logs (Supabase not configured)")
            return []
        
        try:
            query = self.supabase.table(self.table_name).select('*')
            
            # Apply filters
            if application_id:
                query = query.eq('application_id', application_id)
            if user_id:
                query = query.eq('user_id', user_id)
            if file_path:
                query = query.eq('file_path', file_path)
            if operation:
                query = query.eq('operation', operation)
            if provider:
                query = query.eq('provider', provider)
            if start_time:
                query = query.gte('timestamp', start_time.isoformat())
            if end_time:
                query = query.lte('timestamp', end_time.isoformat())
            
            # Order by timestamp (newest first) and limit results
            result = query.order('timestamp', desc=True).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error retrieving access logs: {str(e)}")
            return []

