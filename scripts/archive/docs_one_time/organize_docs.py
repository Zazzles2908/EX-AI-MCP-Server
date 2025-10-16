#!/usr/bin/env python
"""Organize docs/ directory into a clean hierarchical structure."""
import os
import shutil
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"

# Organization plan
ORGANIZATION = {
    # Kimi Review Files
    "reviews/kimi/current": [
        "KIMI_RAW_BATCH_1.md",
        "KIMI_RAW_BATCH_2.md",
        "KIMI_RAW_BATCH_3.md",
        "KIMI_RAW_BATCH_4.md",
        "KIMI_RAW_BATCH_5.md",
        "KIMI_RAW_BATCH_6.md",
        "KIMI_RAW_BATCH_7.md",
        "KIMI_RAW_BATCH_8.md",
        "KIMI_RAW_BATCH_9.md",
        "KIMI_RAW_BATCH_10.md",
        "KIMI_RAW_BATCH_11.md",
        "KIMI_RAW_BATCH_12.md",
        "KIMI_RAW_BATCH_13.md",
        "KIMI_RAW_BATCH_14.md",
        "KIMI_CODE_REVIEW_src.json",
        "KIMI_FRESH_REVIEW_IN_PROGRESS.md",
        "KIMI_FRESH_REVIEW_ANALYSIS.md",
        "KIMI_REVIEW_PROGRESS.md",
        "KIMI_REVALIDATION_ANALYSIS.md",
    ],
    "reviews/kimi/completed": [
        "KIMI_CODE_REVIEW_STARTED.md",
        "KIMI_CODE_REVIEW_SUCCESS.md",
        "KIMI_CODE_REVIEW_FINAL_SUCCESS.md",
        "KIMI_CODE_REVIEW_FIX_SUMMARY.md",
        "KIMI_CODE_REVIEW_WHERE_IS_THE_DATA.md",
        "KIMI_INVESTIGATION_COMPLETE.md",
        "PRE_KIMI_VALIDATION_COMPLETE.md",
    ],
    "reviews/code-review": [
        "CODE_REVIEW_ACTION_PLAN.md",
        "CRITICAL_ISSUES_FOUND.md",
    ],
    
    # Project Status
    "project-status/summaries": [
        "ARCHIVE_COMPLETE_SUMMARY.md",
        "FINAL_RESTRUCTURE_SUMMARY.md",
        "REVIEW_COMPLETE_SUMMARY.md",
        "USER_WAS_RIGHT_SUMMARY.md",
        "EXAI_RESPONSE_SUMMARY.md",
    ],
    "project-status/progress": [
        "REVIEW_IN_PROGRESS.md",
    ],
    "project-status/readiness": [
        "READY_FOR_RESTART.md",
        "READY_TO_TEST.md",
        "HANDOVER_TO_NEXT_AGENT.md",
    ],
    
    # Technical Documentation
    "technical/plans": [
        "MOONSHOT_API_FIX_PLAN.md",
        "MOONSHOT_MODEL_STRATEGY.md",
        "AUTOMATED_CLEANUP_IMPLEMENTED.md",
    ],
    "technical/analyses": [
        "SCRIPT_RUN_RESULTS.md",
    ],
    "technical/fixes": [
        "ERROR_RECOVERY_COMPLETE.md",
        "LANGUAGE_FIX_SUMMARY.md",
    ],
}

# Files to keep at root
KEEP_AT_ROOT = [
    "README.md",
    "KIMI_DESIGN_CONTEXT.md",  # Used by scripts
]


def create_directories():
    """Create all necessary directories."""
    for target_dir in ORGANIZATION.keys():
        full_path = DOCS_ROOT / target_dir
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {target_dir}/")


def move_files(dry_run=True):
    """Move files to their new locations."""
    moved_count = 0
    skipped_count = 0
    missing_count = 0
    
    for target_dir, files in ORGANIZATION.items():
        for filename in files:
            source = DOCS_ROOT / filename
            destination = DOCS_ROOT / target_dir / filename
            
            if not source.exists():
                print(f"⚠ Missing: {filename}")
                missing_count += 1
                continue
            
            if destination.exists():
                print(f"⏭ Skip (exists): {filename} → {target_dir}/")
                skipped_count += 1
                continue
            
            if dry_run:
                print(f"→ Would move: {filename} → {target_dir}/")
            else:
                shutil.move(str(source), str(destination))
                print(f"✓ Moved: {filename} → {target_dir}/")
            
            moved_count += 1
    
    return moved_count, skipped_count, missing_count


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Organize docs/ directory")
    parser.add_argument("--execute", action="store_true", help="Actually move files (default is dry-run)")
    args = parser.parse_args()
    
    print("=" * 80)
    print("DOCS ORGANIZATION SCRIPT")
    print("=" * 80)
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")
    print(f"Docs root: {DOCS_ROOT}")
    print()
    
    # Create directories
    print("📁 Creating directory structure...")
    create_directories()
    print()
    
    # Move files
    print("📦 Moving files...")
    moved, skipped, missing = move_files(dry_run=not args.execute)
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files to move: {moved}")
    print(f"Files skipped (already exist): {skipped}")
    print(f"Files missing: {missing}")
    print()
    
    if not args.execute:
        print("⚠️  DRY-RUN MODE - No files were actually moved")
        print("Run with --execute to perform the actual move")
    else:
        print("✅ Files moved successfully!")
    
    print()
    print("Files kept at root:")
    for filename in KEEP_AT_ROOT:
        if (DOCS_ROOT / filename).exists():
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} (missing)")


if __name__ == "__main__":
    main()

