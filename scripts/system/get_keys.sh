#!/bin/bash

# Get Supabase access token from environment
export SUPABASE_ACCESS_TOKEN="${SUPABASE_ACCESS_TOKEN:-your_supabase_access_token_here}"
PROJECT_REF="mxaazuhlqewmkweewyaz"

# Check if token is set
if [ "$SUPABASE_ACCESS_TOKEN" = "your_supabase_access_token_here" ]; then
    echo "ERROR: SUPABASE_ACCESS_TOKEN environment variable is not set!"
    echo "Please set it with: export SUPABASE_ACCESS_TOKEN=your_token_here"
    exit 1
fi

echo "Getting Supabase project API keys..."
echo "=========================================="

# Get API keys
curl -s -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  "https://api.supabase.com/v1/projects/$PROJECT_REF/api-keys" | python3 -m json.tool

echo ""
echo "=========================================="
echo "Getting project config..."
echo "=========================================="

# Get project config
curl -s -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  "https://api.supabase.com/v1/projects/$PROJECT_REF" | python3 -m json.tool | head -30
