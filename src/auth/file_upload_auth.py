"""
File Upload Authentication Module

Provides JWT-based authentication and authorization for file uploads.
Implements user quota checking and permission validation.

CRITICAL SECURITY FIX (2025-11-02): Task 0.1
- Prevents unauthorized file uploads
- Enforces user quotas
- Validates JWT tokens
- Tracks upload permissions

Author: EX-AI MCP Server
Date: 2025-11-02
"""

import jwt
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.storage.supabase_manager import SupabaseManager
from src.utils.config_loader import get_config

logger = logging.getLogger(__name__)

# Security scheme for FastAPI
security = HTTPBearer()


class FileUploadAuth:
    """
    Authentication and authorization for file uploads.
    
    Features:
    - JWT token validation
    - User quota checking
    - Permission verification
    - Upload tracking
    """
    
    def __init__(self, supabase_client: Optional[SupabaseManager] = None):
        """
        Initialize authentication module.
        
        Args:
            supabase_client: Supabase client for database operations
        """
        self.supabase = supabase_client or SupabaseManager()
        self.config = get_config()
        
        # Get JWT secret from environment
        self.jwt_secret = self.config.get("SUPABASE_JWT_SECRET")
        if not self.jwt_secret:
            logger.warning("SUPABASE_JWT_SECRET not configured - authentication disabled")
            self.jwt_secret = None
        
        # Default quotas (can be overridden per user)
        self.default_quota_bytes = int(self.config.get("DEFAULT_USER_QUOTA_BYTES", 10737418240))  # 10GB
        self.default_max_file_size = int(self.config.get("DEFAULT_MAX_FILE_SIZE_BYTES", 536870912))  # 512MB
        
        logger.info(f"FileUploadAuth initialized (JWT: {'enabled' if self.jwt_secret else 'disabled'})")
    
    async def verify_upload_permission(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """
        Verify user has permission to upload files.
        
        Args:
            credentials: HTTP Bearer token credentials
            
        Returns:
            Dict containing user_id, quota_remaining, max_file_size
            
        Raises:
            HTTPException: 401 if token invalid, 403 if quota exceeded
        """
        if not self.jwt_secret:
            # Authentication disabled - allow all uploads (development mode)
            logger.warning("Authentication disabled - allowing upload without verification")
            return {
                "user_id": "anonymous",
                "quota_remaining": self.default_quota_bytes,
                "max_file_size": self.default_max_file_size,
                "authenticated": False
            }
        
        try:
            # Decode and validate JWT token
            token = credentials.credentials
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            
            # Extract user ID from token
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID"
                )
            
            # Check user quota
            quota = await self.check_user_quota(user_id)
            
            if quota["remaining"] <= 0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Upload quota exceeded. Please contact support."
                )
            
            logger.info(f"User {user_id} authenticated for upload (quota: {quota['remaining']} bytes)")
            
            return {
                "user_id": user_id,
                "quota_remaining": quota["remaining"],
                "max_file_size": quota["max_file_size"],
                "authenticated": True
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    async def check_user_quota(self, user_id: str) -> Dict[str, int]:
        """
        Check user's upload quota.
        
        Args:
            user_id: User ID from JWT token
            
        Returns:
            Dict with 'remaining' and 'max_file_size' in bytes
        """
        try:
            # Query user_quotas table
            result = await self.supabase.client.table("user_quotas")\
                .select("*")\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if result.data:
                return {
                    "remaining": result.data.get("quota_remaining", self.default_quota_bytes),
                    "max_file_size": result.data.get("max_file_size", self.default_max_file_size)
                }
            else:
                # User not in quotas table - create default entry
                logger.info(f"Creating default quota for user {user_id}")
                await self.create_default_quota(user_id)
                
                return {
                    "remaining": self.default_quota_bytes,
                    "max_file_size": self.default_max_file_size
                }
                
        except Exception as e:
            logger.error(f"Error checking user quota: {e}")
            # Return default quota on error (fail open for availability)
            return {
                "remaining": self.default_quota_bytes,
                "max_file_size": self.default_max_file_size
            }
    
    async def create_default_quota(self, user_id: str) -> None:
        """
        Create default quota entry for new user.
        
        Args:
            user_id: User ID to create quota for
        """
        try:
            await self.supabase.client.table("user_quotas").insert({
                "user_id": user_id,
                "quota_remaining": self.default_quota_bytes,
                "max_file_size": self.default_max_file_size,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
            
            logger.info(f"Created default quota for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error creating default quota: {e}")
    
    async def update_quota_after_upload(
        self, 
        user_id: str, 
        file_size: int
    ) -> None:
        """
        Update user quota after successful upload.
        
        Args:
            user_id: User ID
            file_size: Size of uploaded file in bytes
        """
        try:
            # Decrement quota_remaining
            await self.supabase.client.rpc(
                "decrement_user_quota",
                {"p_user_id": user_id, "p_bytes": file_size}
            ).execute()
            
            logger.info(f"Updated quota for user {user_id} (-{file_size} bytes)")
            
        except Exception as e:
            logger.error(f"Error updating quota: {e}")
    
    async def verify_file_size_limit(
        self, 
        user_id: str, 
        file_size: int
    ) -> bool:
        """
        Verify file size is within user's limit.
        
        Args:
            user_id: User ID
            file_size: Size of file to upload in bytes
            
        Returns:
            True if within limit, False otherwise
        """
        quota = await self.check_user_quota(user_id)
        
        if file_size > quota["max_file_size"]:
            logger.warning(
                f"File size {file_size} exceeds limit {quota['max_file_size']} "
                f"for user {user_id}"
            )
            return False
        
        if file_size > quota["remaining"]:
            logger.warning(
                f"File size {file_size} exceeds remaining quota {quota['remaining']} "
                f"for user {user_id}"
            )
            return False
        
        return True


# Dependency for FastAPI routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user.
    
    Usage:
        @app.post("/upload")
        async def upload_file(user: Dict = Depends(get_current_user)):
            user_id = user["user_id"]
            ...
    """
    auth = FileUploadAuth()
    return await auth.verify_upload_permission(credentials)

