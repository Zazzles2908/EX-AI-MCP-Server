"""
Setup test environment for Tool Validation Suite

This script:
1. Verifies all dependencies are installed
2. Checks API keys are set
3. Verifies daemon can start (optional)
4. Creates necessary directories
5. Validates configuration files
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"  ❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Check required dependencies"""
    print("\nChecking dependencies...")
    
    required = [
        'mcp',
        'openai',
        'pydantic',
        'dotenv',
        'zhipuai',
        'httpx'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    return True


def check_api_keys():
    """Check API keys"""
    print("\nChecking API keys...")
    
    kimi_key = os.getenv('MOONSHOT_API_KEY')
    glm_key = os.getenv('ZHIPUAI_API_KEY')
    
    if kimi_key:
        print(f"  ✅ MOONSHOT_API_KEY set ({kimi_key[:10]}...)")
    else:
        print(f"  ⚠️  MOONSHOT_API_KEY not set")
    
    if glm_key:
        print(f"  ✅ ZHIPUAI_API_KEY set ({glm_key[:10]}...)")
    else:
        print(f"  ⚠️  ZHIPUAI_API_KEY not set")
    
    if not kimi_key and not glm_key:
        print(f"\n❌ At least one API key must be set")
        print(f"Set in .env file or environment variables")
        return False
    
    return True


def check_directories():
    """Check and create necessary directories"""
    print("\nChecking directories...")
    
    base_dir = Path(__file__).parent.parent
    
    dirs = [
        base_dir / "tests" / "core_tools",
        base_dir / "tests" / "advanced_tools",
        base_dir / "tests" / "provider_tools",
        base_dir / "tests" / "integration",
        base_dir / "results",
        base_dir / "docs" / "current",
        base_dir / "docs" / "archive"
    ]
    
    for dir_path in dirs:
        if dir_path.exists():
            print(f"  ✅ {dir_path.relative_to(base_dir)}")
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created {dir_path.relative_to(base_dir)}")
    
    return True


def check_config_files():
    """Check configuration files"""
    print("\nChecking configuration files...")
    
    base_dir = Path(__file__).parent.parent
    
    config_file = base_dir / "config" / "test_config.json"
    if config_file.exists():
        print(f"  ✅ test_config.json")
        
        # Validate JSON
        try:
            import json
            with open(config_file) as f:
                config = json.load(f)
            
            # Check for correct model names
            kimi_models = config.get('models', {}).get('kimi', [])
            glm_models = config.get('models', {}).get('glm', [])
            
            if 'kimi-k2-0905-preview' in kimi_models:
                print(f"    ✅ Kimi models correct")
            else:
                print(f"    ⚠️  Kimi models may need updating")
            
            if 'glm-4.5-flash' in glm_models:
                print(f"    ✅ GLM models correct")
            else:
                print(f"    ⚠️  GLM models may need updating")
        except Exception as e:
            print(f"    ⚠️  Error validating config: {e}")
    else:
        print(f"  ❌ test_config.json not found")
        return False
    
    return True


def check_test_files():
    """Check test files"""
    print("\nChecking test files...")
    
    base_dir = Path(__file__).parent.parent / "tests"
    
    test_files = list(base_dir.rglob("test_*.py"))
    
    print(f"  ✅ Found {len(test_files)} test files")
    
    # Count by category
    core = len(list((base_dir / "core_tools").glob("test_*.py")))
    advanced = len(list((base_dir / "advanced_tools").glob("test_*.py")))
    provider = len(list((base_dir / "provider_tools").glob("test_*.py")))
    integration = len(list((base_dir / "integration").glob("test_*.py")))
    
    print(f"    - Core tools: {core}")
    print(f"    - Advanced tools: {advanced}")
    print(f"    - Provider tools: {provider}")
    print(f"    - Integration: {integration}")
    
    expected = 36
    if len(test_files) == expected:
        print(f"  ✅ All {expected} test files present")
        return True
    else:
        print(f"  ⚠️  Expected {expected} test files, found {len(test_files)}")
        return True  # Not critical


def check_daemon_optional():
    """Check if daemon can start (optional)"""
    print("\nChecking daemon (optional)...")
    
    try:
        # Try to import daemon module
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from src.daemon import ws_server
        print(f"  ✅ Daemon module found")
        print(f"  ℹ️  To start daemon: python scripts/run_ws_daemon.py")
        return True
    except ImportError as e:
        print(f"  ⚠️  Daemon module not found (optional)")
        print(f"     {e}")
        return True  # Not critical for provider API tests


def main():
    """Run all checks"""
    print("=" * 60)
    print("Tool Validation Suite - Environment Setup")
    print("=" * 60)
    
    checks = [
        ("Python version", check_python_version),
        ("Dependencies", check_dependencies),
        ("API keys", check_api_keys),
        ("Directories", check_directories),
        ("Configuration", check_config_files),
        ("Test files", check_test_files),
        ("Daemon (optional)", check_daemon_optional)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ Environment setup complete!")
        print("\nNext steps:")
        print("1. Run tests: python scripts/run_all_tests.py")
        print("2. Or run specific tool: python scripts/run_all_tests.py --tool chat")
        print("3. View results in: results/latest/")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

