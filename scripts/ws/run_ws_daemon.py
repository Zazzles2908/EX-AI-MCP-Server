#!/usr/bin/env python
"""WS Daemon launcher - simplified with bootstrap module."""
import sys
from pathlib import Path

# Bootstrap: Setup path and load environment
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env

# Load environment variables
load_env()

from src.daemon.ws_server import main

if __name__ == "__main__":
    main()

