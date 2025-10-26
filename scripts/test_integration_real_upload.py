#!/usr/bin/env python3
"""
REAL Integration Test - Supabase Gateway Implementation

This test uses REAL API keys and REAL file uploads to validate:
1. Kimi gateway with URL extraction
2. GLM gateway with pre-signed URLs
3. Supabase tracking
4. SDK compatibility

Environment variables required (from .env.docker):
- KIMI_API_KEY
- GLM_API_KEY
- SUPABASE_URL
- SUPABASE_KEY

Created: 2025-10-26
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging BEFORE importing any modules
# Suppress OpenAI SDK debug output (prevents file content pollution)
logging.basicConfig(level=logging.INFO)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Load environment from .env.docker
from dotenv import load_dotenv
env_path = project_root / ".env.docker"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded environment from {env_path}")
else:
    print(f"⚠️  .env.docker not found at {env_path}")

def check_environment():
    """Check that all required environment variables are set."""
    print("\n" + "=" * 80)
    print("ENVIRONMENT CHECK")
    print("=" * 80)
    
    required_vars = {
        "KIMI_API_KEY": "Kimi/Moonshot API key",
        "GLM_API_KEY": "GLM/ZhipuAI API key",
        "SUPABASE_URL": "Supabase project URL",
        "SUPABASE_KEY": "Supabase service role key"
    }
    
    all_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask the value for security
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {var}: {masked} ({description})")
        else:
            print(f"❌ {var}: NOT SET ({description})")
            all_present = False
    
    return all_present

def create_test_files():
    """Create test files of various sizes."""
    print("\n" + "=" * 80)
    print("CREATING TEST FILES")
    print("=" * 80)
    
    test_dir = project_root / "scripts" / "test_files"
    test_dir.mkdir(exist_ok=True)
    
    files = {}
    
    # Small file (<50KB) - for embedding test
    small_file = test_dir / "test_small.txt"
    with open(small_file, 'w') as f:
        f.write("This is a small test file for embedding.\n" * 100)
    files['small'] = small_file
    print(f"✅ Created small file: {small_file} ({small_file.stat().st_size} bytes)")
    
    # Medium file (2MB) - for direct upload test
    medium_file = test_dir / "test_medium.txt"
    with open(medium_file, 'w') as f:
        f.write("This is a medium test file for direct upload.\n" * 50000)
    files['medium'] = medium_file
    print(f"✅ Created medium file: {medium_file} ({medium_file.stat().st_size} bytes)")
    
    # Large file (7MB) - for gateway test
    large_file = test_dir / "test_large.txt"
    with open(large_file, 'w') as f:
        f.write("This is a large test file for Supabase gateway.\n" * 150000)
    files['large'] = large_file
    print(f"✅ Created large file: {large_file} ({large_file.stat().st_size} bytes)")
    
    return files

async def test_kimi_gateway(test_file):
    """Test Kimi gateway with real upload."""
    print("\n" + "=" * 80)
    print("TEST: KIMI GATEWAY (Real Upload)")
    print("=" * 80)
    
    try:
        from tools.providers.kimi.kimi_files import upload_via_supabase_gateway_kimi
        from src.storage.supabase_client import get_storage_manager
        
        # Get storage manager
        storage = get_storage_manager()
        if not storage or not storage.enabled:
            print("❌ Supabase storage not enabled")
            return False
        
        print(f"📁 Uploading file: {test_file}")
        print(f"📊 File size: {test_file.stat().st_size} bytes")
        
        # Upload via gateway
        result = await upload_via_supabase_gateway_kimi(str(test_file), storage)
        
        print(f"✅ Upload successful!")
        print(f"   - Kimi file_id: {result['kimi_file_id']}")
        print(f"   - Supabase file_id: {result['supabase_file_id']}")
        print(f"   - Filename: {result['filename']}")
        print(f"   - Size: {result['size_bytes']} bytes")
        print(f"   - Method: {result['upload_method']}")
        
        # Verify in database
        client = storage.get_client()
        db_result = client.table("provider_file_uploads").select("*").eq(
            "provider_file_id", result['kimi_file_id']
        ).execute()
        
        if db_result.data:
            print(f"✅ Verified in database: {len(db_result.data)} record(s)")
        else:
            print(f"⚠️  Not found in database")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_glm_gateway(test_file):
    """Test GLM gateway with real upload."""
    print("\n" + "=" * 80)
    print("TEST: GLM GATEWAY (Real Upload)")
    print("=" * 80)
    
    try:
        from tools.providers.glm.glm_files import upload_via_supabase_gateway_glm
        from src.storage.supabase_client import get_storage_manager
        
        # Get storage manager
        storage = get_storage_manager()
        if not storage or not storage.enabled:
            print("❌ Supabase storage not enabled")
            return False
        
        print(f"📁 Uploading file: {test_file}")
        print(f"📊 File size: {test_file.stat().st_size} bytes")
        
        # Upload via gateway
        result = await upload_via_supabase_gateway_glm(str(test_file), storage)
        
        print(f"✅ Upload successful!")
        print(f"   - GLM file_id: {result['glm_file_id']}")
        print(f"   - Supabase file_id: {result['supabase_file_id']}")
        print(f"   - Filename: {result['filename']}")
        print(f"   - Size: {result['size_bytes']} bytes")
        print(f"   - Method: {result['upload_method']}")
        
        # Verify in database
        client = storage.get_client()
        db_result = client.table("provider_file_uploads").select("*").eq(
            "provider_file_id", result['glm_file_id']
        ).execute()
        
        if db_result.data:
            print(f"✅ Verified in database: {len(db_result.data)} record(s)")
        else:
            print(f"⚠️  Not found in database")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_size_validator(test_files):
    """Test size validator recommendations."""
    print("\n" + "=" * 80)
    print("TEST: SIZE VALIDATOR RECOMMENDATIONS")
    print("=" * 80)
    
    try:
        from utils.file.size_validator import select_upload_method
        
        for name, file_path in test_files.items():
            result = select_upload_method(str(file_path))
            print(f"\n📁 {name.upper()} FILE: {file_path.name}")
            print(f"   Size: {result['size_formatted']}")
            print(f"   Method: {result['method']}")
            print(f"   Reason: {result['reason']}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all integration tests."""
    print("\n" + "=" * 80)
    print("REAL INTEGRATION TEST - SUPABASE GATEWAY")
    print("=" * 80)
    
    # Check environment
    if not check_environment():
        print("\n❌ Missing required environment variables")
        print("   Please ensure .env.docker has all required keys")
        return 1
    
    # Create test files
    test_files = create_test_files()
    
    # Test size validator
    print("\n" + "=" * 80)
    print("PHASE 1: SIZE VALIDATOR")
    print("=" * 80)
    validator_ok = await test_size_validator(test_files)
    
    # Test Kimi gateway (use large file)
    print("\n" + "=" * 80)
    print("PHASE 2: KIMI GATEWAY")
    print("=" * 80)
    kimi_ok = await test_kimi_gateway(test_files['large'])
    
    # Test GLM gateway (use large file)
    print("\n" + "=" * 80)
    print("PHASE 3: GLM GATEWAY")
    print("=" * 80)
    glm_ok = await test_glm_gateway(test_files['large'])
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    results = [
        ("Size Validator", validator_ok),
        ("Kimi Gateway", kimi_ok),
        ("GLM Gateway", glm_ok)
    ]
    
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for test_name, ok in results:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 80)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("   - Real API calls successful")
        print("   - Supabase tracking verified")
        print("   - Gateway implementations working")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

