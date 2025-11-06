# EXAI Provider Capability Matrix & Usage Guide

> **Document Version:** 2.0.0
> **Last Updated:** 2025-11-05
> **Status:** ACTIVE

---

## 📊 Provider Capability Overview

This document provides a comprehensive capability matrix for the EXAI MCP Server's multi-provider architecture, helping you choose the right provider for your specific use case.

### **Provider Comparison**

| Feature | GLM (ZhipuAI) | Kimi (Moonshot) |
|---------|---------------|-----------------|
| **Basic Chat** | ✅ Full Support | ✅ Full Support |
| **File Analysis** | ❌ Limited/No Support | ✅ Full Support |
| **File Size Limit** | 20MB | 100MB |
| **File Persistence** | ❌ No (re-upload required) | ✅ Yes (SHA256 deduplication) |
| **Thinking Mode** | ❌ Not Supported | ✅ Supported |
| **Concurrent Requests** | ✅ Supported | ✅ Supported |
| **Rate Limits** | Standard | Enhanced |
| **Best For** | Text generation, code assistance | File analysis, complex workflows |

---

## 🔧 Provider Selection Strategy

### **When to Use GLM Provider**

The GLM (ZhipuAI) provider is ideal for:

1. **Quick text-based conversations** without file attachments
2. **Code generation and assistance** where no file context is needed
3. **Cost-sensitive operations** on smaller tasks
4. **High-volume text processing** with simple prompts

**Example Usage:**
```
@exai-mcp chat "Explain the difference between synchronous and asynchronous programming in Python"
Model: glm-4.5-flash
Result: ✅ Works perfectly
```

### **When to Use Kimi Provider**

The Kimi (Moonshot) provider is required for:

1. **File analysis operations** (any file size up to 100MB)
2. **Complex workflows requiring thinking mode**
3. **Operations involving document processing**
4. **Multi-step reasoning tasks**

**Example Usage:**
```
@exai-mcp smart_file_query file_path="/mnt/project/EX-AI-MCP-Server/src/main.py" question="Analyze this code for potential improvements"
Result: ✅ Automatically uses Kimi (file analysis requires Kimi)
```

---

## ⚠️ Critical Limitations & Provider Switching

### **File Analysis Limitation**

**IMPORTANT:** File analysis operations **REQUIRE** the Kimi provider. If you request GLM for file operations:

```python
# This will NOT work as expected
@exai-mcp smart_file_query file_path="..." question="..." provider="glm"
# Result: Automatically switches to Kimi with explanation
```

**What Happens:**
1. System detects GLM request for file operation
2. Automatically switches to Kimi provider
3. Returns explanation: "GLM-4.5-Flash cannot analyze files (20MB limit, no persistence). Switching to Kimi provider..."
4. Performs analysis with Kimi

### **Thinking Mode Limitation**

GLM provider **DOES NOT SUPPORT** thinking mode. If you attempt to use thinking_mode with GLM:

```python
# This will FAIL
@exai-mcp chat model="glm-4.5-flash" prompt="..." thinking_mode="enabled"
# Result: TypeError: Completions.create() got an unexpected keyword argument 'thinking_mode'
```

**Solution:** Use Kimi provider for thinking mode operations:

```python
# This will work
@exai-mcp chat model="kimi-thinking-preview" prompt="..." kimi_thinking="enabled"
# Result: ✅ Detailed analysis with thinking process
```

---

## 🛠️ EXAI Tools & Provider Requirements

### **GLM-Compatible Tools**

| Tool | GLM Support | Notes |
|------|------------|-------|
| `chat` | ✅ Yes | Standard chat operations only |
| `glm` tools | ✅ Yes | GLM-specific tools work correctly |

### **Kimi-Required Tools**

| Tool | Kimi Required | Notes |
|------|---------------|-------|
| `smart_file_query` | ✅ Yes | File analysis requires Kimi |
| `kimi_*` tools | ✅ Yes | All Kimi-specific tools |
| `thinking_mode` workflows | ✅ Yes | Only Kimi supports thinking |

### **Provider-Agnostic Tools**

| Tool | Both Providers | Notes |
|------|----------------|-------|
| `listmodels` | ✅ Yes | Lists available models |
| `status` | ✅ Yes | System status check |
| `version` | ✅ Yes | Version information |

---

## 🔄 Automatic Provider Selection

The EXAI MCP Server uses intelligent provider selection based on operation type:

