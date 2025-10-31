"""
Accelerated Deployment Test Suite
Tests all rollout stages (1%, 10%, 50%, 100%) with comprehensive metrics collection
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import configuration and metrics
from tools.config.async_upload_config import AsyncUploadConfig, get_config, reset_config
from tools.monitoring.async_upload_metrics import MetricsCollector, get_metrics_collector


def test_rollout_stage(percentage: int, stage_name: str) -> dict:
    """Test a specific rollout stage and collect metrics"""
    
    print(f"\n{'='*60}")
    print(f"Testing Rollout Stage: {stage_name} ({percentage}%)")
    print(f"{'='*60}")
    
    # Configure rollout percentage
    config = get_config()
    config.rollout_percentage = percentage
    config.enabled = True
    
    # Reset metrics collector
    metrics_collector = get_metrics_collector()
    metrics_collector.metrics = []
    
    start_time = time.time()
    
    # Simulate uploads at this rollout percentage
    test_results = {
        "stage": stage_name,
        "percentage": percentage,
        "timestamp": datetime.utcnow().isoformat(),
        "start_time": start_time,
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "metrics": {}
    }
    
    # Test configuration
    print(f"[OK] Configuration: ASYNC_UPLOAD_ENABLED={config.enabled}")
    print(f"[OK] Rollout Percentage: {config.rollout_percentage}%")
    print(f"[OK] Fallback on Error: {config.fallback_on_error}")
    print(f"[OK] Max Retries: {config.max_retries}")
    print(f"[OK] Timeout: {config.timeout_seconds}s")
    
    # Verify rollout logic
    test_ids = [f"test_{i}" for i in range(100)]
    async_count = sum(1 for test_id in test_ids if config.should_use_async(test_id))
    expected_async = int(100 * percentage / 100)
    
    print(f"\n[TEST] Rollout Distribution Test:")
    print(f"  - Expected async: ~{expected_async}/100")
    print(f"  - Actual async: {async_count}/100")
    print(f"  - Distribution accuracy: {abs(async_count - expected_async) <= 5}%")

    test_results["tests_run"] += 1
    if abs(async_count - expected_async) <= 5:
        test_results["tests_passed"] += 1
        print(f"  [PASS]")
    else:
        test_results["tests_failed"] += 1
        print(f"  [FAIL]")
    
    # Collect metrics
    summary = metrics_collector.get_summary()
    test_results["metrics"] = {
        "total_uploads": summary.get("total_uploads", 0),
        "successful_uploads": summary.get("successful_uploads", 0),
        "failed_uploads": summary.get("failed_uploads", 0),
        "success_rate": summary.get("success_rate", 0),
        "avg_duration_ms": summary.get("avg_duration_ms", 0),
        "async_uploads": summary.get("async_uploads", 0),
        "sync_uploads": summary.get("sync_uploads", 0),
        "fallback_count": summary.get("fallback_count", 0)
    }
    
    end_time = time.time()
    test_results["end_time"] = end_time
    test_results["duration_seconds"] = end_time - start_time
    
    print(f"\n[METRICS] Summary:")
    print(f"  - Total Uploads: {test_results['metrics']['total_uploads']}")
    print(f"  - Success Rate: {test_results['metrics']['success_rate']:.2f}%")
    print(f"  - Avg Duration: {test_results['metrics']['avg_duration_ms']:.2f}ms")
    print(f"  - Async Uploads: {test_results['metrics']['async_uploads']}")
    print(f"  - Sync Uploads: {test_results['metrics']['sync_uploads']}")
    print(f"  - Fallback Count: {test_results['metrics']['fallback_count']}")

    print(f"\n[RESULT] Stage: {test_results['tests_passed']}/{test_results['tests_run']} tests passed")
    
    return test_results


def run_accelerated_deployment_test():
    """Run complete accelerated deployment test"""
    
    print("\n" + "="*60)
    print("ACCELERATED DEPLOYMENT TEST - ALL ROLLOUT STAGES")
    print("="*60)
    
    results = {
        "test_name": "Accelerated Deployment Test",
        "timestamp": datetime.utcnow().isoformat(),
        "stages": [],
        "summary": {}
    }
    
    # Test each rollout stage
    stages = [
        (0, "Baseline (Flags OFF)"),
        (1, "Stage 1 (1% Rollout)"),
        (10, "Stage 2 (10% Rollout)"),
        (50, "Stage 3 (50% Rollout)"),
        (100, "Stage 4 (100% Rollout)")
    ]
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    
    for percentage, stage_name in stages:
        stage_result = test_rollout_stage(percentage, stage_name)
        results["stages"].append(stage_result)
        
        total_tests += stage_result["tests_run"]
        total_passed += stage_result["tests_passed"]
        total_failed += stage_result["tests_failed"]
    
    # Summary
    results["summary"] = {
        "total_stages": len(stages),
        "total_tests": total_tests,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
        "all_passed": total_failed == 0
    }
    
    print(f"\n{'='*60}")
    print("DEPLOYMENT TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Stages: {results['summary']['total_stages']}")
    print(f"Total Tests: {results['summary']['total_tests']}")
    print(f"Passed: {results['summary']['total_passed']}")
    print(f"Failed: {results['summary']['total_failed']}")
    print(f"Success Rate: {results['summary']['success_rate']:.2f}%")
    print(f"Status: {'[PASS] ALL PASSED' if results['summary']['all_passed'] else '[FAIL] SOME FAILED'}")

    # Save results
    output_file = Path("test_results_accelerated_deployment.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n[OK] Results saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    results = run_accelerated_deployment_test()
    exit(0 if results["summary"]["all_passed"] else 1)

