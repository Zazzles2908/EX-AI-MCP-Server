# Debug Workflow Documentation
**Created:** 2025-10-24  
**Tool:** debug_EXAI-WS  
**Category:** Workflow Tool  
**Purpose:** Structured debugging workflow with expert validation

---

## Overview
**Category:** Workflow  
**Purpose:** Systematic root cause analysis for bugs and errors  
**Complexity:** Complex (multi-step investigation)  
**Typical Duration:** 3-5s per step (varies by complexity)

---

## Primary Use Cases

### Use Case 1: Complex Bug Investigation
**Scenario:** User reports mysterious error or unexpected behavior  
**Input:** Bug description, error messages, relevant files  
**Output:** Root cause analysis, hypothesis validation, fix recommendations  
**Success Criteria:** Root cause identified with high confidence

### Use Case 2: Performance Issue Diagnosis
**Scenario:** System is slow or unresponsive  
**Input:** Performance symptoms, affected operations  
**Output:** Performance bottleneck identification, optimization recommendations  
**Success Criteria:** Bottleneck identified and fix proposed

### Use Case 3: Integration Problem Resolution
**Scenario:** Components fail to work together  
**Input:** Integration points, error logs, configuration  
**Output:** Integration issue root cause, configuration fixes  
**Success Criteria:** Integration restored with validated fix

---

## Typical Execution Flow

### Step 1: Investigation Planning
**Action:** Claude analyzes bug description and plans investigation  
**Duration:** < 1s  
**Dependencies:** Bug description from user

### Step 2: Evidence Gathering
**Action:** Claude uses view/codebase-retrieval to examine code  
**Duration:** 1-2s  
**Dependencies:** Access to codebase

### Step 3: Hypothesis Formation
**Action:** Claude calls debug_EXAI-WS with findings and hypothesis  
**Duration:** 2-4s (includes AI model call)  
**Dependencies:** Evidence from Step 2

### Step 4: Expert Validation
**Action:** EXAI validates hypothesis and provides recommendations  
**Duration:** 2-3s (AI model processing)  
**Output:** Validated root cause, fix recommendations, confidence score

---

## Integration Patterns

### Pattern 1: Standalone Debugging
**Description:** Single bug investigation  
**Example:**
```json
{
  "tool": "debug_EXAI-WS",
  "step": "Investigating null pointer exception in payment processing",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Found that payment gateway returns null when API key is invalid",
  "hypothesis": "Missing API key validation before gateway call",
  "relevant_files": ["/src/payment/gateway.py"]
}
```

### Pattern 2: Chained with Code Review
**Description:** Debug → Fix → Code Review  
**Sequence:**
1. debug_EXAI-WS → Identifies root cause
2. Claude implements fix
3. codereview_EXAI-WS → Validates fix quality

### Pattern 3: Iterative Investigation
**Description:** Multi-step debugging with hypothesis refinement  
**Sequence:**
1. Step 1: Initial investigation (confidence: low)
2. Step 2: Deeper analysis (confidence: medium)
3. Step 3: Hypothesis validation (confidence: high)
4. Step 4: Expert validation (confidence: certain)

---

## Performance Characteristics

### Latency Breakdown
| Phase | Typical Duration | Notes |
|-------|-----------------|-------|
| Parameter Validation | 10 ms | Input validation |
| Evidence Gathering | 1-2s | Claude's investigation |
| Tool Invocation | 50 ms | MCP overhead |
| AI Model Call | 2-3s | EXAI analysis |
| Response Formatting | 30 ms | Result serialization |
| **Total** | **3-5s** | **p95 target** |

### Resource Usage
- **Memory:** 80-100 MB typical, 120 MB peak
- **CPU:** Medium (AI model processing)
- **Network:** Moderate (AI API calls)
- **Disk I/O:** Read-only (code examination)

### Scalability
- **Concurrent Executions:** 5 (single-user environment)
- **Rate Limiting:** AI API limits apply
- **Caching:** Conversation history cached

---

## Common Failure Modes

### Failure Mode 1: No Bug Found
**Symptoms:** Investigation completes but no root cause identified  
**Root Cause:** User misunderstanding or expectation mismatch  
**Frequency:** Occasional (10-15% of cases)  
**Impact:** Low (valid outcome)  
**Recovery:** Recommend discussing with user to clarify expected behavior

**Example Error:**
```
Hypothesis: "No bug found - possible user misunderstanding"
Recommendation: "Recommend discussing with thought partner for clarification"
```

**Resolution:**
- Use chat_EXAI-WS to discuss expected vs actual behavior
- Clarify requirements with user
- Document expected behavior

### Failure Mode 2: AI API Timeout
**Symptoms:** Tool hangs or returns timeout error  
**Root Cause:** AI model processing takes too long  
**Frequency:** Rare (< 1%)  
**Impact:** High (blocks investigation)  
**Recovery:** Retry with simpler prompt or different model

**Example Error:**
```
Error: "AI API timeout after 30 seconds"
```

**Resolution:**
- Reduce complexity of findings/hypothesis
- Use faster model (glm-4.5-flash instead of glm-4.6)
- Break investigation into smaller steps

