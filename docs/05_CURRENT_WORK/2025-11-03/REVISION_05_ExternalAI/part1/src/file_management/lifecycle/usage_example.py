#!/usr/bin/env python3
"""
File Lifecycle Synchronization Usage Example

This example demonstrates how to use the file lifecycle synchronization system
for automated file management.
"""

import asyncio
import json
from pathlib import Path
from lifecycle_sync import (
    LifecycleSync, 
    LifecycleScheduler,
    LifecyclePolicy,
    FileType,
    load_config
)


async def basic_usage_example():
    """Basic usage example"""
    print("=== Basic File Lifecycle Management ===")
    
    # Load configuration
    config = load_config("config_example.json")
    
    # Initialize lifecycle sync
    lifecycle = LifecycleSync(config)
    
    # Create a custom policy
    custom_policy = LifecyclePolicy(
        name="images_quick_cleanup",
        file_types=[FileType.IMAGE],
        retention_days=30,
        archive_after_days=7,
        delete_after_days=30,
        backup_frequency_hours=12,
        auto_archive=True,
        auto_delete=True,
        versioning_enabled=True,
        max_versions=3
    )
    
    lifecycle.create_policy(custom_policy)
    
    # Register some files
    test_files = [
        "./test_data/document1.txt",
        "./test_data/image1.jpg", 
        "./test_data/video1.mp4"
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            file_id = await lifecycle.register_file(file_path, "images_quick_cleanup")
            print(f"Registered file: {file_path} (ID: {file_id})")
    
    # Get file status
    if test_files and Path(test_files[0]).exists():
        file_id = await lifecycle.register_file(test_files[0])
        status = await lifecycle.get_file_status(file_id)
        print(f"File status: {status}")
    
    # Get statistics
    stats = await lifecycle.get_statistics()
    print(f"Statistics: {stats}")
    
    # Force sync
    await lifecycle.sync_now()
    
    print("Basic usage example completed!")


async def advanced_usage_example():
    """Advanced usage with custom policies and scheduling"""
    print("\n=== Advanced File Lifecycle Management ===")
    
    config = load_config("config_example.json")
    
    # Initialize scheduler for background operations
    scheduler = LifecycleScheduler(config)
    
    # Create comprehensive policies
    policies = [
        LifecyclePolicy(
            name="documents_strict",
            file_types=[FileType.DOCUMENT],
            retention_days=90,
            archive_after_days=30,
            delete_after_days=90,
            backup_frequency_hours=24,
            auto_archive=True,
            auto_delete=True,
            versioning_enabled=True,
            max_versions=5
        ),
        LifecyclePolicy(
            name="media_archive_only",
            file_types=[FileType.VIDEO, FileType.AUDIO],
            retention_days=2555,  # 7 years
            archive_after_days=365,
            delete_after_days=2555,
            backup_frequency_hours=168,
            auto_archive=False,
            auto_delete=False,
            versioning_enabled=True,
            max_versions=2
        )
    ]
    
    # Start the scheduler (runs in background)
    await scheduler.start()
    
    print("Advanced scheduler started!")
    print("The system will now:")
    print("- Sync registry every 5 minutes")
    print("- Cleanup orphaned files every hour")
    print("- Process backups every hour")
    print("- Enforce policies every 30 minutes")
    print("\nPress Ctrl+C to stop...")
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
    finally:
        await scheduler.stop()
        print("Scheduler stopped!")


def file_operations_example():
    """Example of file operations with lifecycle management"""
    print("\n=== File Operations Example ===")
    
    config = load_config("config_example.json")
    lifecycle = LifecycleSync(config)
    
    async def run_file_operations():
        # Example file operations
        test_file = "./test_data/sample.txt"
        
        if not Path(test_file).exists():
            print(f"Test file {test_file} not found. Creating...")
            Path(test_file).parent.mkdir(parents=True, exist_ok=True)
            Path(test_file).write_text("Sample file for lifecycle management")
        
        # Register file
        file_id = await lifecycle.register_file(test_file, "documents")
        print(f"Registered file: {file_id}")
        
        # Change policy
        await lifecycle.change_file_policy(file_id, "documents_strict")
        print("Changed policy for file")
        
        # Force operations
        await lifecycle.force_backup(file_id)
        print("Forced backup for file")
        
        await lifecycle.force_archive(file_id)
        print("Forced archive for file")
        
        # Get files by state
        archived_files = await lifecycle.get_files_by_state(
            lifecycle_sync.LifecycleState.ARCHIVED
        )
        print(f"Found {len(archived_files)} archived files")
        
        # Get expired files
        expired_files = await lifecycle.get_expired_files()
        print(f"Found {len(expired_files)} expired files")
    
    # Run the async operations
    asyncio.run(run_file_operations())


if __name__ == "__main__":
    print("File Lifecycle Synchronization Examples")
    print("=====================================")
    
    # Run examples
    try:
        asyncio.run(basic_usage_example())
        advanced_usage_example()
        file_operations_example()
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()