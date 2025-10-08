# EX-AI MCP Server - Maintenance Runbook

**Last Updated:** 2025-10-07  
**Status:** ✅ ACTIVE  
**Purpose:** Operational procedures for maintaining the EX-AI MCP Server

---

## 🎯 Overview

This runbook provides step-by-step procedures for common maintenance tasks, troubleshooting, and system health checks for the EX-AI MCP Server.

---

## 📋 Daily Maintenance

### 1. Health Check

**Run daily to verify system health:**

```bash
# Check server status
python scripts/validate_timeout_hierarchy.py

# Run unit tests
python -m pytest tests/unit/ -v

# Check logs for errors
grep -i "error\|critical" logs/*.log | tail -20
```

**Expected results:**
- ✅ Timeout hierarchy validation passes
- ✅ All unit tests pass (70/70)
- ✅ No critical errors in logs

### 2. Log Review

**Check for issues:**
```bash
# Recent errors
tail -100 logs/mcp_server.log | grep ERROR

# Recent warnings
tail -100 logs/mcp_server.log | grep WARNING

# Timeout issues
grep -i "timeout" logs/*.log | tail -20
```

### 3. Disk Space Check

**Ensure adequate disk space:**
```bash
# Check log directory size
du -sh logs/

# Clean old logs (older than 7 days)
find logs/ -name "*.log" -mtime +7 -delete
```

---

## 🔧 Weekly Maintenance

### 1. Run Full Test Suite

```bash
# Run all validation tests
python tool_validation_suite/scripts/run_all_tests_simple.py

# Check pass rate (should be > 90%)
```

### 2. Update Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update critical packages
pip install --upgrade supabase httpx zhipuai

# Run tests after updates
python -m pytest tests/unit/ -v
```

### 3. Review Supabase Data

```bash
# Check test run count
# Via Supabase MCP or dashboard:
# SELECT COUNT(*) FROM test_runs WHERE run_timestamp > NOW() - INTERVAL '7 days';

# Check for failing tests
# SELECT tool_name, COUNT(*) as failures 
# FROM test_results 
# WHERE status = 'FAIL' AND created_at > NOW() - INTERVAL '7 days'
# GROUP BY tool_name;
```

---

## 🚨 Troubleshooting Procedures

### Issue: Server Won't Start

**Symptoms:**
- Server fails to start
- Import errors
- Port already in use

**Diagnosis:**
```bash
# Check if port is in use
netstat -an | grep 8080  # Windows
lsof -i :8080            # Linux/Mac

# Check for import errors
python -c "import src.server"

# Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); print(os.getenv('DEFAULT_MODEL'))"
```

**Solutions:**
1. Kill process using port: `taskkill /F /PID <pid>` (Windows) or `kill -9 <pid>` (Linux/Mac)
2. Fix import errors: Check Python path and dependencies
3. Verify .env file exists and has correct values

### Issue: Tests Timing Out

**Symptoms:**
- Tests hang and timeout
- No response from server
- Timeout errors in logs

**Diagnosis:**
```bash
# Validate timeout hierarchy
python scripts/validate_timeout_hierarchy.py

# Check current timeout values
grep TIMEOUT .env

