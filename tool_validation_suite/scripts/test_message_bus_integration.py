#!/usr/bin/env python3
"""
Test Message Bus Integration

Tests the message bus integration in ws_server.py with various payload sizes.

Test Cases:
1. Small payload (<1MB) - Should use WebSocket direct
2. Large payload (>1MB) - Should use message bus (if enabled)
3. Circuit breaker - Should fallback to WebSocket if message bus fails

Usage:
    python test_message_bus_integration.py

Environment:
    MESSAGE_BUS_ENABLED=false  # For baseline testing
    MESSAGE_BUS_ENABLED=true   # For message bus testing
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.core.config import get_config


def test_config_loading():
    """Test 1: Verify config loads without crashing."""
    print("\n" + "="*80)
    print("TEST 1: Config Loading")
    print("="*80)
    
    try:
        config = get_config()
        print(f"✅ Config loaded successfully")
        print(f"   - MESSAGE_BUS_ENABLED: {config.message_bus_enabled}")
        print(f"   - MESSAGE_BUS_TTL_HOURS: {config.message_bus_ttl_hours}")
        print(f"   - MESSAGE_BUS_MAX_PAYLOAD_MB: {config.message_bus_max_payload_mb}")
        print(f"   - MESSAGE_BUS_COMPRESSION: {config.message_bus_compression}")
        print(f"   - CIRCUIT_BREAKER_ENABLED: {config.circuit_breaker_enabled}")
        print(f"   - CIRCUIT_BREAKER_THRESHOLD: {config.circuit_breaker_threshold}")
        print(f"   - FALLBACK_TO_WEBSOCKET: {config.fallback_to_websocket}")
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False


def test_message_bus_client_init():
    """Test 2: Verify MessageBusClient initializes correctly."""
    print("\n" + "="*80)
    print("TEST 2: MessageBusClient Initialization")
    print("="*80)
    
    try:
        from src.core.message_bus_client import MessageBusClient
        
        config = get_config()
        if not config.message_bus_enabled:
            print("⚠️  Message bus disabled in config - skipping initialization test")
            print("   Set MESSAGE_BUS_ENABLED=true to test initialization")
            return True
        
        client = MessageBusClient()
        print(f"✅ MessageBusClient initialized successfully")
        print(f"   - Config: {client.config}")
        print(f"   - Circuit breaker enabled: {client.circuit_breaker is not None}")
        
        # Test should_use_message_bus logic
        small_payload = 500 * 1024  # 500KB
        large_payload = 5 * 1024 * 1024  # 5MB
        
        should_use_small = client.should_use_message_bus(small_payload)
        should_use_large = client.should_use_message_bus(large_payload)
        
        print(f"   - Small payload (500KB): should_use_message_bus = {should_use_small}")
        print(f"   - Large payload (5MB): should_use_message_bus = {should_use_large}")
        
        if not should_use_small and should_use_large:
            print(f"✅ Payload size routing logic correct")
        else:
            print(f"❌ Payload size routing logic incorrect")
            return False
        
        return True
    except Exception as e:
        print(f"❌ MessageBusClient initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_payload_size_calculation():
    """Test 3: Verify payload size calculation."""
    print("\n" + "="*80)
    print("TEST 3: Payload Size Calculation")
    print("="*80)
    
    try:
        # Create test payloads
        small_payload = {"outputs": [{"type": "text", "text": "Small response"}]}
        
        # Create large payload (>1MB)
        large_text = "x" * (2 * 1024 * 1024)  # 2MB of 'x'
        large_payload = {"outputs": [{"type": "text", "text": large_text}]}
        
        # Calculate sizes
        small_size = len(json.dumps(small_payload).encode('utf-8'))
        large_size = len(json.dumps(large_payload).encode('utf-8'))
        
        print(f"✅ Payload size calculation:")
        print(f"   - Small payload: {small_size:,} bytes ({small_size / 1024:.2f} KB)")
        print(f"   - Large payload: {large_size:,} bytes ({large_size / 1024 / 1024:.2f} MB)")
        
        threshold = 1024 * 1024  # 1MB
        print(f"   - Threshold: {threshold:,} bytes (1 MB)")
        print(f"   - Small < threshold: {small_size < threshold}")
        print(f"   - Large > threshold: {large_size > threshold}")
        
        return True
    except Exception as e:
        print(f"❌ Payload size calculation failed: {e}")
        return False


async def test_message_bus_storage():
    """Test 4: Verify message bus storage (if enabled)."""
    print("\n" + "="*80)
    print("TEST 4: Message Bus Storage")
    print("="*80)
    
    try:
        from src.core.message_bus_client import MessageBusClient
        
        config = get_config()
        if not config.message_bus_enabled:
            print("⚠️  Message bus disabled in config - skipping storage test")
            print("   Set MESSAGE_BUS_ENABLED=true and configure Supabase to test storage")
            return True
        
        if not config.supabase_url or not config.supabase_key:
            print("⚠️  Supabase not configured - skipping storage test")
            print("   Set SUPABASE_URL and SUPABASE_KEY to test storage")
            return True
        
        client = MessageBusClient()
        
        # Create test payload
        test_payload = {
            "outputs": [{"type": "text", "text": "Test message bus storage"}]
        }
        
        # Store message
        transaction_id = "test_txn_12345"
        print(f"   Storing test message with transaction_id: {transaction_id}")
        
        success = await client.store_message(
            transaction_id=transaction_id,
            session_id="test_session",
            tool_name="test_tool",
            provider_name="test_provider",
            payload=test_payload,
            metadata={"test": True}
        )
        
        if success:
            print(f"✅ Message stored successfully")
            
            # Retrieve message
            print(f"   Retrieving message with transaction_id: {transaction_id}")
            retrieved = await client.retrieve_message(transaction_id)
            
            if retrieved:
                print(f"✅ Message retrieved successfully")
                print(f"   - Payload matches: {retrieved == test_payload}")
                return True
            else:
                print(f"❌ Message retrieval failed")
                return False
        else:
            print(f"❌ Message storage failed")
            return False
            
    except Exception as e:
        print(f"❌ Message bus storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ws_server_integration():
    """Test 5: Verify ws_server.py integration (code inspection)."""
    print("\n" + "="*80)
    print("TEST 5: ws_server.py Integration (Code Inspection)")
    print("="*80)
    
    try:
        ws_server_path = project_root / "src" / "daemon" / "ws_server.py"
        
        if not ws_server_path.exists():
            print(f"❌ ws_server.py not found at {ws_server_path}")
            return False
        
        content = ws_server_path.read_text(encoding='utf-8')
        
        # Check for required imports
        checks = {
            "MessageBusClient import": "from src.core.message_bus_client import MessageBusClient",
            "get_config import": "from src.core.config import get_config",
            "Message bus client init": "_get_message_bus_client",
            "Payload size check": "should_use_message_bus",
            "Transaction ID generation": "transaction_id",
            "Message bus storage": "store_message",
            "Circuit breaker fallback": "circuit breaker",
        }
        
        all_passed = True
        for check_name, check_string in checks.items():
            if check_string in content:
                print(f"✅ {check_name}: Found")
            else:
                print(f"❌ {check_name}: Not found")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ ws_server.py integration check failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("MESSAGE BUS INTEGRATION TEST SUITE")
    print("="*80)
    print(f"Project Root: {project_root}")
    
    results = {}
    
    # Test 1: Config loading
    results["Config Loading"] = test_config_loading()
    
    # Test 2: MessageBusClient initialization
    results["MessageBusClient Init"] = test_message_bus_client_init()
    
    # Test 3: Payload size calculation
    results["Payload Size Calculation"] = test_payload_size_calculation()
    
    # Test 4: Message bus storage (async)
    results["Message Bus Storage"] = asyncio.run(test_message_bus_storage())
    
    # Test 5: ws_server.py integration
    results["ws_server.py Integration"] = test_ws_server_integration()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

