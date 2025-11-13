import os
import requests
import json

# Get access token from environment or config
from src.config.settings import Config
config = Config()
access_token = os.getenv("SUPABASE_ACCESS_TOKEN", "")

# Try to get the project API keys from the management API
project_ref = "mxaazuhlqewmkweewyaz"

print("=" * 60)
print("Getting Supabase project keys...")
print("=" * 60)

# Get project details
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Try to get project API keys
url = f"https://api.supabase.com/v1/projects/{project_ref}/api-keys"

try:
    response = requests.get(url, headers=headers)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        keys = response.json()
        print("\n" + "=" * 60)
        print("PROJECT API KEYS FOUND:")
        print("=" * 60)
        for key in keys:
            print(f"\nName: {key.get('name', 'N/A')}")
            print(f"  ID: {key.get('id', 'N/A')}")
            print(f"  Key: {key.get('api_key', 'N/A')[:20]}...")
            print(f"  Type: {key.get('type', 'N/A')}")
            print(f"  Role: {key.get('role', 'N/A')}")
    else:
        print(f"Failed to get keys: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
