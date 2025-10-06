#!/usr/bin/env python
"""Delete ALL files from Kimi platform - no filters, no date checks."""
import os
import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

# Load .env
try:
    from dotenv import load_dotenv
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        load_dotenv(str(env_file))
except Exception:
    pass

from openai import OpenAI

def main():
    api_key = os.getenv("MOONSHOT_API_KEY") or os.getenv("KIMI_API_KEY")
    if not api_key:
        print("ERROR: MOONSHOT_API_KEY or KIMI_API_KEY not found in environment")
        return 1
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.ai/v1"
    )
    
    print("🔍 Listing all files from Kimi platform...")
    try:
        response = client.files.list()
        files = response.data if hasattr(response, 'data') else []
    except Exception as e:
        print(f"ERROR listing files: {e}")
        return 1
    
    if not files:
        print("✅ No files found on platform")
        return 0
    
    print(f"📋 Found {len(files)} files")
    print(f"\n🗑️  Deleting ALL {len(files)} files...")
    
    deleted = 0
    failed = 0
    
    for file in files:
        file_id = file.id if hasattr(file, 'id') else file.get('id')
        filename = file.filename if hasattr(file, 'filename') else file.get('filename', 'unknown')
        
        try:
            client.files.delete(file_id)
            deleted += 1
            if deleted % 10 == 0:
                print(f"  ✓ Deleted {deleted}/{len(files)} files...")
        except Exception as e:
            failed += 1
            print(f"  ✗ Failed to delete {filename} ({file_id}): {e}")
    
    print(f"\n✅ Deletion complete!")
    print(f"   Deleted: {deleted}")
    print(f"   Failed: {failed}")
    print(f"   Total: {len(files)}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

