#!/bin/bash
# Redis Backup Script for EXAI MCP Server
# Date: 2025-10-16
# Description: Creates timestamped backups of Redis data

# Configuration
BACKUP_DIR="./backups/redis"
CONTAINER_NAME="exai-redis"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="redis-backup-$DATE.rdb"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo -e "${YELLOW}[BACKUP] Starting Redis backup...${NC}"

# Trigger background save in Redis
echo -e "${YELLOW}[BACKUP] Triggering BGSAVE in Redis...${NC}"
docker exec "$CONTAINER_NAME" redis-cli BGSAVE

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to trigger BGSAVE in Redis${NC}"
    exit 1
fi

# Wait for BGSAVE to complete (check every second, max 30 seconds)
echo -e "${YELLOW}[BACKUP] Waiting for BGSAVE to complete...${NC}"
for i in {1..30}; do
    LASTSAVE=$(docker exec "$CONTAINER_NAME" redis-cli LASTSAVE)
    sleep 1
    NEWSAVE=$(docker exec "$CONTAINER_NAME" redis-cli LASTSAVE)
    
    if [ "$NEWSAVE" -gt "$LASTSAVE" ]; then
        echo -e "${GREEN}[BACKUP] BGSAVE completed successfully${NC}"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo -e "${RED}[ERROR] BGSAVE timeout after 30 seconds${NC}"
        exit 1
    fi
done

# Copy RDB file from container
echo -e "${YELLOW}[BACKUP] Copying RDB file from container...${NC}"
docker cp "$CONTAINER_NAME:/data/dump.rdb" "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    # Get file size
    FILE_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}[SUCCESS] Redis backup completed: $BACKUP_FILE (Size: $FILE_SIZE)${NC}"
    echo -e "${GREEN}[SUCCESS] Backup location: $BACKUP_DIR/$BACKUP_FILE${NC}"
    
    # Optional: Keep only last 7 backups
    echo -e "${YELLOW}[CLEANUP] Removing old backups (keeping last 7)...${NC}"
    cd "$BACKUP_DIR" && ls -t redis-backup-*.rdb | tail -n +8 | xargs -r rm
    
    # List current backups
    echo -e "${GREEN}[INFO] Current backups:${NC}"
    ls -lh "$BACKUP_DIR"/redis-backup-*.rdb 2>/dev/null || echo "No backups found"
else
    echo -e "${RED}[ERROR] Failed to copy RDB file from container${NC}"
    exit 1
fi

echo -e "${GREEN}[BACKUP] Backup process completed successfully${NC}"
exit 0

