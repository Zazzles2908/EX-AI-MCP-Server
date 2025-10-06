#!/usr/bin/env python
"""
Debug script to inspect what's in ModelResponse.metadata after a web search request.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

def test_model_response_structure():
    """Test what's in ModelResponse after web search"""
    try:
        from src.providers.registry import ModelProviderRegistry
        from src.providers.base import ProviderType
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    print("="*80)
    print("MODEL RESPONSE STRUCTURE DEBUG")
    print("="*80)
    
    # Get Kimi provider
    provider = ModelProviderRegistry.get_provider(ProviderType.KIMI)
    if not provider:
        print("❌ Kimi provider not available")
        return
    
    print(f"\n✓ Provider: {provider}")
    print(f"✓ Provider type: {provider.get_provider_type()}")
    
    # Test query
    test_query = "What is the current weather in Tokyo?"
    
    print(f"\n📝 Test Query: {test_query}")
    print(f"🔧 Web search enabled: True")
    print("\n" + "="*80)
    
    try:
        # Call generate_content with web search
        from src.providers.orchestration.websearch_adapter import build_websearch_provider_kwargs
        
        provider_kwargs, web_event = build_websearch_provider_kwargs(
            provider_type=provider.get_provider_type(),
            use_websearch=True,
            include_event=True
        )
        
        print(f"\n🔧 Provider kwargs: {json.dumps(provider_kwargs, indent=2)}")
        
        model_response = provider.generate_content(
            prompt=test_query,
            model_name="kimi-k2-0905-preview",
            system_prompt="You are a helpful assistant.",
            temperature=0.3,
            **provider_kwargs
        )
        
        print("\n" + "="*80)
        print("MODEL RESPONSE STRUCTURE:")
        print("="*80)
        
        print(f"\n✓ Content length: {len(model_response.content)} chars")
        print(f"✓ Model name: {model_response.model_name}")
        print(f"✓ Provider: {model_response.provider}")
        print(f"✓ Friendly name: {model_response.friendly_name}")
        
        print(f"\n📊 METADATA KEYS:")
        if hasattr(model_response, "metadata") and isinstance(model_response.metadata, dict):
            for key in model_response.metadata.keys():
                print(f"  - {key}")
            
            print(f"\n📋 FULL METADATA:")
            print(json.dumps(model_response.metadata, indent=2, default=str))
            
            # Check for raw
            if "raw" in model_response.metadata:
                raw = model_response.metadata["raw"]
                print(f"\n🔍 RAW RESPONSE TYPE: {type(raw)}")
                
                if isinstance(raw, dict):
                    print(f"\n🔍 RAW RESPONSE KEYS:")
                    for key in raw.keys():
                        print(f"  - {key}")
                    
                    # Check for tool_calls
                    if "choices" in raw:
                        choices = raw["choices"]
                        if choices and len(choices) > 0:
                            message = choices[0].get("message", {})
                            print(f"\n📨 MESSAGE KEYS:")
                            for key in message.keys():
                                print(f"  - {key}")
                            
                            if "tool_calls" in message:
                                tool_calls = message["tool_calls"]
                                print(f"\n🔧 TOOL_CALLS FOUND: {len(tool_calls) if tool_calls else 0}")
                                if tool_calls:
                                    print(json.dumps(tool_calls, indent=2))
                            else:
                                print(f"\n❌ NO tool_calls in message")
                                print(f"   finish_reason: {choices[0].get('finish_reason')}")
        else:
            print("❌ No metadata or metadata is not a dict")
        
        print(f"\n📝 CONTENT (first 500 chars):")
        print(model_response.content[:500])
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_model_response_structure()

