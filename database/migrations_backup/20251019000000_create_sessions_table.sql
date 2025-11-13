-- WEEK 2 (2025-10-19): Create sessions table for session management
-- Migration: Create sessions table and add session_id to conversations

-- ============================================================================
-- CREATE SESSIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS sessions (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- User information
    user_id TEXT NOT NULL,
    
    -- Session metadata
    title TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'expired')),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Session metrics
    turn_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    
    -- Additional metadata (JSONB for flexibility)
    metadata JSONB DEFAULT '{}'::JSONB
);

-- ============================================================================
-- CREATE INDEXES
-- ============================================================================

-- Index on user_id for fast user session lookups
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);

-- Index on status for filtering active sessions
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);

-- Index on created_at for chronological queries
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC);

-- Index on expires_at for cleanup queries
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at) WHERE expires_at IS NOT NULL;

-- Composite index for user + status queries
CREATE INDEX IF NOT EXISTS idx_sessions_user_status ON sessions(user_id, status);

-- ============================================================================
-- ADD SESSION_ID TO CONVERSATIONS TABLE
-- ============================================================================

-- Add session_id column to conversations table (if it doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'conversations' AND column_name = 'session_id'
    ) THEN
        ALTER TABLE conversations ADD COLUMN session_id UUID REFERENCES sessions(id) ON DELETE SET NULL;
        
        -- Create index on session_id for fast session conversation lookups
        CREATE INDEX idx_conversations_session_id ON conversations(session_id);
    END IF;
END $$;

-- ============================================================================
-- CREATE UPDATED_AT TRIGGER
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_sessions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
DROP TRIGGER IF EXISTS trigger_sessions_updated_at ON sessions;
CREATE TRIGGER trigger_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_sessions_updated_at();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on sessions table
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own sessions
CREATE POLICY sessions_select_own ON sessions
    FOR SELECT
    USING (auth.uid()::text = user_id);

-- Policy: Users can insert their own sessions
CREATE POLICY sessions_insert_own ON sessions
    FOR INSERT
    WITH CHECK (auth.uid()::text = user_id);

-- Policy: Users can update their own sessions
CREATE POLICY sessions_update_own ON sessions
    FOR UPDATE
    USING (auth.uid()::text = user_id);

-- Policy: Users can delete their own sessions
CREATE POLICY sessions_delete_own ON sessions
    FOR DELETE
    USING (auth.uid()::text = user_id);

-- Policy: Service role can do everything (for server-side operations)
CREATE POLICY sessions_service_role_all ON sessions
    FOR ALL
    USING (auth.role() = 'service_role');

-- ============================================================================
-- CLEANUP FUNCTION
-- ============================================================================

-- Function to cleanup expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sessions
    WHERE expires_at IS NOT NULL
      AND expires_at < NOW()
      AND status != 'completed';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE sessions IS 'User sessions for conversation tracking and management';
COMMENT ON COLUMN sessions.id IS 'Unique session identifier (UUID)';
COMMENT ON COLUMN sessions.user_id IS 'User identifier (matches auth.uid())';
COMMENT ON COLUMN sessions.title IS 'Human-readable session title';
COMMENT ON COLUMN sessions.status IS 'Session status: active, paused, completed, expired';
COMMENT ON COLUMN sessions.created_at IS 'Session creation timestamp';
COMMENT ON COLUMN sessions.updated_at IS 'Last update timestamp (auto-updated)';
COMMENT ON COLUMN sessions.expires_at IS 'Session expiration timestamp (optional)';
COMMENT ON COLUMN sessions.turn_count IS 'Number of conversation turns in this session';
COMMENT ON COLUMN sessions.total_tokens IS 'Total tokens used in this session';
COMMENT ON COLUMN sessions.metadata IS 'Additional session metadata (JSONB)';

COMMENT ON FUNCTION cleanup_expired_sessions() IS 'Cleanup expired sessions (returns count of deleted sessions)';

