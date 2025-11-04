# File Health Check System

A comprehensive file health monitoring system that provides real-time validation, storage monitoring, and performance analysis for file systems and applications.

## Features

### 🔐 File Integrity Validation
- **SHA-256 Checksum Verification**: Validate file integrity using cryptographic checksums
- **Corruption Detection**: Identify files that have been modified or corrupted
- **Expected Checksum Validation**: Support for validating files against known good checksums
- **Large File Support**: Efficient handling of files up to 100MB with configurable limits

### 💾 Storage Quota Monitoring
- **Real-time Usage Tracking**: Monitor disk usage and storage capacity
- **Configurable Thresholds**: Set warning (80%) and critical (90%) usage thresholds
- **Space Analysis**: Track total, used, and available storage space
- **Alert Generation**: Automatic alerts when storage limits are exceeded

### 🔍 File Accessibility Verification
- **Permission Analysis**: Check read, write, and execute permissions
- **Ownership Information**: Verify file owner and group attributes
- **File System Access**: Ensure files are accessible and not corrupted
- **Cross-platform Support**: Works on Linux, macOS, and Windows systems

### ⚡ Performance Metrics
- **Upload/Download Speeds**: Measure file transfer performance
- **File Access Time**: Track how quickly files can be accessed
- **System Resource Usage**: Monitor CPU and memory usage
- **Disk I/O Statistics**: Track read/write operations and throughput

### 📊 Automated Health Reporting
- **Comprehensive Reports**: Generate detailed health reports with all metrics
- **Alert System**: Automatic detection and reporting of issues
- **Recommendations**: Provide actionable recommendations for system health
- **Historical Tracking**: Store and retrieve historical health reports (with Supabase)

### ☁️ Supabase Integration
- **Cloud Storage**: Store health reports in Supabase database
- **Historical Analysis**: Retrieve and analyze historical health data
- **Real-time Monitoring**: Continuous health monitoring with cloud synchronization

## Quick Start

### Installation

1. Install required dependencies:
```bash
pip install psutil aiofiles aiohttp
```

2. (Optional) Install Supabase client for cloud features:
```bash
pip install supabase
```

### Basic Usage

```python
import asyncio
from src.file_management.health.health_checker import FileHealthChecker

async def main():
    # Initialize the health checker
    checker = FileHealthChecker(
        supabase_url="your_supabase_url",
        supabase_key="your_supabase_key"
    )
    
    # Define files to monitor
    files_to_check = ["/path/to/file1.txt", "/path/to/file2.txt"]
    
    # Generate comprehensive health report
    report = await checker.generate_health_report(files_to_check)
    
    # Save report to file
    await checker.save_health_report(report, "health_report.json")
    
    # Check the results
    print(f"Overall Status: {report.overall_status.value}")
    print(f"Files Checked: {len(report.integrity_checks)}")
    print(f"Alerts: {len(report.alerts)}")

# Run the example
asyncio.run(main())
```

### Running the Demo

```bash
python src/file_management/health/demo.py
```

### Running Tests

```bash
python src/file_management/health/test_health_checker.py
```

## API Reference

### FileHealthChecker Class

#### Constructor
```python
FileHealthChecker(supabase_url: Optional[str] = None, supabase_key: Optional[str] = None)
```

#### Core Methods

##### validate_file_integrity(file_path, expected_checksum=None)
Validates file integrity using SHA-256 checksums.

**Parameters:**
- `file_path` (str): Path to the file to validate
- `expected_checksum` (str, optional): Expected SHA-256 checksum

**Returns:** `FileIntegrityCheck` object with validation results

##### monitor_storage_quota(storage_path=None)
Monitors storage usage and quota status.

**Parameters:**
- `storage_path` (str, optional): Path to monitor (defaults to current directory)

**Returns:** `StorageQuotaInfo` object with usage statistics

##### verify_file_accessibility(file_path)
Checks file accessibility and permissions.

**Parameters:**
- `file_path` (str): Path to the file to check

**Returns:** `AccessibilityResult` object with permission details

##### measure_performance_metrics(test_file_path=None)
Measures file system and application performance.

**Parameters:**
- `test_file_path` (str, optional): Path for performance testing

**Returns:** `PerformanceMetrics` object with performance data

##### generate_health_report(files_to_check, storage_path=None)
Generates a comprehensive health report.

**Parameters:**
- `files_to_check` (List[str]): List of file paths to validate
- `storage_path` (str, optional): Storage path to monitor

**Returns:** `HealthReport` object with all health metrics

##### save_health_report(report, output_path)
Saves a health report to a JSON file.

**Parameters:**
- `report` (HealthReport): Report object to save
- `output_path` (str): Output file path

**Returns:** `bool` - True if saved successfully

## Configuration

