-- Optimize Messages Query Performance
-- Phase 3.1: Slow Query Optimization
-- Created: 2025-11-01
-- Target: Reduce get_conversation_messages from 0.544s to <0.2s

-- Add composite index for efficient conversation message retrieval
-- This index supports the query pattern: WHERE conversation_id = X ORDER BY created_at DESC
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_conversation_id_created 
ON messages(conversation_id, created_at DESC);

-- Add standalone index for conversation_id (if not exists)
-- This provides fallback for queries that don't use ordering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_conversation_id 
ON messages(conversation_id);

-- Add index for created_at alone (for time-based queries)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_created_at 
ON messages(created_at DESC);

-- Analyze table to update statistics for query planner
ANALYZE messages;

