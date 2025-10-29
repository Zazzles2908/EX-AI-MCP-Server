"""
Performance Benchmarks for WebSocket Resilience Features.

This package provides benchmarks for:
- Hash algorithm performance (xxhash vs SHA256)
- Connection cleanup overhead
- Metrics collection overhead
- Circuit breaker latency

Created: 2025-10-28
Phase: 2.4 Week 1.5 - Performance Benchmarks
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

__all__ = [
    'run_all_benchmarks',
    'hash_performance',
    'cleanup_performance',
    'metrics_overhead',
    'circuit_breaker_latency'
]

