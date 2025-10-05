# Test Documentation Template

**Created:** 2025-10-06  
**Purpose:** Standard template for documenting test expected behavior

---

## Test Function Documentation Format

Each test function should include comprehensive documentation following this format:

```python
def test_<tool>_<variation>_<provider>(mcp_client: MCPClient, **kwargs):
    """
    Test <tool> - <variation> with <provider>
    
    **Purpose:**
    <Brief description of what this test validates>
    
    **Test Input:**
    - field1: <description and example value>
    - field2: <description and example value>
    - model: <provider model being tested>
    
    **Expected Behavior:**
    - Tool should <expected action 1>
    - Response should contain <expected content>
    - Status should be <expected status>
    - Duration should be <expected range>
    
    **Success Criteria:**
    - outputs array is not empty
    - response contains expected content
    - no errors in response
    - <additional criteria>
    
    **Known Issues:**
    - <any known limitations or issues>
    
    **Related:**
    - Tool: tools/<category>/<tool>.py
    - Schema: <link to schema if applicable>
    """
    # Test implementation
    pass
```

---

## Example: Chat Tool Test

```python
def test_chat_basic_glm(mcp_client: MCPClient, **kwargs):
    """
    Test chat - basic functionality with GLM
    
    **Purpose:**
    Validates basic chat functionality using GLM-4.5-flash model.
    Tests the complete MCP stack: protocol → daemon → server → tool → provider → API.
    
    **Test Input:**
    - prompt: "What is 2+2? Answer with just the number."
    - model: "glm-4.5-flash"
    
    **Expected Behavior:**
    - Tool should send prompt to GLM API
    - Response should contain the answer "4"
    - Response should be concise (following instruction)
    - Status should be "success" or "continuation_available"
    
    **Success Criteria:**
    - outputs array contains at least 1 element
    - response text contains "4"
    - no error status in response
    - response time < 30 seconds
    
    **Known Issues:**
    - None
    
    **Related:**
    - Tool: tools/chat.py
    - Provider: src/providers/glm/glm_client.py
    """
    result = mcp_client.call_tool(
        tool_name="chat",
        arguments={
            "prompt": "What is 2+2? Answer with just the number.",
            "model": "glm-4.5-flash"
        },
        test_name="chat",
        variation="basic_glm"
    )
    
    outputs = result.get("outputs", [])
    success = len(outputs) > 0
    
    content = ""
    if outputs and isinstance(outputs[0], dict):
        content = outputs[0].get("text", "")
    
    # Check if response contains "4"
    contains_answer = "4" in content
    
    return {
        "success": success and contains_answer,
        "content": content[:200],
        "outputs_count": len(outputs)
    }
```

---

## Example: Workflow Tool Test (Consensus)

```python
def test_consensus_basic_glm(mcp_client: MCPClient, **kwargs):
    """
    Test consensus - basic functionality with GLM
    
    **Purpose:**
    Validates consensus workflow tool with multi-model consultation.
    Tests step-by-step consensus gathering from multiple AI models.
    
    **Test Input:**
    - step: "Gather consensus on whether Python or JavaScript is better for web backend development"
    - step_number: 1
    - total_steps: 1
    - next_step_required: False
    - findings: "Initial analysis: Both languages have strong ecosystems. Need expert consensus."
    - models: [
        {"name": "glm-4.5-flash", "stance": "neutral"},
        {"name": "kimi-k2-0905-preview", "stance": "neutral"}
      ]
    - model: "glm-4.5-flash"
    
    **Expected Behavior:**
    - Tool should validate all required workflow fields
    - Tool should consult each model in the models array
    - Response should synthesize perspectives from all models
    - Status should indicate workflow completion
    
    **Success Criteria:**
    - outputs array contains at least 1 element
    - response contains analysis from multiple perspectives
    - no validation errors for required fields
    - workflow status indicates completion
    
    **Known Issues:**
    - None
    
    **Related:**
    - Tool: tools/workflows/consensus.py
    - Schema: tools/workflows/consensus_schema.py
    - Base: tools/workflow/base.py
    """
    result = mcp_client.call_tool(
        tool_name="consensus",
        arguments={
            "step": "Gather consensus on whether Python or JavaScript is better for web backend development",
            "step_number": 1,
            "total_steps": 1,
            "next_step_required": False,
            "findings": "Initial analysis: Both languages have strong ecosystems. Need expert consensus.",
            "models": [
                {"name": "glm-4.5-flash", "stance": "neutral"},
                {"name": "kimi-k2-0905-preview", "stance": "neutral"}
            ],
            "model": "glm-4.5-flash"
        },
        test_name="consensus",
        variation="basic_glm"
    )
    
    outputs = result.get("outputs", [])
    success = len(outputs) > 0
    
    content = ""
    if outputs and isinstance(outputs[0], dict):
        content = outputs[0].get("text", "")
    
    return {
        "success": success,
        "content": content[:200] if content else "",
        "outputs_count": len(outputs)
    }
```

---

## Documentation Checklist

When documenting a test, ensure you include:

- [ ] **Purpose** - What does this test validate?
- [ ] **Test Input** - All input fields with descriptions
- [ ] **Expected Behavior** - What should happen?
- [ ] **Success Criteria** - How do we know it passed?
- [ ] **Known Issues** - Any limitations or known problems?
- [ ] **Related** - Links to relevant source files

---

## Tool Categories

### Simple Tools
- **chat** - Basic chat functionality
- **challenge** - Critical thinking prompts
- **listmodels** - Model listing
- **version** - Server version info
- **status** - Server status
- **health** - Health check
- **activity** - Activity logs
- **provider_capabilities** - Provider info

### Workflow Tools
All workflow tools require these fields:
- `step` - Current step description
- `step_number` - Current step number (1-based)
- `total_steps` - Total number of steps
- `next_step_required` - Whether another step is needed
- `findings` - Current findings/observations

Workflow tools:
- **analyze** - Code analysis
- **debug** - Code debugging
- **codereview** - Code review
- **refactor** - Code refactoring
- **secaudit** - Security audit
- **planner** - Task planning
- **tracer** - Execution tracing
- **testgen** - Test generation
- **consensus** - Multi-model consensus
- **thinkdeep** - Deep thinking
- **docgen** - Documentation generation
- **precommit** - Pre-commit checks

### Provider Tools
- **kimi_*** - Kimi-specific tools
- **glm_*** - GLM-specific tools

---

## Best Practices

1. **Be Specific** - Document exact expected values, not vague descriptions
2. **Include Examples** - Show actual input/output examples
3. **Document Edge Cases** - Note any special conditions or limitations
4. **Keep Updated** - Update docs when test behavior changes
5. **Link to Source** - Always reference the actual tool implementation

---

**End of Template**

