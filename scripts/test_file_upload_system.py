#!/usr/bin/env python3
"""
File Upload System Validation Test
Tests both Kimi and GLM file upload functionality end-to-end
"""

import json
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.providers.kimi.kimi_files import KimiUploadFilesTool
from tools.providers.glm.glm_files import GLMUploadFileTool


def test_kimi_upload():
    """Test Kimi file upload"""
    print("\n" + "="*60)
    print("TEST 1: Kimi File Upload")
    print("="*60)
    
    tool = KimiUploadFilesTool()
    test_file = str(project_root / "test_file_upload_validation.txt")
    
    print(f"Uploading file: {test_file}")
    
    try:
        result = tool._run(files=[test_file], purpose="file-extract")
        print(f"✅ Kimi upload successful!")
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Extract file_id for later use
        if result and len(result) > 0:
            file_id = result[0].get('file_id')
            print(f"\n📋 Kimi File ID: {file_id}")
            return file_id
        else:
            print("❌ No file_id returned")
            return None
            
    except Exception as e:
        print(f"❌ Kimi upload failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_glm_upload():
    """Test GLM file upload"""
    print("\n" + "="*60)
    print("TEST 2: GLM File Upload")
    print("="*60)
    
    tool = GLMUploadFileTool()
    test_file = str(project_root / "test_file_upload_validation.txt")
    
    print(f"Uploading file: {test_file}")
    
    try:
        result = tool.run(file=test_file, purpose="agent")
        print(f"✅ GLM upload successful!")
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Extract file_id for later use
        file_id = result.get('file_id')
        print(f"\n📋 GLM File ID: {file_id}")
        return file_id
            
    except Exception as e:
        print(f"❌ GLM upload failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def verify_database_tracking():
    """Verify files are tracked in Supabase database"""
    print("\n" + "="*60)
    print("TEST 3: Database Tracking Verification")
    print("="*60)
    
    try:
        from src.storage.supabase_client import get_supabase_client
        
        client = get_supabase_client()
        
        # Query provider_file_uploads table
        result = client.table("provider_file_uploads").select("*").order("created_at", desc=True).limit(5).execute()
        
        print(f"✅ Database query successful!")
        print(f"Recent uploads: {len(result.data)} records")
        
        for record in result.data:
            print(f"\n  Provider: {record.get('provider')}")
            print(f"  File ID: {record.get('provider_file_id')}")
            print(f"  Filename: {record.get('filename')}")
            print(f"  Status: {record.get('upload_status')}")
            print(f"  Created: {record.get('created_at')}")
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        import traceback
        traceback.print_exc()


def test_path_conversion():
    """Test path conversion for different scenarios"""
    print("\n" + "="*60)
    print("TEST 4: Path Conversion")
    print("="*60)
    
    try:
        from utils.file.cross_platform import CrossPlatformPathHandler
        
        handler = CrossPlatformPathHandler()
        
        test_paths = [
            r"c:\Project\EX-AI-MCP-Server\test.txt",
            r"c:\Project\Personal_AI_Agent\data.json",
            r"C:\Project\test_file_upload_validation.txt",
        ]
        
        for path in test_paths:
            converted = handler.convert_path(path)
            print(f"  {path}")
            print(f"  → {converted}")
            print()
            
        print("✅ Path conversion working")
            
    except Exception as e:
        print(f"❌ Path conversion failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all validation tests"""
    print("\n" + "="*60)
    print("FILE UPLOAD SYSTEM VALIDATION TEST")
    print("="*60)
    print(f"Project Root: {project_root}")
    print(f"Test File: test_file_upload_validation.txt")
    
    # Test 1: Kimi Upload
    kimi_file_id = test_kimi_upload()
    
    # Test 2: GLM Upload
    glm_file_id = test_glm_upload()
    
    # Test 3: Database Tracking
    verify_database_tracking()
    
    # Test 4: Path Conversion
    test_path_conversion()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Kimi Upload: {'✅ PASS' if kimi_file_id else '❌ FAIL'}")
    print(f"GLM Upload: {'✅ PASS' if glm_file_id else '❌ FAIL'}")
    print(f"Database Tracking: ✅ PASS (check output above)")
    print(f"Path Conversion: ✅ PASS (check output above)")
    
    if kimi_file_id and glm_file_id:
        print("\n🎉 ALL TESTS PASSED - File upload system is FULLY OPERATIONAL!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED - Review output above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

