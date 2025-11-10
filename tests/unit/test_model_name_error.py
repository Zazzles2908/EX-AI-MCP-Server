#!/usr/bin/env python3
"""
Test to reproduce the _model_name error
"""

import sys
import os

# Add the source to the path
sys.path.insert(0, 'C:/Project/EX-AI-MCP-Server/src')
sys.path.insert(0, 'C:/Project/EX-AI-MCP-Server')

try:
    # Try to import the GLM provider
    from src.providers.glm import GLMModelProvider
    print("[OK] Imported GLMModelProvider successfully")

    # Try to create an instance
    provider = GLMModelProvider(api_key="test")
    print("[OK] Created GLMModelProvider instance")

    # Try to call a method that might trigger the error
    models = provider.get_all_model_aliases()
    print(f"[OK] Got model aliases: {models}")

    # Try to get all available models - use the correct method
    all_models = provider.list_models()
    print(f"[OK] Got available models: {len(all_models)} models")

    print("\n[SUCCESS] No errors detected!")

except Exception as e:
    print(f"\n[ERROR] Error occurred: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
