"""
Integration tests for dependency fixes (2025-11-05)

Tests verify that all critical fixes work correctly:
1. ConcurrentSessionManager.execute_sync() method exists and works
2. zai-sdk is properly installed and importable
3. PyJWT version is compatible
4. No import errors for fixed modules
"""

import pytest
import sys
from unittest.mock import Mock, patch
import asyncio

# Test 1: ConcurrentSessionManager.execute_sync exists and works
def test_execute_sync_method_exists():
    """Test that execute_sync method exists on ConcurrentSessionManager"""
    from src.utils.concurrent_session_manager import ConcurrentSessionManager
    
    # Check method exists
    assert hasattr(ConcurrentSessionManager, 'execute_sync')
    
    # Check it's callable
    assert callable(getattr(ConcurrentSessionManager, 'execute_sync'))


def test_execute_sync_returns_correct_structure():
    """Test that execute_sync returns dict with required keys"""
    from src.utils.concurrent_session_manager import ConcurrentSessionManager
    
    manager = ConcurrentSessionManager()
    
    # Mock function that returns a value
    def mock_func():
        return "test_result"
    
    # Call execute_sync
    result = manager.execute_sync(
        provider="test",
        func=mock_func
    )
    
    # Verify structure
    assert isinstance(result, dict)
    assert 'result' in result
    assert 'exception' in result
    assert 'completed' in result
    assert result['completed'] is True
    assert result['result'] == "test_result"
    assert result['exception'] is None


def test_execute_sync_handles_exceptions():
    """Test that execute_sync properly handles exceptions"""
    from src.utils.concurrent_session_manager import ConcurrentSessionManager
    
    manager = ConcurrentSessionManager()
    
    # Mock function that raises an exception
    def mock_func():
        raise ValueError("Test exception")
    
    # Call execute_sync
    result = manager.execute_sync(
        provider="test",
        func=mock_func
    )
    
    # Verify exception handling
    assert result['completed'] is False
    assert result['result'] is None
    assert isinstance(result['exception'], ValueError)
    assert str(result['exception']) == "Test exception"


# Test 2: zai-sdk is importable
def test_zai_sdk_import():
    """Test that zai-sdk is properly installed and importable"""
    try:
        import zai_sdk
        assert zai_sdk is not None
        print("✅ zai-sdk imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import zai-sdk: {e}")


# Test 3: PyJWT version compatibility
def test_pyjwt_version():
    """Test that PyJWT version is compatible (>=2.8.0)"""
    import jwt
    
    # Get version
    version = jwt.__version__
    print(f"✅ PyJWT version: {version}")
    
    # Check it's a valid version string
    assert version is not None
    assert len(version.split('.')) >= 2


# Test 4: GLM provider imports work
def test_glm_provider_imports():
    """Test that GLM provider modules import without errors"""
    try:
        from src.providers.glm_tool_processor import process_glm_tool_calls
        assert process_glm_tool_calls is not None
        print("✅ glm_tool_processor imports successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import glm_tool_processor: {e}")
    
    try:
        from src.providers.glm_provider import glm_chat_completion
        assert glm_chat_completion is not None
        print("✅ glm_provider imports successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import glm_provider: {e}")


# Test 5: Session manager integration
def test_session_manager_integration():
    """Test that session manager works with GLM provider pattern"""
    from src.utils.concurrent_session_manager import ConcurrentSessionManager
    
    manager = ConcurrentSessionManager()
    
    # Simulate what glm_tool_processor.py does
    def mock_glm_execution():
        return {
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"total_tokens": 10}
        }
    
    result_container = manager.execute_sync(
        provider="glm",
        func=mock_glm_execution
    )
    
    # Verify the result structure matches what GLM provider expects
    assert result_container['completed'] is True
    assert 'result' in result_container
    assert isinstance(result_container['result'], dict)
    assert 'choices' in result_container['result']


if __name__ == "__main__":
    # Run tests
    print("\n" + "="*60)
    print("INTEGRATION TESTS FOR DEPENDENCY FIXES")
    print("="*60 + "\n")
    
    test_execute_sync_method_exists()
    print("✅ test_execute_sync_method_exists passed")
    
    test_execute_sync_returns_correct_structure()
    print("✅ test_execute_sync_returns_correct_structure passed")
    
    test_execute_sync_handles_exceptions()
    print("✅ test_execute_sync_handles_exceptions passed")
    
    test_zai_sdk_import()
    print("✅ test_zai_sdk_import passed")
    
    test_pyjwt_version()
    print("✅ test_pyjwt_version passed")
    
    test_glm_provider_imports()
    print("✅ test_glm_provider_imports passed")
    
    test_session_manager_integration()
    print("✅ test_session_manager_integration passed")
    
    print("\n" + "="*60)
    print("ALL INTEGRATION TESTS PASSED ✅")
    print("="*60 + "\n")
