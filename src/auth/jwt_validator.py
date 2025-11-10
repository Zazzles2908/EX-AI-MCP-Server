"""
JWT Validator - Authentication Module for WebSocket Server

This module provides JWT (JSON Web Token) authentication for the WebSocket server.
It implements secure token validation with configurable grace periods for migration.

BATCH 4.3 (2025-11-02): JWT Authentication Implementation
- Secure JWT token validation
- Configurable grace period for migration (2 weeks default)
- Support for both authenticated and legacy connections during transition
- Integration with WebSocket connection handler

Security Features:
- HS256 algorithm (HMAC with SHA-256)
- Token expiration validation
- Issuer and audience validation (optional)
- Grace period for backward compatibility

Usage:
    from src.auth.jwt_validator import JWTValidator
    
    validator = JWTValidator(secret_key=os.getenv("JWT_SECRET_KEY"))
    
    # Validate token
    payload = validator.validate_token(token)
    if payload:
        # Token valid - proceed with authenticated request
        user_id = payload.get("sub")
    else:
        # Token invalid - reject request
        raise Unauthorized("Invalid token")
    
    # Check if grace period is active
    if validator.is_grace_period_active():
        # Allow both authenticated and unauthenticated connections
        pass
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logging.warning("PyJWT not installed - JWT authentication will be disabled")

logger = logging.getLogger(__name__)


class JWTValidationError(Exception):
    """Raised when JWT validation fails."""
    pass


class JWTValidator:
    """
    Validates JWT tokens for WebSocket authentication.
    
    This class provides secure JWT token validation with support for:
    - Token signature verification
    - Expiration checking
    - Issuer/audience validation
    - Grace period for migration
    
    Attributes:
        secret_key: Secret key for JWT signature verification
        algorithm: JWT algorithm (default: HS256)
        grace_period_end: Timestamp when grace period ends (None = no grace period)
    """
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        grace_period_days: int = 14,
        issuer: Optional[str] = None,
        audience: Optional[str] = None
    ):
        """
        Initialize JWT validator.
        
        Args:
            secret_key: Secret key for JWT signature verification
            algorithm: JWT algorithm (default: HS256)
            grace_period_days: Number of days for grace period (0 = no grace period)
            issuer: Expected token issuer (optional)
            audience: Expected token audience (optional)
        
        Raises:
            ValueError: If secret_key is empty or PyJWT is not installed
        """
        if not JWT_AVAILABLE:
            raise ValueError("PyJWT is not installed - cannot create JWTValidator")
        
        if not secret_key:
            raise ValueError("secret_key cannot be empty")
        
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.issuer = issuer
        self.audience = audience
        
        # Calculate grace period end time
        if grace_period_days > 0:
            self.grace_period_end = datetime.utcnow() + timedelta(days=grace_period_days)
            logger.info(f"[JWT_VALIDATOR] Grace period active until {self.grace_period_end.isoformat()}")
        else:
            self.grace_period_end = None
            logger.info("[JWT_VALIDATOR] No grace period - strict authentication enforced")
        
        logger.info(f"[JWT_VALIDATOR] Initialized with algorithm={algorithm}, issuer={issuer}, audience={audience}")
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a JWT token and return the payload.
        
        This method:
        1. Verifies token signature
        2. Checks expiration
        3. Validates issuer/audience (if configured)
        4. Returns payload if valid
        
        Args:
            token: JWT token string
        
        Returns:
            Token payload as dictionary if valid, None if invalid
        
        Examples:
            >>> validator = JWTValidator(secret_key="secret")
            >>> payload = validator.validate_token("eyJ...")
            >>> if payload:
            ...     user_id = payload.get("sub")
            ...     logger.info("Token validated successfully")
        """
        if not token:
            logger.debug("[JWT_VALIDATOR] Empty token provided")
            return None
        
        try:
            # Decode and validate token
            options = {
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "require": ["exp", "iat"]
            }
            
            # Add issuer/audience validation if configured
            if self.issuer:
                options["verify_iss"] = True
            if self.audience:
                options["verify_aud"] = True
            
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options=options,
                issuer=self.issuer,
                audience=self.audience
            )
            
            logger.debug(f"[JWT_VALIDATOR] Token validated successfully for user: {payload.get('sub', 'unknown')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("[JWT_VALIDATOR] Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"[JWT_VALIDATOR] Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"[JWT_VALIDATOR] Unexpected error validating token: {e}")
            return None
    
    def is_grace_period_active(self) -> bool:
        """
        Check if grace period is currently active.
        
        During grace period, both authenticated and unauthenticated
        connections are allowed for backward compatibility.
        
        Returns:
            True if grace period is active, False otherwise
        """
        if self.grace_period_end is None:
            return False
        
        return datetime.utcnow() < self.grace_period_end
    
    def should_enforce_auth(self) -> bool:
        """
        Check if authentication should be strictly enforced.
        
        Returns:
            True if auth should be enforced (grace period ended), False otherwise
        """
        return not self.is_grace_period_active()
    
    def get_grace_period_remaining(self) -> Optional[timedelta]:
        """
        Get remaining time in grace period.
        
        Returns:
            Remaining time as timedelta, or None if no grace period
        """
        if self.grace_period_end is None:
            return None
        
        remaining = self.grace_period_end - datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)


