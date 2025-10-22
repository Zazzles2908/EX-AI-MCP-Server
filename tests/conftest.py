"""
Pytest configuration for Phase 2.3 file handling tests

Loads environment variables from .env.docker for testing
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env.docker
def load_env_docker():
    """Load environment variables from .env.docker"""
    env_file = project_root / ".env.docker"
    if not env_file.exists():
        return
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Remove inline comments
                if '#' in value:
                    value = value.split('#')[0].strip()
                
                # Set environment variable
                os.environ[key] = value

# Load environment variables before tests run
load_env_docker()

