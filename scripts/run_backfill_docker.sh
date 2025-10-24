#!/bin/bash
# Docker Backfill Execution Script
# Runs the SHA256 backfill script inside the Docker container
# Reference: EXAI consultation (Continuation: 9222d725-b6cd-44f1-8406-274e5a3b3389)

set -e  # Exit on error

echo "=========================================="
echo "DOCKER BACKFILL EXECUTION"
echo "=========================================="

# Find the running container dynamically
echo "1. Finding running Docker container..."
CONTAINER_NAME=$(docker ps --format "table {{.Names}}" | grep -v NAMES | head -1)

if [ -z "$CONTAINER_NAME" ]; then
    echo "❌ ERROR: No running container found"
    echo "   Please start the Docker container first"
    exit 1
fi

echo "✅ Found container: $CONTAINER_NAME"

# Test environment loading
echo ""
echo "2. Testing Supabase environment variables..."
SUPABASE_URL=$(docker exec "$CONTAINER_NAME" python -c "import os; print(os.getenv('SUPABASE_URL', 'NOT_SET'))")

if [ "$SUPABASE_URL" = "NOT_SET" ]; then
    echo "❌ ERROR: SUPABASE_URL not set in container"
    echo "   Check that .env.docker is loaded in docker-compose.yml"
    exit 1
fi

echo "✅ SUPABASE_URL: $SUPABASE_URL"

# Run the backfill script
echo ""
echo "3. Running backfill script..."
echo "=========================================="
docker exec -it "$CONTAINER_NAME" python /app/scripts/quick_backfill_sha256.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ BACKFILL COMPLETED SUCCESSFULLY"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Run verification: ./scripts/verify_backfill_docker.sh"
    echo "2. Check logs for any errors"
    echo "3. Proceed with shadow mode enablement"
else
    echo ""
    echo "=========================================="
    echo "❌ BACKFILL FAILED"
    echo "=========================================="
    echo ""
    echo "Check the logs above for error details"
    exit 1
fi

