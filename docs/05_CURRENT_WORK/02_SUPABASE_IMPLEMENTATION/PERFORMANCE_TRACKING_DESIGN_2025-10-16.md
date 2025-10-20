# Smart Performance Tracking System Design

**Created:** 2025-10-16  
**Status:** ✅ DESIGN COMPLETE - Ready for Implementation  
**EXAI Conversation:** `0a6d1ef3-1311-4bfd-8230-57cb8e1d09ff`  
**Model Used:** GLM-4.6 with web search (53.4s response time)  
**Supabase Database:** Personal AI (mxaazuhlqewmkweewyaz)

---

## 🎯 **DESIGN GOALS**

1. Track model response times by model+tool combination
2. Use statistical aggregation (avg, p50, p95, p99) instead of storing every call
3. Time-windowed data retention (hourly/daily aggregates)
4. Minimal storage overhead
5. Easy to query for performance insights
6. Integrate with existing Supabase infrastructure

---

## 📊 **DATABASE SCHEMA**

### **1. Reference Tables**

```sql
-- Models available in the system
CREATE TABLE models (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  provider TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tools available in the system
CREATE TABLE tools (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Model-Tool-Parameter combinations
CREATE TABLE model_tool_configs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_id UUID REFERENCES models(id),
  tool_id UUID REFERENCES tools(id),
  parameters JSONB NOT NULL DEFAULT '{}',
  parameter_hash TEXT GENERATED ALWAYS AS (md5(parameters::text)) STORED,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(model_id, tool_id, parameter_hash)
);
```

### **2. Time-Series Metrics Tables**

```sql
-- Hourly aggregated metrics
CREATE TABLE performance_metrics_hourly (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_tool_config_id UUID REFERENCES model_tool_configs(id),
  time_bucket TIMESTAMPTZ NOT NULL,
  call_count INTEGER NOT NULL DEFAULT 0,
  success_count INTEGER NOT NULL DEFAULT 0,
  error_count INTEGER NOT NULL DEFAULT 0,
  
  -- Response time metrics (in milliseconds)
  avg_response_time FLOAT NOT NULL,
  min_response_time FLOAT NOT NULL,
  max_response_time FLOAT NOT NULL,
  p50_response_time FLOAT NOT NULL,
  p95_response_time FLOAT NOT NULL,
  p99_response_time FLOAT NOT NULL,
  
  -- Token usage metrics
  avg_input_tokens FLOAT,
  avg_output_tokens FLOAT,
  total_input_tokens BIGINT,
  total_output_tokens BIGINT,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(model_tool_config_id, time_bucket)
);

-- Daily aggregated metrics (similar structure)
CREATE TABLE performance_metrics_daily (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_tool_config_id UUID REFERENCES model_tool_configs(id),
  time_bucket TIMESTAMPTZ NOT NULL,
  call_count INTEGER NOT NULL DEFAULT 0,
  success_count INTEGER NOT NULL DEFAULT 0,
  error_count INTEGER NOT NULL DEFAULT 0,
  avg_response_time FLOAT NOT NULL,
  min_response_time FLOAT NOT NULL,
  max_response_time FLOAT NOT NULL,
  p50_response_time FLOAT NOT NULL,
  p95_response_time FLOAT NOT NULL,
  p99_response_time FLOAT NOT NULL,
  avg_input_tokens FLOAT,
  avg_output_tokens FLOAT,
  total_input_tokens BIGINT,
  total_output_tokens BIGINT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(model_tool_config_id, time_bucket)
);

-- Create indexes for efficient querying
CREATE INDEX idx_performance_metrics_hourly_config_time ON performance_metrics_hourly(model_tool_config_id, time_bucket DESC);
CREATE INDEX idx_performance_metrics_daily_config_time ON performance_metrics_daily(model_tool_config_id, time_bucket DESC);
```

### **3. Raw Data Table (Short Retention)**

```sql
-- Raw performance data (kept for 7 days)
CREATE TABLE performance_metrics_raw (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_tool_config_id UUID REFERENCES model_tool_configs(id),
  call_timestamp TIMESTAMPTZ NOT NULL,
  response_time_ms FLOAT NOT NULL,
  input_tokens INTEGER,
  output_tokens INTEGER,
  success BOOLEAN NOT NULL,
  error_type TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for efficient aggregation jobs
CREATE INDEX idx_performance_metrics_raw_config_time ON performance_metrics_raw(model_tool_config_id, call_timestamp);
```

---

## ⏱️ **RETENTION POLICY**

| Data Type | Retention Period | Purpose |
|-----------|-----------------|---------|
| **Raw data** | 7 days | Detailed troubleshooting |
| **Hourly aggregates** | 90 days | Medium-term trend analysis |
| **Daily aggregates** | 2 years | Long-term capacity planning |
| **Weekly aggregates** | Indefinite | Historical patterns |

---

## 🔧 **PARAMETER HANDLING STRATEGY**

**Hybrid Approach:**
1. Hash only **performance-affecting parameters** (thinking_mode, use_websearch, streaming, max_tokens, temperature)
2. Store full parameter JSON in reference table for debugging
3. Group by parameter hash for performance tracking
4. Allow querying by specific parameters when needed

