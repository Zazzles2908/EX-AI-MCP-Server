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
    """
    try:
        from dotenv import load_dotenv
        
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
            return True
        
        return False
        
    except ImportError:
        # python-dotenv not available
        return False
    except Exception:
        # Any other error during loading
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

