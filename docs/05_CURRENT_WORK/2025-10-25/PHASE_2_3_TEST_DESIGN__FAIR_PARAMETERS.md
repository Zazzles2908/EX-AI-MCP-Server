# Phase 2.3: WebSocket-Based SDK Comparison - Fair Testing Parameters

**Created:** 2025-10-25  
**Status:** 🔄 DESIGN PHASE  
**Goal:** Compare provider performance through MCP WebSocket server with FAIR parameters

---

## 🎯 **TESTING PHILOSOPHY: FAIRNESS FIRST**

**Critical Principle:** All parameters must be identical except the variable being tested (provider/SDK)

**What We're Testing:**
- Provider performance (GLM vs Kimi) through production architecture
- SDK overhead (if any) when using same provider
- Semaphore contention patterns under load

**What We're NOT Testing:**
- Direct SDK performance (already proven invalid in Phase 2.1)
- Different models or configurations
- Unrealistic synthetic workloads

---

## ⚖️ **FAIR TESTING PARAMETERS**

### **1. Model Selection** ✅ FAIR
**Requirement:** Use equivalent models from each provider

**GLM Models:**
- `glm-4.6` - Flagship model (200k context)
- `glm-4.5-flash` - Fast model (128k context)

**Kimi Models:**
- `kimi-k2-0905-preview` - Flagship model (256k context)
- `moonshot-v1-128k` - Standard model (128k context)

**Fair Comparison:**
| Test | GLM Model | Kimi Model | Rationale |
|------|-----------|------------|-----------|
| Flagship | glm-4.6 (200k) | kimi-k2-0905-preview (256k) | Both are flagship models with large context windows |
| Fast | glm-4.5-flash (128k) | moonshot-v1-128k (128k) | Both are optimized for speed with same context |

---

### **2. Temperature & Parameters** ✅ FAIR
**Requirement:** Identical generation parameters

```python
FAIR_PARAMETERS = {
    "temperature": 0.7,  # Same for both providers
    "max_tokens": None,  # Let model decide (same for both)
    "top_p": 1.0,        # Same for both
    "frequency_penalty": 0.0,  # Same for both
    "presence_penalty": 0.0,   # Same for both
}
```

**Rationale:** Different temperatures would bias results toward more/less creative responses

---

### **3. Test Prompts** ✅ FAIR
**Requirement:** Identical prompts for both providers

**Prompt Categories:**
1. **Short QA (50-100 tokens)** - "What is the capital of France?"
2. **Medium Code (200-500 tokens)** - "Write a Python function to reverse a string"
3. **Long Analysis (500-1000 tokens)** - "Analyze the pros and cons of microservices architecture"
4. **Complex Reasoning (1000+ tokens)** - "Design a distributed caching system"

**Prompt Selection:**
- Use REAL prompts from Phase 1 baseline data (976 conversations)
- Select representative samples from each category
- Same prompts sent to both providers

**Rationale:** Synthetic prompts may favor one provider's training data

---

### **4. Concurrency & Load** ✅ FAIR
**Requirement:** Same concurrency levels for both providers

**Test Scenarios:**
| Scenario | Concurrent Requests | Duration | Total Requests |
|----------|-------------------|----------|----------------|
| Low Load | 5 | 5 minutes | ~150 |
| Medium Load | 10 | 5 minutes | ~300 |
| High Load | 20 | 5 minutes | ~600 |
| Burst Load | 50 | 1 minute | ~300 |

**Execution Pattern:**
1. Run GLM test scenario
2. Wait 2 minutes (cooldown)
3. Run Kimi test scenario
4. Wait 2 minutes (cooldown)
5. Repeat for next scenario

**Rationale:** Prevents one provider from benefiting from warmed-up connections

---

### **5. Network & Infrastructure** ✅ FAIR
**Requirement:** Same network conditions and infrastructure

**Controls:**
- ✅ Both providers tested through MCP WebSocket server (`ws://localhost:8079`)
- ✅ Same semaphore limits (global + provider-specific)
- ✅ Same timeout settings (from `.env.docker`)
- ✅ Same retry logic and error handling
- ✅ Same connection pooling and keep-alive settings

**Rationale:** Direct SDK calls would bypass production overhead

---

### **6. Measurement & Metrics** ✅ FAIR
**Requirement:** Same metrics collected for both providers

**Metrics Collected (from latency tracking):**
- `total_latency_ms` - End-to-end time
- `global_sem_wait_ms` - Global semaphore wait time
- `provider_sem_wait_ms` - Provider-specific semaphore wait time
- `processing_ms` - Actual provider processing time
- `tokens_in` - Input tokens
- `tokens_out` - Output tokens

