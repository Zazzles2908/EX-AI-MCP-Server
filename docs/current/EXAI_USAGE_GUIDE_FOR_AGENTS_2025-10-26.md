# EXAI Usage Guide for AI Agents

**Date:** 2025-10-26 17:00 AEDT  
**Version:** 1.0  
**Target Audience:** AI Agents using EXAI MCP Server  
**EXAI Consultation:** Continuation ID `2e18c3e8-805e-440d-b501-aa73d4a91229`

---

## 📋 Quick Reference

**When to use EXAI:**
- Complex code analysis and architectural decisions
- Security audits and vulnerability assessment
- Performance optimization recommendations
- Design pattern validation
- Multi-step problem solving with context retention

**When NOT to use EXAI:**
- Simple file operations (use direct tools)
- Basic CRUD operations
- Routine data transformations
- When offline analysis is sufficient

---

## 🎯 Core Consultation Patterns

### Single-Step Consultations

**Use for:** Simple, direct questions that don't require follow-up

```python
# Example: Security analysis
response = chat_EXAI_WS(
    prompt="Analyze this code for security issues",
    files=["/app/src/auth.py"],
    model="glm-4.6",
    use_websearch=False
)
```

### Multi-Step Consultations with Continuation

**Use for:** Complex analysis requiring multiple rounds of discussion

```python
# Step 1: Initial analysis
response1 = chat_EXAI_WS(
    prompt="Review this architecture and identify potential issues",
    files=["/app/docs/architecture.md"],
    model="glm-4.6"
)

# Extract continuation_id from response1
continuation_id = response1.get('continuation_offer', {}).get('continuation_id')

# Step 2: Deep dive on specific issues
response2 = chat_EXAI_WS(
    prompt="Focus on the security vulnerabilities mentioned and provide remediation steps",
    continuation_id=continuation_id,
    model="glm-4.6"
)
```

---

## 🔑 Continuation ID Management

### Best Practices

1. **Always extract and store** `continuation_id` from responses
2. **Use for related queries** within the same session/context
3. **Continuation IDs expire** after 24 hours of inactivity
4. **Track in session state** for complex workflows
5. **Create NEW continuation IDs** for different tasks/contexts

### Implementation Pattern

```python
class EXAIConsultationManager:
    def __init__(self):
        self.active_consultations = {}
    
    def start_consultation(self, prompt, files=None, model="glm-4.6"):
        response = chat_EXAI_WS(
            prompt=prompt,
            files=files or [],
            model=model
        )
        
        if response.get('continuation_offer', {}).get('continuation_id'):
            continuation_id = response['continuation_offer']['continuation_id']
            self.active_consultations[continuation_id] = {
                'started_at': datetime.utcnow(),
                'context': prompt[:100] + "..."
            }
        
        return response
    
    def continue_consultation(self, continuation_id, prompt):
        if continuation_id not in self.active_consultations:
            raise ValueError("Invalid or expired continuation ID")
        
        return chat_EXAI_WS(
            prompt=prompt,
            continuation_id=continuation_id,
            model="glm-4.6"
        )
```

---

## 🤖 Model Selection Guidelines

### GLM-4.6 (Premium Model)

**Use for:**
- Complex analysis and code review
- Architectural decisions
- Security audits
- Performance optimization
- Multi-step reasoning

**Characteristics:**
- Deep reasoning capabilities
- Comprehensive responses
- Higher token cost
- Response time: 2-3x slower than flash

### GLM-4.5-Flash (Fast Model)

**Use for:**
- Quick questions
- Simple analysis
- Routing decisions
- Validation checks
- When speed is critical

**Characteristics:**
- Fast responses
- Cost-effective
- Lower token cost
- Good for simple tasks

### Decision Matrix

```python
def select_model(task_type, complexity, urgency):
    if urgency == "high" and complexity in ["low", "medium"]:
        return "glm-4.5-flash"
    elif complexity == "high" or task_type in ["code_review", "architecture", "security"]:
        return "glm-4.6"
    else:
        return "glm-4.5-flash"  # Default
```

---

## 🌐 Web Search Usage

### Enable Web Search When:

- Current information is needed (API changes, new libraries)
- Documentation verification is required
- Industry best practices research
- Competitive analysis
- Framework/library updates

### Disable Web Search When:

- Analyzing internal code/documents
- General programming questions
- Offline analysis is sufficient
- To reduce response latency
- Working with proprietary code

### Examples

```python
# Example: Research current best practices
response = chat_EXAI_WS(
    prompt="What are the current best practices for React state management in 2025?",
    use_websearch=True,
    model="glm-4.6"
)

# Example: Internal code analysis
response = chat_EXAI_WS(
    prompt="Review this React component for performance issues",
    files=["/app/src/components/UserProfile.jsx"],
    use_websearch=False,
    model="glm-4.6"
)
```

---

## 📝 Prompt Structuring Best Practices

### Effective Prompt Structure

1. **Context First** - Provide relevant background
2. **Clear Task** - Specific, actionable request
3. **Constraints** - Any limitations or requirements
4. **Format** - Desired output format
5. **Examples** - When helpful, provide examples

### Template

```python
def structure_prompt(context, task, constraints=None, format=None, examples=None):
    prompt_parts = [f"Context: {context}"]
    
    prompt_parts.append(f"Task: {task}")
    
    if constraints:
        prompt_parts.append(f"Constraints: {constraints}")
    
    if format:
        prompt_parts.append(f"Output Format: {format}")
    
    if examples:
        prompt_parts.append(f"Examples: {examples}")
    
    return "\n\n".join(prompt_parts)
```

