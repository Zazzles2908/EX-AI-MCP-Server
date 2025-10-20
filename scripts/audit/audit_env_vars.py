#!/usr/bin/env python3
"""
Audit Environment Variables - Find os.getenv() calls with defaults not in .env

Last Updated: 2025-10-09

This script:
1. Scans all Python files for os.getenv() calls
2. Extracts variable names and default values
3. Checks if they exist in .env file
4. Reports missing variables

Usage:
    python scripts/audit/audit_env_vars.py
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Get repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"

# Patterns to match os.getenv() calls
GETENV_PATTERN = r'os\.getenv\(["\']([A-Z_][A-Z0-9_]*)["\'](?:,\s*["\']([^"\']*)["\']|\s*,\s*(\d+|True|False|None))?\)'

# Directories to scan
SCAN_DIRS = ["src", "tools", "scripts"]

# Directories to skip
SKIP_DIRS = {"__pycache__", ".venv", "venvs", "node_modules", ".git"}


def load_env_vars() -> Set[str]:
    """Load all variable names from .env file."""
    env_vars = set()
    
    if not ENV_FILE.exists():
        print(f"⚠️  .env file not found at {ENV_FILE}")
        return env_vars
    
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                var_name = line.split('=', 1)[0].strip()
                env_vars.add(var_name)
    
    return env_vars


def scan_file(file_path: Path) -> List[Tuple[str, str, int, str]]:
    """
    Scan a Python file for os.getenv() calls.
    
    Returns:
        List of (var_name, default_value, line_number, line_content)
    """
    results = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        for match in re.finditer(GETENV_PATTERN, content):
            var_name = match.group(1)
            default_value = match.group(2) or match.group(3) or "None"
            
            # Find line number
            line_num = content[:match.start()].count('\n') + 1
            line_content = lines[line_num - 1].strip()
            
            results.append((var_name, default_value, line_num, line_content))
    
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
    
    return results


def scan_codebase() -> Dict[str, List[Tuple[Path, str, int, str]]]:
    """
    Scan entire codebase for os.getenv() calls.
    
    Returns:
        Dict mapping var_name to list of (file_path, default_value, line_number, line_content)
    """
    all_vars = {}
    
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if not dir_path.exists():
            continue
        
        for py_file in dir_path.rglob("*.py"):
            # Skip directories in SKIP_DIRS
            if any(skip_dir in py_file.parts for skip_dir in SKIP_DIRS):
                continue
            
            results = scan_file(py_file)
            for var_name, default_value, line_num, line_content in results:
                if var_name not in all_vars:
                    all_vars[var_name] = []
                all_vars[var_name].append((py_file, default_value, line_num, line_content))
    
    return all_vars


def main():
    print("=" * 80)
    print("Environment Variable Audit")
    print("Last Updated: 2025-10-09")
    print("=" * 80)
    print()
    
    # Load .env variables
    print("📋 Loading .env file...")
    env_vars = load_env_vars()
    print(f"   Found {len(env_vars)} variables in .env")
    print()
    
    # Scan codebase
    print("🔍 Scanning codebase for os.getenv() calls...")
    all_vars = scan_codebase()
    print(f"   Found {len(all_vars)} unique environment variables in code")
    print()
    
    # Find missing variables
    missing_vars = {}
    for var_name, usages in all_vars.items():
        if var_name not in env_vars:
            # Filter out variables with None or empty defaults (likely optional)
            non_none_usages = [u for u in usages if u[1] not in ("None", "", "''", '""')]
            if non_none_usages:
                missing_vars[var_name] = non_none_usages
    
    # Report results
    if missing_vars:
        print("⚠️  MISSING VARIABLES IN .env")
        print("=" * 80)
        print()
        
        for var_name in sorted(missing_vars.keys()):
            usages = missing_vars[var_name]
            print(f"❌ {var_name}")
            
            # Group by default value
            defaults = {}
            for file_path, default_value, line_num, line_content in usages:
                if default_value not in defaults:
                    defaults[default_value] = []
                defaults[default_value].append((file_path, line_num, line_content))
            
            for default_value, locations in defaults.items():
                print(f"   Default: {default_value}")
                for file_path, line_num, line_content in locations[:3]:  # Show max 3 locations
                    rel_path = file_path.relative_to(REPO_ROOT)
                    print(f"   - {rel_path}:{line_num}")
                if len(locations) > 3:
                    print(f"   ... and {len(locations) - 3} more locations")
            print()
        
        print("=" * 80)
        print(f"Total missing variables: {len(missing_vars)}")
        print()
        print("💡 Recommendation:")
        print("   Add these variables to .env and .env.example")
        print()
    else:
        print("✅ All environment variables with defaults are in .env!")
        print()
    
    # Show variables in .env but not used in code (potential cleanup)
    used_vars = set(all_vars.keys())
    unused_in_env = env_vars - used_vars
    
    if unused_in_env:
        print("ℹ️  VARIABLES IN .env BUT NOT FOUND IN CODE")
        print("=" * 80)
        print()
        for var_name in sorted(unused_in_env):
            print(f"   {var_name}")
        print()
        print(f"Total: {len(unused_in_env)}")
        print("Note: These may be used dynamically or in non-Python files")
        print()


if __name__ == "__main__":
    main()