**Derived Metrics:**
- Tokens per second (TPS) = `tokens_out / (processing_ms / 1000)`
- Semaphore overhead = `(global_sem_wait_ms + provider_sem_wait_ms) / total_latency_ms`
- Success rate = `successful_requests / total_requests`

**Rationale:** Consistent metrics enable apples-to-apples comparison

---

### **7. Time of Day & System Load** ✅ FAIR
**Requirement:** Control for external factors

**Controls:**
- Run tests during off-peak hours (minimize external load)
- Alternate provider order (GLM first, then Kimi, then Kimi first, then GLM)
- Monitor system resources (CPU, memory, network) during tests
- Discard test runs if system load exceeds threshold

**Rationale:** External factors (network congestion, system load) can skew results

---

## 🔬 **TEST IMPLEMENTATION DESIGN**

### **WebSocket Test Client**
```python
class FairWebSocketTestClient:
    """
    WebSocket-based test client that ensures fair comparison
    """
    
    def __init__(self, host="127.0.0.1", port=8079):
        self.host = host
        self.port = port
        self.ws = None
        
    async def run_fair_comparison(self, prompts, provider_a, provider_b):
        """
        Run fair comparison between two providers
        
        Args:
            prompts: List of test prompts
            provider_a: First provider config (model, params)
            provider_b: Second provider config (model, params)
            
        Returns:
            Comparison results with statistical analysis
        """
        # Randomize order to prevent bias
        order = random.choice([
            (provider_a, provider_b),
            (provider_b, provider_a)
        ])
        
        results = {}
        for provider in order:
            # Run test with cooldown
            results[provider['name']] = await self.run_test_scenario(
                prompts=prompts,
                model=provider['model'],
                params=provider['params']
            )
            
            # Cooldown period
            await asyncio.sleep(120)  # 2 minutes
            
        return self.analyze_results(results)
```

---

## 📊 **STATISTICAL ANALYSIS**

### **Comparison Metrics**
1. **Mean Latency** - Average performance
2. **Median Latency (P50)** - Typical performance
3. **P95 Latency** - Worst-case performance (95th percentile)
4. **P99 Latency** - Extreme worst-case (99th percentile)
5. **Standard Deviation** - Consistency
6. **Success Rate** - Reliability

### **Statistical Significance**
- Use **t-test** to determine if differences are statistically significant
- Require **p-value < 0.05** for significance
- Report **confidence intervals** (95%)

### **Decision Criteria**
**Choose Provider A if:**
- Mean latency ≥15% better AND statistically significant
- P95 latency ≥20% better AND statistically significant
- Success rate ≥99% (both providers)

**Stick with Current Provider if:**
- Differences <10% OR not statistically significant
- Better ecosystem/developer experience

---

## 🚨 **BIAS PREVENTION CHECKLIST**

Before running tests, verify:

- [ ] Same model tier (flagship vs flagship, fast vs fast)
- [ ] Same temperature and generation parameters
- [ ] Same prompts (from real production data)
- [ ] Same concurrency levels
- [ ] Same infrastructure (MCP WebSocket server)
- [ ] Same metrics collection
- [ ] Randomized test order
- [ ] Cooldown periods between tests
- [ ] System load monitoring
- [ ] Statistical significance testing

---

## 📝 **TEST EXECUTION PLAN**

### **Phase 2.3.1: Preparation** (1 hour)
1. Select representative prompts from Phase 1 baseline data
2. Verify infrastructure (Docker, WebSocket server, Supabase)
3. Create test client with fair parameters
4. Dry run to validate methodology

### **Phase 2.3.2: Execution** (4 hours)
1. Run low load scenario (GLM → Kimi)
2. Run medium load scenario (Kimi → GLM)
3. Run high load scenario (GLM → Kimi)
4. Run burst load scenario (Kimi → GLM)

### **Phase 2.3.3: Analysis** (2 hours)
1. Query Supabase for latency metrics
2. Calculate statistical measures
3. Perform significance testing
4. Generate comparison report

### **Phase 2.3.4: Validation** (1 hour)
1. EXAI review of methodology
2. EXAI review of results
3. Final recommendation

**Total Duration:** 8 hours (1 day)

---

## 🔗 **DEPENDENCIES**

**Prerequisites:**
- ✅ Phase 0: Infrastructure foundation complete
- ✅ Phase 1: Baseline data collected
- ✅ Phase 2.0: Latency tracking implemented
- ⏳ Phase 2.2: Production baseline collected (48 hours)

**Blockers:**
- None (infrastructure ready)

---

**Last Updated:** 2025-10-25  
**Status:** Design complete, awaiting Phase 2.2 baseline data  
**EXAI Consultation:** Pending (will validate before execution)

