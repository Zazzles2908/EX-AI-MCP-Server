# Supabase Integration Verification Guide

**Last Updated:** 2025-10-07  
**Status:** ✅ ACTIVE  
**Purpose:** How to verify Supabase integration is working and tracking test results

---

## 🎯 Overview

The EX-AI MCP Server test validation suite uses **dual storage strategy**:
1. **JSON files** - Immediate debugging, git history, offline access
2. **Supabase** - Historical tracking, trend analysis, querying

This guide shows you how to verify Supabase integration is working correctly.

---

## ✅ Quick Verification Checklist

### 1. Check Environment Variables

**Required Variables:**
```bash
# In .env or tool_validation_suite/.env.testing
SUPABASE_PROJECT_ID=mxaazuhlqewmkweewyaz
SUPABASE_TRACKING_ENABLED=true  # Must be "true" to enable
SUPABASE_ACCESS_TOKEN=sbp_...   # Your Supabase access token
```

**Verify:**
```bash
# Check if variables are set
echo $SUPABASE_TRACKING_ENABLED
echo $SUPABASE_PROJECT_ID
```

### 2. Verify Supabase SDK Installed

```bash
# Check if Supabase Python SDK is installed
python -c "import supabase; print('✅ Supabase SDK installed')"

# If not installed:
pip install supabase
```

### 3. Run Tests with Supabase Tracking

```bash
# Run simple test runner (creates run_id automatically)
python tool_validation_suite/scripts/run_all_tests_simple.py

# Expected output:
# ✅ Created Supabase test run: 123
#    Branch: main, Commit: abc1234
```

### 4. Verify Data in Supabase

**Option A: Using Supabase MCP Tools (Recommended)**
```python
# Through Augment Agent or MCP client
list_organizations_supabase-mcp-full()
get_organization_supabase-mcp-full(id="your-org-id")
execute_sql_supabase-mcp-full(
    project_id="mxaazuhlqewmkweewyaz",
    query="SELECT COUNT(*) FROM test_results;"
)
```

**Option B: Using Supabase Dashboard**
1. Go to https://supabase.com/dashboard
2. Select project `mxaazuhlqewmkweewyaz`
3. Go to Table Editor
4. Check tables: `test_runs`, `test_results`, `watcher_insights`

**Expected Results:**
- `test_runs` table should have at least 1 row
- `test_results` table should have multiple rows (one per test)
- `watcher_insights` table should have rows if watcher is enabled

---

## 🔍 Detailed Verification Steps

### Step 1: Enable Supabase Tracking

**Edit `.env` or `tool_validation_suite/.env.testing`:**
```bash
# Change from false to true
SUPABASE_TRACKING_ENABLED=true
```

**Verify the change:**
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); print(f'Enabled: {os.getenv(\"SUPABASE_TRACKING_ENABLED\")}')"
```

### Step 2: Verify Supabase Client Initialization

**Test the client:**
```python
# Create test script: test_supabase_connection.py
import os
from dotenv import load_dotenv
load_dotenv('.env')

from tool_validation_suite.utils.supabase_client import get_supabase_client

client = get_supabase_client()

if client and client.enabled:
    print("✅ Supabase client initialized successfully")
    print(f"   Project ID: {client.project_id}")
    print(f"   Enabled: {client.enabled}")
else:
    print("❌ Supabase client not enabled")
    print(f"   Check SUPABASE_TRACKING_ENABLED: {os.getenv('SUPABASE_TRACKING_ENABLED')}")
    print(f"   Check SUPABASE_ACCESS_TOKEN: {'Set' if os.getenv('SUPABASE_ACCESS_TOKEN') else 'Not set'}")
```

**Run:**
```bash
python test_supabase_connection.py
```

### Step 3: Run Tests and Verify run_id Creation

**Run tests:**
```bash
python tool_validation_suite/scripts/run_all_tests_simple.py --category core
```

**Expected output:**
```
============================================================
EX-AI MCP Server - Simple Test Runner
============================================================
Start Time: 2025-10-07T10:30:00
Dry Run: False
============================================================

✅ Created Supabase test run: 42
   Branch: main, Commit: abc1234

Finding test scripts...
Found 15 test scripts (filtered to 5 core tests)
...
✅ Updated Supabase test run 42 with final results
```

**Key indicators:**
- ✅ "Created Supabase test run: X" appears
- ✅ "Updated Supabase test run X with final results" appears
- ✅ No errors about Supabase connection

### Step 4: Query Supabase for Results

**Using Python:**
```python
from tool_validation_suite.utils.supabase_client import get_supabase_client

client = get_supabase_client()

if client and client.enabled:
    # Query test runs
    result = client.client.table("test_runs").select("*").order("run_timestamp", desc=True).limit(5).execute()
    print(f"Recent test runs: {len(result.data)}")
    
    # Query test results
    result = client.client.table("test_results").select("*").limit(10).execute()
    print(f"Test results: {len(result.data)}")
```

**Using Supabase MCP (through Augment Agent):**
```sql
-- Get recent test runs
SELECT id, run_timestamp, branch_name, total_tests, tests_passed, pass_rate
FROM test_runs
ORDER BY run_timestamp DESC
LIMIT 5;

-- Get test results for latest run
SELECT tool_name, variation, provider, model, status, watcher_quality
FROM test_results
WHERE run_id = (SELECT id FROM test_runs ORDER BY run_timestamp DESC LIMIT 1);

