-- Create validation metrics table in monitoring schema
-- Stores aggregated validation metrics for analysis and monitoring

-- Create table
CREATE TABLE IF NOT EXISTS monitoring.validation_metrics (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    total_events INT NOT NULL DEFAULT 0,
    passed_events INT NOT NULL DEFAULT 0,
    failed_events INT NOT NULL DEFAULT 0,
    pass_rate FLOAT NOT NULL DEFAULT 0.0,
    avg_validation_time_ms FLOAT NOT NULL DEFAULT 0.0,
    total_errors INT NOT NULL DEFAULT 0,
    total_warnings INT NOT NULL DEFAULT 0,
    flush_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_validation_metrics_event_type 
    ON monitoring.validation_metrics(event_type);

CREATE INDEX IF NOT EXISTS idx_validation_metrics_created_at 
    ON monitoring.validation_metrics(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_validation_metrics_flush_timestamp 
    ON monitoring.validation_metrics(flush_timestamp DESC);

-- Create composite index for time-series queries
CREATE INDEX IF NOT EXISTS idx_validation_metrics_event_time 
    ON monitoring.validation_metrics(event_type, created_at DESC);

-- Enable RLS
ALTER TABLE monitoring.validation_metrics ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for service role (allow all)
CREATE POLICY "Allow service role full access" 
    ON monitoring.validation_metrics
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Create RLS policy for authenticated users (read-only)
CREATE POLICY "Allow authenticated users to read metrics" 
    ON monitoring.validation_metrics
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION monitoring.update_validation_metrics_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS trigger_update_validation_metrics_timestamp 
    ON monitoring.validation_metrics;

CREATE TRIGGER trigger_update_validation_metrics_timestamp
    BEFORE UPDATE ON monitoring.validation_metrics
    FOR EACH ROW
    EXECUTE FUNCTION monitoring.update_validation_metrics_timestamp();

-- Create view for recent metrics (last 24 hours)
CREATE OR REPLACE VIEW monitoring.validation_metrics_recent AS
SELECT 
    event_type,
    total_events,
    passed_events,
    failed_events,
    pass_rate,
    avg_validation_time_ms,
    total_errors,
    total_warnings,
    created_at
FROM monitoring.validation_metrics
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- Create view for metrics summary by event type
CREATE OR REPLACE VIEW monitoring.validation_metrics_summary AS
SELECT 
    event_type,
    COUNT(*) as flush_count,
    SUM(total_events) as total_events,
    SUM(passed_events) as total_passed,
    SUM(failed_events) as total_failed,
    AVG(pass_rate) as avg_pass_rate,
    AVG(avg_validation_time_ms) as avg_validation_time,
    SUM(total_errors) as total_errors,
    SUM(total_warnings) as total_warnings,
    MAX(created_at) as last_flush
FROM monitoring.validation_metrics
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY event_type
ORDER BY total_events DESC;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON monitoring.validation_metrics TO service_role;
GRANT SELECT ON monitoring.validation_metrics_recent TO service_role;
GRANT SELECT ON monitoring.validation_metrics_summary TO service_role;