```javascript
// Function to identify performance-affecting parameters
function getPerformanceAffectingParameters(parameters) {
  const significantParams = {};
  
  const performanceAffectingParams = [
    'thinking_mode',
    'use_websearch',
    'streaming',
    'max_tokens',
    'temperature'
  ];
  
  performanceAffectingParams.forEach(param => {
    if (parameters[param] !== undefined) {
      significantParams[param] = parameters[param];
    }
  });
  
  return significantParams;
}
```

---

## 📈 **AGGREGATION STRATEGY**

**Automated Aggregation Function:**

```sql
CREATE OR REPLACE FUNCTION aggregate_performance_metrics()
RETURNS void AS $$
DECLARE
  current_hour TIMESTAMPTZ := date_trunc('hour', NOW());
BEGIN
  INSERT INTO performance_metrics_hourly (
    model_tool_config_id, time_bucket, call_count, success_count, error_count,
    avg_response_time, min_response_time, max_response_time,
    p50_response_time, p95_response_time, p99_response_time,
    avg_input_tokens, avg_output_tokens, total_input_tokens, total_output_tokens
  )
  SELECT
    model_tool_config_id, current_hour,
    COUNT(*),
    COUNT(*) FILTER (WHERE success = true),
    COUNT(*) FILTER (WHERE success = false),
    AVG(response_time_ms),
    MIN(response_time_ms),
    MAX(response_time_ms),
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_ms),
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms),
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms),
    AVG(input_tokens), AVG(output_tokens),
    SUM(input_tokens), SUM(output_tokens)
  FROM performance_metrics_raw
  WHERE call_timestamp >= current_hour AND call_timestamp < current_hour + INTERVAL '1 hour'
  GROUP BY model_tool_config_id
  ON CONFLICT (model_tool_config_id, time_bucket) DO UPDATE SET
    call_count = EXCLUDED.call_count,
    success_count = EXCLUDED.success_count,
    error_count = EXCLUDED.error_count,
    avg_response_time = EXCLUDED.avg_response_time,
    min_response_time = EXCLUDED.min_response_time,
    max_response_time = EXCLUDED.max_response_time,
    p50_response_time = EXCLUDED.p50_response_time,
    p95_response_time = EXCLUDED.p95_response_time,
    p99_response_time = EXCLUDED.p99_response_time,
    avg_input_tokens = EXCLUDED.avg_input_tokens,
    avg_output_tokens = EXCLUDED.avg_output_tokens,
    total_input_tokens = EXCLUDED.total_input_tokens,
    total_output_tokens = EXCLUDED.total_output_tokens;
END;
$$ LANGUAGE plpgsql;
```

**Automated Cleanup Function:**

```sql
CREATE OR REPLACE FUNCTION cleanup_old_performance_data()
RETURNS void AS $$
BEGIN
  DELETE FROM performance_metrics_raw WHERE call_timestamp < NOW() - INTERVAL '7 days';
  DELETE FROM performance_metrics_hourly WHERE time_bucket < NOW() - INTERVAL '90 days';
  DELETE FROM performance_metrics_daily WHERE time_bucket < NOW() - INTERVAL '2 years';
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup to run daily at 2 AM
SELECT cron.schedule(
  'cleanup-performance-data',
  '0 2 * * *',
  'SELECT cleanup_old_performance_data();'
);
```

---

## 🔍 **QUERY INTERFACE**

```sql
-- Get performance trends for a model-tool combination
CREATE OR REPLACE FUNCTION get_performance_trends(
  model_name TEXT,
  tool_name TEXT,
  start_time TIMESTAMPTZ,
  end_time TIMESTAMPTZ,
  granularity TEXT DEFAULT 'hourly'
)
RETURNS TABLE (
  time_bucket TIMESTAMPTZ,
  avg_response_time FLOAT,
  p95_response_time FLOAT,
  p99_response_time FLOAT,
  call_count INTEGER,
  success_rate FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    m.time_bucket, m.avg_response_time, m.p95_response_time, m.p99_response_time,
    m.call_count,
    CASE WHEN m.call_count > 0 THEN m.success_count::float / m.call_count ELSE 0 END AS success_rate
  FROM performance_metrics_hourly m
  JOIN model_tool_configs c ON m.model_tool_config_id = c.id
  JOIN models model ON c.model_id = model.id
  JOIN tools tool ON c.tool_id = tool.id
  WHERE model.name = model_name
    AND tool.name = tool_name
    AND m.time_bucket >= start_time
    AND m.time_bucket <= end_time
  ORDER BY m.time_bucket;
END;
$$ LANGUAGE plpgsql;
```

---

## 📊 **FIRST DATA POINT**

**GLM-4.6 Performance Tracking Design Call:**
- **Model:** glm-4.6
- **Tool:** chat
- **Parameters:** use_websearch=true
- **Response Time:** 53.4 seconds
- **Tokens:** ~4029 (estimated)
- **Success:** ✅ Yes
- **Timestamp:** 2025-10-16

---

## 🚀 **NEXT STEPS**

1. **Implement schema in Supabase** - Create tables and indexes
2. **Build data collection layer** - Integrate with EXAI tools
3. **Set up aggregation jobs** - Schedule hourly/daily aggregation
4. **Create query functions** - Implement performance trend queries
5. **Build dashboard** - Visualize performance metrics
6. **Test with real data** - Validate aggregation accuracy

---

**Status:** ✅ Design complete, ready for implementation

