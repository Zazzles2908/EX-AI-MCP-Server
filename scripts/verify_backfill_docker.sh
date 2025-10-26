#!/bin/bash
# Docker Verification Script
# Runs the backfill verification script inside the Docker container
# Reference: EXAI consultation (Continuation: 9222d725-b6cd-44f1-8406-274e5a3b3389)

set -e  # Exit on error

echo "=========================================="
echo "DOCKER BACKFILL VERIFICATION"
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

# Run the verification script
echo ""
echo "2. Running verification script..."
echo "=========================================="
docker exec -it "$CONTAINER_NAME" python /app/scripts/verify_backfill.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ VERIFICATION PASSED"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "❌ VERIFICATION FAILED"
    echo "=========================================="
    exit 1
fi

