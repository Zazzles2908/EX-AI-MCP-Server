#!/usr/bin/env python3
"""
Archive all superseded documentation files now that system-reference is complete.
"""

from pathlib import Path
import shutil
from datetime import datetime

# Create archive folder with timestamp
timestamp = datetime.now().strftime("%Y%m%d")
archive_base = Path("docs/archive/superseded-20251003")
archive_base.mkdir(parents=True, exist_ok=True)

print("🗂️  Archiving superseded documentation...")
print(f"📁 Archive location: {archive_base}")
print()

# Files/folders to archive (superseded by system-reference)
to_archive = {
    # Root-level summary files (superseded by FINAL_RESTRUCTURE_SUMMARY.md)
    "docs/AGENTIC_TRANSFORMATION_ROADMAP.md": "root-summaries/",
    "docs/CLEANUP_EXECUTION_SUMMARY.md": "root-summaries/",
    "docs/COMPLETE_RESTRUCTURE_SUMMARY.md": "root-summaries/",
    "docs/CONSOLIDATION_SUMMARY.md": "root-summaries/",
    "docs/DOCUMENTATION_REORGANIZATION_COMPLETE.md": "root-summaries/",
    "docs/EXTRACTION_COMPLETE_SUMMARY.md": "root-summaries/",
    "docs/RESTRUCTURE_SUMMARY.md": "root-summaries/",
    "docs/KIMI_AUDIT_STRATEGY.md": "root-summaries/",
    "docs/PHASE3_KIMI_CLEANUP_AND_FINDINGS.md": "root-summaries/",
    
    # JSON analysis files (superseded)
    "docs/COMPREHENSIVE_CONSOLIDATION_ANALYSIS.json": "analysis-json/",
    "docs/EXAI_ANALYSIS_PROGRESS.json": "analysis-json/",
    "docs/EXAI_CODEBASE_ANALYSIS_20251003_085804.json": "analysis-json/",
    
    # Architecture folder (superseded by system-reference/02-provider-architecture.md)
    "docs/architecture/": "architecture/",
    
    # Current folder (superseded by system-reference)
    "docs/current/": "current/",
    
    # Upgrades folder (superseded by system-reference/07-upgrade-roadmap.md)
    "docs/upgrades/": "upgrades/",
}

# Archive each item
archived_count = 0
for source, dest_subfolder in to_archive.items():
    source_path = Path(source)
    
    if not source_path.exists():
        print(f"⚠️  Skipped (not found): {source}")
        continue
    
    # Create destination
    dest_path = archive_base / dest_subfolder / source_path.name
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Move to archive
    if source_path.is_dir():
        if dest_path.exists():
            shutil.rmtree(dest_path)
        shutil.copytree(source_path, dest_path)
        shutil.rmtree(source_path)
        print(f"✅ Archived folder: {source_path.name} → {dest_subfolder}")
    else:
        shutil.copy2(source_path, dest_path)
        source_path.unlink()
        print(f"✅ Archived file: {source_path.name} → {dest_subfolder}")
    
    archived_count += 1

print()
print(f"🎉 Archived {archived_count} items successfully!")
print()
print("📁 Remaining active documentation:")
print("  - docs/system-reference/ (primary documentation)")
print("  - docs/guides/ (user guides)")
print("  - docs/ux/ (UX improvements)")
print("  - docs/archive/ (historical reference)")
print("  - docs/README.md (main index)")
print("  - docs/FINAL_RESTRUCTURE_SUMMARY.md (latest summary)")

