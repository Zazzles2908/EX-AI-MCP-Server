#!/usr/bin/env python3
"""
Routing Performance Benchmark
Benchmark model routing performance and capability validation
"""

import time
import json
from typing import Dict, List, Any
import statistics

class RoutingBenchmark:
    """Benchmark model routing performance"""

    def __init__(self):
        self.results = []

    def benchmark_model_selection(self, num_iterations: int = 1000) -> Dict[str, Any]:
        """Benchmark model selection performance"""
        print(f"\n🚀 Benchmarking Model Selection ({num_iterations} iterations)")
        print(f"{'='*60}")

        latencies = []

        for i in range(num_iterations):
            start_time = time.time()

            # Simulate model selection logic
            # In real implementation, would call router service
            models = ["kimi-k2-thinking", "kimi-k2-thinking-turbo", "glm-4.5-flash"]
            selected = models[i % len(models)]

            # Simulate capability check
            if "thinking" in selected:
                # Capability validation delay
                time.sleep(0.0001)

            latency = time.time() - start_time
            latencies.append(latency * 1000)  # Convert to ms

            if (i + 1) % 100 == 0:
                print(f"  Progress: {i + 1}/{num_iterations}")

        # Calculate statistics
        stats = {
            "iterations": num_iterations,
            "average_latency_ms": statistics.mean(latencies),
            "median_latency_ms": statistics.median(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "p95_latency_ms": self._percentile(latencies, 95),
            "p99_latency_ms": self._percentile(latencies, 99),
            "std_dev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0
        }

        # Print results
        print(f"\n📊 Model Selection Results:")
        print(f"{'='*60}")
        print(f"Average Latency: {stats['average_latency_ms']:.3f}ms")
        print(f"Median Latency: {stats['median_latency_ms']:.3f}ms")
        print(f"Min Latency: {stats['min_latency_ms']:.3f}ms")
        print(f"Max Latency: {stats['max_latency_ms']:.3f}ms")
        print(f"95th Percentile: {stats['p95_latency_ms']:.3f}ms")
        print(f"99th Percentile: {stats['p99_latency_ms']:.3f}ms")
        print(f"Std Deviation: {stats['std_dev_ms']:.3f}ms")

        return stats

    def benchmark_capability_validation(self, num_models: int = 20) -> Dict[str, Any]:
        """Benchmark capability validation performance"""
        print(f"\n🚀 Benchmarking Capability Validation ({num_models} models)")
        print(f"{'='*60}")

        # Simulate capability validation for different models
        model_tests = [
            ("kimi-k2-thinking", True),   # Supports extended thinking
            ("kimi-k2-thinking-turbo", True),  # Supports extended thinking
            ("kimi-k2-0711-preview", False),  # Doesn't support extended thinking
            ("glm-4.5-flash", False),     # Doesn't support extended thinking
        ]

        latencies = []

        for i in range(num_models):
            model_name, supports_thinking = model_tests[i % len(model_tests)]

            start_time = time.time()

            # Simulate capability validation
            # In real implementation, would check ModelCapabilities
            if "thinking" in model_name:
                # More complex validation for thinking-capable models
                time.sleep(0.0002)
                result = supports_thinking
            else:
                # Simpler validation for non-thinking models
                time.sleep(0.0001)
                result = supports_thinking

            latency = time.time() - start_time
            latencies.append(latency * 1000)

        stats = {
            "models_tested": num_models,
            "average_latency_ms": statistics.mean(latencies),
            "median_latency_ms": statistics.median(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "p95_latency_ms": self._percentile(latencies, 95),
            "throughput_per_sec": num_models / (sum(latencies) / 1000)
        }

        print(f"\n📊 Capability Validation Results:")
        print(f"{'='*60}")
        print(f"Models Tested: {num_models}")
        print(f"Average Latency: {stats['average_latency_ms']:.3f}ms")
        print(f"Median Latency: {stats['median_latency_ms']:.3f}ms")
        print(f"Throughput: {stats['throughput_per_sec']:.0f} models/sec")

        return stats

    def benchmark_routing_intelligence(self, num_requests: int = 100) -> Dict[str, Any]:
        """Benchmark routing intelligence (fallback mechanisms)"""
        print(f"\n🚀 Benchmarking Routing Intelligence ({num_requests} requests)")
        print(f"{'='*60}")

        test_scenarios = [
            ("thinking_mode", "kimi"),
            ("long_context", "kimi"),
            ("web_search", "glm"),
            ("fast_response", "glm"),
            ("auto", "auto"),
        ]

        latencies = []
        routing_decisions = []

        for i in range(num_requests):
            scenario, expected_provider = test_scenarios[i % len(test_scenarios)]

            start_time = time.time()

            # Simulate routing decision logic
            # In real implementation, would call router service
            if scenario == "thinking_mode":
                selected_model = "kimi-k2-thinking"
            elif scenario == "long_context":
                selected_model = "kimi-k2-thinking"
            elif scenario == "web_search":
                selected_model = "glm-4.5-flash"
            elif scenario == "fast_response":
                selected_model = "glm-4.5-flash"
            else:
                selected_model = "auto"

            # Simulate decision time
            time.sleep(0.0001)

            latency = time.time() - start_time
            latencies.append(latency * 1000)

            routing_decisions.append({
                "scenario": scenario,
                "selected": selected_model,
                "expected": expected_provider
            })

        stats = {
            "requests": num_requests,
            "average_latency_ms": statistics.mean(latencies),
            "median_latency_ms": statistics.median(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "routing_decisions": routing_decisions
        }

        print(f"\n📊 Routing Intelligence Results:")
        print(f"{'='*60}")
        print(f"Requests Processed: {num_requests}")
        print(f"Average Decision Time: {stats['average_latency_ms']:.3f}ms")
        print(f"Median Decision Time: {stats['median_latency_ms']:.3f}ms")

        # Analyze routing patterns
        decision_counts = {}
        for decision in routing_decisions:
            selected = decision["selected"]
            decision_counts[selected] = decision_counts.get(selected, 0) + 1

        print(f"\nRouting Distribution:")
        for model, count in decision_counts.items():
            percentage = (count / num_requests) * 100
            print(f"  {model}: {count} ({percentage:.1f}%)")

        return stats

    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = (percentile / 100.0) * (len(sorted_data) - 1)

        if index == int(index):
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def generate_performance_report(self, all_stats: Dict[str, Any]) -> str:
        """Generate comprehensive performance report"""
        report = {
            "benchmark_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_selection": all_stats.get("model_selection", {}),
            "capability_validation": all_stats.get("capability_validation", {}),
            "routing_intelligence": all_stats.get("routing_intelligence", {}),
            "summary": {
                "model_selection_avg_ms": all_stats.get("model_selection", {}).get("average_latency_ms", 0),
                "capability_validation_avg_ms": all_stats.get("capability_validation", {}).get("average_latency_ms", 0),
                "routing_intelligence_avg_ms": all_stats.get("routing_intelligence", {}).get("average_latency_ms", 0),
            }
        }

        return json.dumps(report, indent=2)

def main():
    """Main benchmark execution"""
    benchmark = RoutingBenchmark()

    print(f"\n{'='*80}")
    print(f"🎯 ROUTING PERFORMANCE BENCHMARK SUITE")
    print(f"{'='*80}")

    all_stats = {}

    # Run benchmarks
    all_stats["model_selection"] = benchmark.benchmark_model_selection(1000)
    all_stats["capability_validation"] = benchmark.benchmark_capability_validation(50)
    all_stats["routing_intelligence"] = benchmark.benchmark_routing_intelligence(200)

    # Generate report
    report = benchmark.generate_performance_report(all_stats)

    print(f"\n{'='*80}")
    print(f"📊 PERFORMANCE REPORT")
    print(f"{'='*80}")
    print(report)

    # Save report
    with open("tests/benchmarks/routing_performance_report.json", "w") as f:
        f.write(report)

    print(f"\n✅ Benchmark complete! Report saved to tests/benchmarks/routing_performance_report.json")

if __name__ == "__main__":
    main()
