-- Real-Time Latency Monitoring Queries
-- Created: 2025-10-25
-- Purpose: Monitor production performance metrics from latency tracking infrastructure

-- ============================================================================
-- QUERY 1: Hourly Semaphore Contention Analysis
-- ============================================================================
-- Shows average semaphore wait times by provider over the last hour
-- Use this to identify bottlenecks in real-time

SELECT 
  metadata->'latency_metrics'->>'provider_name' as provider,
  COUNT(*) as execution_count,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'latency_ms' AS FLOAT))::numeric, 2) as avg_total_latency_ms,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'global_sem_wait_ms' AS FLOAT))::numeric, 2) as avg_global_wait_ms,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'provider_sem_wait_ms' AS FLOAT))::numeric, 2) as avg_provider_wait_ms,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'processing_ms' AS FLOAT))::numeric, 2) as avg_processing_ms,
  ROUND(MAX(CAST(metadata->'latency_metrics'->>'latency_ms' AS FLOAT))::numeric, 2) as max_latency_ms,
  ROUND(MIN(CAST(metadata->'latency_metrics'->>'latency_ms' AS FLOAT))::numeric, 2) as min_latency_ms
FROM messages
WHERE role = 'assistant' 
  AND metadata->'latency_metrics' IS NOT NULL
  AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY metadata->'latency_metrics'->>'provider_name'
ORDER BY avg_global_wait_ms DESC;

-- ============================================================================
-- QUERY 2: Model Performance Comparison (Last 24 Hours)
-- ============================================================================
-- Compare performance across different models

SELECT 
  metadata->>'model_used' as model,
  metadata->'latency_metrics'->>'provider_name' as provider,
  COUNT(*) as execution_count,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'latency_ms' AS FLOAT))::numeric, 2) as avg_latency_ms,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'global_sem_wait_ms' AS FLOAT))::numeric, 2) as avg_global_wait_ms,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'provider_sem_wait_ms' AS FLOAT))::numeric, 2) as avg_provider_wait_ms,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'processing_ms' AS FLOAT))::numeric, 2) as avg_processing_ms,
  ROUND(AVG(CAST(metadata->>'tokens_in' AS FLOAT))::numeric, 2) as avg_tokens_in,
  ROUND(AVG(CAST(metadata->>'tokens_out' AS FLOAT))::numeric, 2) as avg_tokens_out
FROM messages
WHERE role = 'assistant' 
  AND metadata->'latency_metrics' IS NOT NULL
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY metadata->>'model_used', metadata->'latency_metrics'->>'provider_name'
ORDER BY avg_latency_ms ASC;

-- ============================================================================
-- QUERY 3: Bottleneck Detection (Last Hour)
-- ============================================================================
-- Identify requests where semaphore wait time exceeds processing time
-- This indicates contention is the bottleneck, not provider performance

SELECT 
  metadata->>'tool_name' as tool,
  metadata->'latency_metrics'->>'provider_name' as provider,
  COUNT(*) as bottleneck_count,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'global_sem_wait_ms' AS FLOAT))::numeric, 2) as avg_global_wait,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'provider_sem_wait_ms' AS FLOAT))::numeric, 2) as avg_provider_wait,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'processing_ms' AS FLOAT))::numeric, 2) as avg_processing
FROM messages
WHERE role = 'assistant' 
  AND metadata->'latency_metrics' IS NOT NULL
  AND created_at > NOW() - INTERVAL '1 hour'
  AND (
    CAST(metadata->'latency_metrics'->>'global_sem_wait_ms' AS FLOAT) > 
    CAST(metadata->'latency_metrics'->>'processing_ms' AS FLOAT)
    OR
    CAST(metadata->'latency_metrics'->>'provider_sem_wait_ms' AS FLOAT) > 
    CAST(metadata->'latency_metrics'->>'processing_ms' AS FLOAT)
  )
GROUP BY metadata->>'tool_name', metadata->'latency_metrics'->>'provider_name'
ORDER BY bottleneck_count DESC;

