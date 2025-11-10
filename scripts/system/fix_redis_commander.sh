#!/bin/bash

echo "Fixing Redis Commander configuration..."

# Check the REDIS_PASSWORD in .env.docker
REDIS_PASSWORD=$(grep "^REDIS_PASSWORD=" .env.docker | cut -d'=' -f2 | tr -d ' ')

echo "REDIS_PASSWORD from .env.docker: ${REDIS_PASSWORD:0:10}..."

# The issue is that the REDIS_PASSWORD contains special characters that break JSON
# Redis Commander expects: REDIS_HOSTS=local:host:port:db:password

# Test if password needs escaping
echo ""
echo "Testing password encoding..."
echo "$REDIS_PASSWORD" | python3 -c "import json, sys; password = sys.stdin.read().strip(); print('Password JSON-safe:', json.dumps(password))"

# Create a fixed redis-commander config
mkdir -p redis-commander/config

cat > redis-commander/config/local-production.json << 'REDISCONF'
{
  "title": "Local Production Redis",
  "defaultACE": {
    "username": "default",
    "password": ""
  },
  "hostname": "redis",
  "port": 6379,
  "database": 0,
  "useAuthentication": true
}
REDISCONF

echo "Created redis-commander config"
cat redis-commander/config/local-production.json

# Update docker-compose to use the config file
echo ""
echo "Docker compose should work with this configuration"
