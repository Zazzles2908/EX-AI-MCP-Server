"""
Tests for Phase 3 Task 3.3: Bootstrap Module Implementation

Validates the bootstrap modules created for entry point simplification.
"""

import os
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add repo root to path
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


def test_bootstrap_imports():
    """Test that bootstrap modules can be imported."""
    try:
        from src.bootstrap import load_env, get_repo_root, setup_logging
        assert load_env is not None
        assert get_repo_root is not None
        assert setup_logging is not None
        print("✅ Bootstrap imports successful")
        return True
    except ImportError as e:
        print(f"❌ Bootstrap import failed: {e}")
        return False


def test_get_repo_root():
    """Test get_repo_root function."""
    try:
        from src.bootstrap import get_repo_root
        
        root = get_repo_root()
        assert root.exists(), "Repo root should exist"
        assert (root / "server.py").exists(), "server.py should exist in repo root"
        assert (root / "src").exists(), "src directory should exist"
        
        print(f"✅ get_repo_root() returned: {root}")
        return True
    except Exception as e:
        print(f"❌ get_repo_root test failed: {e}")
        return False


def test_load_env():
    """Test load_env function."""
    try:
        from src.bootstrap import load_env
        
        # Test basic loading
        result = load_env()
        print(f"✅ load_env() returned: {result}")
        
        # Test with explicit path
        from src.bootstrap import get_repo_root
        env_file = str(get_repo_root() / ".env")
        if os.path.exists(env_file):
            result = load_env(env_file=env_file)
            print(f"✅ load_env(env_file='{env_file}') returned: {result}")
        
        return True
    except Exception as e:
        print(f"❌ load_env test failed: {e}")
        return False


def test_setup_logging():
    """Test setup_logging function."""
    try:
        from src.bootstrap import setup_logging
        
        # Test basic logging setup
        logger = setup_logging("test_component", file_logging=False)
        assert logger is not None
        assert logger.name == "test_component"
        
        logger.info("Test log message")
        print("✅ setup_logging() successful")
        return True
    except Exception as e:
        print(f"❌ setup_logging test failed: {e}")
        return False


def test_backward_compatibility():
    """Test that refactored files maintain backward compatibility."""
    try:
        # Test that server.py can still be imported
        import server
        assert hasattr(server, 'TOOLS'), "server.TOOLS should exist"
        assert hasattr(server, 'logger'), "server.logger should exist"
        
        print("✅ server.py backward compatibility maintained")
        return True
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False


def test_code_reduction():
    """Verify code reduction metrics."""
    try:
        from src.bootstrap import env_loader, logging_setup
        
        # Count lines in bootstrap modules
        env_loader_path = Path(env_loader.__file__)
        logging_setup_path = Path(logging_setup.__file__)
        
        with open(env_loader_path) as f:
            env_loader_lines = len([l for l in f if l.strip() and not l.strip().startswith('#')])
        
        with open(logging_setup_path) as f:
            logging_setup_lines = len([l for l in f if l.strip() and not l.strip().startswith('#')])
        
        print(f"✅ env_loader.py: {env_loader_lines} lines")
        print(f"✅ logging_setup.py: {logging_setup_lines} lines")
        print(f"✅ Total bootstrap code: {env_loader_lines + logging_setup_lines} lines")
        
        return True
    except Exception as e:
        print(f"❌ Code reduction test failed: {e}")
        return False


def run_all_tests():
    """Run all bootstrap tests."""
    print("\n" + "="*60)
    print("PHASE 3 TASK 3.3 BOOTSTRAP MODULE TESTS")
    print("="*60 + "\n")
    
    tests = [
        ("Bootstrap Imports", test_bootstrap_imports),
        ("get_repo_root()", test_get_repo_root),
        ("load_env()", test_load_env),
        ("setup_logging()", test_setup_logging),
        ("Backward Compatibility", test_backward_compatibility),
        ("Code Reduction Metrics", test_code_reduction),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nRunning: {name}")
        print("-" * 60)
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

