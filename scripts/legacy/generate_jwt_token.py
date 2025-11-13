#!/usr/bin/env python3
"""
Generate JWT Token for EXAI MCP WebSocket Authentication

This script generates a JWT token for authenticating with the EXAI MCP WebSocket server.
The token is signed with the JWT_SECRET_KEY from .env.docker and includes:
- User ID (sub)
- Issuer (iss)
- Audience (aud)
- Expiration time (exp)
- Issued at time (iat)

Usage:
    python scripts/generate_jwt_token.py [--user-id USER_ID] [--expires-days DAYS]

Examples:
    # Generate token for default user (expires in 365 days)
    python scripts/generate_jwt_token.py
    
    # Generate token for specific user (expires in 30 days)
    python scripts/generate_jwt_token.py --user-id jazeel@example.com --expires-days 30
    
    # Generate token that never expires (expires in 10 years)
    python scripts/generate_jwt_token.py --expires-days 3650

Author: EX-AI MCP Server Team
Date: 2025-11-03
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add repo root to path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

# Load environment from .env.docker (where JWT_SECRET_KEY is stored)
from dotenv import load_dotenv
env_docker_path = repo_root / ".env.docker"
if env_docker_path.exists():
    load_dotenv(env_docker_path)
    print(f"Loaded environment from: {env_docker_path}")
else:
    print(f"WARNING: .env.docker not found at {env_docker_path}")
    # Try loading from .env as fallback
    env_path = repo_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment from: {env_path}")

try:
    import jwt
except ImportError:
    print("ERROR: PyJWT is not installed. Install it with: pip install PyJWT>=2.8.0")
    sys.exit(1)


def generate_jwt_token(
    user_id: str = "jazeel@example.com",
    expires_days: int = 365,
    secret_key: str = None,
    algorithm: str = "HS256",
    issuer: str = "exai-mcp-server",
    audience: str = "exai-mcp-client"
) -> str:
    """
    Generate a JWT token for WebSocket authentication.
    
    Args:
        user_id: User identifier (email or username)
        expires_days: Number of days until token expires
        secret_key: JWT secret key (from .env.docker)
        algorithm: JWT algorithm (default: HS256)
        issuer: Token issuer
        audience: Token audience
    
    Returns:
        JWT token string
    """
    if not secret_key:
        secret_key = os.getenv("JWT_SECRET_KEY", "").strip()
        if not secret_key:
            raise ValueError(
                "JWT_SECRET_KEY not found in environment. "
                "Make sure .env.docker is loaded or pass secret_key parameter."
            )
    
    # Create payload
    now = datetime.utcnow()
    payload = {
        "sub": user_id,  # Subject (user identifier)
        "iss": issuer,   # Issuer
        "aud": audience, # Audience
        "iat": int(now.timestamp()),  # Issued at
        "exp": int((now + timedelta(days=expires_days)).timestamp()),  # Expiration
    }
    
    # Generate token
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    
    return token


def main():
    parser = argparse.ArgumentParser(
        description="Generate JWT token for EXAI MCP WebSocket authentication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate token for default user (expires in 365 days)
  python scripts/generate_jwt_token.py
  
  # Generate token for specific user (expires in 30 days)
  python scripts/generate_jwt_token.py --user-id jazeel@example.com --expires-days 30
  
  # Generate token that never expires (expires in 10 years)
  python scripts/generate_jwt_token.py --expires-days 3650
        """
    )
    
    parser.add_argument(
        "--user-id",
        default="jazeel@example.com",
        help="User identifier (email or username). Default: jazeel@example.com"
    )
    
    parser.add_argument(
        "--expires-days",
        type=int,
        default=365,
        help="Number of days until token expires. Default: 365 (1 year)"
    )
    
    parser.add_argument(
        "--output",
        choices=["token", "env", "both"],
        default="both",
        help="Output format: 'token' (just the token), 'env' (env var format), 'both' (default)"
    )
    
    args = parser.parse_args()
    
    try:
        # Load JWT configuration from environment
        secret_key = os.getenv("JWT_SECRET_KEY", "").strip()
        algorithm = os.getenv("JWT_ALGORITHM", "HS256").strip()
        issuer = os.getenv("JWT_ISSUER", "exai-mcp-server").strip()
        audience = os.getenv("JWT_AUDIENCE", "exai-mcp-client").strip()
        
        if not secret_key:
            print("ERROR: JWT_SECRET_KEY not found in environment")
            print("Make sure .env.docker is loaded or set JWT_SECRET_KEY environment variable")
            sys.exit(1)
        
        # Generate token
        token = generate_jwt_token(
            user_id=args.user_id,
            expires_days=args.expires_days,
            secret_key=secret_key,
            algorithm=algorithm,
            issuer=issuer,
            audience=audience
        )
        
        # Calculate expiration date
        expiration_date = datetime.utcnow() + timedelta(days=args.expires_days)
        
        # Output based on format
        if args.output in ["token", "both"]:
            print("\n" + "="*80)
            print("JWT TOKEN GENERATED SUCCESSFULLY")
            print("="*80)
            print(f"\nUser ID: {args.user_id}")
            print(f"Expires: {expiration_date.strftime('%Y-%m-%d %H:%M:%S UTC')} ({args.expires_days} days)")
            print(f"Issuer: {issuer}")
            print(f"Audience: {audience}")
            print(f"Algorithm: {algorithm}")
            print("\nToken:")
            print("-"*80)
            print(token)
            print("-"*80)
        
        if args.output in ["env", "both"]:
            print("\n" + "="*80)
            print("ENVIRONMENT VARIABLE FORMAT")
            print("="*80)
            print("\nAdd this to your .env file:")
            print("-"*80)
            print(f"EXAI_JWT_TOKEN={token}")
            print("-"*80)
            print("\nOr add to VSCode MCP config:")
            print("-"*80)
            print(f'"EXAI_JWT_TOKEN": "{token}"')
            print("-"*80)
        
        print("\n" + "="*80)
        print("USAGE INSTRUCTIONS")
        print("="*80)
        print("\n1. Add to .env file:")
        print(f"   EXAI_JWT_TOKEN={token}")
        print("\n2. Add to VSCode MCP config (config/daemon/mcp-config.augmentcode.vscode1.json):")
        print('   "env": {')
        print('     ...')
        print(f'     "EXAI_JWT_TOKEN": "{token}"')
        print('   }')
        print("\n3. Restart VSCode to apply changes")
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"ERROR: Failed to generate JWT token: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