def create_jwt_validator_from_env() -> Optional[JWTValidator]:
    """
    Create JWTValidator from environment variables.
    
    Reads configuration from:
    - JWT_SECRET_KEY: Secret key for JWT validation (required)
    - JWT_ALGORITHM: JWT algorithm (default: HS256)
    - JWT_GRACE_PERIOD_DAYS: Grace period in days (default: 14)
    - JWT_ISSUER: Expected token issuer (optional)
    - JWT_AUDIENCE: Expected token audience (optional)
    
    Returns:
        JWTValidator instance if JWT_SECRET_KEY is set, None otherwise
    
    Examples:
        # .env.docker
        JWT_SECRET_KEY=your-secret-key-here
        JWT_GRACE_PERIOD_DAYS=14
        
        # Python
        validator = create_jwt_validator_from_env()
        if validator:
            payload = validator.validate_token(token)
    """
    if not JWT_AVAILABLE:
        logger.warning("[JWT_VALIDATOR] PyJWT not installed - JWT authentication disabled")
        return None
    
    secret_key = os.getenv("JWT_SECRET_KEY", "").strip()
    if not secret_key:
        # UX FIX: Make JWT warning more prominent for production deployments
        logger.warning("=" * 80)
        logger.warning("SECURITY WARNING: JWT authentication is DISABLED")
        logger.warning("=" * 80)
        logger.warning("To enable secure authentication:")
        logger.warning("  1. Set JWT_SECRET_KEY in your .env file")
        logger.warning("  2. Generate a secure secret: python -c 'import secrets; print(secrets.token_hex(32))'")
        logger.warning("  3. Restart the server")
        logger.warning("=" * 80)
        return None
    
    algorithm = os.getenv("JWT_ALGORITHM", "HS256").strip()
    grace_period_days = int(os.getenv("JWT_GRACE_PERIOD_DAYS", "14"))
    issuer = os.getenv("JWT_ISSUER", "").strip() or None
    audience = os.getenv("JWT_AUDIENCE", "").strip() or None
    
    try:
        validator = JWTValidator(
            secret_key=secret_key,
            algorithm=algorithm,
            grace_period_days=grace_period_days,
            issuer=issuer,
            audience=audience
        )
        logger.info("[JWT_VALIDATOR] JWT validator created from environment")
        return validator
    except Exception as e:
        logger.error(f"[JWT_VALIDATOR] Failed to create validator: {e}")
        return None


# Global validator instance (lazy-initialized)
_global_validator: Optional[JWTValidator] = None


def get_global_validator() -> Optional[JWTValidator]:
    """
    Get global JWTValidator instance (singleton).
    
    Returns:
        JWTValidator instance or None if JWT authentication is disabled
    """
    global _global_validator
    if _global_validator is None:
        _global_validator = create_jwt_validator_from_env()
    return _global_validator


__all__ = [
    "JWTValidator",
    "JWTValidationError",
    "create_jwt_validator_from_env",
    "get_global_validator",
]