-- Get watcher insights
SELECT quality_score, strengths, weaknesses, recommendations
FROM watcher_insights
WHERE test_result_id IN (
    SELECT id FROM test_results 
    WHERE run_id = (SELECT id FROM test_runs ORDER BY run_timestamp DESC LIMIT 1)
);
```

---

## 🚨 Troubleshooting

### Issue: "Supabase tracking disabled"

**Possible Causes:**
1. `SUPABASE_TRACKING_ENABLED=false` in .env
2. `SUPABASE_ACCESS_TOKEN` not set
3. Supabase SDK not installed

**Solutions:**
```bash
# 1. Enable tracking
echo "SUPABASE_TRACKING_ENABLED=true" >> .env

# 2. Set access token
echo "SUPABASE_ACCESS_TOKEN=sbp_your_token_here" >> .env

# 3. Install SDK
pip install supabase
```

### Issue: "Could not create Supabase test run"

**Possible Causes:**
1. Invalid access token
2. Network connectivity issues
3. Supabase project not accessible

**Solutions:**
```bash
# Test connection manually
python -c "
from supabase import create_client
client = create_client(
    'https://mxaazuhlqewmkweewyaz.supabase.co',
    'your_access_token_here'
)
result = client.table('test_runs').select('*').limit(1).execute()
print(f'✅ Connection successful: {len(result.data)} rows')
"
```

### Issue: "No data in Supabase tables"

**Possible Causes:**
1. Tests ran with `SUPABASE_TRACKING_ENABLED=false`
2. Tests ran before Supabase integration was activated
3. run_id not passed to TestRunner

**Solutions:**
1. Verify `SUPABASE_TRACKING_ENABLED=true` in .env
2. Re-run tests: `python tool_validation_suite/scripts/run_all_tests_simple.py`
3. Check logs for "Created Supabase test run" message

### Issue: "TEST_RUN_ID environment variable not set"

**Cause:** Individual test files not receiving run_id from parent script

**Solution:** Always run tests through `run_all_tests_simple.py`, not directly:
```bash
# ✅ Correct (creates run_id)
python tool_validation_suite/scripts/run_all_tests_simple.py

# ❌ Wrong (no run_id)
python tool_validation_suite/tests/core_tools/test_chat.py
```

---

## 📊 Verification Success Criteria

**Supabase integration is working correctly if:**

1. ✅ `SUPABASE_TRACKING_ENABLED=true` in .env
2. ✅ Supabase SDK installed (`pip list | grep supabase`)
3. ✅ Test runner creates run_id (check console output)
4. ✅ `test_runs` table has rows (`SELECT COUNT(*) FROM test_runs;`)
5. ✅ `test_results` table has rows (`SELECT COUNT(*) FROM test_results;`)
6. ✅ No errors in test runner output about Supabase
7. ✅ Final results updated in Supabase (check console output)

---

## 🔄 Integration Flow

**How Supabase tracking works:**

```
1. run_all_tests_simple.py starts
   ↓
2. Creates Supabase test run → returns run_id
   ↓
3. Sets TEST_RUN_ID environment variable
   ↓
4. For each test script:
   - Spawns subprocess with TEST_RUN_ID in env
   - Test script creates TestRunner(run_id=TEST_RUN_ID)
   - TestRunner inserts test_result into Supabase
   - Watcher inserts watcher_insight into Supabase
   ↓
5. After all tests complete:
   - Updates test run with final statistics
   - Saves results to JSON file (dual storage)
```

---

## 📝 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_PROJECT_ID` | Yes | `mxaazuhlqewmkweewyaz` | Supabase project ID |
| `SUPABASE_TRACKING_ENABLED` | Yes | `false` | Enable/disable Supabase tracking |
| `SUPABASE_ACCESS_TOKEN` | Yes | None | Supabase access token (service role key) |
| `TEST_RUN_ID` | Auto | None | Set automatically by test runner |

---

## 🎯 Next Steps

**After verifying Supabase is working:**

1. **Query historical data** - Analyze trends over time
2. **Create dashboards** - Visualize test results
3. **Set up alerts** - Notify on test failures
4. **Track watcher quality** - Monitor AI observation quality
5. **Identify patterns** - Find recurring issues

**Useful queries:**
```sql
-- Pass rate trend over time
SELECT DATE(run_timestamp) as date, AVG(pass_rate) as avg_pass_rate
FROM test_runs
GROUP BY DATE(run_timestamp)
ORDER BY date DESC;

-- Most failing tools
SELECT tool_name, COUNT(*) as failures
FROM test_results
WHERE status = 'FAIL'
GROUP BY tool_name
ORDER BY failures DESC;

-- Watcher quality distribution
SELECT quality_score, COUNT(*) as count
FROM watcher_insights
GROUP BY quality_score
ORDER BY quality_score DESC;
```

---

## ✅ Summary

**Supabase integration provides:**
- ✅ Historical tracking of all test runs
- ✅ Trend analysis and pattern detection
- ✅ Watcher insights storage and querying
- ✅ Issue tracking and resolution monitoring
- ✅ Dual storage (JSON + DB) for reliability

**To verify it's working:**
1. Enable tracking in .env
2. Run tests through run_all_tests_simple.py
3. Check console for "Created Supabase test run" message
4. Query Supabase tables for data

**For help:**
- Check troubleshooting section above
- Review `tool_validation_suite/docs/current/integrations/SUPABASE_INTEGRATION_COMPLETE.md`
- Check logs in `tool_validation_suite/results/latest/`

