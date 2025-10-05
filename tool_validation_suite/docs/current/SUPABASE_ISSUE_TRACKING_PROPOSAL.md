# Supabase Issue Tracking System - Proposal

**Date:** 2025-10-06  
**Purpose:** Proposal for using Supabase to track test validation suite issues and results  
**Status:** DRAFT

---

## 🎯 Problem Statement

Currently, issue tracking for the test validation suite is done through:
- Markdown files (ISSUES_CHECKLIST.md, PHASE_*_COMPLETE.md)
- JSON observation files (watcher_observations/*.json)
- Manual analysis and documentation

**Limitations:**
- No historical tracking of issue resolution
- Difficult to query and analyze trends
- Manual effort to correlate issues across test runs
- No automated reporting or dashboards
- Hard to track which issues recur vs. are truly fixed

---

## 💡 Proposed Solution

Create dedicated Supabase tables to track:
1. **Test runs** - Each full test suite execution
2. **Test results** - Individual test outcomes
3. **Issues** - Identified problems with status tracking
4. **Watcher observations** - Structured watcher analysis
5. **Performance metrics** - Historical performance data

---

## 📊 Proposed Schema

### Table 1: `test_runs`
Tracks each execution of the test validation suite.

```sql
CREATE TABLE test_runs (
  id BIGSERIAL PRIMARY KEY,
  run_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  branch_name TEXT NOT NULL,
  commit_hash TEXT,
  watcher_model TEXT NOT NULL, -- e.g., "glm-4.5-air"
  total_tests INTEGER NOT NULL,
  tests_passed INTEGER NOT NULL,
  tests_failed INTEGER NOT NULL,
  tests_skipped INTEGER NOT NULL,
  pass_rate NUMERIC(5,2), -- e.g., 85.50
  avg_watcher_quality NUMERIC(4,2), -- e.g., 7.25
  total_duration_secs INTEGER,
  total_cost_usd NUMERIC(10,4),
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_test_runs_timestamp ON test_runs(run_timestamp DESC);
CREATE INDEX idx_test_runs_branch ON test_runs(branch_name);
```

### Table 2: `test_results`
Individual test outcomes for each run.

```sql
CREATE TABLE test_results (
  id BIGSERIAL PRIMARY KEY,
  run_id BIGINT NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE,
  tool_name TEXT NOT NULL,
  variation TEXT NOT NULL, -- e.g., "basic_glm", "basic_kimi"
  provider TEXT NOT NULL, -- "glm" or "kimi"
  model TEXT NOT NULL, -- e.g., "glm-4.5-air"
  status TEXT NOT NULL, -- "PASS", "FAIL", "SKIP", "ERROR"
  execution_status TEXT, -- e.g., "success", "consensus_failed"
  duration_secs NUMERIC(10,3),
  memory_mb INTEGER,
  cpu_percent NUMERIC(5,2),
  tokens_total INTEGER,
  cost_usd NUMERIC(10,6),
  watcher_quality INTEGER, -- 1-10
  watcher_observations JSONB, -- Full watcher observation
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_test_results_run ON test_results(run_id);
CREATE INDEX idx_test_results_tool ON test_results(tool_name);
CREATE INDEX idx_test_results_status ON test_results(status);
CREATE INDEX idx_test_results_watcher_quality ON test_results(watcher_quality);
```

### Table 3: `issues`
Tracks identified issues with resolution status.

```sql
CREATE TABLE issues (
  id BIGSERIAL PRIMARY KEY,
  issue_code TEXT NOT NULL UNIQUE, -- e.g., "PHASE2-HIGH-001"
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL, -- "production" or "test_infrastructure"
  priority TEXT NOT NULL, -- "CRITICAL", "HIGH", "MEDIUM", "LOW"
  status TEXT NOT NULL DEFAULT 'OPEN', -- "OPEN", "IN_PROGRESS", "RESOLVED", "WONT_FIX"
  root_cause TEXT,
  resolution TEXT,
  affected_tools TEXT[], -- Array of tool names
  first_detected_run_id BIGINT REFERENCES test_runs(id),
  resolved_run_id BIGINT REFERENCES test_runs(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_issues_status ON issues(status);
CREATE INDEX idx_issues_priority ON issues(priority);
CREATE INDEX idx_issues_category ON issues(category);
```

### Table 4: `issue_occurrences`
Tracks when issues appear in test runs.

```sql
CREATE TABLE issue_occurrences (
  id BIGSERIAL PRIMARY KEY,
  issue_id BIGINT NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  run_id BIGINT NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE,
  test_result_id BIGINT REFERENCES test_results(id) ON DELETE CASCADE,
  severity TEXT, -- How severe was this occurrence
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(issue_id, run_id, test_result_id)
);

CREATE INDEX idx_issue_occurrences_issue ON issue_occurrences(issue_id);
CREATE INDEX idx_issue_occurrences_run ON issue_occurrences(run_id);
```

### Table 5: `watcher_insights`
Structured watcher observations for analysis.

```sql
CREATE TABLE watcher_insights (
  id BIGSERIAL PRIMARY KEY,
  test_result_id BIGINT NOT NULL REFERENCES test_results(id) ON DELETE CASCADE,
  quality_score INTEGER NOT NULL CHECK (quality_score BETWEEN 1 AND 10),
  strengths TEXT[],
  weaknesses TEXT[],
  anomalies TEXT[],
  recommendations TEXT[],
  confidence_level TEXT, -- "high", "medium", "low"
  raw_observation JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_watcher_insights_test_result ON watcher_insights(test_result_id);
CREATE INDEX idx_watcher_insights_quality ON watcher_insights(quality_score);
```

---

## 🔄 Integration Points

### 1. Test Runner Integration
Update `tool_validation_suite/utils/test_runner.py` to:
- Create `test_runs` record at start
- Insert `test_results` after each test
- Insert `watcher_insights` from watcher observations
- Update `test_runs` with final statistics

### 2. Issue Detection
Create `tool_validation_suite/utils/issue_detector.py` to:
- Analyze test results for known issue patterns
- Create/update `issues` records
- Track `issue_occurrences`
- Flag recurring vs. new issues

### 3. Reporting
Create `tool_validation_suite/utils/supabase_reporter.py` to:
- Generate trend reports
- Compare runs over time
- Identify regression patterns
- Export data for analysis

---

## 📈 Benefits

### 1. Historical Tracking
- Track test pass rates over time
- Identify trends and regressions
- Measure impact of fixes

### 2. Automated Analysis
- Query issues by status, priority, category
- Find recurring issues automatically
- Correlate issues across test runs

### 3. Better Reporting
- Generate dashboards in Supabase
- Export data for visualization
- Share results with team

### 4. Issue Lifecycle Management
- Track from detection to resolution
- Verify fixes don't regress
- Document root causes and solutions

### 5. Performance Monitoring
- Track performance metrics over time
- Identify performance regressions
- Optimize slow tests

---

## 🚀 Implementation Plan

### Phase 1: Schema Setup (30 minutes) ✅ CURRENT
1. Create all tables in Supabase
2. Set up indexes for performance
3. Test table creation

### Phase 2: Supabase Client Utility (30 minutes)
1. Create `tool_validation_suite/utils/supabase_client.py`
2. Implement connection management
3. Add helper methods for CRUD operations
4. Test connection

### Phase 3: Watcher Integration (1-2 hours) - PRIORITY
1. Update `glm_watcher.py` to save observations to Supabase
2. Parse watcher observations into structured format
3. Insert into `watcher_insights` table
4. Maintain backward compatibility (still save JSON files)
5. **Key Feature:** Watcher can query historical observations for context

### Phase 4: Test Runner Integration (1-2 hours)
1. Update `test_runner.py` to create `test_runs` record at start
2. Insert `test_results` after each test
3. Link watcher insights to test results
4. Update `test_runs` with final statistics
5. Maintain backward compatibility (still save JSON files)

### Phase 5: Issue Tracking (2-3 hours)
1. Create `issue_detector.py`
2. Define issue detection patterns
3. Implement automatic issue creation/updating
4. Track issue occurrences
5. Backfill existing issues from ISSUES_CHECKLIST.md

### Phase 6: Reporting (1-2 hours)
1. Create `supabase_reporter.py`
2. Implement trend analysis queries
3. Generate comparison reports
4. Create export functionality

**Total Estimated Time:** 6-10 hours

---

## 🔄 Dual Storage Strategy

**Key Design Decision:** Maintain both JSON files AND Supabase storage

### JSON Files (Existing)
- **Purpose:** Immediate debugging, git history, offline access
- **Location:** `tool_validation_suite/results/latest/`
- **Format:** Individual JSON files per test/observation
- **Retention:** Latest run + historical archives

### Supabase Database (New)
- **Purpose:** Historical tracking, trend analysis, querying
- **Location:** Supabase cloud database
- **Format:** Structured relational data
- **Retention:** All runs (with optional cleanup policy)

### Benefits of Dual Storage
1. **Backward Compatibility:** Existing tools continue to work
2. **Debugging:** JSON files for immediate inspection
3. **Analysis:** Supabase for historical trends
4. **Reliability:** Fallback if Supabase unavailable
5. **Git History:** JSON files tracked in version control

---

## 📝 Example Queries

### Get latest test run summary
```sql
SELECT 
  run_timestamp,
  branch_name,
  total_tests,
  pass_rate,
  avg_watcher_quality,
  total_cost_usd
FROM test_runs
ORDER BY run_timestamp DESC
LIMIT 1;
```

### Find failing tests
```sql
SELECT 
  tr.tool_name,
  tr.variation,
  tr.status,
  tr.error_message,
  tr.watcher_quality
FROM test_results tr
JOIN test_runs r ON tr.run_id = r.id
WHERE r.run_timestamp = (SELECT MAX(run_timestamp) FROM test_runs)
  AND tr.status = 'FAIL'
ORDER BY tr.watcher_quality ASC;
```

### Track issue resolution
```sql
SELECT 
  i.issue_code,
  i.title,
  i.status,
  i.created_at,
  i.resolved_at,
  COUNT(io.id) as occurrence_count
FROM issues i
LEFT JOIN issue_occurrences io ON i.id = io.issue_id
GROUP BY i.id
ORDER BY i.priority, i.created_at DESC;
```

### Compare test runs
```sql
SELECT 
  run_timestamp,
  pass_rate,
  avg_watcher_quality,
  total_cost_usd,
  LAG(pass_rate) OVER (ORDER BY run_timestamp) as prev_pass_rate,
  pass_rate - LAG(pass_rate) OVER (ORDER BY run_timestamp) as pass_rate_change
FROM test_runs
ORDER BY run_timestamp DESC
LIMIT 10;
```

---

## ⚠️ Considerations

### 1. Data Volume
- Each test run generates ~60 test_results records
- Watcher observations can be large (JSON)
- Consider data retention policy (e.g., keep last 100 runs)

### 2. Performance
- Indexes on frequently queried columns
- Consider partitioning for large datasets
- Batch inserts for efficiency

### 3. Security
- RLS policies if multi-user
- API key management
- Read-only access for reporting

### 4. Migration
- Import historical data from JSON files
- Backfill issues from ISSUES_CHECKLIST.md
- Preserve existing markdown documentation

---

## 🎯 Next Steps

1. **Review proposal** - Get feedback on schema and approach
2. **Create tables** - Set up Supabase schema
3. **Implement basic integration** - Start with test_runs and test_results
4. **Test with one run** - Validate data insertion
5. **Expand integration** - Add watcher insights and issue tracking
6. **Create reporting** - Build analysis queries and reports

---

**End of Proposal**

