#!/usr/bin/env python3
"""
Restructure system-reference files into focused, maintainable pieces.
"""

from pathlib import Path
import shutil

# Create archive folder
archive_dir = Path("docs/archive/old-system-reference-20251003")
archive_dir.mkdir(parents=True, exist_ok=True)

# Files to restructure
files_to_process = [
    "docs/system-reference/02-provider-architecture.md",
    "docs/system-reference/04-features-and-capabilities.md",
    "docs/system-reference/05-api-endpoints-reference.md"
]

# Archive original files
for file_path in files_to_process:
    src = Path(file_path)
    if src.exists():
        dst = archive_dir / f"{src.stem}-ARCHIVED-20251003{src.suffix}"
        shutil.copy2(src, dst)
        print(f"✅ Archived {src.name} → {dst.name}")

print("\n📦 All files archived successfully!")
print(f"📁 Archive location: {archive_dir}")

