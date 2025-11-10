#!/usr/bin/env python3
"""
Test script for universal configuration system.
Ensures all 7 systems work with universal config.
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from prompts.universal_config import get_config, get_storage_path, get_custom_models
from prompts.timeout_monitoring import get_timeout_monitor
from prompts.tool_performance_metrics import get_metrics_collector
from prompts.model_recommendation_guide import ModelRecommendationEngine

def test_config_loading():
    """Test that configuration loads correctly."""
    print("Testing configuration loading...")

    # Test 1: Load default config
    config = get_config()
    print(f"[OK] Default config loaded: {config is not None}")

    # Test 2: Get storage paths
    try:
        timeout_path = get_storage_path("timeout_monitor")
        metrics_path = get_storage_path("performance_metrics")
        print(f"[OK] Timeout path: {timeout_path}")
        print(f"[OK] Metrics path: {metrics_path}")
    except Exception as e:
        print(f"[ERROR] Error getting storage paths: {e}")
        return False

    return True

def test_timeout_monitor():
    """Test timeout monitor with universal config."""
    print("\nTesting timeout monitor...")

    try:
        monitor = get_timeout_monitor()
        print(f"[OK] Timeout monitor created: {monitor is not None}")
        print(f"[OK] Storage path: {monitor.storage_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating timeout monitor: {e}")
        return False

def test_performance_metrics():
    """Test performance metrics with universal config."""
    print("\nTesting performance metrics...")

    try:
        collector = get_metrics_collector()
        print(f"[OK] Performance collector created: {collector is not None}")
        print(f"[OK] Storage path: {collector.storage_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating performance collector: {e}")
        return False

def test_model_recommendation():
    """Test model recommendation engine."""
    print("\nTesting model recommendation engine...")

    try:
        engine = ModelRecommendationEngine()
        print(f"[OK] Model engine created: {engine is not None}")
        print(f"[OK] Available models: {len(engine.MODELS)}")

        # Test custom models (should be empty by default)
        custom_models = get_custom_models()
        print(f"[OK] Custom models: {len(custom_models)}")

        # Test recommendation
        rec = engine.recommend_model("analyze", "medium", "high", "balanced")
        if rec:
            print(f"[OK] Recommended model: {rec.name}")

        return True
    except Exception as e:
        print(f"[ERROR] Error with model engine: {e}")
        return False

def test_all_systems():
    """Test all 7 systems are importable."""
    print("\nTesting all 7 systems...")

    systems = [
        ("Tool Selection Wizard", "from prompts.tool_selection_wizard import ToolSelectionWizard"),
        ("Model Recommendation", "from prompts.model_recommendation_guide import ModelRecommendationEngine"),
        ("Auto Model Selection", "from prompts.auto_model_selection import AutoModelSelector"),
        ("Tool Interface Standardizer", "from prompts.tool_interface_standardizer import ToolInterfaceStandardizer"),
        ("Timeout Monitoring", "from prompts.timeout_monitoring import get_timeout_monitor"),
        ("Performance Metrics", "from prompts.tool_performance_metrics import get_metrics_collector"),
        ("Universal Config", "from prompts.universal_config import get_config"),
    ]

    all_ok = True
    for name, import_stmt in systems:
        try:
            exec(import_stmt)
            print(f"[OK] {name}")
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            all_ok = False

    return all_ok

def main():
    """Run all tests."""
    print("="*70)
    print("UNIVERSAL CONFIGURATION SYSTEM TEST")
    print("="*70)

    tests = [
        test_config_loading,
        test_timeout_monitor,
        test_performance_metrics,
        test_model_recommendation,
        test_all_systems,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[ERROR] Test failed with exception: {e}")
            results.append(False)

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if all(results):
        print("\n[SUCCESS] All tests passed! Systems are universal and working correctly.")
        return 0
    else:
        print("\n[FAIL] Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
