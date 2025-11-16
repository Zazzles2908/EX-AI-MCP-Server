"""
Test Suite for Parallax-Inspired KV Cache Management

This test suite validates the KV cache implementation including:
- Cache operations (get, set, delete)
- TTL and expiration handling
- Memory management and eviction
- Conversation context caching
- Provider integration
- Performance metrics
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, '/app/src')

from providers.kv_cache_manager import ParallaxKVCacheManager, get_kv_cache
from providers.conversation_context_cache import get_conversation_cache, ConversationContextCache
from providers.cached_provider_wrapper import create_cached_provider


async def test_kv_cache_basic_operations():
    """Test basic KV cache operations."""
    print("\n🧪 Testing basic KV cache operations...")
    
    cache = ParallaxKVCacheManager(max_size_mb=10, max_entries=100)
    
    # Test set and get
    await cache.set("test_key", {"data": "test_value"})
    value = await cache.get("test_key")
    assert value == {"data": "test_value"}, "Basic set/get failed"
    print("✅ Basic set/get works")
    
    # Test TTL
    await cache.set("ttl_key", {"data": "ttl_value"}, ttl=1)
    assert await cache.get("ttl_key") is not None, "TTL entry should exist immediately"
    await asyncio.sleep(1.1)
    assert await cache.get("ttl_key") is None, "TTL entry should expire"
    print("✅ TTL expiration works")
    
    # Test tags
    await cache.set("tagged_key", {"data": "tagged"}, tags={"user:123", "session:abc"})
    await cache.set("other_key", {"data": "other"}, tags={"user:456"})
    
    tagged_data = await cache.get_by_tags({"user:123"})
    assert "tagged_key" in tagged_data, "Tag-based lookup failed"
    print("✅ Tag-based lookup works")
    
    # Test existence
    assert await cache.exists("test_key"), "Existence check failed"
    await cache.delete("test_key")
    assert not await cache.exists("test_key"), "Delete failed"
    print("✅ Existence check and delete work")
    
    await cache.close()
    print("✅ Basic operations test completed")


async def test_kv_cache_memory_management():
    """Test memory management and eviction."""
    print("\n🧪 Testing memory management and eviction...")
    
    # Small cache to force evictions
    cache = ParallaxKVCacheManager(max_size_mb=1, max_entries=10)
    
    # Add multiple entries to trigger eviction
    for i in range(15):
        await cache.set(f"key_{i}", {"data": f"value_{i}" * 100})  # Large values
    
    # Check that we don't exceed limits
    assert len(cache) <= 10, f"Entry count exceeded limit: {len(cache)}"
    print("✅ Memory management and LRU eviction works")
    
    await cache.close()


async def test_conversation_context_cache():
    """Test conversation context caching."""
    print("\n🧪 Testing conversation context cache...")
    
    kv_cache = await get_kv_cache()
    conv_cache = ConversationContextCache(
        cache_manager=kv_cache,
        enable_response_caching=True,
        max_conversation_history=10
    )
    
    # Test context caching
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"}
    ]
    
    success = await conv_cache.cache_conversation_context(
        conversation_id="test_conv_123",
        messages=messages,
        provider="test_provider",
        model="test_model",
        metadata={"topic": "greeting"}
    )
    assert success, "Context caching failed"
    
    # Retrieve context
    context = await conv_cache.get_conversation_context(
        conversation_id="test_conv_123",
        provider="test_provider",
        model="test_model"
    )
    assert context is not None, "Context retrieval failed"
    assert len(context.messages) == 3, f"Wrong message count: {len(context.messages)}"
    
    print("✅ Conversation context caching works")
    
    # Test response caching
    response_cached = await conv_cache.cache_response(
        provider="test_provider",
        model="test_model",
        messages=messages,
        response_content="I'm doing well, thanks!",
        usage={"input_tokens": 10, "output_tokens": 8}
    )
    assert response_cached, "Response caching failed"
    
    # Try to retrieve cached response
    cached_response = await conv_cache.get_cached_response(
        provider="test_provider",
        model="test_model",
        messages=messages
    )
    assert cached_response is not None, "Cached response retrieval failed"
    assert cached_response.content == "I'm doing well, thanks!", "Wrong cached content"
    
    print("✅ Response caching and retrieval works")


async def test_cached_provider_wrapper():
    """Test cached provider wrapper."""
    print("\n🧪 Testing cached provider wrapper...")
    
    # Create a mock provider
    class MockProvider:
        def __init__(self):
            self.call_count = 0
        
        def get_provider_type(self):
            from providers.base import ProviderType
            return ProviderType.CUSTOM
        
        async def chat_completions_create(self, **kwargs):
            self.call_count += 1
            return {
                "provider": "mock",
                "model": kwargs.get("model", "test"),
                "content": f"Response {self.call_count}",
                "usage": {"input_tokens": 5, "output_tokens": 10}
            }
    
    mock_provider = MockProvider()
    kv_cache = await get_kv_cache()
    conv_cache = ConversationContextCache(kv_cache)
    
    from providers.cached_provider_wrapper import CachedModelProvider
    
    cached_provider = CachedModelProvider(
        provider=mock_provider,
        conversation_cache=conv_cache,
        enable_context_caching=True,
        enable_response_caching=True
    )
    
    # Test first call - should hit the provider
    messages = [{"role": "user", "content": "test"}]
    response1 = await cached_provider.chat_completions_create(
        model="test",
        messages=messages,
        conversation_id="test_conv"
    )
    
    assert mock_provider.call_count == 1, "First call should hit provider"
    assert response1["content"] == "Response 1", "Wrong response content"
    
    # Test second call with same parameters - should use cache
    response2 = await cached_provider.chat_completions_create(
        model="test",
        messages=messages,
        conversation_id="test_conv"
    )
    
    assert mock_provider.call_count == 1, "Second call should use cache"
    assert response2["content"] == "Response 1", "Should return cached response"
    assert response2["metadata"]["cached"] is True, "Should mark as cached"
    
    print("✅ Cached provider wrapper works")
    
    # Test conversation context caching
    context = await cached_provider.get_conversation_context("test_conv", "test")
    assert context is not None, "Context should be cached"
    
    print("✅ Conversation context integration works")


async def test_performance_metrics():
    """Test performance metrics collection."""
    print("\n🧪 Testing performance metrics...")
    
    cache = ParallaxKVCacheManager(
        max_size_mb=10,
        max_entries=50,
        enable_metrics=True
    )
    
    # Perform various operations
    for i in range(10):
        await cache.set(f"key_{i}", {"data": f"value_{i}"})
        await cache.get(f"key_{i}")
    
    # Test miss
    await cache.get("nonexistent_key")
    
    # Get metrics
    metrics = cache.get_metrics()
    
    assert "hits" in metrics, "Hits metric missing"
    assert "misses" in metrics, "Misses metric missing"
    assert "hit_rate" in metrics, "Hit rate metric missing"
    assert metrics["hits"] == 10, f"Wrong hits count: {metrics['hits']}"
    assert metrics["misses"] == 1, f"Wrong misses count: {metrics['misses']}"
    assert metrics["hit_rate"] == 10/11, f"Wrong hit rate: {metrics['hit_rate']}"
    
    print("✅ Performance metrics collection works")
    
    await cache.close()


async def test_cache_warming():
    """Test cache warming functionality."""
    print("\n🧪 Testing cache warming...")
    
    cache = ParallaxKVCacheManager(max_size_mb=10, max_entries=50)
    
    warming_data = {
        "warm_key_1": {
            "value": {"data": "warm_data_1"},
            "ttl": 3600,
            "tags": {"warm", "test"}
        },
        "warm_key_2": {
            "value": {"data": "warm_data_2"},
            "ttl": 1800,
            "tags": {"warm"}
        }
    }
    
    await cache.warm_cache(warming_data)
    
    # Verify warmed data
    value1 = await cache.get("warm_key_1")
    value2 = await cache.get("warm_key_2")
    
    assert value1 == {"data": "warm_data_1"}, "Warm data 1 incorrect"
    assert value2 == {"data": "warm_data_2"}, "Warm data 2 incorrect"
    
    print("✅ Cache warming works")
    
    await cache.close()


async def run_comprehensive_tests():
    """Run all cache tests."""
    print("🚀 Running Parallax KV Cache Management Tests...")
    print("=" * 60)
    
    tests = [
        test_kv_cache_basic_operations,
        test_kv_cache_memory_management,
        test_conversation_context_cache,
        test_cached_provider_wrapper,
        test_performance_metrics,
        test_cache_warming
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All KV cache tests passed! Parallax-inspired caching is working correctly!")
        
        # Show cache statistics
        kv_cache = await get_kv_cache()
        stats = kv_cache.get_metrics()
        print(f"\n📈 Cache Statistics:")
        print(f"   Total entries: {len(kv_cache)}")
        print(f"   Hit rate: {stats.get('hit_rate', 0):.2%}")
        print(f"   Current size: {stats.get('current_size_mb', 0):.2f} MB")
        print(f"   Memory usage: {stats.get('total_size_bytes', 0) / (1024*1024):.2f} MB")
        
        return True
    else:
        print(f"⚠️  {failed} test(s) failed. Check implementation.")
        return False


async def cleanup():
    """Cleanup test resources."""
    from providers.kv_cache_manager import close_kv_cache
    from providers.conversation_context_cache import close_conversation_cache
    
    await close_conversation_cache()
    await close_kv_cache()


if __name__ == "__main__":
    async def main():
        success = await run_comprehensive_tests()
        await cleanup()
        sys.exit(0 if success else 1)
    
    asyncio.run(main())
