"""
Load Testing Configuration
Created: 2025-10-19
Purpose: Configuration for EXAI MCP Server load testing suite
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class TestConfig:
    """Configuration for load testing"""
    
    # Server configuration
    server_url: str = "ws://localhost:8079"
    
    # Concurrency limits (match server configuration)
    global_max_inflight: int = 5
    session_max_inflight: int = 2
    
    # Test parameters
    test_duration_seconds: int = 300  # 5 minutes
    concurrent_sessions: int = 10  # 2x global limit for stress testing
    
    # Tool distribution (must sum to 1.0)
    tool_patterns: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'debug': {
            'frequency': 0.20,  # 20% of calls
            'duration_range': (5, 15),  # 5-15 seconds
            'timeout_sensitivity': 'low',
            'model': 'glm-4.5-flash'
        },
        'chat': {
            'frequency': 0.40,  # 40% of calls
            'duration_range': (10, 30),  # 10-30 seconds
            'timeout_sensitivity': 'medium',
            'model': 'glm-4.5-flash'
        },
        'thinkdeep': {
            'frequency': 0.15,  # 15% of calls
            'duration_range': (30, 120),  # 30-120 seconds
            'timeout_sensitivity': 'high',
            'model': 'glm-4.6'
        },
        'analyze': {
            'frequency': 0.15,  # 15% of calls
            'duration_range': (20, 60),  # 20-60 seconds
            'timeout_sensitivity': 'medium',
            'model': 'glm-4.5-flash'
        },
        'codereview': {
            'frequency': 0.10,  # 10% of calls
            'duration_range': (15, 45),  # 15-45 seconds
            'timeout_sensitivity': 'medium',
            'model': 'glm-4.5-flash'
        }
    })
    
    # Test scenarios
    force_timeouts: bool = False
    simulate_semaphore_failures: bool = False
    check_cross_session_blocking: bool = True
    
    # Reporting
    report_output_dir: str = "scripts/load_testing/reports"
    generate_html_report: bool = True
    generate_json_report: bool = True
    
    # Monitoring
    monitor_semaphore_health: bool = True
    monitor_prometheus_metrics: bool = True
    prometheus_url: str = "http://localhost:8080/metrics"
    
    def validate(self) -> bool:
        """Validate configuration"""
        # Check tool frequencies sum to 1.0
        total_frequency = sum(
            pattern['frequency'] 
            for pattern in self.tool_patterns.values()
        )
        if abs(total_frequency - 1.0) > 0.01:
            raise ValueError(f"Tool frequencies must sum to 1.0, got {total_frequency}")
        
        return True


# Predefined test scenarios
BASELINE_TEST = TestConfig(
    concurrent_sessions=5,  # Matches global limit
    test_duration_seconds=180,  # 3 minutes
)

STRESS_TEST = TestConfig(
    concurrent_sessions=10,  # 2x global limit
    test_duration_seconds=300,  # 5 minutes
)

EXTREME_TEST = TestConfig(
    concurrent_sessions=15,  # 3x global limit
    test_duration_seconds=600,  # 10 minutes
)

TIMEOUT_TEST = TestConfig(
    concurrent_sessions=5,
    test_duration_seconds=180,
    force_timeouts=True,
)

RECOVERY_TEST = TestConfig(
    concurrent_sessions=10,
    test_duration_seconds=300,
    simulate_semaphore_failures=True,
)

