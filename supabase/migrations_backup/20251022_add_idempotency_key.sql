-- Migration: Add idempotency key to messages table
-- Purpose: Prevent duplicate message insertion
-- Date: 2025-10-22
-- Reference: EXAI consultation on message deduplication

-- Step 1: Add idempotency_key column (allows NULL initially for safe migration)
ALTER TABLE messages ADD COLUMN IF NOT EXISTS idempotency_key TEXT;

-- Step 2: Create function to generate idempotency key for existing messages
CREATE OR REPLACE FUNCTION generate_idempotency_key_for_message(message_id UUID)
RETURNS TEXT AS $$
DECLARE
  msg_record RECORD;
  key_string TEXT;
BEGIN
  -- Fetch message data
  SELECT conversation_id, role, content, created_at 
  INTO msg_record
  FROM messages 
  WHERE id = message_id;
  
  -- Generate deterministic key from message data
  key_string := msg_record.conversation_id::TEXT || ':' || 
                msg_record.role::TEXT || ':' || 
                msg_record.content || ':' || 
                EXTRACT(EPOCH FROM msg_record.created_at)::TEXT;
  
  -- Return SHA-256 hash
  RETURN encode(digest(key_string, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql;

-- Step 3: Backfill idempotency keys for existing messages
-- This is done in a transaction to ensure consistency
DO $$
DECLARE
  msg_id UUID;
  generated_key TEXT;
  total_updated INTEGER := 0;
BEGIN
  -- Process all messages without idempotency keys
  FOR msg_id IN 
    SELECT id FROM messages WHERE idempotency_key IS NULL
  LOOP
    -- Generate key for this message
    generated_key := generate_idempotency_key_for_message(msg_id);
    
    -- Update the message
    UPDATE messages 
    SET idempotency_key = generated_key 
    WHERE id = msg_id;
    
    total_updated := total_updated + 1;
    
    -- Log progress every 100 messages
    IF total_updated % 100 = 0 THEN
      RAISE NOTICE 'Backfilled % messages...', total_updated;
    END IF;
  END LOOP;
  
  RAISE NOTICE 'Migration complete: Backfilled % messages', total_updated;
END $$;

-- Step 4: Add unique constraint on idempotency_key
CREATE UNIQUE INDEX IF NOT EXISTS idx_messages_idempotency_key 
ON messages (idempotency_key);

-- Step 5: Add partial unique index as additional safety for messages without idempotency keys
-- This prevents duplicates even if idempotency_key is NULL (shouldn't happen after migration)
CREATE UNIQUE INDEX IF NOT EXISTS idx_messages_conversation_content_time 
ON messages (conversation_id, content, DATE_TRUNC('second', created_at))
WHERE idempotency_key IS NULL;

-- Step 6: Create upsert function for application use
CREATE OR REPLACE FUNCTION upsert_message_with_idempotency(
  p_conversation_id UUID,
  p_role message_role,
  p_content TEXT,
  p_metadata JSONB DEFAULT '{}',
  p_idempotency_key TEXT
) RETURNS UUID AS $$
DECLARE
  message_id UUID;
BEGIN
  -- Try to insert first
  INSERT INTO messages (
    conversation_id, role, content, metadata, idempotency_key
  ) VALUES (
    p_conversation_id, p_role, p_content, p_metadata, p_idempotency_key
  ) ON CONFLICT (idempotency_key) DO NOTHING
  RETURNING id INTO message_id;
  
  -- If insert didn't happen (conflict), fetch existing message ID
  IF message_id IS NULL THEN
    SELECT id INTO message_id FROM messages 
    WHERE idempotency_key = p_idempotency_key;
  END IF;
  
  RETURN message_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Add comments for documentation
COMMENT ON COLUMN messages.idempotency_key IS 'SHA-256 hash for deduplication: hash(conversation_id:role:content:timestamp)';
COMMENT ON FUNCTION upsert_message_with_idempotency IS 'Safely insert message with idempotency key, returns existing message ID if duplicate';
COMMENT ON FUNCTION generate_idempotency_key_for_message IS 'Generate idempotency key for existing message (used during migration)';

