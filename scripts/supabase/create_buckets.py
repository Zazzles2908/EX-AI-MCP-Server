"""
Create Supabase Storage Buckets
Date: 2025-10-30
EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9

Creates required storage buckets for the Universal File Hub.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables from .env.docker
env_path = Path(__file__).parent.parent.parent / '.env.docker'
load_dotenv(env_path)

def create_buckets():
    """Create required storage buckets."""
    print("=" * 80)
    print("Creating Supabase Storage Buckets")
    print("=" * 80)
    
    from supabase import create_client
    
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    client = create_client(url, service_key)
    
    # Define required buckets
    buckets_config = [
        {
            'name': 'user-files',
            'public': False,
            'file_size_limit': 104857600,  # 100MB
            'allowed_mime_types': None  # Allow all types
        },
        {
            'name': 'results',
            'public': False,
            'file_size_limit': 104857600,  # 100MB
            'allowed_mime_types': None
        },
        {
            'name': 'generated-files',
            'public': False,
            'file_size_limit': 104857600,  # 100MB
            'allowed_mime_types': None
        }
    ]
    
    # Get existing buckets
    print("\n1. Checking existing buckets...")
    existing_buckets = client.storage.list_buckets()
    existing_names = [b.name if hasattr(b, 'name') else b.get('name') for b in existing_buckets]
    print(f"   Found {len(existing_names)} existing buckets: {existing_names}")
    
    # Create missing buckets
    print("\n2. Creating missing buckets...")
    created = 0
    skipped = 0
    
    for config in buckets_config:
        bucket_name = config['name']
        
        if bucket_name in existing_names:
            print(f"   ⏭️  Skipping '{bucket_name}' (already exists)")
            skipped += 1
            continue
        
        try:
            # Create bucket (without options - set limits via dashboard)
            result = client.storage.create_bucket(
                bucket_name,
                options={'public': config['public']}
            )
            print(f"   ✅ Created '{bucket_name}'")
            created += 1

        except Exception as e:
            print(f"   ❌ Failed to create '{bucket_name}': {e}")
    
    # Verify all buckets exist
    print("\n3. Verifying buckets...")
    final_buckets = client.storage.list_buckets()
    final_names = [b.name if hasattr(b, 'name') else b.get('name') for b in final_buckets]
    
    all_exist = all(config['name'] in final_names for config in buckets_config)
    
    if all_exist:
        print("   ✅ All required buckets exist")
        for config in buckets_config:
            print(f"      - {config['name']}")
    else:
        print("   ❌ Some buckets are missing")
        missing = [config['name'] for config in buckets_config if config['name'] not in final_names]
        print(f"      Missing: {missing}")
        return False
    
    print("\n" + "=" * 80)
    print(f"✅ Bucket creation complete: {created} created, {skipped} skipped")
    print("=" * 80)
    print("\nNext step: Execute database schema")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = create_buckets()
    sys.exit(0 if success else 1)

