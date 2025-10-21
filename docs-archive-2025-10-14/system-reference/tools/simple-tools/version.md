# version_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Utility Tool  
**Related:** [listmodels.md](listmodels.md)

---

## Purpose

Get server version, configuration details, and list of available tools

---

## Use Cases

- Check server version and build information
- Verify configuration settings
- List all available tools
- Debug server setup issues
- Understand server capabilities

---

## Key Features

- **Version information** - Server version and build details
- **Configuration details** - Active providers, settings, features
- **Tool listing** - All available tools and their categories
- **Diagnostic information** - Helpful for troubleshooting

---

## Key Parameters

- `model` (optional): Ignored by version tool

---

## Output Information

Displays:
- Server version number
- Build date and commit hash
- Active providers (GLM, Kimi)
- Configuration settings
- Available tools (simple, workflow, utility)
- Feature flags and capabilities

---

## Usage Examples

### Basic Usage
```
"Show server version"
```

### Configuration Check
```
"What's the current server configuration?"
```

### Troubleshooting
```
"Display version and configuration for debugging"
```

---

## Best Practices

- Run version check after server updates
- Use for troubleshooting configuration issues
- Verify tool availability before use
- Check feature flags for capability verification

---

## When to Use

- **Use `version` for:** Checking server version and configuration
- **Use `listmodels` for:** Discovering available AI models
- **Use `chat` for:** Asking questions about server capabilities

---

## Related Tools

- [listmodels.md](listmodels.md) - List available AI models

