# Architecture - Tool Validation Suite

**Purpose:** Comprehensive explanation of how the testing system works  
**Audience:** Developers, next agents, technical users  
**Last Updated:** 2025-10-05

---

## 🏗️ SYSTEM OVERVIEW

The Tool Validation Suite is a **completely independent testing ground** designed to validate all 30 tools in the EX-AI MCP Server with real-world scenarios.

### Key Design Principles

1. **Independence** - Separate from main codebase to avoid clutter
2. **Real-World Testing** - Uses real API calls, not mocks
3. **Comprehensive Coverage** - Tests all tools with 12 variations each
4. **Meta-Validation** - GLM-4.5-Flash observes and validates tests
5. **Result Tracking** - Stores all results for historical analysis
6. **Cost Awareness** - Tracks and limits API costs

---

## 📊 ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                     TEST ORCHESTRATION LAYER                     │
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │ Test Runner  │─────▶│   Test       │─────▶│   Result     │  │
│  │              │      │   Executor   │      │   Collector  │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                      │                      │          │
└─────────┼──────────────────────┼──────────────────────┼──────────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TESTING COMPONENTS                          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   API        │  │ Conversation │  │    File      │          │
│  │   Client     │  │   Tracker    │  │  Uploader    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Response    │  │ Performance  │  │     Cost     │          │
│  │  Validator   │  │   Monitor    │  │   Tracker    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                         │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Kimi API    │  │   GLM API    │  │ GLM Watcher  │          │
│  │  (Testing)   │  │  (Testing)   │  │ (Observer)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                   │                  │
│         ▼                 ▼                   ▼                  │
│  Real API Calls    Real API Calls    Independent Validation     │
└─────────────────────────────────────────────────────────────────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RESULT STORAGE                             │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Test       │  │   Watcher    │  │   Reports    │          │
│  │   Results    │  │ Observations │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 TEST EXECUTION FLOW

### 1. **Initialization Phase**

```
1. Load .env.testing configuration
2. Validate API keys
3. Create result directories
4. Initialize GLM Watcher
5. Load test configuration
6. Prepare test fixtures
```

### 2. **Test Execution Phase**

For each tool (30 tools):
```
For each variation (12 variations):
    1. Prepare test input
    2. Execute tool with real API call
    3. Monitor performance (CPU, memory, time)
    4. Track API costs
    5. Validate response
    6. Send to GLM Watcher for observation
    7. Collect results
    8. Save logs and API responses
```

### 3. **Observation Phase (GLM Watcher)**

For each test execution:
```
1. Receive test context (tool, input, output)
2. Analyze with GLM-4.5-Flash
3. Validate response quality
4. Detect anomalies
5. Provide suggestions
6. Save observations
```

### 4. **Result Aggregation Phase**

```
1. Collect all test results
2. Aggregate statistics
3. Calculate pass/fail rates
4. Summarize costs
5. Compile watcher observations
6. Generate reports
```

---

## 🔍 GLM WATCHER - INDEPENDENT OBSERVER

### Purpose

The GLM Watcher is an **independent validation layer** that observes every test execution and provides meta-analysis.

### Why Separate API Key?

- **Independence:** Ensures watcher is truly independent from tools being tested
- **Isolation:** Prevents watcher from affecting test results
- **Accountability:** Separate billing for observation vs testing
- **Reliability:** Watcher continues even if main GLM key fails

### What Does the Watcher Do?

For each test, the watcher:

1. **Receives Test Context:**
   - Tool name
   - Input parameters
   - Expected behavior
   - Actual output
   - Performance metrics

2. **Analyzes Quality:**
   - Response correctness
   - Response completeness
   - Response relevance
   - Error handling quality

3. **Detects Anomalies:**
   - Unexpected behavior
   - Performance issues
   - Cost anomalies
   - Pattern deviations

4. **Provides Suggestions:**
   - Improvement recommendations
   - Alternative approaches
   - Optimization opportunities

