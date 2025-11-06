#!/usr/bin/env python3
"""
Test File Consolidation Script

Consolidates 63 scattered test files from scripts/ and root directory
into the main tests/ directory following professional Python testing standards.

Distribution:
- 159 files already in tests/ (well organized)
- 54 files in scripts/ (need consolidation)
- 9 files in root (need consolidation)
- Total: 63 files to consolidate
"""

import os
import shutil
from pathlib import Path
import re

# Configuration
REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_ROOT = REPO_ROOT / "tests"
SCRIPTS_ROOT = REPO_ROOT / "scripts"

# Test categories mapping
TEST_CATEGORIES = {
    # WebSocket tests
    'websocket': r'(?i)(ws_?connection|websocket)',
    'connection': r'(?i)(connection|connect)',

    # Provider tests
    'glm': r'(?i)(glm)',
    'kimi': r'(?i)(kimi)',

    # Integration tests
    'integration': r'(?i)(integration|hybrid)',

    # File operations
    'file': r'(?i)(file_(management|upload|download)|smart_file)',

    # Monitoring & health
    'monitoring': r'(?i)(monitoring|health|metrics)',

    # Security
    'security': r'(?i)(security|auth|jwt)',

    # Supabase
    'supabase': r'(?i)(supabase)',

    # Validation
    'validation': r'(?i)(validation|verify|check)',

    # Performance
    'performance': r'(?i)(performance|load|stress|benchmark)',

    # End-to-end
    'e2e': r'(?i)(e2e|end.?to.?end)',

    # SDK
    'sdk': r'(?i)/sdk',

    # Phase-based
    'phase1': r'(?i)phase1',
    'phase2': r'(?i)phase2',
    'phase3': r'(?i)phase3',
    'phase4': r'(?i)phase4',
    'phase5': r'(?i)phase5',
    'phase6': r'(?i)phase6',
    'phase7': r'(?i)phase7',
    'phase8': r'(?i)phase8',
}

# Already organized directories in tests/
EXISTING_STRUCTURE = {
    'unit': TESTS_ROOT / 'unit',
    'integration': TESTS_ROOT / 'integration',
    'e2e': TESTS_ROOT / 'e2e',
    'validation': TESTS_ROOT / 'validation',
    'performance': TESTS_ROOT / 'performance',
    'sdk': TESTS_ROOT / 'sdk',
    'functional': TESTS_ROOT / 'functional',
    'load_testing': TESTS_ROOT / 'load_testing',
}


def categorize_test_file(filename):
    """Determine category for a test file based on its name."""
    filename_lower = filename.lower()

    # Check against patterns
    for category, pattern in TEST_CATEGORIES.items():
        if re.search(pattern, filename_lower):
            return category

    # Default to 'misc' if no pattern matches
    return 'misc'


def get_target_directory(category):
    """Get target directory for a category."""
    # Check existing structure
    if category in EXISTING_STRUCTURE:
        return EXISTING_STRUCTURE[category]

    # Create new category directories
    category_dir = TESTS_ROOT / category
    category_dir.mkdir(parents=True, exist_ok=True)
    return category_dir


def consolidate_test_files():
    """Consolidate test files from scripts/ and root to tests/."""
    print("=" * 70)
    print("EX-AI MCP Server - Test Consolidation")
    print("=" * 70)
    print()

    moved_count = 0
    duplicate_count = 0
    error_count = 0

    # Process scripts/ directory
    print("\n[Step 1/2] Processing scripts/ directory...")
    script_tests = list(SCRIPTS_ROOT.glob("**/test_*.py")) + list(SCRIPTS_ROOT.glob("**/*_test.py"))

    for test_file in script_tests:
        if test_file.name == 'test_websocket_comprehensive.py':
            print(f"[SKIP] {test_file.name} (already consolidated)")
            continue

        category = categorize_test_file(test_file.name)
        target_dir = get_target_directory(category)
        target_file = target_dir / test_file.name

        # Check for duplicates
        if target_file.exists():
            print(f"[DUPLICATE] {test_file.name} already exists in {target_dir.name}/")
            # Keep the one in tests/ (more organized), delete the one in scripts/
            try:
                test_file.unlink()
                print(f"[DELETED] {test_file}")
                duplicate_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to delete {test_file}: {e}")
                error_count += 1
            continue

        # Move file
        try:
            shutil.move(str(test_file), str(target_file))
            print(f"[MOVED] {test_file.relative_to(REPO_ROOT)} -> tests/{category}/{test_file.name}")
            moved_count += 1
        except Exception as e:
            print(f"[ERROR] Failed to move {test_file}: {e}")
            error_count += 1

    # Process root directory
    print("\n[Step 2/2] Processing root directory...")
    root_tests = list(REPO_ROOT.glob("test_*.py")) + list(REPO_ROOT.glob("*_test.py"))

    for test_file in root_tests:
        category = categorize_test_file(test_file.name)
        target_dir = get_target_directory(category)
        target_file = target_dir / test_file.name

        # Check for duplicates
        if target_file.exists():
            print(f"[DUPLICATE] {test_file.name} already exists in {target_dir.name}/")
            # Keep the one in tests/, delete the one in root
            try:
                test_file.unlink()
                print(f"[DELETED] {test_file}")
                duplicate_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to delete {test_file}: {e}")
                error_count += 1
            continue

        # Move file
        try:
            shutil.move(str(test_file), str(target_file))
            print(f"[MOVED] {test_file.relative_to(REPO_ROOT)} -> tests/{category}/{test_file.name}")
            moved_count += 1
        except Exception as e:
            print(f"[ERROR] Failed to move {test_file}: {e}")
            error_count += 1

    # Summary
    print("\n" + "=" * 70)
    print("CONSOLIDATION SUMMARY")
    print("=" * 70)
    print(f"Files moved to tests/: {moved_count}")
    print(f"Duplicate files deleted: {duplicate_count}")
    print(f"Errors: {error_count}")
    print()

    # Show final test structure
    print("Final tests/ structure:")
    for item in sorted(TESTS_ROOT.rglob("*")):
        if item.is_file() and item.suffix == '.py':
            rel_path = item.relative_to(TESTS_ROOT)
            print(f"  - {rel_path}")

    print()
    print("[OK] Test consolidation complete!")
    print("=" * 70)

    return moved_count, duplicate_count, error_count


if __name__ == "__main__":
    consolidate_test_files()
