"""
Test script for parallel file upload functionality
"""
import os
import time
from pathlib import Path

# Set environment variables for testing
os.environ["KIMI_FILES_PARALLEL_UPLOADS"] = "true"
os.environ["KIMI_FILES_MAX_PARALLEL"] = "3"

from tools.providers.kimi.kimi_upload import KimiUploadAndExtractTool

def test_parallel_upload():
    """Test parallel file upload"""
    print("=" * 60)
    print("Testing Parallel File Upload")
    print("=" * 60)
    
    # Create tool instance
    tool = KimiUploadAndExtractTool()
    print(f"✓ Tool created: {tool.get_name()}")
    
    # Test files
    test_files = [
        "test_upload_1.txt",
        "test_upload_2.txt",
        "test_upload_3.txt"
    ]
    
    # Verify files exist
    for f in test_files:
        if not Path(f).exists():
            print(f"✗ File not found: {f}")
            return False
        print(f"✓ File exists: {f}")
    
    print("\n" + "=" * 60)
    print("Starting upload test...")
    print("=" * 60)
    
    try:
        start_time = time.time()
        
        # Call the _run method directly
        messages = tool._run(files=test_files, purpose="file-extract")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✓ Upload completed in {duration:.2f} seconds")
        print(f"✓ Received {len(messages)} messages")
        
        # Display results
        for i, msg in enumerate(messages, 1):
            print(f"\nMessage {i}:")
            print(f"  Role: {msg.get('role')}")
            print(f"  File ID: {msg.get('_file_id')}")
            print(f"  Content length: {len(msg.get('content', ''))} chars")
            print(f"  Content preview: {msg.get('content', '')[:100]}...")
        
        print("\n" + "=" * 60)
        print("✅ TEST PASSED - Parallel upload working!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sequential_upload():
    """Test sequential file upload (fallback)"""
    print("\n" + "=" * 60)
    print("Testing Sequential File Upload (Fallback)")
    print("=" * 60)
    
    # Disable parallel uploads
    os.environ["KIMI_FILES_PARALLEL_UPLOADS"] = "false"
    
    # Create tool instance
    tool = KimiUploadAndExtractTool()
    print(f"✓ Tool created: {tool.get_name()}")
    
    # Test files
    test_files = ["test_upload_1.txt"]
    
    print("\n" + "=" * 60)
    print("Starting sequential upload test...")
    print("=" * 60)
    
    try:
        start_time = time.time()
        
        # Call the _run method directly
        messages = tool._run(files=test_files, purpose="file-extract")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✓ Upload completed in {duration:.2f} seconds")
        print(f"✓ Received {len(messages)} messages")
        
        print("\n" + "=" * 60)
        print("✅ TEST PASSED - Sequential upload working!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🧪 PARALLEL FILE UPLOAD TEST SUITE\n")
    
    # Test 1: Parallel upload
    test1_passed = test_parallel_upload()
    
    # Test 2: Sequential upload (fallback)
    test2_passed = test_sequential_upload()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Parallel Upload: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Sequential Upload: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED!")
        exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        exit(1)

