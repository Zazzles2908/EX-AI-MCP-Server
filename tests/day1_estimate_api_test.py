"""
Day 1 Integration Test - Estimate API and Duration Recording

Tests the adaptive timeout estimate API endpoint and duration recording functionality.

Created: 2025-11-03
Purpose: Validate Day 1 implementation before K2 review
"""

import asyncio
import aiohttp
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.monitoring.connection_monitor import get_monitor


async def test_estimate_api():
    """Test the /api/v1/timeout/estimate endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Estimate API Endpoint")
    print("="*60)
    
    # Test data
    test_cases = [
        {
            "name": "K2 with low confidence (should trigger estimate API)",
            "model": "kimi-k2",
            "messages": [
                {"role": "user", "content": "Test message"}
            ],
            "request_type": "text"
        },
        {
            "name": "GLM model",
            "model": "glm-4.6",
            "messages": [],
            "request_type": "text"
        },
        {
            "name": "K2 without messages (no estimate API call)",
            "model": "kimi-k2",
            "messages": [],
            "request_type": "text"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for test_case in test_cases:
            print(f"\n📝 Test: {test_case['name']}")
            print(f"   Model: {test_case['model']}")
            
            try:
                async with session.post(
                    'http://localhost:8081/api/v1/timeout/estimate',
                    json={
                        "model": test_case["model"],
                        "messages": test_case["messages"],
                        "request_type": test_case["request_type"]
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Status: {response.status}")
                        print(f"   Timeout: {data.get('timeout')}s")
                        print(f"   Confidence: {data.get('confidence')}")
                        print(f"   Source: {data.get('source')}")
                        print(f"   Provider: {data.get('metadata', {}).get('provider')}")
                        
                        if data.get('metadata', {}).get('estimated_tokens'):
                            print(f"   Estimated Tokens: {data['metadata']['estimated_tokens']}")
                    else:
                        print(f"   ❌ Status: {response.status}")
                        error_text = await response.text()
                        print(f"   Error: {error_text}")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")


async def test_duration_recording():
    """Test the ConnectionMonitor.record_duration() method"""
    print("\n" + "="*60)
    print("TEST 2: Duration Recording")
    print("="*60)
    
    monitor = get_monitor()
    
    # Test cases
    test_cases = [
        {
            "model": "kimi-k2",
            "duration_ms": 258000,  # 4.3 minutes (like the K2 call)
            "prompt_tokens": 1500,
            "completion_tokens": 500,
            "request_type": "text_only"
        },
        {
            "model": "glm-4.6",
            "duration_ms": 5000,  # 5 seconds
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "request_type": "text_only"
        },
        {
            "model": "kimi-k2",
            "duration_ms": 180000,  # 3 minutes
            "prompt_tokens": None,
            "completion_tokens": None,
            "request_type": "file_based"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['model']}")
        print(f"   Duration: {test_case['duration_ms']/1000:.1f}s")
        print(f"   Tokens: {test_case.get('prompt_tokens', 'N/A')} + {test_case.get('completion_tokens', 'N/A')}")
        
        try:
            monitor.record_duration(
                model=test_case["model"],
                duration_ms=test_case["duration_ms"],
                prompt_tokens=test_case["prompt_tokens"],
                completion_tokens=test_case["completion_tokens"],
                request_type=test_case["request_type"]
            )
            print(f"   ✅ Duration recorded successfully")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Verify events were recorded
    print("\n📊 Checking recorded events...")
    recent_events = monitor.get_recent_events(limit=10)
    adaptive_events = [e for e in recent_events if e.get('metadata', {}).get('adaptive_timeout')]
    
    print(f"   Total recent events: {len(recent_events)}")
    print(f"   Adaptive timeout events: {len(adaptive_events)}")
    
    if adaptive_events:
        print("\n   Latest adaptive timeout event:")
        latest = adaptive_events[0]
        print(f"   - Model: {latest.get('metadata', {}).get('model')}")
        print(f"   - Duration: {latest.get('metadata', {}).get('adaptive_timeout_ms', 0)/1000:.1f}s")
        print(f"   - Provider: {latest.get('connection_type')}")
        print(f"   - Request Type: {latest.get('metadata', {}).get('request_type')}")


async def test_adaptive_timeout_engine():
    """Test the adaptive timeout engine integration"""
    print("\n" + "="*60)
    print("TEST 3: Adaptive Timeout Engine")
    print("="*60)
    
    try:
        from src.core.adaptive_timeout import get_engine, is_adaptive_timeout_enabled
        
        print(f"\n📝 Adaptive Timeout Enabled: {is_adaptive_timeout_enabled()}")
        
        if is_adaptive_timeout_enabled():
            engine = get_engine()
            
            # Test timeout calculation for different models
            test_models = ["kimi-k2", "glm-4.6", "kimi-latest"]
            
            for model in test_models:
                timeout, metadata = engine.get_adaptive_timeout_safe(model, base_timeout=180)
                print(f"\n   Model: {model}")
                print(f"   Timeout: {timeout}s")
                print(f"   Confidence: {metadata.get('confidence', 0):.2f}")
                print(f"   Source: {metadata.get('source')}")
                print(f"   Samples: {metadata.get('samples_used', 0)}")
        else:
            print("   ⚠️  Adaptive timeout is disabled (ADAPTIVE_TIMEOUT_ENABLED=false)")
            print("   This is expected for Day 1 - feature flag is off by default")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("DAY 1 INTEGRATION TESTS - Adaptive Timeout Architecture")
    print("="*60)
    print("\nTesting:")
    print("1. Estimate API endpoint (/api/v1/timeout/estimate)")
    print("2. Duration recording (ConnectionMonitor.record_duration)")
    print("3. Adaptive timeout engine integration")
    print("\nNote: Monitoring server must be running on port 8081")
    print("="*60)
    
    # Run tests
    await test_estimate_api()
    await test_duration_recording()
    await test_adaptive_timeout_engine()
    
    print("\n" + "="*60)
    print("TESTS COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Check monitoring dashboard at http://localhost:8081/monitoring_dashboard.html")
    print("2. Verify timeout accuracy chart is visible")
    print("3. Review Day 1 completion report")
    print("4. Submit to K2 for validation")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

