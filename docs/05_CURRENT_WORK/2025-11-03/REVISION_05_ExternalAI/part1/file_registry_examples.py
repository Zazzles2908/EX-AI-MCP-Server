#!/usr/bin/env python3
"""
File Registry Examples

This script demonstrates common use cases for the FileRegistry system.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from file_management.registry import FileRegistry, FileType


def example_1_basic_operations():
    """Example 1: Basic file registration and retrieval"""
    print("=== Example 1: Basic Operations ===")
    
    # Initialize registry
    registry = FileRegistry("example1.db")
    
    # Create a test file
    test_file = "example_document.txt"
    with open(test_file, 'w') as f:
        f.write("This is a test document for the file registry.")
    
    # Register the file
    file_id = registry.register_file(
        test_file,
        tags=["example", "document", "test"],
        custom_metadata={
            "category": "demo",
            "importance": "medium"
        }
    )
    
    print(f"Registered file with ID: {file_id}")
    
    # Retrieve the file
    metadata = registry.get_file(file_id)
    print(f"Retrieved: {metadata.name}")
    print(f"Type: {metadata.file_type}")
    print(f"Size: {metadata.size} bytes")
    print(f"Tags: {metadata.tags}")
    
    # Clean up
    os.remove(test_file)
    os.remove("example1.db")
    print("✓ Example 1 completed\n")


def example_2_search_and_filter():
    """Example 2: Search and filtering"""
    print("=== Example 2: Search and Filter ===")
    
    registry = FileRegistry("example2.db")
    
    # Create test files of different types
    files_to_create = [
        ("report.pdf", "PDF Report content", FileType.DOCUMENT),
        ("data.json", '{"status": "processed"}', FileType.DATA),
        ("image.png", "Fake image data", FileType.IMAGE),
        ("script.py", "print('Hello World')", FileType.CODE),
        ("archive.zip", "Zip content", FileType.ARCHIVE)
    ]
    
    registered_ids = []
    for filename, content, file_type in files_to_create:
        with open(filename, 'w') as f:
            f.write(content)
        
        # Tag based on type
        tags = [file_type.value, "example", "batch"]
        file_id = registry.register_file(filename, tags=tags)
        registered_ids.append(file_id)
    
    print(f"Created and registered {len(files_to_create)} files")
    
    # Search examples
    print("\n--- Search Examples ---")
    
    # Search by type
    documents = registry.search_files(file_type=FileType.DOCUMENT.value)
    print(f"Documents: {len(documents)} found")
    
    # Search by tag
    code_files = registry.search_files(tags=[FileType.CODE.value])
    print(f"Code files: {len(code_files)} found")
    
    # Search by text query
    json_files = registry.search_files(query="data")
    print(f"Files with 'data' in name: {len(json_files)} found")
    
    # Combined search
    example_docs = registry.search_files(
        tags=["example"],
        file_type=FileType.DOCUMENT.value
    )
    print(f"Example documents: {len(example_docs)} found")
    
    # Clean up
    for filename, _, _ in files_to_create:
        if os.path.exists(filename):
            os.remove(filename)
    os.remove("example2.db")
    print("✓ Example 2 completed\n")


def example_3_batch_operations():
    """Example 3: Batch file discovery"""
    print("=== Example 3: Batch Operations ===")
    
    # Create a test directory structure
    test_dir = "example3_files"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create files in subdirectories
    subdirs = ["reports", "images", "data"]
    for subdir in subdirs:
        os.makedirs(os.path.join(test_dir, subdir), exist_ok=True)
    
    # Create various files
    files_to_create = [
        ("example3_files/reports/monthly.pdf", "Monthly report"),
        ("example3_files/reports/weekly.txt", "Weekly summary"),
        ("example3_files/data/sales.json", '{"sales": 1000}'),
        ("example3_files/data/inventory.csv", "item,quantity\\napple,50"),
        ("example3_files/images/logo.png", "Logo image"),
    ]
    
    for filepath, content in files_to_create:
        with open(filepath, 'w') as f:
            f.write(content)
    
    print(f"Created directory structure with {len(files_to_create)} files")
    
    registry = FileRegistry("example3.db")
    
    # Discover and register all files
    print("\n--- Discovering Files ---")
    registered_ids = registry.discover_files(test_dir, recursive=True)
    print(f"Discovered and registered: {len(registered_ids)} files")
    
    # Show statistics
    stats = registry.get_file_stats()
    print(f"Registry stats: {stats['total_files']} files, {stats['total_size_mb']} MB")
    
    # Search in specific directory
    print("\n--- Directory-based Search ---")
    reports_dir = os.path.abspath(os.path.join(test_dir, "reports"))
    reports = registry.search_files(directory=reports_dir)
    print(f"Files in reports directory: {len(reports)}")
    
    # Clean up
    import shutil
    shutil.rmtree(test_dir)
    os.remove("example3.db")
    print("✓ Example 3 completed\n")


def example_4_metadata_management():
    """Example 4: Metadata management and updates"""
    print("=== Example 4: Metadata Management ===")
    
    registry = FileRegistry("example4.db")
    
    # Create and register file
    test_file = "metadata_example.txt"
    with open(test_file, 'w') as f:
        f.write("File for metadata demonstration.")
    
    file_id = registry.register_file(
        test_file,
        tags=["initial"],
        custom_metadata={"version": "1.0", "status": "draft"}
    )
    
    print(f"Registered file with initial metadata")
    
    # Update metadata
    print("\n--- Updating Metadata ---")
    registry.update_file(
        file_id,
        tags=["initial", "reviewed", "approved"],
        custom_metadata={
            "version": "2.0",
            "status": "approved",
            "reviewer": "admin",
            "approval_date": "2024-01-01"
        }
    )
    
    # Retrieve updated metadata
    updated_meta = registry.get_file(file_id)
    print(f"Updated tags: {updated_meta.tags}")
    print(f"Updated metadata: {updated_meta.custom_metadata}")
    
    # Show retrieval statistics
    print(f"Retrieval count: {updated_meta.retrieval_count}")
    
    # Clean up
    os.remove(test_file)
    os.remove("example4.db")
    print("✓ Example 4 completed\n")


def example_5_export_import():
    """Example 5: Export and import functionality"""
    print("=== Example 5: Export and Import ===")
    
    registry = FileRegistry("example5.db")
    
    # Create some files
    test_files = [
        ("export_test1.txt", "Test file 1"),
        ("export_test2.json", '{"test": true}'),
        ("export_test3.py", "# Python script")
    ]
    
    registered_ids = []
    for filename, content in test_files:
        with open(filename, 'w') as f:
            f.write(content)
        
        file_id = registry.register_file(
            filename,
            tags=["export", "test"],
            custom_metadata={"source": "example"}
        )
        registered_ids.append(file_id)
    
    print(f"Created and registered {len(test_files)} files")
    
    # Export to JSON
    print("\n--- Exporting to JSON ---")
    export_success = registry.export_registry("export_backup.json", format="json")
    print(f"Export successful: {export_success}")
    
    # Export to CSV
    export_success = registry.export_registry("export_backup.csv", format="csv")
    print(f"CSV export successful: {export_success}")
    
    # Get statistics before import
    stats_before = registry.get_file_stats()
    print(f"Files before import: {stats_before['total_files']}")
    
    # Create new registry and import
    print("\n--- Importing to New Registry ---")
    new_registry = FileRegistry("example5_import.db")
    
    import_success = new_registry.import_registry("export_backup.json", merge=True)
    print(f"Import successful: {import_success}")
    
    stats_after = new_registry.get_file_stats()
    print(f"Files after import: {stats_after['total_files']}")
    
    # Clean up
    for filename, _ in test_files:
        if os.path.exists(filename):
            os.remove(filename)
    
    for backup_file in ["export_backup.json", "export_backup.csv"]:
        if os.path.exists(backup_file):
            os.remove(backup_file)
    
    os.remove("example5.db")
    os.remove("example5_import.db")
    print("✓ Example 5 completed\n")


def example_6_advanced_search():
    """Example 6: Advanced search patterns"""
    print("=== Example 6: Advanced Search ===")
    
    registry = FileRegistry("example6.db")
    
    # Create files with various properties
    files = [
        ("small_file.txt", "Small", 100),
        ("large_report.pdf", "Large", 5000),
        ("medium_image.jpg", "Medium", 2000),
        ("old_data.json", "Old", 1500),
        ("new_script.py", "New", 800),
    ]
    
    import time
    
    registered_ids = []
    for filename, description, size in files:
        with open(filename, 'w') as f:
            f.write(f"{description} file content" + "x" * size)
        
        # Simulate different upload times
        file_id = registry.register_file(
            filename,
            tags=[description.lower()],
            custom_metadata={"size_category": "large" if size > 3000 else "small"}
        )
        registered_ids.append(file_id)
        
        # Small delay to create different timestamps
        time.sleep(0.1)
    
    print(f"Created {len(files)} files with different sizes and timestamps")
    
    # Advanced search examples
    print("\n--- Advanced Search Examples ---")
    
    # Search by size range
    medium_files = registry.search_files(min_size=1000, max_size=3000)
    print(f"Files between 1KB and 3KB: {len(medium_files)}")
    
    # Search by date range (files uploaded in last minute)
    recent_time = (time.time() - 60) * 1000  # 1 minute ago in milliseconds
    recent_files = registry.search_files(
        date_from=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 60))
    )
    print(f"Recent files: {len(recent_files)}")
    
    # Search with multiple criteria
    filtered_files = registry.search_files(
        tags=["new"],
        min_size=500,
        extension=".py"
    )
    print(f"New Python files over 500 bytes: {len(filtered_files)}")
    
    # Complex query
    for metadata in registry.search_files():
        print(f"  {metadata.name}: {metadata.size} bytes, tags: {metadata.tags}")
    
    # Clean up
    for filename, _, _ in files:
        if os.path.exists(filename):
            os.remove(filename)
    os.remove("example6.db")
    print("✓ Example 6 completed\n")


def main():
    """Run all examples"""
    print("File Registry Examples")
    print("=====================\n")
    
    examples = [
        example_1_basic_operations,
        example_2_search_and_filter,
        example_3_batch_operations,
        example_4_metadata_management,
        example_5_export_import,
        example_6_advanced_search
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"Example {example_func.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("All examples completed!")


if __name__ == "__main__":
    main()