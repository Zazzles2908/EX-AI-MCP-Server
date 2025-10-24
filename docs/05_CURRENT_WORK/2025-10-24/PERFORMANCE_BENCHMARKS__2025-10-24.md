# Performance Benchmarks & Targets
**Created:** 2025-10-24  
**Phase:** 0.2 - Performance Benchmark Definitions  
**Purpose:** Define performance targets for all 30 EXAI-WS MCP tools

---

## 📊 Benchmark Categories

### 1. Workflow Tools (Complex, Multi-Step)
**Tools:** debug, analyze, codereview, refactor, secaudit, precommit, testgen, thinkdeep, tracer, docgen, consensus, planner

**Performance Targets:**
- **Latency (Simple Operations):** < 2 seconds (single-step, low complexity)
- **Latency (Complex Operations):** < 5 seconds (multi-step, high complexity)
- **Memory Usage:** < 100 MB per operation
- **Success Rate:** ≥ 95% (excluding user errors)
- **Error Rate:** < 1% (system errors only)
- **Concurrent Operations:** Support 5 simultaneous operations

**Rationale:** Workflow tools involve AI model calls, multi-step processing, and complex analysis. Higher latency acceptable for comprehensive results.

---

### 2. Provider Tools (AI Model Integration)
**Tools:** chat, kimi_chat_with_files, kimi_chat_with_tools, glm_web_search, kimi_upload_files, kimi_manage_files

**Performance Targets:**
- **Latency (Including API):** < 3 seconds (p95)
- **Latency (Excluding API):** < 500 ms (MCP overhead only)
- **Memory Usage:** < 150 MB per operation
- **Success Rate:** ≥ 90% (accounting for API failures)
- **Error Rate:** < 5% (system errors, excluding API errors)
- **API Timeout:** 30 seconds (configurable)
- **Retry Logic:** 3 attempts with exponential backoff

**Rationale:** Provider tools depend on external AI APIs with variable latency. Must handle API failures gracefully.

---

### 3. Utility Tools (Fast, Lightweight)
**Tools:** activity, health, status, listmodels, version, provider_capabilities, self-check, glm_payload_preview, glm_upload_file

**Performance Targets:**
- **Latency:** < 1 second (p99)
- **Memory Usage:** < 50 MB per operation
- **Success Rate:** ≥ 99% (highly reliable)
- **Error Rate:** < 0.1% (system errors only)
- **Concurrent Operations:** Support 10+ simultaneous operations

**Rationale:** Utility tools are informational and should be near-instantaneous. Critical for system health monitoring.

---

## 🎯 System-Level Benchmarks

### WebSocket Layer
- **Connection Establishment:** < 100 ms
- **Message Routing:** < 50 ms (MCP Client → ws_server.py)
- **Protocol Processing:** < 30 ms (ws_server.py → server.py)
- **Ping/Pong Latency:** < 20 ms
- **Max Concurrent Connections:** 5 (single-user development environment)

### MCP Protocol Layer
- **Tool Discovery:** < 50 ms
- **Tool Schema Generation:** < 100 ms
- **Tool Invocation Overhead:** < 50 ms
- **Result Serialization:** < 30 ms

### Provider Layer
- **Provider Selection:** < 10 ms
- **Model Routing:** < 20 ms
- **Token Counting:** < 5 ms
- **Context Engineering:** < 50 ms

### Storage Layer (Supabase)
- **Database Query (Simple):** < 200 ms
- **Database Query (Complex):** < 500 ms
- **File Upload (1 MB):** < 2 seconds
- **File Download (1 MB):** < 1 second
- **Batch Insert (100 records):** < 1 second

---

## 📈 Latency Breakdown Targets

### Layer-by-Layer Analysis
For a typical workflow tool call (e.g., `debug_EXAI-WS`):

1. **MCP Client → WebSocket:** < 50 ms (network latency)
2. **WebSocket → ws_server.py:** < 30 ms (protocol processing)
3. **ws_server.py → server.py:** < 20 ms (internal routing)
4. **server.py → tools/:** < 50 ms (tool dispatch)
5. **tools → providers/:** < 20 ms (provider selection)
6. **providers → External APIs:** 1-3 seconds (AI model processing)
7. **Response Path (reverse):** < 150 ms (total return path)

**Total Target:** < 5 seconds (including AI API)

---

## 🔍 Measurement Methodology

### Metrics Collection
- **p50 (Median):** Typical user experience
- **p95:** Acceptable worst-case for most users
- **p99:** Worst-case scenario threshold
- **Max:** Absolute maximum observed

### Statistical Significance
- **Sample Size:** Minimum 10 runs per tool
- **Outlier Handling:** Remove top/bottom 5% for p95/p99
- **Confidence Interval:** 95% confidence level

