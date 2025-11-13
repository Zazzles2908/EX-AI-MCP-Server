-- Migration: Create truncation_events table for monitoring truncated API responses
-- Date: 2025-10-21
-- Purpose: Track when API responses are truncated due to max_tokens limits
-- Phase: 2.1.2 - Truncation Detection & Logging

-- ============================================================================
-- TRUNCATION_EVENTS TABLE
-- ============================================================================
-- Tracks truncated API responses for monitoring and analysis
CREATE TABLE IF NOT EXISTS truncation_events (
  -- Primary key
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Truncation metadata
  model TEXT NOT NULL,
  finish_reason TEXT NOT NULL,
  is_truncated BOOLEAN NOT NULL DEFAULT TRUE,
  
  -- Context information
  tool_name TEXT,
  conversation_id TEXT,
  
  -- Token usage
  prompt_tokens INTEGER DEFAULT 0,
  completion_tokens INTEGER DEFAULT 0,
  total_tokens INTEGER DEFAULT 0,
  
  -- Additional context (JSONB for flexibility)
  context JSONB DEFAULT '{}',
  
  -- Timestamps
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
-- Index for querying by model
CREATE INDEX IF NOT EXISTS idx_truncation_events_model 
ON truncation_events(model);

-- Index for querying by tool
CREATE INDEX IF NOT EXISTS idx_truncation_events_tool_name 
ON truncation_events(tool_name);

-- Index for querying by conversation
CREATE INDEX IF NOT EXISTS idx_truncation_events_conversation_id 
ON truncation_events(conversation_id);

-- Index for time-based queries (most common)
CREATE INDEX IF NOT EXISTS idx_truncation_events_timestamp 
ON truncation_events(timestamp DESC);

-- Index for created_at (backup/recovery queries)
CREATE INDEX IF NOT EXISTS idx_truncation_events_created_at 
ON truncation_events(created_at DESC);

-- Composite index for model + timestamp (common query pattern)
CREATE INDEX IF NOT EXISTS idx_truncation_events_model_timestamp 
ON truncation_events(model, timestamp DESC);

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================
COMMENT ON TABLE truncation_events IS 'Tracks API responses truncated due to max_tokens limits';
COMMENT ON COLUMN truncation_events.model IS 'Model name that generated the truncated response';
COMMENT ON COLUMN truncation_events.finish_reason IS 'API finish_reason (should be "length" for truncations)';
COMMENT ON COLUMN truncation_events.is_truncated IS 'Always TRUE for records in this table';
COMMENT ON COLUMN truncation_events.tool_name IS 'EXAI tool that was called (debug, codereview, etc.)';
COMMENT ON COLUMN truncation_events.conversation_id IS 'Continuation ID for tracking across conversation turns';
COMMENT ON COLUMN truncation_events.prompt_tokens IS 'Number of tokens in the prompt/input';
COMMENT ON COLUMN truncation_events.completion_tokens IS 'Number of tokens in the completion/output';
COMMENT ON COLUMN truncation_events.total_tokens IS 'Total tokens used (prompt + completion)';
COMMENT ON COLUMN truncation_events.context IS 'Additional context (JSONB) for debugging';
COMMENT ON COLUMN truncation_events.timestamp IS 'When the truncation occurred (from API response)';
COMMENT ON COLUMN truncation_events.created_at IS 'When the record was inserted into Supabase';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================
-- Enable RLS for security
ALTER TABLE truncation_events ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for authenticated users
-- Note: Adjust based on your authentication setup
CREATE POLICY "Allow all operations for authenticated users" 
ON truncation_events 
FOR ALL 
USING (true);

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================
-- Update schema version
INSERT INTO schema_version (version, description) VALUES 
  (2, 'Added truncation_events table for monitoring truncated API responses')
ON CONFLICT (version) DO NOTHING;

