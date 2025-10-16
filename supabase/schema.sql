-- EXAI MCP Server - Supabase Database Schema
-- Created: 2025-10-15
-- Purpose: Persistent storage for conversations, messages, and files

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');
CREATE TYPE file_type AS ENUM ('user_upload', 'generated', 'cache');

-- ============================================================================
-- CONVERSATIONS TABLE
-- ============================================================================
-- Tracks conversation sessions with unique continuation_id
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  continuation_id TEXT UNIQUE NOT NULL,
  title TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE conversations IS 'Stores conversation sessions with unique continuation IDs';
COMMENT ON COLUMN conversations.continuation_id IS 'Unique identifier for conversation continuity across sessions';
COMMENT ON COLUMN conversations.metadata IS 'Stores tool usage, model info, user preferences, etc.';

-- ============================================================================
-- MESSAGES TABLE
-- ============================================================================
-- Individual messages within conversations
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  role message_role NOT NULL,
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE messages IS 'Stores individual messages within conversations';
COMMENT ON COLUMN messages.role IS 'Message sender: user, assistant, or system';
COMMENT ON COLUMN messages.metadata IS 'Stores model used, tokens, thinking mode, etc.';

-- ============================================================================
-- FILES TABLE
-- ============================================================================
-- Uploaded file metadata and storage paths
CREATE TABLE files (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  storage_path TEXT UNIQUE NOT NULL,
  original_name TEXT NOT NULL,
  mime_type TEXT,
  size_bytes INTEGER,
  file_type file_type NOT NULL DEFAULT 'user_upload',
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE files IS 'Tracks uploaded files and their metadata';
COMMENT ON COLUMN files.storage_path IS 'Path in Supabase Storage bucket';
COMMENT ON COLUMN files.file_type IS 'Type: user_upload, generated, or cache';
COMMENT ON COLUMN files.metadata IS 'Stores hash, encoding, processing info, etc.';

-- ============================================================================
-- CONVERSATION_FILES JUNCTION TABLE
-- ============================================================================
-- Many-to-many relationship between conversations and files
CREATE TABLE conversation_files (
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  file_id UUID REFERENCES files(id) ON DELETE CASCADE,
  added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (conversation_id, file_id)
);

COMMENT ON TABLE conversation_files IS 'Links files to conversations (many-to-many)';

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX idx_conversations_continuation_id ON conversations(continuation_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_files_storage_path ON files(storage_path);
CREATE INDEX idx_files_type ON files(file_type);
CREATE INDEX idx_files_created_at ON files(created_at DESC);
CREATE INDEX idx_conversation_files_conversation_id ON conversation_files(conversation_id);
CREATE INDEX idx_conversation_files_file_id ON conversation_files(file_id);

-- ============================================================================
-- UPDATED_AT TRIGGER
-- ============================================================================
-- Automatically update updated_at timestamp on conversations
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - DISABLED FOR INITIAL DEVELOPMENT
-- ============================================================================
-- Enable RLS on all tables (commented out for initial development)
-- Uncomment these when implementing multi-user authentication

-- ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE files ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE conversation_files ENABLE ROW LEVEL SECURITY;

-- Example RLS policies (commented out for initial development)
-- CREATE POLICY "Users can view own conversations" ON conversations
--   FOR SELECT USING (auth.uid()::text = metadata->>'user_id');

-- CREATE POLICY "Users can create own conversations" ON conversations
--   FOR INSERT WITH CHECK (auth.uid()::text = metadata->>'user_id');

-- CREATE POLICY "Users can update own conversations" ON conversations
--   FOR UPDATE USING (auth.uid()::text = metadata->>'user_id');

-- CREATE POLICY "Users can delete own conversations" ON conversations
--   FOR DELETE USING (auth.uid()::text = metadata->>'user_id');

-- ============================================================================
-- INITIAL DATA (OPTIONAL)
-- ============================================================================
-- Add any initial seed data here if needed

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================
CREATE TABLE IF NOT EXISTS schema_version (
  version INTEGER PRIMARY KEY,
  applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  description TEXT
);

INSERT INTO schema_version (version, description) VALUES 
  (1, 'Initial schema: conversations, messages, files, conversation_files');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