The health checker can be configured with the following settings:

```python
checker.config = {
    "storage_warning_threshold": 80.0,        # 80% usage warning
    "storage_critical_threshold": 90.0,       # 90% usage critical
    "checksum_cache_ttl": 3600,               # 1 hour cache TTL
    "max_file_size_for_integrity": 100 * 1024 * 1024,  # 100MB
    "performance_test_file_size": 1024 * 1024,          # 1MB
    "accessibility_timeout": 30,              # 30 seconds
}
```

## Data Structures

### HealthStatus
- `HEALTHY`: All systems operating normally
- `WARNING`: Some issues detected, attention needed
- `CRITICAL`: Major issues requiring immediate attention
- `UNKNOWN`: Unable to determine status

### FileIntegrityCheck
```python
{
    "file_path": str,
    "file_size": int,
    "checksum": str,
    "expected_checksum": Optional[str],
    "is_valid": bool,
    "last_modified": datetime,
    "check_timestamp": datetime
}
```

### StorageQuotaInfo
```python
{
    "total_space": int,
    "used_space": int,
    "available_space": int,
    "usage_percentage": float,
    "warning_threshold": float,
    "critical_threshold": float,
    "check_timestamp": datetime
}
```

### AccessibilityResult
```python
{
    "file_path": str,
    "is_readable": bool,
    "is_writable": bool,
    "is_executable": bool,
    "permissions": str,
    "owner": str,
    "group": str,
    "check_timestamp": datetime
}
```

### PerformanceMetrics
```python
{
    "upload_speed_mbps": float,
    "download_speed_mbps": float,
    "file_access_time_ms": float,
    "checksum_calculation_time_ms": float,
    "disk_io_read_mb": float,
    "disk_io_write_mb": float,
    "cpu_usage_percent": float,
    "memory_usage_percent": float,
    "check_timestamp": datetime
}
```

### HealthReport
```python
{
    "report_id": str,
    "timestamp": datetime,
    "overall_status": HealthStatus,
    "integrity_checks": List[FileIntegrityCheck],
    "storage_quota": StorageQuotaInfo,
    "accessibility_results": List[AccessibilityResult],
    "performance_metrics": PerformanceMetrics,
    "alerts": List[str],
    "recommendations": List[str]
}
```

## Automated Monitoring

### Scheduled Health Checks
```python
async def run_continuous_monitoring():
    checker = FileHealthChecker()
    files_to_monitor = ["/important/file1.txt", "/important/file2.txt"]
    
    # Run health checks every 24 hours
    await checker.run_automated_health_checks(
        files_to_monitor=files_to_monitor,
        report_interval_hours=24
    )
```

### Custom Monitoring Schedule
```python
import asyncio

async def custom_schedule():
    checker = FileHealthChecker()
    
    while True:
        # Generate report every 6 hours
        report = await checker.generate_health_report(["/path/to/files"])
        await checker.save_health_report(report, f"report_{int(time.time())}.json")
        
        # Wait 6 hours
        await asyncio.sleep(6 * 3600)
```

## Supabase Setup

To use cloud storage and historical tracking features:

1. Create a Supabase project at https://supabase.com
2. Create a table called `health_reports`:
```sql
CREATE TABLE health_reports (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(255) UNIQUE NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    overall_status VARCHAR(20) NOT NULL,
    total_files_checked INTEGER NOT NULL,
    files_with_issues INTEGER NOT NULL,
    storage_usage_percent DECIMAL(5,2) NOT NULL,
    alerts_count INTEGER NOT NULL,
    cpu_usage DECIMAL(5,2) NOT NULL,
    memory_usage DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

3. Set environment variables:
```bash
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"
```

## Error Handling

The system includes comprehensive error handling:

- **File Not Found**: Gracefully handles missing files
- **Permission Errors**: Reports accessibility issues without crashing
- **System Resource Issues**: Continues monitoring even with resource constraints
- **Network Issues**: Handles Supabase connection failures gracefully
- **Corrupted Data**: Detects and reports corrupted files

## Performance Considerations

- **Async Operations**: All I/O operations are asynchronous for better performance
- **Concurrent Execution**: Multiple health checks run in parallel
- **Configurable Limits**: Adjustable file size limits for checksum calculation
- **Memory Efficient**: Streaming checksum calculation for large files
- **Resource Monitoring**: Tracks system resources to avoid overload

## Security Features

- **Checksum Validation**: SHA-256 cryptographic checksums for integrity
- **Permission Verification**: Ensures files have appropriate access controls
- **Input Validation**: Validates file paths and parameters
- **Error Information**: Secure error reporting without exposing sensitive data

## License

This implementation is provided as part of the File Health Check System.

## Support

For issues and feature requests, please refer to the project documentation or create an issue in the project repository.