### Example Usage

```python
prompt = structure_prompt(
    context="We're building a file upload system with deduplication",
    task="Review the deduplication logic for race conditions",
    constraints="Must handle concurrent uploads safely",
    format="List of potential issues with severity levels",
    examples="Similar to how database transactions handle concurrency"
)

response = chat_EXAI_WS(
    prompt=prompt,
    files=["/app/utils/file/deduplication.py"],
    model="glm-4.6"
)
```

---

## 🔄 Multi-Step Workflow Pattern

### Workflow Tools (debug, codereview, analyze, etc.)

**These tools enforce investigation between steps:**

```python
# Step 1: Start investigation
response1 = debug_EXAI_WS(
    step="Investigate the file upload timeout issue",
    step_number=1,
    total_steps=3,
    next_step_required=True,
    findings="Initial investigation shows timeout after 30 seconds",
    hypothesis="Network latency or large file size causing timeout",
    files_checked=["/app/tools/kimi_upload_files.py"],
    relevant_files=["/app/tools/kimi_upload_files.py"]
)

# STOP - Investigate based on response1 guidance

# Step 2: Continue investigation
response2 = debug_EXAI_WS(
    step="Analyzed network logs and found connection pooling issue",
    step_number=2,
    total_steps=3,
    next_step_required=True,
    findings="Connection pool exhausted after 5 concurrent uploads",
    hypothesis="Need to increase pool size or implement queuing",
    files_checked=["/app/tools/kimi_upload_files.py", "/app/src/providers/kimi.py"],
    relevant_files=["/app/src/providers/kimi.py"],
    confidence="high"
)

# STOP - Implement fix based on response2

# Step 3: Final validation
response3 = debug_EXAI_WS(
    step="Implemented connection pool increase and tested",
    step_number=3,
    total_steps=3,
    next_step_required=False,
    findings="All tests passing, no timeouts with 20 concurrent uploads",
    hypothesis="Connection pool size was the root cause",
    files_checked=["/app/tools/kimi_upload_files.py", "/app/src/providers/kimi.py"],
    relevant_files=["/app/src/providers/kimi.py"],
    confidence="certain"
)
```

---

## 📊 Continuation ID Tracking

### Active Continuation IDs (as of 2025-10-26)

**Task 1 (File Deduplication):** ✅ COMPLETE
- Continuation ID: `c90cdeec-48bb-4d10-b075-925ebbf39c8a`
- Consultations: 6
- Status: Complete

**Task 2 (WebSocket Stability & Cleanup):** ⏳ ACTIVE
- Continuation ID: `c657a995-0f0d-4b97-91be-2618055313f4`
- Consultations: 1 (planning)
- Status: Active

**Documentation Updates:** ⏳ ACTIVE
- Continuation ID: `2e18c3e8-805e-440d-b501-aa73d4a91229`
- Consultations: 3
- Status: Active

---

## ⚠️ Common Pitfalls

### 1. Reusing Continuation IDs Across Different Tasks

**❌ DON'T:**
```python
# Using Task 1 continuation ID for Task 2
response = chat_EXAI_WS(
    prompt="Help with WebSocket stability",
    continuation_id="c90cdeec-48bb-4d10-b075-925ebbf39c8a",  # Task 1 ID!
    model="glm-4.6"
)
```

**✅ DO:**
```python
# Create NEW continuation ID for Task 2
response = chat_EXAI_WS(
    prompt="Help with WebSocket stability",
    model="glm-4.6"
)
# Extract new continuation_id for Task 2
task2_continuation_id = response['continuation_offer']['continuation_id']
```

### 2. Not Extracting Continuation IDs

**❌ DON'T:**
```python
response = chat_EXAI_WS(prompt="Analyze this code", model="glm-4.6")
# Continuation ID lost!
```

**✅ DO:**
```python
response = chat_EXAI_WS(prompt="Analyze this code", model="glm-4.6")
continuation_id = response.get('continuation_offer', {}).get('continuation_id')
if continuation_id:
    # Store for later use
    self.active_consultations[continuation_id] = {...}
```

### 3. Using Wrong Model for Task

**❌ DON'T:**
```python
# Using flash for complex security audit
response = chat_EXAI_WS(
    prompt="Perform comprehensive security audit",
    files=["/app/src/auth.py"],
    model="glm-4.5-flash"  # Too simple for this task!
)
```

**✅ DO:**
```python
# Using glm-4.6 for complex analysis
response = chat_EXAI_WS(
    prompt="Perform comprehensive security audit",
    files=["/app/src/auth.py"],
    model="glm-4.6"  # Appropriate for complex task
)
```

---

## 📚 Additional Resources

- **EXAI Tools:** `tools/chat_EXAI-WS-VSCode1.py`, `tools/debug_EXAI-WS-VSCode1.py`, etc.
- **Task 1 Completion:** `docs/current/TASK_1_COMPLETION_SUMMARY__FILE_DEDUPLICATION_2025-10-26.md`
- **Task 2 Planning:** `docs/current/TASK_2_PLANNING__WEBSOCKET_CLEANUP_VALIDATION_2025-10-26.md`
- **Master Plan:** `docs/05_CURRENT_WORK/MASTER_PLAN__TESTING_AND_CLEANUP.md`

---

**Last Updated:** 2025-10-26 17:00 AEDT  
**EXAI Consultation:** 2e18c3e8-805e-440d-b501-aa73d4a91229

