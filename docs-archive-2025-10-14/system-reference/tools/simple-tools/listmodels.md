# listmodels_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Utility Tool  
**Related:** [version.md](version.md)

---

## Purpose

Display all available AI models organized by provider

---

## Use Cases

- Discover available models and their capabilities
- Understand which providers are configured
- Check model aliases and context windows
- Verify model availability before use

---

## Key Features

- **Provider organization** - Models grouped by provider (GLM, Kimi)
- **Model details** - Context windows, aliases, capabilities
- **Configuration status** - Shows which providers are active
- **Comprehensive listing** - All available models in one view

---

## Key Parameters

- `model` (optional): Ignored by listmodels tool

---

## Output Information

For each provider, displays:
- Provider name and status
- Available models
- Model aliases
- Context window sizes
- Special capabilities (streaming, web search, multimodal)

---

## Usage Examples

### Basic Usage
```
"List all available models"
```

### Check Specific Provider
```
"Show me all GLM models"
```

### Verify Configuration
```
"What models can I use?"
```

---

## Best Practices

- Run listmodels to discover available models before starting work
- Check context windows when working with large codebases
- Verify provider configuration if models are missing
- Use model aliases for convenience

---

## When to Use

- **Use `listmodels` for:** Discovering available models and their capabilities
- **Use `version` for:** Checking server version and configuration details
- **Use `chat` for:** Asking questions about model selection

---

## Related Tools

- [version.md](version.md) - Server version and configuration

