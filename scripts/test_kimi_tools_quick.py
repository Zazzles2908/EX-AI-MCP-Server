#!/usr/bin/env python3
"""Quick test of Kimi file tools"""
import asyncio
import json
from tools.providers.kimi.kimi_files import KimiManageFilesTool

async def main():
    tool = KimiManageFilesTool()
    
    # List files
    print("Listing files...")
    result = await tool.execute({"operation": "list", "limit": 10})
    data = json.loads(result[0].text)
    print(f"Files: {data.get('count', 0)}")
    
    # Cleanup dry run
    print("\nCleanup dry run...")
    result = await tool.execute({"operation": "cleanup_all", "dry_run": True})
    data = json.loads(result[0].text)
    print(f"Would delete: {data.get('deleted_count', 0)}")
    
    # Actual cleanup
    if data.get('deleted_count', 0) > 0:
        print("\nExecuting cleanup...")
        result = await tool.execute({"operation": "cleanup_all", "dry_run": False})
        data = json.loads(result[0].text)
        print(f"Deleted: {data.get('deleted_count', 0)}")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(main())

