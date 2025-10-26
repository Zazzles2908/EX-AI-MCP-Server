#!/usr/bin/env python3
"""
Create test users in Supabase Auth for multi-user MCP testing.

This script creates two test users:
- Jazeel (jazeel@example.com)
- Michelle (michelle@example.com)

Usage:
    python scripts/create_test_users.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment from .env.docker (where Supabase credentials are stored)
from src.bootstrap import load_env, get_repo_root
env_file = str(get_repo_root() / ".env.docker")
load_env(env_file=env_file)

from supabase import create_client, Client
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_supabase_client() -> Client:
    """Create Supabase client with service role key."""
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not service_key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
    
    return create_client(url, service_key)


def create_user(client: Client, email: str, password: str, user_metadata: dict = None) -> dict:
    """
    Create a user in Supabase Auth.
    
    Args:
        client: Supabase client with service role key
        email: User email address
        password: User password
        user_metadata: Optional user metadata
        
    Returns:
        User data dictionary
    """
    try:
        logger.info(f"Creating user: {email}")
        
        # Create user using admin API
        response = client.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,  # Auto-confirm email for test users
            "user_metadata": user_metadata or {}
        })
        
        logger.info(f"✅ User created successfully: {email}")
        logger.info(f"   User ID: {response.user.id}")
        
        return {
            "id": response.user.id,
            "email": response.user.email,
            "created_at": response.user.created_at
        }
        
    except Exception as e:
        if "already been registered" in str(e):
            logger.warning(f"⚠️  User already exists: {email}")
            # Try to get existing user
            try:
                users = client.auth.admin.list_users()
                for user in users:
                    if user.email == email:
                        logger.info(f"   Found existing user ID: {user.id}")
                        return {
                            "id": user.id,
                            "email": user.email,
                            "created_at": user.created_at
                        }
            except Exception as list_error:
                logger.error(f"Failed to list users: {list_error}")
        else:
            logger.error(f"❌ Failed to create user {email}: {e}")
            raise


def main():
    """Main function to create test users."""
    logger.info("=" * 80)
    logger.info("CREATING TEST USERS FOR MULTI-USER MCP SYSTEM")
    logger.info("=" * 80)
    
    # Create Supabase client
    logger.info("\n1. Initializing Supabase client...")
    client = create_supabase_client()
    logger.info("✅ Supabase client initialized")
    
    # Define test users
    test_users = [
        {
            "email": "jazeel@example.com",
            "password": "TempPass123!Jazeel",
            "metadata": {
                "full_name": "Jazeel",
                "role": "test_user",
                "created_by": "create_test_users.py"
            }
        },
        {
            "email": "michelle@example.com",
            "password": "TempPass123!Michelle",
            "metadata": {
                "full_name": "Michelle",
                "role": "test_user",
                "created_by": "create_test_users.py"
            }
        }
    ]
    
    # Create users
    logger.info("\n2. Creating test users...")
    created_users = []
    
    for user_data in test_users:
        user = create_user(
            client,
            email=user_data["email"],
            password=user_data["password"],
            user_metadata=user_data["metadata"]
        )
        created_users.append(user)
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total users created/verified: {len(created_users)}")
    
    for i, user in enumerate(created_users, 1):
        logger.info(f"\n{i}. {user['email']}")
        logger.info(f"   ID: {user['id']}")
        logger.info(f"   Created: {user['created_at']}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ TEST USERS READY FOR MULTI-USER MCP TESTING")
    logger.info("=" * 80)
    
    logger.info("\nNext steps:")
    logger.info("1. Update .env.docker with MCP_ENABLE_MULTI_USER=true")
    logger.info("2. Implement JWT validation in MCP daemon")
    logger.info("3. Test user authentication and session isolation")
    
    return created_users


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"\n❌ Script failed: {e}")
        sys.exit(1)

