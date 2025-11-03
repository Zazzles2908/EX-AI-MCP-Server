-- Migration: User Quotas Table
-- Date: 2025-11-02
-- Purpose: Track user file upload quotas and limits
-- Task: 0.1 - Implement File Upload Authentication

-- Create user_quotas table
CREATE TABLE IF NOT EXISTS user_quotas (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    quota_remaining BIGINT NOT NULL DEFAULT 10737418240,  -- 10GB default
    max_file_size BIGINT NOT NULL DEFAULT 536870912,      -- 512MB default
    total_uploaded BIGINT NOT NULL DEFAULT 0,             -- Total bytes uploaded
    file_count INTEGER NOT NULL DEFAULT 0,                -- Total files uploaded
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index on user_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_user_quotas_user_id ON user_quotas(user_id);

-- Create function to decrement user quota
CREATE OR REPLACE FUNCTION decrement_user_quota(
    p_user_id UUID,
    p_bytes BIGINT
) RETURNS VOID AS $$
BEGIN
    UPDATE user_quotas
    SET 
        quota_remaining = quota_remaining - p_bytes,
        total_uploaded = total_uploaded + p_bytes,
        file_count = file_count + 1,
        updated_at = NOW()
    WHERE user_id = p_user_id;
    
    -- Create default quota if user doesn't exist
    IF NOT FOUND THEN
        INSERT INTO user_quotas (user_id, quota_remaining, total_uploaded, file_count)
        VALUES (
            p_user_id,
            10737418240 - p_bytes,  -- 10GB - uploaded bytes
            p_bytes,
            1
        );
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create function to increment user quota (for deletions)
CREATE OR REPLACE FUNCTION increment_user_quota(
    p_user_id UUID,
    p_bytes BIGINT
) RETURNS VOID AS $$
BEGIN
    UPDATE user_quotas
    SET 
        quota_remaining = quota_remaining + p_bytes,
        total_uploaded = total_uploaded - p_bytes,
        file_count = file_count - 1,
        updated_at = NOW()
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_quotas_updated_at
    BEFORE UPDATE ON user_quotas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE user_quotas ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only view their own quota
CREATE POLICY "Users can view own quota"
    ON user_quotas
    FOR SELECT
    USING (auth.uid() = user_id);

-- Service role can manage all quotas
CREATE POLICY "Service role can manage quotas"
    ON user_quotas
    FOR ALL
    USING (auth.role() = 'service_role');

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON user_quotas TO authenticated;
GRANT ALL ON user_quotas TO service_role;

-- Create view for quota statistics
CREATE OR REPLACE VIEW user_quota_stats AS
SELECT 
    user_id,
    quota_remaining,
    max_file_size,
    total_uploaded,
    file_count,
    ROUND((total_uploaded::NUMERIC / 10737418240) * 100, 2) AS quota_used_percent,
    created_at,
    updated_at
FROM user_quotas;

-- Grant access to view
GRANT SELECT ON user_quota_stats TO authenticated;
GRANT ALL ON user_quota_stats TO service_role;

-- Insert default quotas for existing users (if any)
-- This is safe to run multiple times
INSERT INTO user_quotas (user_id)
SELECT id FROM auth.users
WHERE id NOT IN (SELECT user_id FROM user_quotas)
ON CONFLICT (user_id) DO NOTHING;

-- Add comments for documentation
COMMENT ON TABLE user_quotas IS 'Tracks file upload quotas and limits for each user';
COMMENT ON COLUMN user_quotas.user_id IS 'Reference to auth.users.id';
COMMENT ON COLUMN user_quotas.quota_remaining IS 'Remaining upload quota in bytes';
COMMENT ON COLUMN user_quotas.max_file_size IS 'Maximum allowed file size in bytes';
COMMENT ON COLUMN user_quotas.total_uploaded IS 'Total bytes uploaded by user';
COMMENT ON COLUMN user_quotas.file_count IS 'Total number of files uploaded';
COMMENT ON FUNCTION decrement_user_quota IS 'Decrements user quota after successful upload';
COMMENT ON FUNCTION increment_user_quota IS 'Increments user quota after file deletion';

