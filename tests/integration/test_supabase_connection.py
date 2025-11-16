import sys
import os
sys.path.insert(0, 'src')

from supabase import create_client, Client

# Test the current Supabase configuration
url = "https://mxaazuhlqewmkweewyaz.supabase.co"
# Use environment variable for the access token
access_token = os.getenv('SUPABASE_ACCESS_TOKEN')

if not access_token:
    print("Error: SUPABASE_ACCESS_TOKEN environment variable not set!")
    print("Please set it with: export SUPABASE_ACCESS_TOKEN=your_token_here")
    sys.exit(1)

print("Testing Supabase connection...")
print(f"URL: {url}")
print(f"Access token: {access_token[:20]}...")

print("Testing Supabase connection...")
print(f"URL: {url}")
print(f"Anon key: {anon_key[:20]}...")

try:
    # Test with anon key
    supabase = create_client(url, anon_key)
    print("\n✓ Anon key works!")
    
    # Test basic query
    response = supabase.table("conversations").select("*").limit(1).execute()
    print(f"✓ Can query conversations table (got {len(response.data)} results)")
    
    # Get service role key from project settings
    print("\n" + "=" * 60)
    print("The service role key needs to be obtained from:")
    print("https://supabase.com/dashboard/project/mxaazuhlqewmkweewyaz/settings/api")
    print("\n1. Copy the 'service_role' key (NOT the anon key)")
    print("2. It should start with 'sbp_' and be DIFFERENT from the anon key")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print(f"Type: {type(e).__name__}")