5. **Generates Observations:**
   - Saved to `results/latest/watcher_observations/`
   - Included in final reports
   - Used for meta-analysis

### Watcher Prompt Template

```python
WATCHER_PROMPT = """
You are an independent test observer analyzing a tool execution.

Tool: {tool_name}
Variation: {variation_name}
Input: {input_data}
Expected: {expected_behavior}
Actual Output: {actual_output}
Performance: {performance_metrics}
Status: {test_status}

Analyze this test execution and provide:
1. Quality assessment (1-10)
2. Correctness validation
3. Anomaly detection
4. Suggestions for improvement
5. Overall confidence in result

Be objective and critical. Your analysis helps validate the testing process.
"""
```

### Watcher Output Format

```json
{
  "tool": "chat",
  "variation": "basic_functionality",
  "timestamp": "2025-10-05T10:30:00Z",
  "quality_score": 9,
  "correctness": "PASS",
  "anomalies": [],
  "suggestions": [
    "Response time could be improved",
    "Consider adding more context"
  ],
  "confidence": 0.95,
  "observations": "Tool performed as expected..."
}
```

---

## 🧩 CORE COMPONENTS

### 1. **Test Runner** (`utils/test_runner.py`)

**Responsibilities:**
- Orchestrate test execution
- Manage test queue
- Handle retries
- Enforce timeouts
- Track progress

**Key Methods:**
```python
class TestRunner:
    def run_all_tests()
    def run_tool_tests(tool_name)
    def run_variation(tool, variation)
    def handle_failure(test, error)
    def enforce_cost_limits()
```

### 2. **API Client** (`utils/api_client.py`)

**Responsibilities:**
- Make API calls to Kimi/GLM
- Handle authentication
- Manage rate limiting
- Track costs
- Save request/response

**Key Methods:**
```python
class APIClient:
    def call_kimi(model, messages, **kwargs)
    def call_glm(model, messages, **kwargs)
    def upload_file_kimi(file_path)
    def upload_file_glm(file_path)
    def track_cost(provider, tokens)
```

### 3. **Conversation Tracker** (`utils/conversation_tracker.py`)

**Responsibilities:**
- Track conversation IDs
- Manage conversation state
- Ensure platform isolation
- Cache conversations
- Clean up expired conversations

**Key Methods:**
```python
class ConversationTracker:
    def create_conversation(provider)
    def get_conversation(conversation_id)
    def add_message(conversation_id, message)
    def is_valid_for_provider(conversation_id, provider)
    def cleanup_expired()
```

### 4. **GLM Watcher** (`utils/glm_watcher.py`)

**Responsibilities:**
- Observe test executions
- Analyze results
- Detect anomalies
- Provide suggestions
- Save observations

**Key Methods:**
```python
class GLMWatcher:
    def observe_test(test_context)
    def analyze_quality(output)
    def detect_anomalies(metrics)
    def generate_suggestions(analysis)
    def save_observation(observation)
```

### 5. **Result Collector** (`utils/result_collector.py`)

**Responsibilities:**
- Collect test results
- Aggregate statistics
- Calculate metrics
- Generate summaries
- Save to files

**Key Methods:**
```python
class ResultCollector:
    def add_result(test_result)
    def get_summary()
    def calculate_pass_rate()
    def get_cost_summary()
    def save_results()
```

---

## 📁 DATA FLOW

### Input Data Flow

```
Test Configuration (config/test_config.json)
    ↓
Test Fixtures (fixtures/sample_prompts/)
    ↓
API Client (utils/api_client.py)
    ↓
Kimi/GLM APIs
    ↓
Response Validator (utils/response_validator.py)
    ↓
GLM Watcher (utils/glm_watcher.py)
    ↓
Result Collector (utils/result_collector.py)
```

### Output Data Flow

```
Test Results
    ↓
results/latest/detailed_results.json
    ↓
Report Generator (utils/report_generator.py)
    ↓
results/reports/VALIDATION_REPORT.md
```