```python
# Logic in smart_file_query.py
def _select_provider(file_size_mb, provider_pref):
    if file_size_mb > 100:
        raise ValueError(f"File size exceeds maximum limit of 100MB")

    if provider_pref == "glm":
        # UX FIX: Provide clear message when GLM is requested
        message = (
            f"GLM-4.5-Flash cannot analyze files (20MB limit, no persistence). "
            f"Switching to Kimi provider (100MB limit, persistent uploads)."
        )
        return "kimi", message

    # All file operations use Kimi
    return "kimi", f"Using Kimi provider for file analysis"
```

---

## 💡 Best Practices

### **For File Operations**

1. **Always use Kimi provider** for file analysis
2. **Check file size first** (max 100MB for Kimi, 20MB for GLM)
3. **Use deduplication** to avoid re-uploading files
4. **Monitor file size** with: `os.path.getsize(file_path) / (1024 * 1024)`

### **For Workflow Tools**

1. **Use Kimi for thinking mode** operations (debug, analyze, codereview)
2. **Check provider capability** before using thinking_mode
3. **Handle provider fallback** gracefully

### **For Cost Optimization**

1. **Use GLM for simple text operations** without file context
2. **Switch to Kimi only when necessary** (files, thinking mode)
3. **Monitor API usage** with built-in metrics

---

## 📝 Example Usage Scenarios

### **Scenario 1: Code Review Without Files**

```bash
# Use GLM for quick code review
@exai-mcp chat "Review this Python function for potential improvements:
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"
Model: glm-4.5-flash
Result: ✅ Fast response, no provider switching
```

### **Scenario 2: File Analysis**

```bash
# File analysis automatically uses Kimi
@exai-mcp smart_file_query file_path="/path/to/large_file.py" question="Identify performance bottlenecks"
Model: glm-4.5-flash (requested)
Result: ✅ Automatically switches to Kimi with explanation
```

### **Scenario 3: Complex Debugging with Thinking**

```bash
# Thinking mode requires Kimi
@exai-mcp chat "Debug this issue step by step" kimi_thinking="enabled"
Model: kimi-thinking-preview
Result: ✅ Detailed step-by-step analysis
```

---

## 🚨 Error Handling

### **Common Errors & Solutions**

#### **Error: "Not found the model glm-4.5-flash" (File Analysis)**
```python
# Solution: Don't specify provider for file analysis
@exai-mcp smart_file_query file_path="..." question="..."
# Let system automatically select Kimi
```

#### **Error: "thinking_mode not supported"**
```python
# Solution: Use Kimi provider for thinking mode
@exai-mcp chat prompt="..." kimi_thinking="enabled" model="kimi-thinking-preview"
```

#### **Error: "File size exceeds limit"**
```python
# Solution: Check file size before operation
file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
if file_size_mb > 100:
    raise ValueError(f"File size {file_size_mb:.2f}MB exceeds 100MB limit")
```

---

## 📊 Performance Metrics

### **Typical Response Times**

| Operation | GLM | Kimi |
|-----------|-----|------|
| Basic Chat | ~2s | ~2s |
| File Analysis (1MB) | N/A | ~5s |
| File Analysis (10MB) | N/A | ~15s |
| Thinking Mode | N/A | ~10s |

### **Throughput Limits**

| Provider | Concurrent Requests | Rate Limit |
|----------|---------------------|------------|
| GLM | 10 | 100/min |
| Kimi | 20 | 200/min |

---

## 🔍 Monitoring & Debugging

### **Check Provider Selection**

```python
# Enable debug logging
import logging
logging.getLogger('tools.smart_file_query').setLevel(logging.DEBUG)

# Check provider selection in logs
logger.debug(f"[SMART_FILE_QUERY] Selected provider: {provider}")
logger.info(f"[SMART_FILE_QUERY] Provider selection: {provider_message}")
```

### **Validate Provider Capabilities**

```python
# Check if provider supports thinking mode
def supports_thinking_mode(provider):
    return provider == "kimi"

# Check if provider supports file operations
def supports_file_operations(provider):
    return provider == "kimi"
```

---

## 📚 Additional Resources

- **API Reference:** `docs/02_Reference/API_REFERENCE.md`
- **System Architecture:** `docs/01_Core_Architecture/SYSTEM_ARCHITECTURE.md`
- **Developer Guide:** `docs/04_Development/HANDOVER_GUIDE.md`
- **Validation Reports:** `docs/05_CURRENT_WORK/validation_reports/`

---

**Document Maintained By:** EX-AI MCP Server Team
**For Updates & Questions:** Contact the development team