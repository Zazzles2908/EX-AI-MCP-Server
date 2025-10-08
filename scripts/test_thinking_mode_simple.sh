#!/bin/bash
# Simple test script that calls thinkdeep with different thinking modes
# and captures the logs

echo "========================================="
echo "TEST 1: Thinkdeep with DEFAULT (minimal)"
echo "========================================="
echo ""
echo "Calling thinkdeep without thinking_mode parameter..."
echo "Expected: Should use minimal from env"
echo ""

# This would be called through your MCP client
# For now, just document what should be tested

cat << 'EOF'
MANUAL TEST INSTRUCTIONS:

1. Open your MCP client (Augment Code, Claude Desktop, etc.)

2. Call thinkdeep with DEFAULT thinking_mode:
   ```
   thinkdeep(
     step="Analyze REST vs GraphQL",
     step_number=1,
     total_steps=1,
     next_step_required=False,
     findings="Testing default thinking mode",
     model="glm-4.5-flash"
   )
   ```

3. Check logs for:
   - "🎯 [THINKING_MODE] SOURCE=ENV_FALLBACK | MODE=minimal"
   - "🔥 [EXPERT_ANALYSIS_START] Thinking Mode: minimal"
   - "🔥 [EXPERT_ANALYSIS_COMPLETE] Thinking Mode: minimal"
   - "🔥 [EXPERT_ANALYSIS_COMPLETE] Total Duration: ~5-7s"

4. Call thinkdeep with USER-PROVIDED thinking_mode=low:
   ```
   thinkdeep(
     step="Analyze microservices vs monolithic",
     step_number=1,
     total_steps=1,
     next_step_required=False,
     findings="Testing user-provided thinking_mode=low",
     model="glm-4.5-flash",
     thinking_mode="low"
   )
   ```

5. Check logs for:
   - "🎯 [THINKING_MODE] SOURCE=USER_PARAMETER | MODE=low"
   - "🔥 [EXPERT_ANALYSIS_START] Thinking Mode: low"
   - "🔥 [EXPERT_ANALYSIS_COMPLETE] Thinking Mode: low"
   - "🔥 [EXPERT_ANALYSIS_COMPLETE] Total Duration: ~8-10s"

6. Call thinkdeep with USER-PROVIDED thinking_mode=high:
   ```
   thinkdeep(
     step="Deep analysis: Event sourcing for trading system?",
     step_number=1,
     total_steps=1,
     next_step_required=False,
     findings="Testing user-provided thinking_mode=high",
     model="glm-4.5-flash",
     thinking_mode="high"
   )
   ```

7. Check logs for:
   - "🎯 [THINKING_MODE] SOURCE=USER_PARAMETER | MODE=high"
   - "🔥 [EXPERT_ANALYSIS_START] Thinking Mode: high"
   - "🔥 [EXPERT_ANALYSIS_COMPLETE] Thinking Mode: high"
   - "🔥 [EXPERT_ANALYSIS_COMPLETE] Total Duration: ~25-30s"

EXPECTED LOG OUTPUT:
====================

For each test, you should see logs like this:

```
🎯 [THINKING_MODE] SOURCE=USER_PARAMETER | MODE=low | REQUEST_HAS_PARAM=True
✅ [THINKING_MODE] FINAL_MODE=low | VALID=True
🔥 [EXPERT_ANALYSIS_START] ========================================
🔥 [EXPERT_ANALYSIS_START] Tool: thinkdeep
🔥 [EXPERT_ANALYSIS_START] Model: glm-4.5-flash
🔥 [EXPERT_ANALYSIS_START] Thinking Mode: low
🔥 [EXPERT_ANALYSIS_START] Temperature: 0.3
🔥 [EXPERT_ANALYSIS_START] Prompt Length: 1234 chars
🔥 [EXPERT_ANALYSIS_START] Thinking Mode Selection Time: 0.001s
🔥 [EXPERT_ANALYSIS_START] ========================================
... (provider call happens here) ...
🔥 [EXPERT_ANALYSIS_COMPLETE] ========================================
🔥 [EXPERT_ANALYSIS_COMPLETE] Tool: thinkdeep
🔥 [EXPERT_ANALYSIS_COMPLETE] Model: glm-4.5-flash
🔥 [EXPERT_ANALYSIS_COMPLETE] Thinking Mode: low
🔥 [EXPERT_ANALYSIS_COMPLETE] Total Duration: 8.45s
🔥 [EXPERT_ANALYSIS_COMPLETE] Response Length: 2345 chars
🔥 [EXPERT_ANALYSIS_COMPLETE] ========================================
```

The key things to verify:
1. SOURCE shows USER_PARAMETER when you pass thinking_mode
2. SOURCE shows ENV_FALLBACK when you don't pass thinking_mode
3. FINAL_MODE matches what you requested
4. Total Duration varies by thinking mode (minimal < low < high)
5. Expert analysis actually runs (not 0.00s)

EOF

