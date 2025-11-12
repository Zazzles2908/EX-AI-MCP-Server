#!/usr/bin/env python3
"""
Hybrid Router Diagnostic Script
Run this to identify specific issues in the hybrid router implementation.
"""

import sys
import os
import json
from typing import Dict, Any

def diagnose_router_issues():
    """Run comprehensive diagnostics on hybrid router components."""
    
    print("=" * 80)
    print("HYBRID ROUTER - DIAGNOSTIC ANALYSIS")
    print("=" * 80)
    
    issues_found = []
    
    # Test 1: Check missing configuration files
    print("\n[1] Configuration File Analysis")
    print("-" * 50)
    
    expected_configs = [
        "src/conf/custom_models.json",
        "auggie-config.json",
        "config.py"
    ]
    
    for config_file in expected_configs:
        if os.path.exists(config_file):
            print(f"  ✅ {config_file} - EXISTS")
        else:
            print(f"  ❌ {config_file} - MISSING")
            issues_found.append(f"Missing config file: {config_file}")
    
    # Test 2: Import chain validation
    print("\n[2] Import Chain Validation")
    print("-" * 50)
    
    imports_to_test = [
        ("src.router.hybrid_router", "HybridRouter"),
        ("src.router.minimax_m2_router", "MiniMaxM2Router"), 
        ("src.router.service", "RouterService"),
        ("src.router.routing_cache", "RoutingCache"),
        ("src.providers.registry_core", "RegistryCore"),
    ]
    
    for module_name, class_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name, None)
            if cls:
                print(f"  ✅ {module_name}.{class_name} - IMPORTABLE")
            else:
                print(f"  ⚠️  {module_name}.{class_name} - CLASS NOT FOUND")
                issues_found.append(f"Class not found: {module_name}.{class_name}")
        except ImportError as e:
            print(f"  ❌ {module_name}.{class_name} - IMPORT ERROR: {e}")
            issues_found.append(f"Import error: {module_name}.{class_name} - {e}")
        except Exception as e:
            print(f"  ❌ {module_name}.{class_name} - UNEXPECTED ERROR: {e}")
            issues_found.append(f"Unexpected error: {module_name}.{class_name} - {e}")
    
    # Test 3: Model availability check
    print("\n[3] Model Availability Analysis") 
    print("-" * 50)
    
    # Expected models from the codebase analysis
    expected_models = {
        "GLM": ["glm-4.5-flash", "glm-4-plus"],
        "KIMI": ["kimi-k2-0711-preview", "kimi-k2-thinking", "kimi-thinking-preview"]
    }
    
    print("  Models referenced in codebase:")
    for provider, models in expected_models.items():
        for model in models:
            print(f"    {provider}: {model}")
    
    # Test 4: Environment variable requirements
    print("\n[4] Environment Variable Requirements")
    print("-" * 50)
    
    required_env_vars = [
        "MINIMAX_ENABLED",
        "MINIMAX_M2_KEY", 
        "MINIMAX_TIMEOUT",
        "MINIMAX_RETRY"
    ]
    
    for env_var in required_env_vars:
        value = os.getenv(env_var)
        if value:
            print(f"  ✅ {env_var} = {value[:10]}..." if len(value) > 10 else f"  ✅ {env_var} = {value}")
        else:
            print(f"  ❌ {env_var} - NOT SET")
            issues_found.append(f"Missing environment variable: {env_var}")
    
    # Test 5: Python package dependencies
    print("\n[5] Python Package Dependencies")
    print("-" * 50)
    
    required_packages = ["anthropic", "asyncio"]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} - INSTALLED")
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED")
            issues_found.append(f"Missing Python package: {package}")
    
    # Test 6: Router service configuration
    print("\n[6] Router Service Configuration Analysis")
    print("-" * 50)
    
    try:
        from src.router.service import RouterService
        
        # Check default model configuration
        router = RouterService()
        fast_default = router._fast_default
        long_default = router._long_default
        
        print(f"  Fast default model: {fast_default}")
        print(f"  Long default model: {long_default}")
        
        # Check if models are properly configured
        if fast_default == "glm-4.5-flash":
            print("  ✅ Fast model properly configured")
        else:
            print(f"  ⚠️  Fast model unusual: {fast_default}")
            
        if long_default == "kimi-k2-0711-preview":
            print("  ✅ Long model properly configured") 
        else:
            print(f"  ⚠️  Long model unusual: {long_default}")
            
    except Exception as e:
        print(f"  ❌ RouterService initialization failed: {e}")
        issues_found.append(f"RouterService initialization error: {e}")
    
    # Test 7: SimpleTool integration check
    print("\n[7] SimpleTool Integration Analysis")
    print("-" * 50)
    
    try:
        # Check if SimpleTool has the new _route_and_execute method
        from tools.simple.base import SimpleTool
        
        if hasattr(SimpleTool, '_route_and_execute'):
            print("  ✅ SimpleTool has _route_and_execute method")
        else:
            print("  ❌ SimpleTool missing _route_and_execute method")
            issues_found.append("SimpleTool missing _route_and_execute method")
            
    except ImportError as e:
        print(f"  ❌ Cannot import SimpleTool: {e}")
        issues_found.append(f"SimpleTool import error: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    if issues_found:
        print(f"\n🔴 ISSUES FOUND ({len(issues_found)}):")
        for i, issue in enumerate(issues_found, 1):
            print(f"  {i}. {issue}")
        
        print(f"\n💡 RECOMMENDED ACTIONS:")
        print("  1. Fix missing configuration files")
        print("  2. Resolve import chain issues")
        print("  3. Set up required environment variables")
        print("  4. Install missing Python packages")
        print("  5. Verify model availability in provider registry")
        
        return False
    else:
        print("\n🟢 NO CRITICAL ISSUES FOUND")
        print("The hybrid router appears to be properly configured.")
        return True

if __name__ == "__main__":
    success = diagnose_router_issues()
    sys.exit(0 if success else 1)
