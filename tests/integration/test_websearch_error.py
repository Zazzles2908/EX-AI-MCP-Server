#!/usr/bin/env python3
"""
Test the actual websearch call that might trigger the _model_name error
"""

import sys
sys.path.insert(0, 'C:/Project/EX-AI-MCP-Server/src')
sys.path.insert(0, 'C:/Project/EX-AI-MCP-Server')

try:
    from src.providers.orchestration.websearch_adapter import build_websearch_provider_kwargs
    from src.providers import ProviderType

    # Test with model name - this is what gets called in base.py line 562
    model_name = "glm-4.5-flash"
    provider_type = ProviderType.GLM

    print(f"Testing build_websearch_provider_kwargs with model_name={model_name}")

    provider_kwargs, web_event = build_websearch_provider_kwargs(
        provider_type=provider_type,
        use_websearch=True,
        model_name=model_name,
        include_event=True,
    )

    print(f"[OK] Success! provider_kwargs: {provider_kwargs}")
    print(f"[OK] web_event: {web_event}")

except Exception as e:
    print(f"\n[ERROR] Error occurred: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
