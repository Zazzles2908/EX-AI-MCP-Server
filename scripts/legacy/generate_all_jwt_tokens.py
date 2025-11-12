#!/usr/bin/env python3
"""
Generate JWT Tokens for All MCP Clients

This script generates separate JWT tokens for each MCP client:
- vscode1@exai-mcp.local (for EXAI-WS-VSCode1)
- vscode2@exai-mcp.local (for EXAI-WS-VSCode2)
- claude@exai-mcp.local (for Claude Desktop)

Each token is unique and can be tracked separately in logs.

Usage:
    python scripts/generate_all_jwt_tokens.py

Author: EX-AI MCP Server Team
Date: 2025-11-03
"""

import os
import sys
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
else:
    print(f"ERROR: .env.docker not found at {env_docker_path}")
    sys.exit(1)

try:
    import jwt
except ImportError:
    print("ERROR: PyJWT is not installed. Install it with: pip install PyJWT>=2.8.0")
    sys.exit(1)


def generate_jwt_token(user_id: str, expires_days: int = 365) -> str:
    """Generate a JWT token for a specific user."""
    secret_key = os.getenv("JWT_SECRET_KEY", "").strip()
    algorithm = os.getenv("JWT_ALGORITHM", "HS256").strip()
    issuer = os.getenv("JWT_ISSUER", "exai-mcp-server").strip()
    audience = os.getenv("JWT_AUDIENCE", "exai-mcp-client").strip()
    
    if not secret_key:
        raise ValueError("JWT_SECRET_KEY not found in environment")
    
    # Create payload
    now = datetime.utcnow()
    payload = {
        "sub": user_id,
        "iss": issuer,
        "aud": audience,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=expires_days)).timestamp()),
    }
    
    # Generate token
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


def main():
    print("="*80)
    print("GENERATING JWT TOKENS FOR ALL MCP CLIENTS")
    print("="*80)
    print()
    
    # Define clients
    clients = [
        {
            "name": "EXAI-WS-VSCode1",
            "user_id": "vscode1@exai-mcp.local",
            "config_file": "config/daemon/mcp-config.augmentcode.vscode1.json",
            "env_var": "EXAI_JWT_TOKEN_VSCODE1"
        },
        {
            "name": "EXAI-WS-VSCode2",
            "user_id": "vscode2@exai-mcp.local",
            "config_file": "config/daemon/mcp-config.augmentcode.vscode2.json",
            "env_var": "EXAI_JWT_TOKEN_VSCODE2"
        },
        {
            "name": "Claude Desktop",
            "user_id": "claude@exai-mcp.local",
            "config_file": "config/daemon/mcp-config.claude.json",
            "env_var": "EXAI_JWT_TOKEN_CLAUDE"
        }
    ]
    
    tokens = {}
    
    # Generate tokens
    for client in clients:
        try:
            token = generate_jwt_token(client["user_id"], expires_days=365)
            tokens[client["name"]] = {
                "user_id": client["user_id"],
                "token": token,
                "config_file": client["config_file"],
                "env_var": client["env_var"]
            }
            print(f"✅ Generated token for {client['name']}")
        except Exception as e:
            print(f"❌ Failed to generate token for {client['name']}: {e}")
            sys.exit(1)
    
    print()
    print("="*80)
    print("TOKENS GENERATED SUCCESSFULLY")
    print("="*80)
    print()
    
    # Display tokens
    for name, info in tokens.items():
        print(f"## {name}")
        print(f"User ID: {info['user_id']}")
        print(f"Config: {info['config_file']}")
        print(f"Token:")
        print(info['token'])
        print()
    
    print("="*80)
    print("CONFIGURATION INSTRUCTIONS")
    print("="*80)
    print()
    
    # VSCode1
    print("### 1. Update config/daemon/mcp-config.augmentcode.vscode1.json")
    print('Add to "env" section:')
    print(f'"EXAI_JWT_TOKEN": "{tokens["EXAI-WS-VSCode1"]["token"]}"')
    print()
    
    # VSCode2
    print("### 2. Update config/daemon/mcp-config.augmentcode.vscode2.json")
    print('Add to "env" section:')
    print(f'"EXAI_JWT_TOKEN": "{tokens["EXAI-WS-VSCode2"]["token"]}"')
    print()
    
    # Claude
    print("### 3. Update config/daemon/mcp-config.claude.json")
    print('Add to "env" section:')
    print(f'"EXAI_JWT_TOKEN": "{tokens["Claude Desktop"]["token"]}"')
    print()
    
    print("="*80)
    print("NEXT STEPS")
    print("="*80)
    print()
    print("1. Update the three config files with their respective tokens")
    print("2. Restart VSCode / Claude Desktop to apply changes")
    print("3. Check logs for JWT authentication success")
    print()
    print("Tokens expire: 2026-11-03 (1 year)")
    print("="*80)


if __name__ == "__main__":
    main()

