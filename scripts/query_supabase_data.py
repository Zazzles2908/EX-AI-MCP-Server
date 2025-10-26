#!/usr/bin/env python3
"""
Query Supabase data to understand what was stored during baseline testing.
Uses Python Supabase client directly since MCP tools require authentication setup.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from supabase import create_client, Client
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
env_path = project_root / ".env.docker"
load_dotenv(env_path)

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ ERROR: Supabase credentials not found in .env.docker")
    sys.exit(1)

print(f"✅ Supabase URL: {SUPABASE_URL}")
print(f"✅ Service Role Key: {SUPABASE_SERVICE_ROLE_KEY[:20]}...")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

print("\n" + "="*80)
print("📊 SUPABASE DATA ANALYSIS - PHASE 1 BASELINE TESTING")
print("="*80)

# Query each table (corrected based on actual schema)
tables = ["conversations", "messages", "provider_file_uploads"]

for table_name in tables:
    print(f"\n{'='*80}")
    print(f"📋 TABLE: {table_name}")
    print(f"{'='*80}")
    
    try:
        # Get total count
        response = supabase.table(table_name).select("*", count="exact").execute()
        total_count = response.count if hasattr(response, 'count') else len(response.data)
        
        print(f"Total records: {total_count}")
        
        if total_count > 0:
            # Get recent records (last 10)
            recent = supabase.table(table_name).select("*").order("created_at", desc=True).limit(10).execute()
            
            print(f"\nRecent records (last 10):")
            for i, record in enumerate(recent.data, 1):
                print(f"\n  Record {i}:")
                for key, value in record.items():
                    if isinstance(value, str) and len(value) > 100:
                        print(f"    {key}: {value[:100]}... (truncated)")
                    else:
                        print(f"    {key}: {value}")
        else:
            print("  (No records found)")
            
    except Exception as e:
        print(f"❌ ERROR querying {table_name}: {e}")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE")
print("="*80)

