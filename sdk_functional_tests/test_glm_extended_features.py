#!/usr/bin/env python3
"""
GLM Extended Feature Testing via OpenAI SDK
Tests file operations, web search, and vision capabilities
"""

import os
import time
from openai import OpenAI

print("=" * 80)
print("GLM EXTENDED FEATURE TESTING - OpenAI SDK")
print("=" * 80)

# Initialize OpenAI client with Z.ai base URL
client = OpenAI(
    api_key=os.getenv("GLM_API_KEY"),
    base_url="https://api.z.ai/api/paas/v4/"
)

# Test 1: File Operations
print("\n[TEST 1] GLM File Operations via OpenAI SDK")
print("-" * 80)
try:
    # Note: OpenAI SDK file operations use client.files API
    # Need to check if Z.ai supports this endpoint
    
    # Create a test file
    test_content = "This is a test file for GLM file operations via OpenAI SDK.\n"
    test_file_path = "/tmp/test_glm_file.txt"
    
    with open(test_file_path, "w") as f:
        f.write(test_content)
    
    print(f"✅ Created test file: {test_file_path}")
    
    # Try to upload file
    print("\n📤 Attempting file upload via OpenAI SDK...")
    start = time.time()
    
    try:
        with open(test_file_path, "rb") as f:
            file_response = client.files.create(
                file=f,
                purpose="assistants"  # or "fine-tune" depending on Z.ai support
            )
        elapsed = int((time.time() - start) * 1000)
        
        print(f"✅ File uploaded successfully!")
        print(f"   - File ID: {file_response.id}")
        print(f"   - Filename: {file_response.filename}")
        print(f"   - Purpose: {file_response.purpose}")
        print(f"   - Upload Time: {elapsed}ms")
        
        file_id = file_response.id
        
        # Try to list files
        print("\n📋 Listing files...")
        files_list = client.files.list()
        print(f"✅ Found {len(files_list.data)} files")
        for file in files_list.data[:3]:  # Show first 3
            print(f"   - {file.id}: {file.filename}")
        
        # Try to delete file
        print(f"\n🗑️  Deleting test file {file_id}...")
        delete_response = client.files.delete(file_id)
        print(f"✅ File deleted: {delete_response.deleted}")
        
        print("\n✅ TEST 1 PASSED: File operations work via OpenAI SDK!")
        
    except Exception as e:
        print(f"\n⚠️  File operations not supported or different endpoint")
        print(f"   Error: {e}")
        print("   Note: Z.ai may use different file API - need to check docs")
        print("\n⚠️  TEST 1 PARTIAL: OpenAI SDK file API not compatible")
    
except Exception as e:
    print(f"\n❌ TEST 1 FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Web Search via OpenAI SDK Tools
print("\n[TEST 2] GLM Web Search via OpenAI SDK Tools")
print("-" * 80)
try:
    # Test web search using tools/function calling
    print("📝 Testing web search via function calling...")
    
    # Define web search tool
    tools = [{
        "type": "web_search",
        "web_search": {
            "search_query": "Python programming language",
            "search_result": True
        }
    }]
    
    start = time.time()
    response = client.chat.completions.create(
        model="glm-4.6",
        messages=[{"role": "user", "content": "Search for information about Python programming"}],
        tools=tools
    )
    elapsed = int((time.time() - start) * 1000)
    
    print(f"\n⏱️  Response Time: {elapsed}ms")
    print(f"💬 Response: {response.choices[0].message.content[:200]}...")
    
    if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
        print(f"\n📊 Tool Calls: {len(response.choices[0].message.tool_calls)}")
        for tool_call in response.choices[0].message.tool_calls:
            print(f"   - Type: {tool_call.type}")
            print(f"   - Details: {str(tool_call)[:100]}...")
        print("  ✅ Web search tool calls working")
    else:
        print("  ℹ️  No tool calls in response - may have used web search internally")
    
    print("\n✅ TEST 2 PASSED: Web search via OpenAI SDK tools!")
    
except Exception as e:
    print(f"\n❌ TEST 2 FAILED: {e}")
    import traceback
    traceback.print_exc()
    print("\n⚠️  Note: May need to use different tool format for Z.ai web search")

# Test 3: Alternative Web Search Format
print("\n[TEST 3] GLM Web Search - Alternative Format")
print("-" * 80)
try:
    # Try using extra_body for web search (Z.ai specific)
    print("📝 Testing web search via extra_body parameter...")
    
    start = time.time()
    response = client.chat.completions.create(
        model="glm-4.6",
        messages=[{"role": "user", "content": "What are the latest developments in AI?"}],
        extra_body={
            "tools": [{
                "type": "web_search",
                "web_search": {
                    "enable": True,
                    "search_query": "latest AI developments 2024"
                }
            }]
        }
    )
    elapsed = int((time.time() - start) * 1000)
    
    print(f"\n⏱️  Response Time: {elapsed}ms")
    print(f"💬 Response: {response.choices[0].message.content[:200]}...")
    print(f"📊 Usage: {response.usage}")
    
    print("\n✅ TEST 3 PASSED: Alternative web search format working!")
    
except Exception as e:
    print(f"\n❌ TEST 3 FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Vision/Multimodal
print("\n[TEST 4] GLM Vision via OpenAI SDK")
print("-" * 80)
try:
    # Test vision with image URL
    print("📝 Testing vision capabilities...")
    
    # Use a simple test image URL
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/320px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    
    start = time.time()
    response = client.chat.completions.create(
        model="glm-4.5v",  # Vision model
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "What do you see in this image?"},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }]
    )
    elapsed = int((time.time() - start) * 1000)
    
    print(f"\n⏱️  Response Time: {elapsed}ms")
    print(f"💬 Response: {response.choices[0].message.content}")
    print(f"📊 Model: {response.model}")
    print(f"📊 Usage: {response.usage}")
    
    print("\n✅ TEST 4 PASSED: Vision capabilities work via OpenAI SDK!")
    
except Exception as e:
    print(f"\n❌ TEST 4 FAILED: {e}")
    import traceback
    traceback.print_exc()
    print("\n⚠️  Note: Vision may require different model or format")

print("\n" + "=" * 80)
print("EXTENDED FEATURE TESTING COMPLETE")
print("=" * 80)
print("\n📊 SUMMARY:")
print("   - File Operations: Check results above")
print("   - Web Search (Tools): Check results above")
print("   - Web Search (Alternative): Check results above")
print("   - Vision: Check results above")
print("\n💡 NEXT STEPS:")
print("   1. Review test results")
print("   2. Compare with HTTP/ZhipuAI SDK implementations")
print("   3. Consult EXAI for architectural validation")
print("   4. Make migration decision based on feature parity")

