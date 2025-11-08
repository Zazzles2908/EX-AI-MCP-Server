#!/usr/bin/env python3
"""
Secure Secrets Management for EX-AI MCP Server
Manages JWT tokens and API keys securely using Supabase
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta

try:
    from supabase import create_client, Client
except ImportError:
    Client = None


class SecretsManager:
    """
    Manages secrets (JWT tokens, API keys) securely.
    Uses Supabase as primary storage with environment variables as fallback.
    """

    def __init__(self, config=None):
        self.config = config
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase: Optional[Client] = None

        if self.supabase_url and self.supabase_key and Client:
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Supabase client: {e}")

    def get_secret(self, key: str) -> Optional[str]:
        """
        Get a secret value

        Priority:
        1. Supabase (if available)
        2. Environment variable
        3. .secrets file (local development)

        Args:
            key: Secret key name

        Returns:
            Secret value or None
        """
        # Try Supabase first (if available)
        if self.supabase:
            try:
                result = self.supabase.table("secrets").select("value").eq("key", key).execute()
                if result.data and len(result.data) > 0:
                    return result.data[0]["value"]
            except Exception as e:
                print(f"Warning: Failed to fetch secret '{key}' from Supabase: {e}")

        # Fall back to environment variable
        env_key = key.upper()
        value = os.getenv(env_key)
        if value:
            return value

        # Fall back to .secrets file (development only)
        secrets_file = Path(".secrets")
        if secrets_file.exists():
            try:
                with open(secrets_file, "r") as f:
                    secrets = json.load(f)
                return secrets.get(key)
            except Exception as e:
                print(f"Warning: Failed to read secrets from file: {e}")

        return None

    def set_secret(self, key: str, value: str, store_in_supabase: bool = False) -> bool:
        """
        Set a secret value

        Args:
            key: Secret key name
            value: Secret value
            store_in_supabase: Whether to store in Supabase

        Returns:
            True if successful
        """
        # Store in Supabase if requested
        if store_in_supabase and self.supabase:
            try:
                self.supabase.table("secrets").upsert(
                    {"key": key, "value": value, "updated_at": datetime.now().isoformat()}
                ).execute()
                return True
            except Exception as e:
                print(f"Warning: Failed to store secret in Supabase: {e}")

        # Store in environment (only for current session)
        os.environ[key.upper()] = value
        return True

    def get_jwt_token(self, client_id: str) -> Optional[str]:
        """
        Get JWT token for a specific client

        Args:
            client_id: Client identifier (e.g., 'claude', 'vscode1', 'vscode2')

        Returns:
            JWT token or None
        """
        # Try to get from environment first
        env_key = f"EXAI_JWT_TOKEN_{client_id.upper()}"
        token = os.getenv(env_key)

        if token:
            return token

        # Try to get from Supabase
        if self.supabase:
            try:
                result = (
                    self.supabase.table("jwt_tokens")
                    .select("token")
                    .eq("client_id", client_id)
                    .execute()
                )
                if result.data and len(result.data) > 0:
                    return result.data[0]["token"]
            except Exception as e:
                print(f"Warning: Failed to fetch JWT token for '{client_id}' from Supabase: {e}")

        return None

    def store_jwt_token(self, client_id: str, token: str, store_in_supabase: bool = False) -> bool:
        """
        Store JWT token for a specific client

        Args:
            client_id: Client identifier
            token: JWT token
            store_in_supabase: Whether to store in Supabase

        Returns:
            True if successful
        """
        # Store in environment
        env_key = f"EXAI_JWT_TOKEN_{client_id.upper()}"
        os.environ[env_key] = token

        # Store in Supabase if requested
        if store_in_supabase and self.supabase:
            try:
                self.supabase.table("jwt_tokens").upsert(
                    {
                        "client_id": client_id,
                        "token": token,
                        "updated_at": datetime.now().isoformat(),
                    }
                ).execute()
                return True
            except Exception as e:
                print(f"Warning: Failed to store JWT token in Supabase: {e}")

        return True

    def generate_jwt_token(
        self,
        client_id: str,
        expires_days: int = 365,
        store_in_supabase: bool = False,
    ) -> str:
        """
        Generate a new JWT token for a client

        Args:
            client_id: Client identifier
            expires_days: Token expiration in days
            store_in_supabase: Whether to store in Supabase

        Returns:
            Generated JWT token
        """
        try:
            import jwt
        except ImportError:
            raise RuntimeError("PyJWT is not installed. Run: pip install PyJWT")

        secret_key = self.get_secret("JWT_SECRET_KEY")
        if not secret_key:
            raise ValueError("JWT_SECRET_KEY not found in secrets")

        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        issuer = os.getenv("JWT_ISSUER", "exai-mcp-server")
        audience = os.getenv("JWT_AUDIENCE", "exai-mcp-client")

        now = datetime.utcnow()
        payload = {
            "sub": client_id,
            "iss": issuer,
            "aud": audience,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=expires_days)).timestamp()),
        }

        token = jwt.encode(payload, secret_key, algorithm=algorithm)

        # Store the token
        self.store_jwt_token(client_id, token, store_in_supabase=store_in_supabase)

        return token

    def list_secrets(self) -> Dict[str, bool]:
        """
        List all configured secrets (without revealing values)

        Returns:
            Dictionary of secret names and their availability
        """
        secrets_to_check = [
            "KIMI_API_KEY",
            "GLM_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_SERVICE_ROLE_KEY",
            "JWT_SECRET_KEY",
            "EXAI_JWT_TOKEN_CLAUDE",
            "EXAI_JWT_TOKEN_VSCODE1",
            "EXAI_JWT_TOKEN_VSCODE2",
        ]

        return {secret: bool(self.get_secret(secret)) for secret in secrets_to_check}


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager instance"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager
