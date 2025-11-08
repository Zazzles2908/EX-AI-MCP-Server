#!/usr/bin/env python3
"""
Auto-Fix Script Issues for EX-AI MCP Server
Automatically fixes common configuration and code quality issues in scripts/

Usage:
    python scripts/auto_fix_script_issues.py --dry-run
    python scripts/auto_fix_script_issues.py --fix
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Fixes to apply
FIXES = [
    {
        "file": "scripts/ws/ws_chat_once.py",
        "search": r'PORT = int\(os\.getenv\("EXAI_WS_PORT", "8765"\)\)',
        "replace": 'PORT = int(os.getenv("EXAI_WS_PORT", "3000"))',
        "description": "Update port from 8765 to 3000"
    },
    {
        "file": "scripts/ws/ws_chat_review_once.py",
        "search": r'PORT = int\(os\.getenv\("EXAI_WS_PORT", "8710"\)\)',
        "replace": 'PORT = int(os.getenv("EXAI_WS_PORT", "3000"))',
        "description": "Update port from 8710 to 3000"
    },
    {
        "file": "scripts/ws/ws_chat_analyze_files.py",
        "search": r'PORT = int\(os\.getenv\("EXAI_WS_PORT", "8765"\)\)',
        "replace": 'PORT = int(os.getenv("EXAI_WS_PORT", "3000"))',
        "description": "Update port from 8765 to 3000"
    },
    {
        "file": "scripts/ws/ws_chat_roundtrip.py",
        "search": r'PORT = int\(os\.getenv\("EXAI_WS_PORT", "8765"\)\)',
        "replace": 'PORT = int(os.getenv("EXAI_WS_PORT", "3000"))',
        "description": "Update port from 8765 to 3000"
    },
    {
        "file": "scripts/validate_environment.py",
        "search": r'ws_port = os\.getenv\("EXAI_WS_PORT", "8079"\)',
        "replace": 'ws_port = os.getenv("EXAI_WS_PORT", "3000")',
        "description": "Update port from 8079 to 3000"
    },
    {
        "file": "scripts/exai_native_mcp_server.py",
        "search": r'EXAI_WS_PORT = int\(os\.getenv\("EXAI_WS_PORT", "8079"\)\)',
        "replace": 'EXAI_WS_PORT = int(os.getenv("EXAI_WS_PORT", "3000"))',
        "description": "Update port from 8079 to 3000"
    },
    {
        "file": "scripts/setup_claude_connection.py",
        "search": r'"EXAI_WS_PORT": "8079"',
        "replace": '"EXAI_WS_PORT": "3000"',
        "description": "Update port from 8079 to 3000 (multiple occurrences)"
    },
    {
        "file": "scripts/setup_claude_connection.py",
        "search": r'result = sock\.connect_ex\(\(.*?, 8079\)\)',
        "replace": r"result = sock.connect_ex(('127.0.0.1', 3000))",
        "description": "Update port validation from 8079 to 3000"
    },
]

def check_file_exists(filepath: str) -> bool:
    """Check if file exists"""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ File not found: {filepath}")
        return False
    return True

def apply_fix(fix: dict, dry_run: bool = False) -> Tuple[bool, str]:
    """Apply a single fix to a file"""
    filepath = fix["file"]

    if not check_file_exists(filepath):
        return False, f"File not found: {filepath}"

    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Apply fix
        new_content, count = re.subn(
            fix["search"],
            fix["replace"],
            content
        )

        if count == 0:
            return False, f"Pattern not found: {fix['description']}"

        # Write file (only if not dry run)
        if not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

        return True, f"Applied fix ({count} occurrence(s)): {fix['description']}"

    except Exception as e:
        return False, f"Error: {e}"

def remove_unused_imports(file_path: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Remove unused pathlib.Path imports"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Check for unused import
        has_pathlib = False
        for i, line in enumerate(lines):
            if 'from pathlib import Path' in line and i < 10:  # Import should be near top
                # Check if Path is used in the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'Path(' not in content or content.count('Path(') <= 1:  # Only in import
                    has_pathlib = True
                    break

        if not has_pathlib:
            return False, "No unused pathlib.Path import found"

        # Remove import
        new_lines = [line for line in lines if 'from pathlib import Path' not in line]

        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

        return True, "Removed unused pathlib.Path import"

    except Exception as e:
        return False, f"Error: {e}"

def add_env_validation(file_path: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Add environment variable validation"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if validation already exists
        if 'required_vars = [' in content or 'Missing required environment variable' in content:
            return False, "Validation already exists"

        # Add validation after imports
        validation_code = '''
def validate_env():
    """Validate required environment variables"""
    required_vars = ["EXAI_WS_HOST", "EXAI_WS_PORT", "EXAI_WS_TOKEN"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

# Validate environment
validate_env()

'''

        # Find insertion point (after imports, before main code)
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_idx = i + 1
            elif line.startswith('def ') or line.startswith('class ') or line.startswith('if __name__'):
                break

        lines.insert(insert_idx, validation_code)
        new_content = '\n'.join(lines)

        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        return True, "Added environment variable validation"

    except Exception as e:
        return False, f"Error: {e}"

def main():
    parser = argparse.ArgumentParser(
        description="Auto-fix script issues in EX-AI MCP Server"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply fixes (default is dry-run)"
    )
    parser.add_argument(
        "--ports-only",
        action="store_true",
        help="Fix only port configuration issues"
    )
    parser.add_argument(
        "--imports",
        action="store_true",
        help="Fix only unused import issues"
    )
    parser.add_argument(
        "--env-validation",
        action="store_true",
        help="Add environment variable validation"
    )

    args = parser.parse_args()
    dry_run = not args.fix

    print("=" * 80)
    print("EX-AI MCP Server - Auto Fix Script Issues")
    print("=" * 80)
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLYING FIXES'}")
    print("=" * 80)
    print()

    # Track results
    applied = []
    skipped = []
    errors = []

    # Apply port fixes
    if not args.imports and not args.env_validation or args.ports_only:
        print("🔧 Fixing port configuration issues...")
        for fix in FIXES:
            success, message = apply_fix(fix, dry_run)
            if success:
                status = "✅" if not dry_run else "📝"
                print(f"  {status} {message}")
                applied.append(message)
            else:
                print(f"  ⚠️  {message}")
                skipped.append(message)

    # Fix unused imports
    if not args.ports_only and not args.env_validation or args.imports:
        print("\n🧹 Removing unused imports...")
        files_with_imports = [
            "scripts/ws/ws_chat_once.py",
            "scripts/ws/ws_chat_review_once.py",
            "scripts/validate_environment.py"
        ]

        for file_path in files_with_imports:
            success, message = remove_unused_imports(file_path, dry_run)
            if success:
                status = "✅" if not dry_run else "📝"
                print(f"  {status} {file_path}: {message}")
                applied.append(f"{file_path}: {message}")
            else:
                print(f"  ⚠️  {file_path}: {message}")
                skipped.append(f"{file_path}: {message}")

    # Add environment validation
    if args.env_validation:
        print("\n🔒 Adding environment variable validation...")
        files_for_validation = [
            "scripts/ws/ws_chat_once.py",
            "scripts/ws/ws_chat_review_once.py",
            "scripts/ws/ws_chat_analyze_files.py",
            "scripts/validate_environment.py"
        ]

        for file_path in files_for_validation:
            success, message = add_env_validation(file_path, dry_run)
            if success:
                status = "✅" if not dry_run else "📝"
                print(f"  {status} {file_path}: {message}")
                applied.append(f"{file_path}: {message}")
            else:
                print(f"  ⚠️  {file_path}: {message}")
                skipped.append(f"{file_path}: {message}")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Applied: {len(applied)}")
    print(f"Skipped: {len(skipped)}")
    print(f"Errors: {len(errors)}")
    print()

    if dry_run:
        print("⚠️  This was a DRY RUN. No changes were made.")
        print("   Run with --fix to apply changes.")
    else:
        print("✅ All fixes applied successfully!")

    print()
    print("=" * 80)
    print("MANUAL FIXES REQUIRED")
    print("=" * 80)
    print()
    print("The following issues require manual fixes:")
    print()
    print("1. 🔴 CRITICAL: Remove hardcoded JWT token")
    print("   File: scripts/setup_claude_connection.py")
    print("   Line: 27")
    print("   Action: Replace with os.getenv('EXAI_JWT_TOKEN_CLAUDE')")
    print()
    print("2. 🔴 CRITICAL: Fix JWT token printing")
    print("   File: scripts/generate_all_jwt_tokens.py")
    print("   Lines: 121-127")
    print("   Action: Remove print statements or add redaction")
    print()
    print("3. 🟡 Create .env.docker with proper JWT_SECRET_KEY")
    print("   Required for: scripts/generate_all_jwt_tokens.py")
    print()
    print("=" * 80)

    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(main())