### Test Conditions
- **Environment:** Docker container on Windows host
- **Load:** Single user, sequential operations
- **Network:** Localhost (minimal latency)
- **Database:** Supabase Pro (production tier)

---

## 🚨 Alert Thresholds

### Critical Alerts (Immediate Action Required)
- Latency > 2x target (e.g., workflow tool > 10s)
- Error rate > 10%
- Success rate < 80%
- Memory usage > 500 MB
- WebSocket disconnections > 3 per hour

### Warning Alerts (Investigation Needed)
- Latency > 1.5x target
- Error rate > 5%
- Success rate < 90%
- Memory usage > 200 MB
- WebSocket reconnections > 1 per hour

### Info Alerts (Monitoring)
- Latency > 1.2x target
- Error rate > 2%
- Success rate < 95%
- Memory usage > 150 MB

---

## 📊 Benchmark Validation Criteria

### Phase 0.3 Success Criteria
- ✅ All 30 tools measured with ≥10 samples each
- ✅ Baseline data stored in Supabase + JSON files
- ✅ p50, p95, p99, max calculated for each tool
- ✅ Layer-by-layer latency breakdown captured
- ✅ Memory usage profiled for each tool
- ✅ Success/failure rates documented
- ✅ Baseline report generated with visualizations

### Regression Detection
- **Latency Regression:** > 20% increase from baseline
- **Memory Regression:** > 30% increase from baseline
- **Success Rate Regression:** > 5% decrease from baseline

---

## 🎯 Tool-Specific Targets

### Workflow Tools (Detailed)
| Tool | Simple Latency | Complex Latency | Memory | Success Rate |
|------|---------------|-----------------|--------|--------------|
| debug | < 2s | < 5s | < 100 MB | ≥ 95% |
| analyze | < 2s | < 5s | < 100 MB | ≥ 95% |
| codereview | < 2s | < 5s | < 100 MB | ≥ 95% |
| refactor | < 2s | < 5s | < 100 MB | ≥ 95% |
| secaudit | < 2s | < 5s | < 100 MB | ≥ 95% |
| precommit | < 2s | < 5s | < 100 MB | ≥ 95% |
| testgen | < 2s | < 5s | < 100 MB | ≥ 95% |
| thinkdeep | < 2s | < 5s | < 100 MB | ≥ 95% |
| tracer | < 2s | < 5s | < 100 MB | ≥ 95% |
| docgen | < 2s | < 5s | < 100 MB | ≥ 95% |
| consensus | < 3s | < 8s | < 150 MB | ≥ 95% |
| planner | < 2s | < 5s | < 100 MB | ≥ 95% |

### Provider Tools (Detailed)
| Tool | Latency (p95) | Memory | Success Rate |
|------|---------------|--------|--------------|
| chat | < 3s | < 150 MB | ≥ 90% |
| kimi_chat_with_files | < 4s | < 150 MB | ≥ 90% |
| kimi_chat_with_tools | < 3s | < 150 MB | ≥ 90% |
| glm_web_search | < 5s | < 150 MB | ≥ 85% |
| kimi_upload_files | < 3s | < 100 MB | ≥ 95% |
| kimi_manage_files | < 2s | < 100 MB | ≥ 95% |

### Utility Tools (Detailed)
| Tool | Latency (p99) | Memory | Success Rate |
|------|---------------|--------|--------------|
| activity | < 500 ms | < 50 MB | ≥ 99% |
| health | < 500 ms | < 50 MB | ≥ 99% |
| status | < 500 ms | < 50 MB | ≥ 99% |
| listmodels | < 500 ms | < 50 MB | ≥ 99% |
| version | < 100 ms | < 30 MB | ≥ 99.9% |
| provider_capabilities | < 500 ms | < 50 MB | ≥ 99% |
| self-check | < 1s | < 50 MB | ≥ 99% |
| glm_payload_preview | < 200 ms | < 50 MB | ≥ 99% |
| glm_upload_file | < 2s | < 100 MB | ≥ 95% |

---

## 📝 Notes

- **Single-User Environment:** Benchmarks optimized for 1-5 concurrent users (development environment)
- **Production Scaling:** For production deployment, multiply concurrent operation targets by expected user count
- **AI Model Variability:** Provider tool latency heavily depends on AI model selection and prompt complexity
- **Network Conditions:** Localhost benchmarks; add network latency for remote deployments
- **Database Performance:** Supabase Pro tier; performance may vary with plan changes

---

**Next Steps:**
1. Implement baseline collection script (Phase 0.3)
2. Run 10+ samples for each of 30 tools
3. Store results in Supabase + JSON files
4. Generate baseline report with visualizations
5. Configure AI Auditor to monitor against these benchmarks

