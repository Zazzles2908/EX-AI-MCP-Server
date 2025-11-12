#!/usr/bin/env python3
"""
Quick test of newly created components
"""

import sys
sys.path.append('/workspace')

print("=== TESTING NEWLY CREATED COMPONENTS ===\n")

# Test registry_core
try:
    from src.providers.registry_core import get_registry_instance, ProviderType
    registry = get_registry_instance()
    print("✅ Provider Registry: Successfully imported and initialized")
    print(f"   Available providers: {len(registry.get_available_providers())}")
    print(f"   Total providers: {len(registry.get_all_providers())}")
except Exception as e:
    print(f"❌ Provider Registry: {e}")

print()

# Test routing_cache
try:
    from src.router.routing_cache import get_routing_cache, CacheStrategy
    cache = get_routing_cache()
    print("✅ Routing Cache: Successfully imported and initialized")
    print(f"   Default TTL: {cache.default_ttl}s, Max size: {cache.max_size}")
    
    # Test caching functionality
    cache.set("test_category", "test_key", {"data": "test_value"})
    result = cache.get("test_category", "test_key")
    print(f"   Cache test: {'✅ Working' if result else '❌ Failed'}")
    
except Exception as e:
    print(f"❌ Routing Cache: {e}")

print()

# Test models
try:
    from tools.models import ToolModelCategory, CategoryMapping
    category = CategoryMapping.get_category_for_tool('test_tool')
    print("✅ Tool Models: Successfully imported and initialized")
    print(f"   Test category for 'test_tool': {category.value}")
    
    # Test model recommendations
    recommended = CategoryMapping.get_recommended_models(category)
    print(f"   Recommended models: {recommended[:3]}...")  # Show first 3
    
except Exception as e:
    print(f"❌ Tool Models: {e}")

print("\n=== INTEGRATION TEST ===\n")

# Test full integration
try:
    # Get registry and cache instances
    registry = get_registry_instance()
    cache = get_routing_cache()
    
    # Test provider availability
    available_providers = registry.get_available_providers()
    print(f"✅ Integration: Registry has {len(available_providers)} available providers")
    
    # Test cache functionality with provider data
    cache.set("provider_status", "available", available_providers)
    cached_providers = cache.get("provider_status", "available")
    print(f"✅ Integration: Cached {len(cached_providers)} providers successfully")
    
    print("\n🎉 ALL CORE COMPONENTS WORKING!")
    
except Exception as e:
    print(f"❌ Integration test failed: {e}")