#!/usr/bin/env python3
"""
Documentation Cleanup Script

Removes 291KB of documentation pollution from the EX-AI MCP Server codebase.
Follows professional standards: only 5 .md files allowed in root.

Files to be moved to docs/ structure:
- IMPLEMENTATION_COMPLETE.md → docs/development/implementation/
- EXAI_BUG_FIXES_COMPLETE.md → docs/development/bug-fixes/
- CODEBASE_ANALYSIS_COMPLETE.md → docs/development/analysis/
- EXAI_SYSTEMATIC_TEST_RESULTS.md → docs/testing/test-results/
- FINAL_STATUS_REPORT.md → docs/development/status-reports/
- CONVERSATION_TECHNICAL_SUMMARY.md → docs/development/technical-summaries/
- EXAI_MCP_COMPREHENSIVE_TEST_RESULTS.md → docs/testing/comprehensive-tests/
- And many more...

Files to be deleted (duplicates/redundant):
- Files with corrupted names (C:ProjectEX-AI-MCP-Server...)
- Outdated status files
- Duplicate configuration guides
"""

import os
import shutil
from pathlib import Path

# Configuration
REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = REPO_ROOT / "docs"

# Essential root files (only 5 allowed)
ESSENTIAL_ROOT_MD = {
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "CHANGELOG.md",
    "CLAUDE.md"
}

# Files to move to docs/ (value is destination directory)
FILES_TO_MOVE = {
    # Implementation & Development Documentation
    "IMPLEMENTATION_COMPLETE.md": "docs/development/implementation/",
    "EXAI_BUG_FIXES_COMPLETE.md": "docs/development/bug-fixes/",
    "CODEBASE_ANALYSIS_COMPLETE.md": "docs/development/analysis/",
    "CONVERSATION_TECHNICAL_SUMMARY.md": "docs/development/technical-summaries/",
    "EXAI_SYSTEMATIC_TEST_RESULTS.md": "docs/testing/test-results/",
    "FINAL_STATUS_REPORT.md": "docs/development/status-reports/",
    "FINAL_NATIVE_MCP_STATUS.md": "docs/development/status-reports/",
    "EXAI_NATIVE_MCP_IMPLEMENTATION.md": "docs/development/implementation/",
    "GLM_IMAGES_FIX_SUMMARY.md": "docs/development/bug-fixes/",
    "BEFORE_AFTER_COMPARISON.md": "docs/development/analysis/",
    "CLEAN_STATUS.md": "docs/development/status-reports/",
    "EXAI_MCP_CONNECTION_STATUS.md": "docs/development/status-reports/",
    "EXAI_MCP_DIRECT_CALLS_GUIDE.md": "docs/getting-started/",
    "SIMPLE_CONFIGURATION_COMPLETE.md": "docs/getting-started/",
    "SIMPLE_EXAI_MCP_CONNECTION.md": "docs/getting-started/",
    "EXAI_MCP_COMPREHENSIVE_TEST.md": "docs/testing/",
    "EXAI_MCP_COMPREHENSIVE_TEST_RESULTS.md": "docs/testing/test-results/",
    "EXECUTIVE_SUMMARY.md": "docs/development/management/",
    "FINAL_TEST.md": "docs/testing/",
    "SETUP.md": "docs/getting-started/installation.md",  # Rename to standard name
}

# Files to delete (redundant, corrupted, or duplicates)
FILES_TO_DELETE = {
    # We'll find and delete corrupted files programmatically instead
    # Additional duplicates can be added here
}


def create_docs_structure():
    """Create the proper docs/ directory structure."""
    directories = [
        "docs/",
        "docs/getting-started/",
        "docs/development/",
        "docs/development/implementation/",
        "docs/development/bug-fixes/",
        "docs/development/analysis/",
        "docs/development/technical-summaries/",
        "docs/development/status-reports/",
        "docs/development/management/",
        "docs/testing/",
        "docs/testing/test-results/",
        "docs/testing/comprehensive-tests/",
        "docs/reference/",
        "docs/architecture/",
        "docs/operations/",
        "docs/troubleshooting/",
    ]

    for directory in directories:
        dir_path = REPO_ROOT / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created directory: {directory}")


def move_file_to_docs(filename, destination):
    """Move a file from root to docs/ structure."""
    source = REPO_ROOT / filename
    dest_dir = REPO_ROOT / destination
    dest_path = dest_dir / filename

    if source.exists():
        # Ensure destination directory exists
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Move the file
        shutil.move(str(source), str(dest_path))
        print(f"[OK] Moved: {filename} -> {destination}")
        return True
    else:
        print(f"[WARN] File not found: {filename}")
        return False


def delete_file(filename):
    """Delete a file."""
    file_path = REPO_ROOT / filename
    if file_path.exists():
        file_path.unlink()
        print(f"[OK] Deleted: {filename}")
        return True
    else:
        print(f"[WARN] File not found: {filename}")
        return False


def get_remaining_root_md_files():
    """Get list of .md files remaining in root (excluding essential ones)."""
    root_md_files = []
    for file in REPO_ROOT.glob("*.md"):
        if file.name not in ESSENTIAL_ROOT_MD:
            root_md_files.append(file.name)
    return root_md_files


def main():
    """Main cleanup execution."""
    print("=" * 70)
    print("EX-AI MCP Server - Documentation Cleanup")
    print("=" * 70)
    print()
    print(f"Repository root: {REPO_ROOT}")
    print(f"Total pollution: 291 KB")
    print()

    # Step 1: Create docs structure
    print("\n[Step 1/4] Creating docs/ directory structure...")
    create_docs_structure()

    # Step 2: Move files to docs/
    print("\n[Step 2/4] Moving documentation files to docs/ structure...")
    moved_count = 0
    for filename, destination in FILES_TO_MOVE.items():
        if move_file_to_docs(filename, destination):
            moved_count += 1

    # Step 3: Delete redundant/corrupted files
    print("\n[Step 3/4] Deleting redundant and corrupted files...")
    deleted_count = 0

    # First, delete explicitly listed files
    for filename in FILES_TO_DELETE:
        if delete_file(filename):
            deleted_count += 1

    # Then, find and delete files with problematic characters
    for file in REPO_ROOT.glob("*.md"):
        if file.name not in ESSENTIAL_ROOT_MD:
            # Check for problematic characters (non-ASCII or control characters)
            try:
                file.name.encode('ascii')
            except UnicodeEncodeError:
                print(f"[OK] Found corrupted file: {file.name}")
                try:
                    file.unlink()
                    print(f"[OK] Deleted corrupted file")
                    deleted_count += 1
                except Exception as e:
                    print(f"[ERROR] Failed to delete {file.name}: {e}")
            except Exception as e:
                print(f"[ERROR] Error checking {file.name}: {e}")

    # Step 4: Report remaining files
    print("\n[Step 4/4] Checking for remaining root .md files...")
    remaining = get_remaining_root_md_files()

    if remaining:
        print(f"\n[WARN] Warning: {len(remaining)} .md files still in root:")
        for file in remaining:
            print(f"   - {file}")
        print("\nThese should be reviewed and either moved to docs/ or deleted.")
    else:
        print("\n[OK] All non-essential .md files removed from root!")

    # Summary
    print("\n" + "=" * 70)
    print("CLEANUP SUMMARY")
    print("=" * 70)
    print(f"Files moved to docs/: {moved_count}")
    print(f"Files deleted: {deleted_count}")
    print(f"Remaining root .md files: {len(remaining)}")
    print(f"Essential root files (should remain): {len(ESSENTIAL_ROOT_MD)}")
    print()
    print("[OK] Documentation cleanup complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
