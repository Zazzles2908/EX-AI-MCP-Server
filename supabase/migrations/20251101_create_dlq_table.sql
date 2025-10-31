-- Dead Letter Queue Table for Failed Metrics Operations
-- Phase 2.4.6: MetricsPersister Resilience
-- Date: 2025-11-01

-- Create DLQ table in monitoring schema
CREATE TABLE IF NOT EXISTS monitoring.dead_letter_queue (
    id BIGSERIAL PRIMARY KEY,
    original_payload JSONB NOT NULL,
    failure_reason TEXT,
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_retry_at TIMESTAMP WITH TIME ZONE,
    recovered_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'retrying', 'recovered', 'failed')),
    
    -- Indexes for common queries
    CONSTRAINT dlq_retry_limit CHECK (retry_count <= max_retries)
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_dlq_status ON monitoring.dead_letter_queue(status);
CREATE INDEX IF NOT EXISTS idx_dlq_created_at ON monitoring.dead_letter_queue(created_at);
CREATE INDEX IF NOT EXISTS idx_dlq_status_created ON monitoring.dead_letter_queue(status, created_at);
CREATE INDEX IF NOT EXISTS idx_dlq_pending_retry ON monitoring.dead_letter_queue(status, retry_count) 
    WHERE status = 'pending' AND retry_count < max_retries;

-- Create function to increment retry count
CREATE OR REPLACE FUNCTION monitoring.increment_retry_count(item_id BIGINT)
RETURNS INT AS $$
DECLARE
    new_count INT;
BEGIN
    UPDATE monitoring.dead_letter_queue
    SET retry_count = retry_count + 1,
        last_retry_at = NOW(),
        status = CASE 
            WHEN retry_count + 1 >= max_retries THEN 'failed'
            ELSE 'retrying'
        END
    WHERE id = item_id;
    
    SELECT retry_count INTO new_count FROM monitoring.dead_letter_queue WHERE id = item_id;
    RETURN new_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to get DLQ statistics
CREATE OR REPLACE FUNCTION monitoring.get_dlq_stats()
RETURNS TABLE (
    total_pending INT,
    total_recovered INT,
    total_failed INT,
    avg_retry_count NUMERIC,
    oldest_pending_age_hours INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) FILTER (WHERE status = 'pending')::INT as total_pending,
        COUNT(*) FILTER (WHERE status = 'recovered')::INT as total_recovered,
        COUNT(*) FILTER (WHERE status = 'failed')::INT as total_failed,
        ROUND(AVG(retry_count), 2)::NUMERIC as avg_retry_count,
        EXTRACT(EPOCH FROM (NOW() - MIN(created_at)))::INT / 3600 as oldest_pending_age_hours
    FROM monitoring.dead_letter_queue;
END;
$$ LANGUAGE plpgsql;

-- Create view for pending items ready for retry
CREATE OR REPLACE VIEW monitoring.dlq_pending_retry AS
SELECT 
    id,
    original_payload,
    failure_reason,
    retry_count,
    max_retries,
    created_at,
    last_retry_at,
    EXTRACT(EPOCH FROM (NOW() - created_at))::INT as age_seconds
FROM monitoring.dead_letter_queue
WHERE status = 'pending' 
  AND retry_count < max_retries
ORDER BY created_at ASC;

-- Create view for DLQ summary
CREATE OR REPLACE VIEW monitoring.dlq_summary AS
SELECT 
    status,
    COUNT(*) as count,
    MIN(created_at) as oldest_item,
    MAX(created_at) as newest_item,
    ROUND(AVG(retry_count), 2) as avg_retries
FROM monitoring.dead_letter_queue
GROUP BY status;

-- Enable RLS (Row Level Security) if needed
ALTER TABLE monitoring.dead_letter_queue ENABLE ROW LEVEL SECURITY;

-- Create policy for service role (allow all operations)
CREATE POLICY "Allow service role full access" ON monitoring.dead_letter_queue
    FOR ALL USING (true) WITH CHECK (true);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON monitoring.dead_letter_queue TO authenticated;
GRANT SELECT ON monitoring.dlq_pending_retry TO authenticated;
GRANT SELECT ON monitoring.dlq_summary TO authenticated;
GRANT EXECUTE ON FUNCTION monitoring.increment_retry_count TO authenticated;
GRANT EXECUTE ON FUNCTION monitoring.get_dlq_stats TO authenticated;

-- Add comment for documentation
COMMENT ON TABLE monitoring.dead_letter_queue IS 'Dead Letter Queue for storing failed metrics operations with retry tracking';
COMMENT ON COLUMN monitoring.dead_letter_queue.original_payload IS 'Original operation payload that failed';
COMMENT ON COLUMN monitoring.dead_letter_queue.failure_reason IS 'Reason why the operation failed';
COMMENT ON COLUMN monitoring.dead_letter_queue.retry_count IS 'Number of retry attempts made';
COMMENT ON COLUMN monitoring.dead_letter_queue.max_retries IS 'Maximum number of retries allowed';
COMMENT ON COLUMN monitoring.dead_letter_queue.status IS 'Current status: pending, retrying, recovered, or failed';

