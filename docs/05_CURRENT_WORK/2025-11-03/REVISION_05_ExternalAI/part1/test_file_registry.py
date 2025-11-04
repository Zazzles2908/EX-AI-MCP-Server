#!/usr/bin/env python3
"""
Test script for File Registry Implementation

This script demonstrates the key features of the FileRegistry class.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from file_management.registry import FileRegistry, FileType


def create_test_files():
    """Create test files for demonstration"""
    test_dir = "test_files"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create various test files
    test_files = {
        "document.txt": "This is a test document with some content.",
        "image.jpg": "fake image data",  # In real scenario, this would be binary image data
        "data.json": '{"key": "value", "numbers": [1, 2, 3]}',
        "script.py": "#!/usr/bin/env python3\nprint('Hello, World!')",
        "archive.zip": "fake zip content"
    }
    
    created_files = []
    for filename, content in test_files.items():
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        created_files.append(filepath)
    
    return created_files


def test_file_registry():
    """Test the FileRegistry functionality"""
    print("=== File Registry Test ===\n")
    
    # Create test files
    print("1. Creating test files...")
    test_files = create_test_files()
    print(f"Created {len(test_files)} test files")
    
    # Initialize registry
    print("\n2. Initializing File Registry...")
    registry = FileRegistry("test_registry.db")
    print(f"Registry initialized: {registry}")
    
    # Register files
    print("\n3. Registering files...")
    registered_ids = []
    for filepath in test_files:
        try:
            file_id = registry.register_file(
                filepath, 
                tags=["test", "demo"],
                custom_metadata={"source": "test_script", "priority": "low"}
            )
            registered_ids.append(file_id)
            print(f"✓ Registered: {os.path.basename(filepath)} -> {file_id[:8]}...")
        except Exception as e:
            print(f"✗ Failed to register {filepath}: {e}")
    
    # Test file retrieval
    print("\n4. Testing file retrieval...")
    for i, file_id in enumerate(registered_ids):
        metadata = registry.get_file(file_id)
        if metadata:
            print(f"✓ Retrieved: {metadata.name} ({metadata.file_type}, {metadata.size} bytes)")
        else:
            print(f"✗ Failed to retrieve file {i+1}")
    
    # Test search functionality
    print("\n5. Testing search functionality...")
    
    # Search by name
    results = registry.search_files(query="test")
    print(f"Found {len(results)} files matching 'test'")
    
    # Search by type
    results = registry.search_files(file_type=FileType.DOCUMENT.value)
    print(f"Found {len(results)} document files")
    
    # Search by tag
    results = registry.search_files(tags=["test"])
    print(f"Found {len(results)} files with 'test' tag")
    
    # Get statistics
    print("\n6. Registry statistics:")
    stats = registry.get_file_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test file update
    print("\n7. Testing file update...")
    if registered_ids:
        file_id = registered_ids[0]
        success = registry.update_file(
            file_id,
            tags=["test", "demo", "updated"],
            custom_metadata={"updated": True, "update_time": "now"}
        )
        print(f"✓ File update {'successful' if success else 'failed'}")
        
        # Verify update
        metadata = registry.get_file(file_id)
        print(f"  Updated tags: {metadata.tags}")
        print(f"  Updated metadata: {metadata.custom_metadata}")
    
    # Test export functionality
    print("\n8. Testing export...")
    export_success = registry.export_registry("test_export.json", format="json")
    print(f"✓ Export {'successful' if export_success else 'failed'}")
    
    # Cleanup
    print("\n9. Cleaning up...")
    
    # Remove test files and registry
    import shutil
    if os.path.exists("test_files"):
        shutil.rmtree("test_files")
    
    if os.path.exists("test_registry.db"):
        os.remove("test_registry.db")
    
    if os.path.exists("test_export.json"):
        os.remove("test_export.json")
    
    print("✓ Cleanup completed")
    print("\n=== Test Completed Successfully! ===")


if __name__ == "__main__":
    try:
        test_file_registry()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)