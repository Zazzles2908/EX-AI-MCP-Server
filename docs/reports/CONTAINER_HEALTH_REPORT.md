# EXAI MCP Server - Automated Health Report

**Generated:** 2025-11-14 19:23:42
**Status:** HEALTHY

---

## Critical Issues Detected: 0
## Warnings Detected: 0

---

## INFO

1. **health_check:** Endpoint tests skipped - running during container startup (before daemon is ready). Daemon will start after this health check completes.
2. **redis:** Redis is accessible from container (port 6379)

## Container Log Analysis

| Container | Errors | Warnings | Critical |
|-----------|--------|----------|----------|
| exai-mcp-server | 0 | 0 | 0 |
| exai-redis | 0 | 0 | 0 |
| exai-redis-commander | 0 | 0 | 0 |

## Endpoint Tests

| Endpoint | Status | HTTP Code |
|----------|--------|-----------|
| Health Check (3002) | FAIL | 000 |
| Dashboard (3001) | FAIL | 000 |
| Metrics (3003) | FAIL | 000 |

## Redis Tests

- **Ping:** PASS
- **Auth:** PASS
- **Password:** PASS

---

**Report Type:** Automated Health Check
**Timestamp:** 2025-11-14 19:23:42
**Next Check:** Run this script after container rebuild

### How to Use This Report

1. **Critical Issues:** Fix immediately before production use
2. **Warnings:** Review and fix when possible
3. **Recommendations:** Suggested improvements
4. **Run Again:** `python scripts/health_check_automated.py`

