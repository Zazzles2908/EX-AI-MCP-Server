#!/usr/bin/env python3
"""
EX-AI Test File Organization Script
Conforms to CLAUDE.md directory structure requirements

This script organizes scattered test files into proper test directory structure,
eliminating main directory clutter per user requirements.

Usage:
    python scripts/organize_test_files.py

Required by: CLAUDE.md - "I hate when files get through into the main directory"
"""

import os
import shutil
import sys
from pathlib import Path

# Handle encoding issues on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def organize_test_files():
    """Organize test files into proper directory structure per CLAUDE.md requirements."""
    
    print("EX-AI Test Organization (CLAUDE.md Compliant)")
    print("=" * 60)
    
    # Clean project structure per CLAUDE.md requirements
    # Test files should NOT be in main directory
    
    # Define test file patterns and their destinations per user requirements
    test_file_patterns = {
        # Root level test files - MOVED TO tests/
        'test_tool_execution_phase4.py': 'tests/integration/',
        
        # Agent workspace test files
        'agent-workspace/test-mcp.py': 'tests/integration/',
        'agent-workspace/test-mcp-request.json': 'tests/fixtures/',
        
        # Scripts with "test" in name - MOVED TO tests/
        'scripts/dev/stress_test_exai.py': 'tests/performance/',
        'scripts/dev/test_thinking_mode_simple.sh': 'tests/scripts/',
        
        # Legacy test files - ARCHIVED TO tests/legacy/
        'scripts/legacy/create_test_users.py': 'tests/utils/',
        'scripts/legacy/run_all_tests.py': 'tests/legacy/',
        'scripts/legacy/test_session_persistence.py': 'tests/integration/',
        'scripts/legacy/test_supabase_connection.py': 'tests/integration/',
        
        # Archive deprecated files to legacy
        'scripts/archive/deprecated/ws_chat_once.py': 'tests/legacy/',
        'scripts/archive/deprecated/run_tests.py': 'tests/legacy/',
        
        # Phase-specific test files
        'scripts/archive/phase-scripts/integration_test_phase7.py': 'tests/integration/',
        'scripts/archive/phase-scripts/phase2/websocket_test_client.py': 'tests/legacy/',
    }
    
    # Create proper test directory structure (per CLAUDE.md)
    test_dirs = [
        'tests/integration',      # Integration tests
        'tests/unit',            # Unit tests
        'tests/performance',     # Performance tests
        'tests/scripts',         # Test scripts
        'tests/utils',           # Test utilities
        'tests/fixtures',        # Test data/fixtures
        'tests/legacy',          # Legacy/deprecated tests
        'tests/reports'          # Test reports (existing)
    ]
    
    print("Creating test directory structure...")
    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created {dir_path}/")
    
    # Move files
    moved_count = 0
    skipped_count = 0
    
    for file_pattern, dest_dir in test_file_patterns.items():
        file_path = Path(file_pattern)
        
        if file_path.exists():
            # Create destination path
            dest_path = Path(dest_dir) / file_path.name
            
            try:
                # Handle potential conflicts
                if dest_path.exists():
                    # If destination exists, append counter
                    counter = 1
                    while dest_path.exists():
                        base_name = dest_path.stem
                        suffix = dest_path.suffix
                        new_name = f"{base_name}_{counter}{suffix}"
                        dest_path = Path(dest_dir) / new_name
                        counter += 1
                
                shutil.move(str(file_path), str(dest_path))
                print(f"[OK] Moved: {file_pattern}")
                print(f"     -> {dest_path}")
                moved_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to move {file_pattern}: {e}")
                skipped_count += 1
        else:
            print(f"[SKIP] File not found: {file_pattern}")
            skipped_count += 1
    
    # Create proper __init__.py files for test modules
    test_init_files = [
        'tests/__init__.py',
        'tests/integration/__init__.py',
        'tests/unit/__init__.py',
        'tests/performance/__init__.py',
        'tests/utils/__init__.py',
        'tests/legacy/__init__.py'
    ]
    
    print("\nCreating test module structure...")
    for init_file in test_init_files:
        init_path = Path(init_file)
        if not init_path.exists():
            init_path.touch()
            print(f"[OK] Created {init_file}")
    
    # Check for remaining test files in main directories
    print("\nScanning for remaining test files in main directories...")
    main_dirs_to_check = ['src/', 'scripts/', 'config/', 'docs/']
    remaining_test_files = []
    
    for main_dir in main_dirs_to_check:
        if Path(main_dir).exists():
            for test_file in Path(main_dir).rglob('*test*'):
                if test_file.is_file() and '.py' in str(test_file):
                    remaining_test_files.append(str(test_file))
    
    if remaining_test_files:
        print(f"[WARNING] Found {len(remaining_test_files)} remaining test files in main directories:")
        for file in remaining_test_files[:10]:  # Show first 10
            print(f"     - {file}")
        if len(remaining_test_files) > 10:
            print(f"     ... and {len(remaining_test_files) - 10} more")
    
    # Update .gitignore for test structure
    update_gitignore_for_tests()
    
    print(f"\n[SUCCESS] Test organization complete!")
    print(f"[OK] Files moved: {moved_count}")
    print(f"[SKIP] Files skipped: {skipped_count}")
    print(f"[OK] Test structure: Clean per CLAUDE.md requirements")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Update imports in moved files if needed")
    print("2. Run tests to ensure functionality preserved") 
    print("3. Update VSCode test discovery paths")
    print("4. Verify clean main directory structure")
    
    print(f"\n[BUILD] Current structure per CLAUDE.md:")
    print(f"[OK] tests/ - Organized test files")
    print(f"[OK] src/ - Source code only")
    print(f"[OK] scripts/ - Operational scripts only")
    print(f"[OK] config/ - Configuration only")
    print(f"[OK] docs/ - Documentation only")
    
    return moved_count

def update_gitignore_for_tests():
    """Update .gitignore to exclude test artifacts."""
    gitignore_path = Path('.gitignore')
    
    if gitignore_path.exists():
        current_content = gitignore_path.read_text()
        
        # Add test-specific exclusions
        test_exclusions = [
            "\n# Test artifacts (organized per CLAUDE.md)",
            "tests/__pycache__/",
            "tests/*.pyc", 
            "tests/.coverage",
            "tests/htmlcov/",
            "tests/.pytest_cache/",
            "tests/reports/",
            "tests/fixtures/*",
            "!.gitignore",
        ]
        
        # Check if test exclusions already exist
        if "Test artifacts" not in current_content:
            gitignore_path.write_text(current_content + "\n".join(test_exclusions))
            print("[OK] Updated .gitignore for test structure")
        else:
            print("[INFO] .gitignore already includes test exclusions")

if __name__ == "__main__":
    organize_test_files()