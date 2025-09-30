# MCP Evidence: listmodels

## Raw Output

# Available AI Models

## Moonshot Kimi ✅
**Status**: Configured and available

**Models**:
- `kimi-k2-0905-preview` - 128K context
- `kimi-k2-0711-preview` - 128K context
- `moonshot-v1-8k` - 8K context
- `moonshot-v1-32k` - 32K context
- `kimi-k2-turbo-preview` - 256K context
- `moonshot-v1-128k` - 128K context
- `moonshot-v1-8k-vision-preview` - 8K context
- `moonshot-v1-32k-vision-preview` - 32K context
- `moonshot-v1-128k-vision-preview` - 128K context
- `kimi-latest` - 128K context
- `kimi-thinking-preview` - 128K context

**Aliases**:
- `kimi-k2-0711` → `kimi-k2-0711-preview`
- `kimi-k2-0905` → `kimi-k2-0905-preview`
- `kimi-k2-turbo` → `kimi-k2-turbo-preview`
- `kimi-k2` → `kimi-k2-0905-preview`

## ZhipuAI GLM ✅
**Status**: Configured and available

**Models**:
- `glm-4.5-flash` - 128K context
- `glm-4.5` - 128K context
- `glm-4.5-air` - 128K context

**Aliases**:
- `glm-4.5-air` → `glm-4.5-flash`
- `glm-4.5-x` → `glm-4.5-air`

## OpenRouter ❌
**Status**: Not configured (set OPENROUTER_API_KEY)
**Note**: Provides access to GPT-5, O3, Mistral, and many more

## Custom/Local API ❌
**Status**: Not configured (set CUSTOM_API_URL)
**Example**: CUSTOM_API_URL=http://localhost:11434 (for Ollama)

## Summary
**Configured Providers**: 2
**Total Available Models**: 19

**Usage Tips**:
- Use model aliases (e.g., 'flash', 'gpt5', 'opus') for convenience
- In auto mode, the CLI Agent will select the best model for each task
- Custom models are only available when CUSTOM_API_URL is set
- OpenRouter provides access to many cloud models with one API key
