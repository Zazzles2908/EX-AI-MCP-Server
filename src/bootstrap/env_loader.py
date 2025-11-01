"""
Environment Loader Module

Consolidates .env file loading and repository root path resolution.
Replaces duplicate implementations in:
- scripts/run_ws_shim.py lines 14-25
- scripts/ws/run_ws_daemon.py lines 5-14
- server.py lines 52-70
"""

import os
import sys
from pathlib import Path
from typing import Optional


def get_repo_root(start_path: Optional[Path] = None) -> Path:
    """
    Get the repository root directory.
    
    Args:
        start_path: Starting path for search (defaults to this file's location)
        
    Returns:
        Path to repository root
    """
    if start_path is None:
        start_path = Path(__file__).resolve()
    
    # Navigate up from src/bootstrap/ to repo root
    # This file is at: repo_root/src/bootstrap/env_loader.py
    # So we go up 2 levels: bootstrap -> src -> repo_root
    return start_path.parent.parent.parent


def load_env(env_file: Optional[str] = None, override: bool = True) -> bool:
    """
    Load environment variables from .env file.

    Args:
        env_file: Explicit path to .env file (optional)
        override: Whether to override existing environment variables (default: True)
                  CRITICAL: Must be True to ensure .env file values take precedence
                  over inherited environment variables from parent processes

    Returns:
        True if .env file was loaded, False otherwise

    CRITICAL FIX (2025-11-01): Added transparent logging to show which .env file is loaded
    - Helps debug configuration issues
    - Shows Redis/Supabase credential status
    - Clarifies which environment file is active
    """
    try:
        from dotenv import load_dotenv
        import logging
        logger = logging.getLogger(__name__)

        # Determine .env file path
        if env_file and os.path.exists(env_file):
            env_path = env_file
        else:
            # Check ENV_FILE environment variable
            explicit_env = os.getenv("ENV_FILE")
            if explicit_env and os.path.exists(explicit_env):
                env_path = explicit_env
            else:
                # Default to .env in repo root
                repo_root = get_repo_root()
                env_path = str(repo_root / ".env")

        # Load .env file if it exists
        if os.path.exists(env_path):
            load_dotenv(dotenv_path=env_path, override=override)

            # TRANSPARENT LOGGING: Show which file was loaded and key credentials
            logger.info(f"[ENV_LOADER] ✅ Loaded environment from: {env_path}")
            logger.info(f"[ENV_LOADER] REDIS_URL: {'SET' if os.getenv('REDIS_URL') else 'NOT SET'}")
            logger.info(f"[ENV_LOADER] REDIS_PASSWORD: {'SET' if os.getenv('REDIS_PASSWORD') else 'NOT SET'}")
            logger.info(f"[ENV_LOADER] SUPABASE_URL: {'SET' if os.getenv('SUPABASE_URL') else 'NOT SET'}")
            logger.info(f"[ENV_LOADER] SUPABASE_SERVICE_ROLE_KEY: {'SET' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else 'NOT SET'}")
            logger.info(f"[ENV_LOADER] SUPABASE_ANON_KEY: {'SET' if os.getenv('SUPABASE_ANON_KEY') else 'NOT SET'}")
            logger.info(f"[ENV_LOADER] LOG_LEVEL: {os.getenv('LOG_LEVEL', 'NOT SET')}")

            return True
        else:
            logger.warning(f"[ENV_LOADER] ⚠️ Environment file not found: {env_path}")

        return False

    except ImportError:
        # python-dotenv not available
        return False
    except Exception as e:
        # Any other error during loading
        print(f"[ENV_LOADER] ❌ Error loading environment: {e}")
        return False


def setup_path() -> None:
    """
    Ensure repository root is on sys.path.
    Idempotent - safe to call multiple times.
    """
    repo_root = get_repo_root()
    repo_root_str = str(repo_root)
    
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

