#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         SUPABASE API KEY VALIDATION TOOL                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get keys from user
read -p "Enter SUPABASE_ANON_KEY: " ANON_KEY
read -s -p "Enter SUPABASE_SERVICE_ROLE_KEY: " SERVICE_KEY
echo ""
echo ""

# Test anon key
echo "Testing SUPABASE_ANON_KEY..."
echo "----------------------------------------"
ANON_TEST=$(curl -s -w "\n%{http_code}" -H "apikey: $ANON_KEY" -H "Authorization: Bearer $ANON_KEY" "https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/")

ANON_HTTP_CODE=$(echo "$ANON_TEST" | tail -n 1)
ANON_BODY=$(echo "$ANON_TEST" | head -n -1)

if [ "$ANON_HTTP_CODE" = "200" ] || [ "$ANON_HTTP_CODE" = "404" ] || [ "$ANON_HTTP_CODE" = "406" ]; then
    echo "✅ ANON KEY WORKS (HTTP $ANON_HTTP_CODE)"
else
    echo "❌ ANON KEY FAILED (HTTP $ANON_HTTP_CODE)"
    echo "Response: $ANON_BODY"
fi

echo ""

# Test service role key
echo "Testing SUPABASE_SERVICE_ROLE_KEY..."
echo "----------------------------------------"
SERVICE_TEST=$(curl -s -w "\n%{http_code}" -H "apikey: $SERVICE_KEY" -H "Authorization: Bearer $SERVICE_KEY" "https://mxaazuhlqewmkweewyaz.supabase.co/rest/v1/")

SERVICE_HTTP_CODE=$(echo "$SERVICE_TEST" | tail -n 1)
SERVICE_BODY=$(echo "$SERVICE_TEST" | head -n -1)

if [ "$SERVICE_HTTP_CODE" = "200" ] || [ "$SERVICE_HTTP_CODE" = "404" ] || [ "$SERVICE_HTTP_CODE" = "406" ]; then
    echo "✅ SERVICE ROLE KEY WORKS (HTTP $SERVICE_HTTP_CODE)"
else
    echo "❌ SERVICE ROLE KEY FAILED (HTTP $SERVICE_HTTP_CODE)"
    echo "Response: $SERVICE_BODY"
fi

echo ""

# Check if keys are different
echo "Checking if keys are different..."
echo "----------------------------------------"
if [ "$ANON_KEY" = "$SERVICE_KEY" ]; then
    echo "❌ KEYS ARE IDENTICAL! This will cause errors."
    echo "The anon and service_role keys must be DIFFERENT."
    exit 1
else
    echo "✅ Keys are different"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    VALIDATION COMPLETE                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "If both keys show ✅, you can now update .env and .env.docker files"
echo "and build the container with: docker-compose up -d"
echo ""

# Generate the update commands
echo "Update commands:"
echo "----------------------------------------"
echo "In .env:"
echo "SUPABASE_URL=https://mxaazuhlqewmkweewyaz.supabase.co"
echo "SUPABASE_ANON_KEY=$ANON_KEY"
echo "SUPABASE_SERVICE_ROLE_KEY=$SERVICE_KEY"
echo ""
echo "In .env.docker:"
echo "SUPABASE_URL=https://mxaazuhlqewmkweewyaz.supabase.co"
echo "SUPABASE_ANON_KEY=$ANON_KEY"
echo "SUPABASE_SERVICE_ROLE_KEY=$SERVICE_KEY"
