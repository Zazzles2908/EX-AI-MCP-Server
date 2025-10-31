#!/usr/bin/env python3
"""
File Operations SDK Test
Tests GLM and Kimi file upload/management via their respective SDKs
"""
import os
import time
import tempfile
from pathlib import Path
from zhipuai import ZhipuAI
from openai import OpenAI

print("=" * 80)
print("FILE OPERATIONS SDK TEST")
print("=" * 80)

# Create a test file
test_content = """This is a test file for SDK file operations.
It contains multiple lines of text.
Line 3: Testing file upload functionality.
Line 4: Verifying SDK integration.
"""

with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write(test_content)
    test_file_path = f.name

print(f"\n📄 Created test file: {test_file_path}")
print(f"📝 Content length: {len(test_content)} bytes")

# Test 1: GLM File Upload
print("\n[TEST 1] GLM File Upload via ZhipuAI SDK")
print("-" * 80)
try:
    glm_client = ZhipuAI(api_key=os.getenv("GLM_API_KEY"))
    
    # Upload file
    start = time.time()
    with open(test_file_path, 'rb') as file:
        glm_file = glm_client.files.create(
            file=file,
            purpose="file-extract"
        )
    elapsed = int((time.time() - start) * 1000)
    
    print(f"✅ File uploaded successfully")
    print(f"⏱️  Upload time: {elapsed}ms")
    print(f"📊 File ID: {glm_file.id}")
    print(f"📊 Filename: {glm_file.filename}")
    print(f"📊 Purpose: {glm_file.purpose}")
    print(f"📊 Bytes: {glm_file.bytes}")
    
    glm_file_id = glm_file.id
    
    # List files
    print("\n📋 Listing GLM files...")
    files_list = glm_client.files.list()
    print(f"✅ Found {len(files_list.data)} file(s)")
    
    # Delete file
    print(f"\n🗑️  Deleting file {glm_file_id}...")
    glm_client.files.delete(file_id=glm_file_id)
    print("✅ File deleted successfully")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Kimi File Upload
print("\n[TEST 2] Kimi File Upload via OpenAI SDK")
print("-" * 80)
try:
    kimi_client = OpenAI(
        api_key=os.getenv("KIMI_API_KEY"),
        base_url="https://api.moonshot.ai/v1"
    )
    
    # Upload file
    start = time.time()
    with open(test_file_path, 'rb') as file:
        kimi_file = kimi_client.files.create(
            file=file,
            purpose="file-extract"
        )
    elapsed = int((time.time() - start) * 1000)
    
    print(f"✅ File uploaded successfully")
    print(f"⏱️  Upload time: {elapsed}ms")
    print(f"📊 File ID: {kimi_file.id}")
    print(f"📊 Filename: {kimi_file.filename}")
    print(f"📊 Purpose: {kimi_file.purpose}")
    print(f"📊 Bytes: {kimi_file.bytes}")
    
    kimi_file_id = kimi_file.id
    
    # List files
    print("\n📋 Listing Kimi files...")
    files_list = kimi_client.files.list()
    print(f"✅ Found {len(files_list.data)} file(s)")
    
    # Delete file
    print(f"\n🗑️  Deleting file {kimi_file_id}...")
    kimi_client.files.delete(file_id=kimi_file_id)
    print("✅ File deleted successfully")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
os.unlink(test_file_path)
print(f"\n🧹 Cleaned up test file: {test_file_path}")

print("\n" + "=" * 80)
print("FILE OPERATIONS TEST COMPLETE")
print("=" * 80)

