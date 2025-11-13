"""
Test Provider Routing Bug

This script tests if Kimi models are being routed to the correct provider.
It should help us identify where the routing bug is occurring.
"""

import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging to see DEBUG output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment
from dotenv import load_dotenv
env_path = project_root / ".env.docker"
load_dotenv(env_path)

print(f"✅ Loaded environment from {env_path}")
print(f"✅ KIMI_API_KEY: {os.getenv('KIMI_API_KEY', '')[:10]}...")
print(f"✅ GLM_API_KEY: {os.getenv('GLM_API_KEY', '')[:10]}...")

# Initialize providers
from src.server.providers.provider_config import configure_providers
configure_providers()

# Test provider routing
from src.providers.registry import ModelProviderRegistry
from src.providers.registry_core import get_registry_instance

print("\n" + "="*80)
print("TESTING PROVIDER ROUTING")
print("="*80)

# Test 1: Get provider for Kimi model
print("\n📍 Test 1: Get provider for 'kimi-k2-0905-preview'")
provider = get_registry_instance().get_provider_for_model("kimi-k2-0905-preview")
if provider:
    print(f"✅ Provider type: {provider.get_provider_type()}")
    print(f"✅ Provider class: {provider.__class__.__name__}")
    print(f"✅ Base URL: {getattr(provider, 'base_url', 'N/A')}")
    
    # Check if it's the correct provider
    from src.providers.base import ProviderType
    if provider.get_provider_type() == ProviderType.KIMI:
        print("✅ CORRECT: Kimi model routed to Kimi provider")
    else:
        print(f"❌ WRONG: Kimi model routed to {provider.get_provider_type()} provider")
else:
    print("❌ No provider found for kimi-k2-0905-preview")

# Test 2: Get provider for GLM model
print("\n📍 Test 2: Get provider for 'glm-4.6'")
provider = get_registry_instance().get_provider_for_model("glm-4.6")
if provider:
    print(f"✅ Provider type: {provider.get_provider_type()}")
    print(f"✅ Provider class: {provider.__class__.__name__}")
    print(f"✅ Base URL: {getattr(provider, 'base_url', 'N/A')}")
    
    # Check if it's the correct provider
    from src.providers.base import ProviderType
    if provider.get_provider_type() == ProviderType.GLM:
        print("✅ CORRECT: GLM model routed to GLM provider")
    else:
        print(f"❌ WRONG: GLM model routed to {provider.get_provider_type()} provider")
else:
    print("❌ No provider found for glm-4.6")

# Test 3: Check provider priority order
print("\n📍 Test 3: Check provider priority order")
print(f"Priority order: {ModelProviderRegistry.PROVIDER_PRIORITY_ORDER}")

# Test 4: Check registered providers
print("\n📍 Test 4: Check registered providers")
registry = ModelProviderRegistry()
print(f"Registered providers: {list(registry._providers.keys())}")

# Test 5: Check Kimi provider validation
print("\n📍 Test 5: Check Kimi provider model validation")
from src.providers.base import ProviderType
from src.providers.registry_core import get_registry_instance
kimi_provider = ModelProviderRegistry.get_provider(ProviderType.KIMI)
if kimi_provider:
    validates = kimi_provider.validate_model_name("kimi-k2-0905-preview")
    print(f"Kimi provider validates 'kimi-k2-0905-preview': {validates}")
    print(f"Kimi provider base_url: {getattr(kimi_provider, 'base_url', 'N/A')}")
else:
    print("❌ Kimi provider not found")

# Test 6: Check GLM provider validation
print("\n📍 Test 6: Check GLM provider model validation")
glm_provider = ModelProviderRegistry.get_provider(ProviderType.GLM)
if glm_provider:
    validates = glm_provider.validate_model_name("kimi-k2-0905-preview")
    print(f"GLM provider validates 'kimi-k2-0905-preview': {validates}")
    print(f"GLM provider base_url: {getattr(glm_provider, 'base_url', 'N/A')}")
else:
    print("❌ GLM provider not found")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)