---

## 🔐 SECURITY & ISOLATION

### API Key Isolation

- **Kimi Key:** Used only for Kimi tool testing
- **GLM Key:** Used only for GLM tool testing
- **Watcher Key:** Used only for observation (separate account)

### Data Isolation

- **Conversation IDs:** Platform-specific, cannot cross platforms
- **File Uploads:** Stored separately for Kimi and GLM
- **Cache:** Separate cache directories for each provider

### Cost Protection

- **Per-Test Limit:** $0.50 USD maximum
- **Total Limit:** $10.00 USD maximum
- **Alert Threshold:** $5.00 USD
- **Auto-Stop:** Stops if limits exceeded

---

## 📊 PERFORMANCE MONITORING

### Metrics Tracked

1. **Response Time:** Time from request to response
2. **Memory Usage:** Peak memory during test
3. **CPU Usage:** Peak CPU during test
4. **API Latency:** Time for API call
5. **Token Usage:** Tokens consumed
6. **Cost:** USD cost per test

### Monitoring Implementation

```python
class PerformanceMonitor:
    def start_monitoring(test_id)
    def record_metric(metric_name, value)
    def get_metrics(test_id)
    def check_thresholds()
    def alert_if_exceeded()
```

---

## 🎯 SUCCESS CRITERIA VALIDATION

Each test validates 12 criteria:

1. **Execution:** No errors during execution
2. **Response Structure:** Valid JSON/text format
3. **Response Time:** Within timeout limits
4. **Progress Heartbeat:** Sent for long operations
5. **Logging:** All events logged
6. **Error Handling:** Graceful error handling
7. **API Integration:** Real API call successful
8. **File Upload:** Files uploaded correctly
9. **Conversation ID:** Tracked correctly
10. **Web Search:** Activated when needed
11. **Resource Cleanup:** No leaks
12. **Cost Tracking:** Costs tracked

---

## 🔄 CONVERSATION ID MANAGEMENT

### Platform-Specific Handling

**Kimi:**
- Conversation ID format: `kimi_conv_{uuid}`
- Stored in: `cache/kimi/`
- TTL: 1 hour
- Can be reused within Kimi tools

**GLM:**
- Conversation ID format: `glm_conv_{uuid}`
- Stored in: `cache/glm/`
- TTL: 1 hour
- Can be reused within GLM tools

### Cross-Platform Isolation

```python
def validate_conversation_id(conv_id, provider):
    if provider == "kimi" and not conv_id.startswith("kimi_"):
        raise ValueError("Invalid conversation ID for Kimi")
    if provider == "glm" and not conv_id.startswith("glm_"):
        raise ValueError("Invalid conversation ID for GLM")
```

---

## 📝 LOGGING ARCHITECTURE

### Log Levels

- **DEBUG:** Detailed execution flow
- **INFO:** Test progress and results
- **WARNING:** Non-critical issues
- **ERROR:** Test failures
- **CRITICAL:** System failures

### Log Files

```
results/latest/test_logs/
├── core_tools/
│   ├── chat.log
│   ├── analyze.log
│   └── ...
├── advanced_tools/
│   └── ...
└── provider_tools/
    └── ...
```

---

## 🎯 NEXT STEPS

After understanding the architecture:

1. Read **TESTING_GUIDE.md** to learn how to run tests
2. Read **RESULTS_ANALYSIS.md** to interpret results
3. Review `utils/` directory for implementation details
4. Check `config/` for configuration options

---

## 📚 RELATED DOCUMENTATION

- **README.md** - Overview
- **SETUP_GUIDE.md** - Setup instructions
- **TESTING_GUIDE.md** - How to run tests
- **RESULTS_ANALYSIS.md** - Interpreting results
- **API_INTEGRATION.md** - API details
- **CONVERSATION_ID_GUIDE.md** - Conversation management