# Check logs for timeout errors
grep -i "timeout" logs/*.log | tail -20
```

**Solutions:**
1. Increase `WORKFLOW_TOOL_TIMEOUT_SECS` in .env
2. Verify timeout hierarchy (daemon = 1.5x, shim = 2x, client = 2.5x)
3. Check network connectivity to API providers

### Issue: Supabase Not Tracking

**Symptoms:**
- No data in Supabase tables
- "Supabase tracking disabled" messages
- Tests run but no database records

**Diagnosis:**
```bash
# Check Supabase configuration
grep SUPABASE .env

# Test Supabase connection
python -c "
from tool_validation_suite.utils.supabase_client import get_supabase_client
client = get_supabase_client()
print(f'Enabled: {client.enabled if client else False}')
"
```

**Solutions:**
1. Set `SUPABASE_TRACKING_ENABLED=true` in .env
2. Set `SUPABASE_ACCESS_TOKEN` in .env
3. Install Supabase SDK: `pip install supabase`
4. See: `tool_validation_suite/docs/current/guides/SUPABASE_VERIFICATION_GUIDE.md`

### Issue: Model Configuration Errors

**Symptoms:**
- "Model not found" errors
- Wrong model being used
- API key errors

**Diagnosis:**
```bash
# Check model configuration
python -c "
from src.providers.kimi_config import SUPPORTED_MODELS as KIMI
from src.providers.glm_config import SUPPORTED_MODELS as GLM
print(f'Kimi models: {list(KIMI.keys())}')
print(f'GLM models: {list(GLM.keys())}')
"

# Check API keys
grep API_KEY .env | grep -v "^#"
```

**Solutions:**
1. Verify model name is correct (check `src/providers/kimi_config.py` or `glm_config.py`)
2. Verify API keys are set in .env
3. Check base URLs are correct (z.ai for GLM, moonshot.ai for Kimi)

---

## 🔄 Restart Procedures

### Graceful Restart

```bash
# 1. Stop server gracefully
# Send SIGTERM to allow cleanup
kill -TERM <pid>

# 2. Wait for shutdown (max 30 seconds)
sleep 5

# 3. Verify stopped
ps aux | grep server.py

# 4. Start server
python server.py
```

### Force Restart

```bash
# 1. Force kill
kill -9 <pid>  # Linux/Mac
taskkill /F /PID <pid>  # Windows

# 2. Clean up stale files
rm -f *.pid *.sock

# 3. Start server
python server.py
```

### Restart with Clean State

```bash
# 1. Stop server
kill -TERM <pid>

# 2. Clear caches
rm -rf tool_validation_suite/cache/*

# 3. Clear old logs
find logs/ -name "*.log" -mtime +1 -delete

# 4. Start server
python server.py
```

---

## 📊 Performance Monitoring

### Check Response Times

```bash
# Analyze logs for slow requests
grep "duration" logs/mcp_activity.log | awk '{print $NF}' | sort -n | tail -10
```

### Monitor Memory Usage

```bash
# Check process memory
ps aux | grep python | grep server

# Monitor over time
watch -n 5 'ps aux | grep python | grep server'
```

### Check API Rate Limits

```bash
# Check for rate limit errors
grep -i "rate limit\|429" logs/*.log

# Check API call frequency
grep "API call" logs/*.log | wc -l
```

---

## 🔐 Security Maintenance

### Rotate API Keys

**Procedure:**
1. Generate new API keys from provider dashboards
2. Update .env file with new keys
3. Restart server
4. Verify connectivity
5. Revoke old keys

### Review Access Logs

```bash
# Check for suspicious activity
grep -i "unauthorized\|forbidden\|401\|403" logs/*.log

# Check for unusual patterns
grep "API call" logs/*.log | awk '{print $1}' | sort | uniq -c | sort -rn
```

---

## 📦 Backup Procedures

### Backup Configuration

```bash
# Backup .env files
cp .env .env.backup.$(date +%Y%m%d)
cp tool_validation_suite/.env.testing .env.testing.backup.$(date +%Y%m%d)

# Backup configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
    .env \
    config.py \
    src/providers/*_config.py
```

### Backup Logs

```bash
# Archive old logs
tar -czf logs_archive_$(date +%Y%m%d).tar.gz logs/

# Move to archive directory
mv logs_archive_*.tar.gz archives/
```

### Backup Test Results

```bash
# Backup test results
cp -r tool_validation_suite/results tool_validation_suite/results.backup.$(date +%Y%m%d)
```

---

## 🔍 Investigation Tools

### Available Scripts

**Location:** `scripts/`

1. **validate_timeout_hierarchy.py** - Validate timeout configuration
2. **investigate_all_branches.py** - Analyze git branches
3. **investigate_unique_commits.py** - Find unique commits
4. **investigate_script_redundancy.py** - Find duplicate code

**Usage:**
```bash
# Validate timeouts
python scripts/validate_timeout_hierarchy.py

# Investigate branches
python scripts/investigate_all_branches.py

# Find unique commits
python scripts/investigate_unique_commits.py
```

---

## 📈 Metrics to Track

### System Health Metrics

- **Uptime:** Target > 99%
- **Response time:** Target < 5s for simple tools, < 60s for workflow tools
- **Error rate:** Target < 1%
- **Test pass rate:** Target > 90%

### Performance Metrics

- **API call latency:** Monitor p50, p95, p99
- **Memory usage:** Monitor for leaks
- **Disk usage:** Keep logs < 1GB
- **Cache hit rate:** Monitor Kimi context caching

### Business Metrics

- **Tests run per day:** Track usage
- **Supabase records:** Track data growth
- **Watcher quality scores:** Track AI observation quality
- **Cost per test:** Monitor API costs

---

## ✅ Maintenance Checklist

### Daily
- [ ] Check server status
- [ ] Review error logs
- [ ] Verify disk space

### Weekly
- [ ] Run full test suite
- [ ] Update dependencies
- [ ] Review Supabase data
- [ ] Check performance metrics

### Monthly
- [ ] Rotate API keys
- [ ] Archive old logs
- [ ] Review security logs
- [ ] Update documentation
- [ ] Backup configuration

### Quarterly
- [ ] Full system audit
- [ ] Performance optimization
- [ ] Dependency updates
- [ ] Documentation review

---

## 🆘 Emergency Contacts

**For critical issues:**
1. Check this runbook first
2. Review investigation documents in `tool_validation_suite/docs/current/investigations/`
3. Check troubleshooting guides
4. Escalate if unresolved

**Useful Resources:**
- Timeout Guide: `tool_validation_suite/docs/current/guides/TIMEOUT_CONFIGURATION_GUIDE.md`
- Supabase Guide: `tool_validation_suite/docs/current/guides/SUPABASE_VERIFICATION_GUIDE.md`
- Logging Guide: `tool_validation_suite/docs/current/guides/LOGGING_CONFIGURATION_GUIDE.md`
- Architecture: `tool_validation_suite/docs/current/ARCHITECTURE.md`

---

## ✅ Summary

**This runbook covers:**
- ✅ Daily, weekly, monthly maintenance procedures
- ✅ Common troubleshooting scenarios
- ✅ Restart procedures
- ✅ Performance monitoring
- ✅ Security maintenance
- ✅ Backup procedures
- ✅ Investigation tools
- ✅ Metrics to track

**For help:**
- Check relevant guides in `tool_validation_suite/docs/current/guides/`
- Review investigation documents for similar issues
- Use investigation scripts in `scripts/`

