# MCP Protocol Implementation Guide

## Overview

This guide provides comprehensive documentation for the MCP (Model Context Protocol) implementation in EX-AI-MCP-Server, focusing on proper protocol usage and best practices.

## Table of Contents

1. [MCP Protocol Fundamentals](#mcp-protocol-fundamentals)
2. [Correct Message Structure](#correct-message-structure)
3. [Tool Reference](#tool-reference)
4. [Common Mistakes](#common-mistakes)
5. [Testing & Validation](#testing--validation)
6. [Examples](#examples)

---

## MCP Protocol Fundamentals

### JSON-RPC 2.0 Standard

All MCP messages must follow the JSON-RPC 2.0 specification:

```json
{
  "jsonrpc": "2.0",
  "id": "unique_request_identifier",
  "method": "method_name",
  "params": {
    // method-specific parameters
  }
}
```

**Required Fields:**
- `jsonrpc`: Must be `"2.0"`
- `id`: Unique identifier for the request (string or number)
- `method`: The method to invoke
- `params`: Method parameters (object)

### MCP Methods

#### `initialize`
Initializes the MCP client connection.

```json
{
  "jsonrpc": "2.0",
  "id": "init_1",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "test-client",
      "version": "1.0.0"
    }
  }
}
```

#### `tools/list`
Lists all available tools on the server.

```json
{
  "jsonrpc": "2.0",
  "id": "list_1",
  "method": "tools/list"
}
```

#### `tools/call`
Calls a specific tool with parameters.

```json
{
  "jsonrpc": "2.0",
  "id": "call_1",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      // tool-specific arguments
    }
  }
}
```

---

## Correct Message Structure

### Standard Tool Call

```json
{
  "jsonrpc": "2.0",
  "id": "request_id",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      // Arguments specific to the tool
    }
  }
}
```

### Success Response

```json
{
  "jsonrpc": "2.0",
  "id": "request_id",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Response text"
      }
    ]
  }
}
```

### Error Response

```json
{
  "jsonrpc": "2.0",
  "id": "request_id",
  "error": {
    "code": -32600,
    "message": "Error description",
    "data": {
      // Additional error details
    }
  }
}
```

---

## Tool Reference

### 1. kimi_chat_with_tools

Chat with Kimi AI models (GLM, KIMI, MiniMax).

**Parameters:**
- `prompt` (string, required): The chat prompt
- `model` (string, optional): Model name (defaults to auto-select)
- `tools` (array, optional): List of tools to enable
- `tool_choice` (string, optional): Tool selection strategy

**Example:**

```json
{
  "jsonrpc": "2.0",
  "id": "kimi_chat_1",
  "method": "tools/call",
  "params": {
    "name": "kimi_chat_with_tools",
    "arguments": {
      "prompt": "What are the capabilities of kimi-k2-thinking?",
      "model": "kimi-k2-thinking"
    }
  }
}
```

### 2. analyze

Structured analysis workflow tool.

**Required Parameters:**
- `step` (string): Description of analysis step
- `step_number` (int): Current step index
- `total_steps` (int): Total number of steps
- `next_step_required` (bool): Whether another step is needed
- `findings` (string): Summary of discoveries

**Optional Parameters:**
- `files_checked` (array): Files examined
- `relevant_files` (array): Relevant files
- `relevant_context` (array): Context information
- `issues_found` (array): Issues identified
- `backtrack_from_step` (int): Optional backtracking
- `images` (array): Visual context

**Example:**

```json
{
  "jsonrpc": "2.0",
  "id": "analyze_1",
  "method": "tools/call",
  "params": {
    "name": "analyze",
    "arguments": {
      "step": "Analyze kimi-k2-thinking model capabilities",
      "step_number": 1,
      "total_steps": 1,
      "next_step_required": false,
      "findings": "Model has 256K context and extended thinking support"
    }
  }
}
```

### 3. status

Get server status and diagnostics.

**Parameters:** None

**Example:**

```json
{
  "jsonrpc": "2.0",
  "id": "status_1",
  "method": "tools/call",
  "params": {
    "name": "status",
    "arguments": {}
  }
}
```

### 4. listmodels

List all available AI models.

**Parameters:** None

**Example:**

```json
{
  "jsonrpc": "2.0",
  "id": "listmodels_1",
  "method": "tools/call",
  "params": {
    "name": "listmodels",
    "arguments": {}
  }
}
```

---

## Common Mistakes

### ❌ Mistake 1: Wrong Tool Name

```json
{
  "jsonrpc": "2.0",
  "id": "error_1",
  "method": "tools/call",
  "params": {
    "name": "chat",  // WRONG - tool doesn't exist
    "arguments": {
      "prompt": "Hello"
    }
  }
}
```

**Error:** `"Tool not found: chat"`

**✅ Correct:**

```json
{
  "jsonrpc": "2.0",
  "id": "correct_1",
  "method": "tools/call",
  "params": {
    "name": "kimi_chat_with_tools",  // CORRECT
    "arguments": {
      "prompt": "Hello"
    }
  }
}
```

### ❌ Mistake 2: Missing Required Fields in analyze

```json
{
  "jsonrpc": "2.0",
  "id": "error_2",
  "method": "tools/call",
  "params": {
    "name": "analyze",
    "arguments": {
      "prompt": "test"  // WRONG - missing required fields
    }
  }
}
```

**Error:** `"5 validation errors for AnalyzeWorkflowRequest"`

**✅ Correct:**

```json
{
  "jsonrpc": "2.0",
  "id": "correct_2",
  "method": "tools/call",
  "params": {
    "name": "analyze",
    "arguments": {
      "step": "Analysis description",
      "step_number": 1,
      "total_steps": 1,
      "next_step_required": false,
      "findings": "Summary"
    }
  }
}
```

### ❌ Mistake 3: Missing jsonrpc Field

```json
{
  "id": "error_3",
  "method": "tools/call",
  "params": {
    "name": "kimi_chat_with_tools",
    "arguments": {
      "prompt": "Test"
    }
  }
}
```

**Error:** Protocol violation

**✅ Correct:**

```json
{
  "jsonrpc": "2.0",  // REQUIRED
  "id": "correct_3",
  "method": "tools/call",
  "params": {
    "name": "kimi_chat_with_tools",
    "arguments": {
      "prompt": "Test"
    }
  }
}
```

---

## Testing & Validation

### Running Tests

```bash
# Run comprehensive MCP tests
python tests/protocol/mcp/mcp_comprehensive_test.py

# Run Kimi-specific tests
python tests/protocol/mcp/test_kimi_complete_mcp.py

# Run configuration validation
python tests/validation/configuration_validation_test.py
```

### Validation Checklist

Before deploying MCP calls, verify:

- [ ] JSON-RPC 2.0 structure is correct
- [ ] Tool name matches exactly (case-sensitive)
- [ ] All required parameters are present
- [ ] Optional parameters are properly formatted
- [ ] Request ID is unique
- [ ] Response parsing handles both success and error cases

---

## Examples

### Complete Kimi k2-thinking Test

```bash
cat << 'EOF' | python tests/protocol/mcp/mcp_comprehensive_test.py
{
  "jsonrpc": "2.0",
  "id": "test_kimi",
  "method": "tools/call",
  "params": {
    "name": "kimi_chat_with_tools",
    "arguments": {
      "prompt": "Confirm you are kimi-k2-thinking with 256K context",
      "model": "kimi-k2-thinking"
    }
  }
}
EOF
```

### Model Discovery Test

```bash
cat << 'EOF' | python tests/protocol/mcp/mcp_comprehensive_test.py
{
  "jsonrpc": "2.0",
  "id": "discover_models",
  "method": "tools/call",
  "params": {
    "name": "listmodels",
    "arguments": {}
  }
}
EOF
```

### Analyze Workflow Test

```bash
cat << 'EOF' | python tests/protocol/mcp/mcp_comprehensive_test.py
{
  "jsonrpc": "2.0",
  "id": "analyze_workflow",
  "method": "tools/call",
  "params": {
    "name": "analyze",
    "arguments": {
      "step": "Test analyze workflow structure",
      "step_number": 1,
      "total_steps": 1,
      "next_step_required": false,
      "findings": "Successfully tested workflow",
      "files_checked": [],
      "relevant_files": [],
      "relevant_context": [],
      "issues_found": []
    }
  }
}
EOF
```

---

## Best Practices

1. **Always use unique request IDs** to track responses
2. **Validate responses** before parsing
3. **Handle errors gracefully** with try-catch blocks
4. **Use proper tool names** - check `tools/list` first
5. **Include all required fields** for complex tools like `analyze`
6. **Test with simple calls first** before complex workflows
7. **Monitor response times** for performance optimization

---

## Support

For issues or questions:
- Check test files in `tests/protocol/mcp/`
- Review server logs in `logs/`
- Validate configuration with `tests/validation/configuration_validation_test.py`

---

**Last Updated:** 2025-11-15
**Version:** 1.0.0
