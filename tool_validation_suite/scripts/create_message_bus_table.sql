-- ============================================================================
-- Supabase Message Bus Table Schema
-- ============================================================================
-- Purpose: Store large message payloads (up to 100MB) with guaranteed integrity
-- Created: 2025-10-07 (Phase 2B)
-- Based on: Expert guidance from GLM-4.6 with web search
-- ============================================================================

-- Create custom types
CREATE TYPE message_status AS ENUM ('pending', 'complete', 'error', 'expired');
CREATE TYPE compression_type AS ENUM ('none', 'gzip', 'zstd');

-- Main message_bus table
CREATE TABLE message_bus (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id VARCHAR(255) NOT NULL UNIQUE,
    session_id VARCHAR(255) NOT NULL,
    tool_name VARCHAR(100) NOT NULL,
    provider_name VARCHAR(100) NOT NULL,
    
    -- Payload storage with TOAST optimization
    payload JSONB,
    payload_size_bytes BIGINT NOT NULL,
    compression_type compression_type NOT NULL DEFAULT 'none',
    compressed_size_bytes BIGINT,
    
    -- Integrity and metadata
    checksum VARCHAR(64) NOT NULL, -- SHA-256 hash
    status message_status NOT NULL DEFAULT 'pending',
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    accessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '48 hours'),
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT valid_payload_size CHECK (payload_size_bytes > 0),
    CONSTRAINT valid_compressed_size CHECK (compressed_size_bytes IS NULL OR compressed_size_bytes > 0),
    CONSTRAINT checksum_length CHECK (length(checksum) = 64)
);

-- ============================================================================
-- Indexing Strategy
-- ============================================================================

-- Primary query patterns
CREATE INDEX idx_message_bus_transaction_id ON message_bus(transaction_id);
CREATE INDEX idx_message_bus_session_id ON message_bus(session_id);
CREATE INDEX idx_message_bus_status ON message_bus(status);

-- Cleanup and maintenance
CREATE INDEX idx_message_bus_expires_at ON message_bus(expires_at);
CREATE INDEX idx_message_bus_created_at ON message_bus(created_at);

-- Composite indexes for common queries
CREATE INDEX idx_message_bus_session_status ON message_bus(session_id, status);
CREATE INDEX idx_message_bus_tool_provider ON message_bus(tool_name, provider_name);

-- Partial index for active messages (optimizes cleanup)
CREATE INDEX idx_message_bus_active ON message_bus(expires_at) 
    WHERE status IN ('pending', 'complete');

-- ============================================================================
-- Row Level Security (RLS)
-- ============================================================================

ALTER TABLE message_bus ENABLE ROW LEVEL SECURITY;

-- Policy: Users can access their own session messages
CREATE POLICY "Users can access their own session messages" ON message_bus
    FOR ALL USING (session_id = current_setting('app.current_session_id', true));

-- Policy: System can manage all messages
CREATE POLICY "System can manage all messages" ON message_bus
    FOR ALL USING (current_setting('app.is_system', true) = 'true');

-- Policy: Tools can only write to their own messages
CREATE POLICY "Tools can only write to their own messages" ON message_bus
    FOR INSERT WITH CHECK (
        provider_name = current_setting('app.provider_name', true) AND
        tool_name = current_setting('app.tool_name', true)
    );

-- Policy: Read access based on session ownership
CREATE POLICY "Read access based on session ownership" ON message_bus
    FOR SELECT USING (
        session_id = current_setting('app.current_session_id', true) OR
        current_setting('app.is_system', true) = 'true'
    );

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function to set session context
CREATE OR REPLACE FUNCTION set_session_context(session_id_param VARCHAR)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_session_id', session_id_param, true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clean expired messages
CREATE OR REPLACE FUNCTION cleanup_expired_messages()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete expired messages
    DELETE FROM message_bus 
    WHERE expires_at < NOW() OR status = 'expired';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Archive Table (Optional - for debugging)
-- ============================================================================

CREATE TABLE message_bus_archive (
    LIKE message_bus INCLUDING ALL
);

-- Function to archive before cleanup
CREATE OR REPLACE FUNCTION archive_and_cleanup_expired_messages()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Archive before deletion
    INSERT INTO message_bus_archive
    SELECT * FROM message_bus 
    WHERE expires_at < NOW() OR status = 'expired';
    
    -- Delete expired messages
    DELETE FROM message_bus 
    WHERE expires_at < NOW() OR status = 'expired';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Maintenance Log Table
-- ============================================================================

CREATE TABLE maintenance_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation VARCHAR(100) NOT NULL,
    records_affected INTEGER NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- Chunking Support (for messages >50MB)
-- ============================================================================

CREATE TABLE message_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES message_bus(id) ON DELETE CASCADE,
    chunk_sequence INTEGER NOT NULL,
    chunk_data BYTEA NOT NULL,
    UNIQUE(message_id, chunk_sequence)
);

CREATE INDEX idx_message_chunks_message_id ON message_chunks(message_id);

-- ============================================================================
-- Scheduled Cleanup (requires pg_cron extension)
-- ============================================================================
-- Note: Uncomment if pg_cron is available
-- SELECT cron.schedule('cleanup-expired-messages', '0 */6 * * *', 'SELECT cleanup_expired_messages();');

-- ============================================================================
-- Grants (adjust based on your Supabase setup)
-- ============================================================================
-- GRANT ALL ON message_bus TO authenticated;
-- GRANT ALL ON message_bus_archive TO authenticated;
-- GRANT ALL ON message_chunks TO authenticated;
-- GRANT ALL ON maintenance_log TO authenticated;

-- ============================================================================
-- End of Schema
-- ============================================================================

