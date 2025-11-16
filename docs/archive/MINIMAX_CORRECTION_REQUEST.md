# MiniMax Model Correction Request

## Issue Identified

I incorrectly documented MiniMax model information in the implementation. I need to correct this based on the official documentation at: https://platform.minimax.io/docs/api-reference/text-anthropic-api

## What I Need Corrected

1. **Correct Model Names**: What are the actual available MiniMax models?
2. **Context Windows**: What are the actual context window sizes for each model?
3. **Capabilities**: What features does each model actually support?
   - Function calling support
   - Thinking/reasoning capabilities  
   - Vision capabilities
   - Streaming support
4. **Model Specifications**: Any other technical parameters I may have incorrect

## Current Implementation

The current MiniMax provider has hardcoded information that may be incorrect:

```python
SUPPORTED_MODELS = {
    "MiniMax-M2-Stable": ModelCapabilities(
        context_window=200000,
        supports_extended_thinking=True,
        supports_function_calling=False,
        supports_vision=False,
    )
}
```

## Request

Please provide the correct MiniMax model information so I can update:

1. `src/providers/minimax.py` - Provider implementation
2. `docs/api/provider-apis/minimax-api.md` - API documentation

This is important for accuracy and ensuring the MiniMax provider works correctly with the actual available models and their true capabilities.

## Alternative

If you prefer, I can provide a more generic MiniMax provider that only uses basic features that are likely to be common across most models, and then we can add specific model capabilities as we verify them.