### Failure Mode 3: Insufficient Evidence
**Symptoms:** Low confidence score, vague recommendations  
**Root Cause:** Claude didn't gather enough evidence before calling tool  
**Frequency:** Occasional (5-10%)  
**Impact:** Medium (requires more investigation)  
**Recovery:** Continue investigation with more evidence gathering

**Example Error:**
```
Confidence: "low"
Recommendation: "Gather more evidence about error conditions"
```

**Resolution:**
- Use view tool to examine more files
- Check error logs and stack traces
- Trace execution paths more thoroughly

---

## Error Handling Patterns

### Retry Logic
**Enabled:** Yes  
**Max Retries:** 3 attempts  
**Backoff Strategy:** Exponential (1s, 2s, 4s)  
**Retry Conditions:** AI API timeout, network errors

### Circuit Breaker
**Enabled:** Yes  
**Failure Threshold:** 3 consecutive failures  
**Cooldown Period:** 60 seconds  
**Reset Conditions:** Successful call or manual reset

### Graceful Degradation
**Fallback Behavior:** Return findings without AI validation  
**Partial Results:** Yes (Claude's analysis without EXAI validation)  
**User Notification:** Clear message about degraded mode

---

## Dependencies

### Internal Dependencies
- **Required Services:** WebSocket daemon, MCP server
- **Required Tools:** view, codebase-retrieval (for evidence gathering)
- **Required Data:** Codebase access, error logs

### External Dependencies
- **APIs:** GLM or Kimi AI API
- **Databases:** Supabase (for conversation persistence)
- **File Systems:** Project workspace

### Configuration Dependencies
- **Environment Variables:** KIMI_API_KEY or GLM_API_KEY, SUPABASE_URL, SUPABASE_KEY
- **Configuration Files:** .env.docker
- **Secrets:** AI API keys

---

## Best Practices

### Do's ✅
- Gather comprehensive evidence before calling debug tool
- Start with low confidence and increase as evidence accumulates
- Use relevant_files to pass file paths (not code snippets in prompt)
- Set next_step_required=false when investigation is complete
- Document both successful and failed hypotheses

### Don'ts ❌
- Don't call debug tool without investigating first
- Don't pass large code snippets in step parameter
- Don't set confidence to 'certain' unless 200% sure
- Don't skip evidence gathering to save time
- Don't ignore EXAI recommendations

### Tips 💡
- Use continuation_id for follow-up questions
- Set use_websearch=true for external documentation
- Use thinking_mode=high for complex bugs
- Break complex investigations into multiple steps
- Document dead ends to avoid repeating them

---

## Monitoring & Observability

### Key Metrics
- **Latency:** p50=3s, p95=5s, p99=8s, max=15s
- **Success Rate:** 95% (excluding user errors)
- **Error Rate:** < 1% (system errors only)
- **Confidence Distribution:** 60% high/very_high, 30% medium, 10% low

### Alerts
- **Critical:** Latency > 10s, Error rate > 10%, Success rate < 80%
- **Warning:** Latency > 7s, Error rate > 5%, Success rate < 90%
- **Info:** Latency > 5s, Low confidence rate > 20%

### Logging
- **Log Level:** INFO (DEBUG for troubleshooting)
- **Log Format:** JSON structured logs
- **Log Destination:** Supabase + local files

---

## Examples

### Example 1: Simple Bug
**Scenario:** Null pointer exception

**Input:**
```json
{
  "step": "Investigating null pointer in payment processing",
  "step_number": 1,
  "total_steps": 1,
  "next_step_required": false,
  "findings": "Payment gateway returns null when API key is missing",
  "hypothesis": "Missing API key validation",
  "confidence": "high",
  "relevant_files": ["/src/payment/gateway.py"]
}
```

**Output:**
```json
{
  "root_cause": "Missing API key validation before gateway call",
  "fix_recommendation": "Add API key validation in gateway initialization",
  "confidence": "very_high",
  "validation": "EXAI confirmed hypothesis"
}
```

### Example 2: Complex Investigation
**Scenario:** Race condition in concurrent processing

**Step 1 Input:**
```json
{
  "step": "Investigating intermittent failures in batch processing",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Failures occur only under high load",
  "hypothesis": "Possible race condition",
  "confidence": "low"
}
```

**Step 2 Input:**
```json
{
  "step": "Examining shared state access patterns",
  "step_number": 2,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Multiple threads access shared cache without locking",
  "hypothesis": "Race condition in cache access",
  "confidence": "high"
}
```

**Step 3 Input:**
```json
{
  "step": "Validated race condition with thread safety analysis",
  "step_number": 3,
  "total_steps": 3,
  "next_step_required": false,
  "findings": "Cache.get() and Cache.set() not atomic",
  "hypothesis": "Need thread-safe cache implementation",
  "confidence": "certain"
}
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-24 | Initial documentation |

---

## Related Documentation
- [Performance Benchmarks](../PERFORMANCE_BENCHMARKS__2025-10-24.md)
- [Workflow Template](../WORKFLOW_DOCUMENTATION_TEMPLATE__2025-10-24.md)
- [Testing Plan](../COMPREHENSIVE_TESTING_AND_CLEANUP_PLAN__2025-10-24.md)

