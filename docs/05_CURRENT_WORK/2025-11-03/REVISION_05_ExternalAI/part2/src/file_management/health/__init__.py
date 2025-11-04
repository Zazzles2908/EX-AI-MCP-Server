"""
File Health Check System Package

This package provides comprehensive file health monitoring including:
- File integrity validation using checksums
- Storage quota monitoring and alerts
- File accessibility verification
- Performance metrics collection
- Automated health reporting
- Supabase integration for data storage

Main Classes:
- FileHealthChecker: Main class for health monitoring
- HealthStatus: Enumeration for health status values
- FileIntegrityCheck: Result data structure for integrity checks
- StorageQuotaInfo: Result data structure for storage monitoring
- AccessibilityResult: Result data structure for accessibility checks
- PerformanceMetrics: Result data structure for performance measurements
- HealthReport: Comprehensive health report container

Usage Example:
```python
from src.file_management.health.health_checker import FileHealthChecker

# Initialize checker
checker = FileHealthChecker(supabase_url="your_url", supabase_key="your_key")

# Generate health report
report = await checker.generate_health_report(["/path/to/file1", "/path/to/file2"])

# Save report
await checker.save_health_report(report, "/path/to/report.json")
```
"""

from .health_checker import (
    FileHealthChecker,
    HealthStatus,
    FileIntegrityCheck,
    StorageQuotaInfo,
    AccessibilityResult,
    PerformanceMetrics,
    HealthReport
)

__all__ = [
    "FileHealthChecker",
    "HealthStatus",
    "FileIntegrityCheck",
    "StorageQuotaInfo", 
    "AccessibilityResult",
    "PerformanceMetrics",
    "HealthReport"
]

__version__ = "1.0.0"