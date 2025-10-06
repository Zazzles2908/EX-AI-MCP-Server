#!/usr/bin/env python3
"""
Setup Validation Script

Validates that the tool validation suite is properly configured and ready to run tests.

Checks:
1. Python version
2. Environment file exists
3. API keys configured
4. Required directories exist
5. Dependencies installed
6. API connectivity

Usage:
    python scripts/validate_setup.py

Created: 2025-10-05
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
import requests
from dotenv import load_dotenv


def print_header(text):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_check(name, status, message=""):
    """Print check result."""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name}")
    if message:
        print(f"   {message}")


def check_python_version():
    """Check Python version."""
    print_header("1. Python Version")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 12:
        print_check("Python version", True, f"Python {version_str}")
        return True
    else:
        print_check("Python version", False, f"Python {version_str} (requires 3.12+)")
        return False


def check_environment_file():
    """Check environment file exists."""
    print_header("2. Environment Configuration")
    
    env_path = Path("tool_validation_suite/.env.testing")
    
    if env_path.exists():
        print_check("Environment file", True, str(env_path))
        load_dotenv(env_path)
        return True
    else:
        print_check("Environment file", False, f"{env_path} not found")
        print("   Run: cp tool_validation_suite/.env.testing.example tool_validation_suite/.env.testing")
        return False


def check_api_keys():
    """Check API keys are configured."""
    print_header("3. API Keys")
    
    all_ok = True
    
    # Check Kimi API key
    kimi_key = os.getenv("KIMI_API_KEY")
    if kimi_key and kimi_key != "sk-your_kimi_api_key_here":
        print_check("Kimi API key", True, f"{kimi_key[:20]}...")
    else:
        print_check("Kimi API key", False, "Not configured")
        all_ok = False
    
    # Check GLM API key
    glm_key = os.getenv("GLM_API_KEY")
    if glm_key and "your_glm_api_key_here" not in glm_key:
        print_check("GLM API key", True, f"{glm_key[:20]}...")
    else:
        print_check("GLM API key", False, "Not configured")
        all_ok = False
    
    # Check GLM Watcher key
    watcher_key = os.getenv("GLM_WATCHER_KEY")
    if watcher_key and "your_watcher_glm_key_here" not in watcher_key:
        print_check("GLM Watcher key", True, f"{watcher_key[:20]}...")
        
        # Verify watcher key is different from main GLM key
        if watcher_key == glm_key:
            print_check("Watcher key independence", False, "Watcher key should be different from main GLM key")
            all_ok = False
        else:
            print_check("Watcher key independence", True, "Watcher key is independent")
    else:
        print_check("GLM Watcher key", False, "Not configured")
        all_ok = False
    
    return all_ok


def check_directories():
    """Check required directories exist."""
    print_header("4. Directory Structure")
    
    required_dirs = [
        "tool_validation_suite/results/latest/test_logs",
        "tool_validation_suite/results/latest/api_responses/kimi",
        "tool_validation_suite/results/latest/api_responses/glm",
        "tool_validation_suite/results/latest/watcher_observations",
        "tool_validation_suite/results/history",
        "tool_validation_suite/results/reports",
        "tool_validation_suite/cache/kimi",
        "tool_validation_suite/cache/glm",
        "tool_validation_suite/fixtures/sample_files",
        "tool_validation_suite/fixtures/sample_prompts",
        "tool_validation_suite/fixtures/expected_responses",
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print_check(dir_path, True)
        else:
            print_check(dir_path, False, "Creating...")
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"   Created: {dir_path}")
            except Exception as e:
                print(f"   Error: {e}")
                all_ok = False
    
    return all_ok


def check_dependencies():
    """Check required dependencies are installed."""
    print_header("5. Dependencies")
    
    required_packages = [
        "requests",
        "python-dotenv",
        "psutil"
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_check(package, True)
        except ImportError:
            print_check(package, False, f"Run: pip install {package}")
            all_ok = False
    
    return all_ok


def check_api_connectivity():
    """Check API connectivity."""
    print_header("6. API Connectivity")
    
    all_ok = True
    
    # Check Kimi API
    kimi_key = os.getenv("KIMI_API_KEY")
    kimi_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1")
    
    if kimi_key:
        try:
            response = requests.post(
                f"{kimi_url}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {kimi_key}"
                },
                json={
                    "model": "moonshot-v1-8k",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 5
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print_check("Kimi API", True, "Connection successful")
            else:
                print_check("Kimi API", False, f"HTTP {response.status_code}")
                all_ok = False
        except Exception as e:
            print_check("Kimi API", False, str(e))
            all_ok = False
    else:
        print_check("Kimi API", False, "No API key")
        all_ok = False
    
    # Check GLM API
    glm_key = os.getenv("GLM_API_KEY")
    glm_url = os.getenv("GLM_BASE_URL", "https://api.z.ai/api/paas/v4")
    
    if glm_key:
        try:
            response = requests.post(
                f"{glm_url}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {glm_key}"
                },
                json={
                    "model": "glm-4-flash",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 5
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print_check("GLM API", True, "Connection successful")
            else:
                print_check("GLM API", False, f"HTTP {response.status_code}")
                all_ok = False
        except Exception as e:
            print_check("GLM API", False, str(e))
            all_ok = False
    else:
        print_check("GLM API", False, "No API key")
        all_ok = False
    
    # Check GLM Watcher API
    watcher_key = os.getenv("GLM_WATCHER_KEY")
    
    if watcher_key:
        try:
            response = requests.post(
                f"{glm_url}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {watcher_key}"
                },
                json={
                    "model": "glm-4-flash",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 5
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print_check("GLM Watcher API", True, "Connection successful")
            else:
                print_check("GLM Watcher API", False, f"HTTP {response.status_code}")
                all_ok = False
        except Exception as e:
            print_check("GLM Watcher API", False, str(e))
            all_ok = False
    else:
        print_check("GLM Watcher API", False, "No API key")
        all_ok = False
    
    return all_ok


def main():
    """Run all validation checks."""
    print("\n" + "="*60)
    print("  TOOL VALIDATION SUITE - SETUP VALIDATION")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_environment_file),
        ("API Keys", check_api_keys),
        ("Directories", check_directories),
        ("Dependencies", check_dependencies),
        ("API Connectivity", check_api_connectivity),
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
    print_header("SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        symbol = "✅" if result else "❌"
        print(f"{symbol} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 Setup complete! Ready to run tests.")
        print("\nNext steps:")
        print("  1. Read TESTING_GUIDE.md")
        print("  2. Run: python scripts/run_all_tests.py --limit 1")
        print("  3. Review results: cat results/latest/summary.json")
        return 0
    else:
        print("\n⚠️  Setup incomplete. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

