"""
Quick test to verify environment variables are being loaded
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("ENVIRONMENT VARIABLE TEST")
print("=" * 80)

# Test critical environment variables
env_vars = [
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "CONVERSATION_STORAGE_BACKEND",
    "UPLOAD_FILES_IMMEDIATELY",
    "ENABLE_FALLBACK"
]

print("\n1. Checking environment variables:")
for var in env_vars:
    value = os.getenv(var)
    if value:
        # Mask sensitive values
        if "KEY" in var or "TOKEN" in var:
            display_value = f"{value[:10]}..." if len(value) > 10 else "***"
        else:
            display_value = value
        print(f"   ✅ {var} = {display_value}")
    else:
        print(f"   ❌ {var} = NOT SET")

print("\n2. Testing SupabaseStorageManager initialization:")
try:
    from src.storage.supabase_client import get_storage_manager
    
    storage = get_storage_manager()
    print(f"   ✅ SupabaseStorageManager created")
    print(f"   ✅ Enabled: {storage.enabled}")
    print(f"   ✅ URL: {storage.url}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n3. Testing storage factory:")
try:
    from utils.conversation.storage_factory import get_conversation_storage
    
    storage = get_conversation_storage()
    print(f"   ✅ Storage factory created: {type(storage).__name__}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