-- ============================================================================
-- QUERY 4: Alert Threshold Violations (Last Hour)
-- ============================================================================
-- Find requests exceeding alert thresholds:
-- - Global semaphore wait > 100ms
-- - Provider semaphore wait > 200ms
-- - Total latency > 500ms

SELECT 
  created_at,
  metadata->>'tool_name' as tool,
  metadata->'latency_metrics'->>'provider_name' as provider,
  ROUND(CAST(metadata->'latency_metrics'->>'latency_ms' AS FLOAT)::numeric, 2) as total_latency,
  ROUND(CAST(metadata->'latency_metrics'->>'global_sem_wait_ms' AS FLOAT)::numeric, 2) as global_wait,
  ROUND(CAST(metadata->'latency_metrics'->>'provider_sem_wait_ms' AS FLOAT)::numeric, 2) as provider_wait,
  CASE 
    WHEN CAST(metadata->'latency_metrics'->>'global_sem_wait_ms' AS FLOAT) > 100 THEN 'GLOBAL_SEM_CONTENTION'
    WHEN CAST(metadata->'latency_metrics'->>'provider_sem_wait_ms' AS FLOAT) > 200 THEN 'PROVIDER_SEM_CONTENTION'
    WHEN CAST(metadata->'latency_metrics'->>'latency_ms' AS FLOAT) > 500 THEN 'HIGH_LATENCY'
  END as alert_type
FROM messages
WHERE role = 'assistant' 
  AND metadata->'latency_metrics' IS NOT NULL
  AND created_at > NOW() - INTERVAL '1 hour'
  AND (
    CAST(metadata->'latency_metrics'->>'global_sem_wait_ms' AS FLOAT) > 100
    OR CAST(metadata->'latency_metrics'->>'provider_sem_wait_ms' AS FLOAT) > 200
    OR CAST(metadata->'latency_metrics'->>'latency_ms' AS FLOAT) > 500
  )
ORDER BY created_at DESC
LIMIT 50;

-- ============================================================================
-- QUERY 5: Performance Trends (Last 48 Hours, Hourly Buckets)
-- ============================================================================
-- Track performance trends over time to identify patterns

SELECT 
  DATE_TRUNC('hour', created_at) as hour,
  metadata->'latency_metrics'->>'provider_name' as provider,
  COUNT(*) as execution_count,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'latency_ms' AS FLOAT))::numeric, 2) as avg_latency_ms,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'global_sem_wait_ms' AS FLOAT))::numeric, 2) as avg_global_wait_ms,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'provider_sem_wait_ms' AS FLOAT))::numeric, 2) as avg_provider_wait_ms
FROM messages
WHERE role = 'assistant' 
  AND metadata->'latency_metrics' IS NOT NULL
  AND created_at > NOW() - INTERVAL '48 hours'
GROUP BY DATE_TRUNC('hour', created_at), metadata->'latency_metrics'->>'provider_name'
ORDER BY hour DESC, provider;

-- ============================================================================
-- QUERY 6: Percentile Analysis (Last 24 Hours)
-- ============================================================================
-- Calculate P50, P95, P99 latency for each provider

SELECT 
  metadata->'latency_metrics'->>'provider_name' as provider,
  COUNT(*) as execution_count,
  ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY CAST(metadata->'latency_metrics'->>'latency_ms' AS FLOAT))::numeric, 2) as p50_latency_ms,
  ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY CAST(metadata->'latency_metrics'->>'latency_ms' AS FLOAT))::numeric, 2) as p95_latency_ms,
  ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY CAST(metadata->'latency_metrics'->>'latency_ms' AS FLOAT))::numeric, 2) as p99_latency_ms,
  ROUND(AVG(CAST(metadata->'latency_metrics'->>'latency_ms' AS FLOAT))::numeric, 2) as avg_latency_ms
FROM messages
WHERE role = 'assistant' 
  AND metadata->'latency_metrics' IS NOT NULL
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY metadata->'latency_metrics'->>'provider_name'
ORDER BY p95_latency_ms ASC;

