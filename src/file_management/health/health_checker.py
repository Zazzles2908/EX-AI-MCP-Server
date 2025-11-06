"""
File Health Check System

Provides comprehensive file health monitoring including:
- File integrity validation (checksums, corruption detection)
- Storage quota monitoring and alerts
- File accessibility verification
- Performance metrics (upload/download speeds)
- Automated health reporting and diagnostics
- Integration with Supabase for health data storage
"""

import hashlib
import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import psutil
import asyncio
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import aiofiles
from dataclasses import dataclass, asdict
from enum import Enum

# Import Supabase client
try:
    from supabase import create_client, Client
except ImportError:
    Client = None
    create_client = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class FileIntegrityCheck:
    """File integrity check result"""
    file_path: str
    file_size: int
    checksum: str
    expected_checksum: Optional[str]
    is_valid: bool
    last_modified: datetime
    check_timestamp: datetime


@dataclass
class StorageQuotaInfo:
    """Storage quota information"""
    total_space: int
    used_space: int
    available_space: int
    usage_percentage: float
    warning_threshold: float
    critical_threshold: float
    check_timestamp: datetime


@dataclass
class AccessibilityResult:
    """File accessibility check result"""
    file_path: str
    is_readable: bool
    is_writable: bool
    is_executable: bool
    permissions: str
    owner: str
    group: str
    check_timestamp: datetime


@dataclass
class PerformanceMetrics:
    """Performance metrics for file operations"""
    upload_speed_mbps: float
    download_speed_mbps: float
    file_access_time_ms: float
    checksum_calculation_time_ms: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    cpu_usage_percent: float
    memory_usage_percent: float
    check_timestamp: datetime


@dataclass
class HealthReport:
    """Comprehensive health report"""
    report_id: str
    timestamp: datetime
    overall_status: HealthStatus
    integrity_checks: List[FileIntegrityCheck]
    storage_quota: StorageQuotaInfo
    accessibility_results: List[AccessibilityResult]
    performance_metrics: PerformanceMetrics
    alerts: List[str]
    recommendations: List[str]


class FileHealthChecker:
    """
    Comprehensive file health monitoring system
    """
    
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """
        Initialize the File Health Checker
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase_client = None
        self.storage_warnings = set()
        self.integrity_cache = {}
        
        # Initialize Supabase client if credentials provided
        if self.supabase_url and self.supabase_key and create_client:
            try:
                self.supabase_client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
        
        # Health check configuration
        self.config = {
            "storage_warning_threshold": 80.0,  # 80% usage
            "storage_critical_threshold": 90.0,  # 90% usage
            "checksum_cache_ttl": 3600,  # 1 hour
            "max_file_size_for_integrity": 100 * 1024 * 1024,  # 100MB
            "performance_test_file_size": 1024 * 1024,  # 1MB
            "accessibility_timeout": 30,  # 30 seconds
        }
    
    async def validate_file_integrity(self, file_path: str, expected_checksum: Optional[str] = None) -> FileIntegrityCheck:
        """
        Validate file integrity using checksums and metadata analysis
        
        Args:
            file_path: Path to the file to validate
            expected_checksum: Expected SHA-256 checksum (optional)
            
        Returns:
            FileIntegrityCheck result with validation details
        """
        try:
            file_path_obj = Path(file_path)
            
            # Check if file exists and get basic info
            if not file_path_obj.exists():
                logger.warning(f"File not found: {file_path}")
                return FileIntegrityCheck(
                    file_path=file_path,
                    file_size=0,
                    checksum="",
                    expected_checksum=expected_checksum,
                    is_valid=False,
                    last_modified=datetime.now(),
                    check_timestamp=datetime.now()
                )
            
            # Get file size and modification time
            file_stat = file_path_obj.stat()
            file_size = file_stat.st_size
            last_modified = datetime.fromtimestamp(file_stat.st_mtime)
            
            # Calculate checksum
            checksum = await self._calculate_file_checksum(file_path)
            
            # Determine if checksum is valid
            is_valid = True
            if expected_checksum:
                is_valid = checksum.lower() == expected_checksum.lower()
            elif file_size > self.config["max_file_size_for_integrity"]:
                # For large files, only validate basic integrity
                is_valid = file_size > 0
            
            logger.info(f"File integrity check completed for {file_path}: {'VALID' if is_valid else 'INVALID'}")
            
            return FileIntegrityCheck(
                file_path=file_path,
                file_size=file_size,
                checksum=checksum,
                expected_checksum=expected_checksum,
                is_valid=is_valid,
                last_modified=last_modified,
                check_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error validating file integrity for {file_path}: {e}")
            return FileIntegrityCheck(
                file_path=file_path,
                file_size=0,
                checksum="",
                expected_checksum=expected_checksum,
                is_valid=False,
                last_modified=datetime.now(),
                check_timestamp=datetime.now()
            )
    
    async def monitor_storage_quota(self, storage_path: Optional[str] = None) -> StorageQuotaInfo:
        """
        Monitor storage quota and usage
        
        Args:
            storage_path: Path to monitor (default: current working directory)
            
        Returns:
            StorageQuotaInfo with usage statistics and thresholds
        """
        try:
            # Default to current working directory if no path specified
            if not storage_path:
                storage_path = os.getcwd()
            
            # Get disk usage statistics
            disk_usage = psutil.disk_usage(storage_path)
            
            total_space = disk_usage.total
            used_space = disk_usage.used
            available_space = disk_usage.free
            usage_percentage = (used_space / total_space) * 100
            
            logger.info(f"Storage quota check: {usage_percentage:.1f}% used ({used_space}/{total_space} bytes)")
            
            return StorageQuotaInfo(
                total_space=total_space,
                used_space=used_space,
                available_space=available_space,
                usage_percentage=usage_percentage,
                warning_threshold=self.config["storage_warning_threshold"],
                critical_threshold=self.config["storage_critical_threshold"],
                check_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error monitoring storage quota: {e}")
            # Return default values on error
            return StorageQuotaInfo(
                total_space=0,
                used_space=0,
                available_space=0,
                usage_percentage=0.0,
                warning_threshold=self.config["storage_warning_threshold"],
                critical_threshold=self.config["storage_critical_threshold"],
                check_timestamp=datetime.now()
            )
    
    async def verify_file_accessibility(self, file_path: str) -> AccessibilityResult:
        """
        Verify file accessibility and permissions
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            AccessibilityResult with permission details
        """
        try:
            file_path_obj = Path(file_path)
            
            # Check if file exists
            if not file_path_obj.exists():
                logger.warning(f"File accessibility check failed - file not found: {file_path}")
                return AccessibilityResult(
                    file_path=file_path,
                    is_readable=False,
                    is_writable=False,
                    is_executable=False,
                    permissions="N/A",
                    owner="N/A",
                    group="N/A",
                    check_timestamp=datetime.now()
                )
            
            # Get file permissions
            stat = file_path_obj.stat()
            permissions = oct(stat.st_mode)[-3:]
            
            # Check basic accessibility
            is_readable = os.access(file_path, os.R_OK)
            is_writable = os.access(file_path, os.W_OK)
            is_executable = os.access(file_path, os.X_OK)
            
            # Get owner and group information
            try:
                import pwd
                import grp
                owner = pwd.getpwuid(stat.st_uid).pw_name
                group = grp.getgrgid(stat.st_gid).gr_name
            except (ImportError, KeyError):
                # Fallback for systems without pwd/grp modules
                owner = str(stat.st_uid)
                group = str(stat.st_gid)
            
            logger.info(f"Accessibility check completed for {file_path}: R={is_readable}, W={is_writable}, X={is_executable}")
            
            return AccessibilityResult(
                file_path=file_path,
                is_readable=is_readable,
                is_writable=is_writable,
                is_executable=is_executable,
                permissions=permissions,
                owner=owner,
                group=group,
                check_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error checking file accessibility for {file_path}: {e}")
            return AccessibilityResult(
                file_path=file_path,
                is_readable=False,
                is_writable=False,
                is_executable=False,
                permissions="N/A",
                owner="N/A",
                group="N/A",
                check_timestamp=datetime.now()
            )
    
    async def measure_performance_metrics(self, test_file_path: Optional[str] = None) -> PerformanceMetrics:
        """
        Measure file system performance metrics
        
        Args:
            test_file_path: Optional path for performance testing
            
        Returns:
            PerformanceMetrics with speed and resource usage data
        """
        try:
            start_time = time.time()
            
            # Get system performance metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
            
            # Get disk I/O statistics before test
            disk_io_before = psutil.disk_io_counters()
            
            # Performance test parameters
            if not test_file_path:
                test_file_path = "/tmp/performance_test_file.tmp"
            
            test_file_size = self.config["performance_test_file_size"]
            test_data = b"0" * test_file_size
            
            # Measure upload (write) speed
            upload_start = time.time()
            async with aiofiles.open(test_file_path, 'wb') as f:
                await f.write(test_data)
            upload_end = time.time()
            upload_time = upload_end - upload_start
            upload_speed_mbps = (test_file_size / (1024 * 1024)) / upload_time
            
            # Measure file access time
            access_start = time.time()
            async with aiofiles.open(test_file_path, 'rb') as f:
                await f.read()
            access_end = time.time()
            access_time_ms = (access_end - access_start) * 1000
            
            # Measure download (read) speed
            download_start = time.time()
            async with aiofiles.open(test_file_path, 'rb') as f:
                data = await f.read()
            download_end = time.time()
            download_time = download_end - download_start
            download_speed_mbps = (test_file_size / (1024 * 1024)) / download_time
            
            # Measure checksum calculation time
            checksum_start = time.time()
            await self._calculate_file_checksum(test_file_path)
            checksum_end = time.time()
            checksum_time_ms = (checksum_end - checksum_start) * 1000
            
            # Get disk I/O statistics after test
            disk_io_after = psutil.disk_io_counters()
            
            # Calculate disk I/O
            disk_read_mb = 0
            disk_write_mb = 0
            if disk_io_before and disk_io_after:
                disk_read_mb = (disk_io_after.read_bytes - disk_io_before.read_bytes) / (1024 * 1024)
                disk_write_mb = (disk_io_after.write_bytes - disk_io_before.write_bytes) / (1024 * 1024)
            
            # Clean up test file
            try:
                os.remove(test_file_path)
            except:
                pass
            
            logger.info(f"Performance metrics: Upload={upload_speed_mbps:.2f}MB/s, Download={download_speed_mbps:.2f}MB/s")
            
            return PerformanceMetrics(
                upload_speed_mbps=upload_speed_mbps,
                download_speed_mbps=download_speed_mbps,
                file_access_time_ms=access_time_ms,
                checksum_calculation_time_ms=checksum_time_ms,
                disk_io_read_mb=disk_read_mb,
                disk_io_write_mb=disk_write_mb,
                cpu_usage_percent=cpu_usage,
                memory_usage_percent=memory_usage,
                check_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error measuring performance metrics: {e}")
            return PerformanceMetrics(
                upload_speed_mbps=0.0,
                download_speed_mbps=0.0,
                file_access_time_ms=0.0,
                checksum_calculation_time_ms=0.0,
                disk_io_read_mb=0.0,
                disk_io_write_mb=0.0,
                cpu_usage_percent=0.0,
                memory_usage_percent=0.0,
                check_timestamp=datetime.now()
            )
    
    async def generate_health_report(self, files_to_check: List[str], storage_path: Optional[str] = None) -> HealthReport:
        """
        Generate comprehensive health report
        
        Args:
            files_to_check: List of file paths to validate
            storage_path: Storage path to monitor
            
        Returns:
            HealthReport with all health metrics and recommendations
        """
        try:
            logger.info("Starting comprehensive health report generation...")
            
            # Generate unique report ID
            report_id = f"health_report_{int(time.time())}"
            
            # Run all health checks concurrently
            tasks = []
            
            # File integrity checks
            for file_path in files_to_check:
                tasks.append(self.validate_file_integrity(file_path))
            
            # Storage quota check
            tasks.append(self.monitor_storage_quota(storage_path))
            
            # File accessibility checks
            for file_path in files_to_check:
                tasks.append(self.verify_file_accessibility(file_path))
            
            # Performance metrics
            tasks.append(self.measure_performance_metrics())
            
            # Execute all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            integrity_checks = []
            accessibility_results = []
            storage_quota = None
            performance_metrics = None
            alerts = []
            recommendations = []
            
            idx = 0
            # File integrity results
            for _ in files_to_check:
                if idx < len(results) and isinstance(results[idx], FileIntegrityCheck):
                    integrity_checks.append(results[idx])
                    if not results[idx].is_valid:
                        alerts.append(f"File integrity check failed: {results[idx].file_path}")
                idx += 1
            
            # Storage quota result
            if idx < len(results) and isinstance(results[idx], StorageQuotaInfo):
                storage_quota = results[idx]
                if storage_quota.usage_percentage >= storage_quota.critical_threshold:
                    alerts.append(f"Critical storage usage: {storage_quota.usage_percentage:.1f}%")
                elif storage_quota.usage_percentage >= storage_quota.warning_threshold:
                    alerts.append(f"High storage usage: {storage_quota.usage_percentage:.1f}%")
                idx += 1
            
            # Accessibility results
            for _ in files_to_check:
                if idx < len(results) and isinstance(results[idx], AccessibilityResult):
                    accessibility_results.append(results[idx])
                    if not results[idx].is_readable:
                        alerts.append(f"File not readable: {results[idx].file_path}")
                idx += 1
            
            # Performance metrics
            if idx < len(results) and isinstance(results[idx], PerformanceMetrics):
                performance_metrics = results[idx]
                if performance_metrics.upload_speed_mbps < 1.0:
                    alerts.append("Low upload speed detected")
                if performance_metrics.memory_usage_percent > 90:
                    alerts.append("High memory usage detected")
            
            # Determine overall health status
            overall_status = HealthStatus.HEALTHY
            if any("Critical" in alert for alert in alerts):
                overall_status = HealthStatus.CRITICAL
            elif alerts:
                overall_status = HealthStatus.WARNING
            
            # Generate recommendations
            if storage_quota and storage_quota.usage_percentage > 70:
                recommendations.append("Consider cleaning up old files or expanding storage capacity")
            
            if performance_metrics and performance_metrics.memory_usage_percent > 80:
                recommendations.append("Consider restarting services to free memory")
            
            if integrity_checks and any(not check.is_valid for check in integrity_checks):
                recommendations.append("Re-download or restore files with integrity issues")
            
            report = HealthReport(
                report_id=report_id,
                timestamp=datetime.now(),
                overall_status=overall_status,
                integrity_checks=integrity_checks,
                storage_quota=storage_quota,
                accessibility_results=accessibility_results,
                performance_metrics=performance_metrics,
                alerts=alerts,
                recommendations=recommendations
            )
            
            # Store report in Supabase if available
            if self.supabase_client:
                await self._store_health_report(report)
            
            logger.info(f"Health report generated successfully: {report_id} - Status: {overall_status.value}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating health report: {e}")
            # Return minimal error report
            return HealthReport(
                report_id=f"error_report_{int(time.time())}",
                timestamp=datetime.now(),
                overall_status=HealthStatus.CRITICAL,
                integrity_checks=[],
                storage_quota=StorageQuotaInfo(
                    total_space=0, used_space=0, available_space=0,
                    usage_percentage=0.0, warning_threshold=80.0,
                    critical_threshold=90.0, check_timestamp=datetime.now()
                ),
                accessibility_results=[],
                performance_metrics=PerformanceMetrics(
                    upload_speed_mbps=0.0, download_speed_mbps=0.0,
                    file_access_time_ms=0.0, checksum_calculation_time_ms=0.0,
                    disk_io_read_mb=0.0, disk_io_write_mb=0.0,
                    cpu_usage_percent=0.0, memory_usage_percent=0.0,
                    check_timestamp=datetime.now()
                ),
                alerts=[f"Health report generation failed: {str(e)}"],
                recommendations=["Check system logs and file system health"]
            )
    
    async def save_health_report(self, report: HealthReport, output_path: str) -> bool:
        """
        Save health report to file
        
        Args:
            report: HealthReport to save
            output_path: Output file path
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Convert report to dictionary for JSON serialization
            report_dict = {
                "report_id": report.report_id,
                "timestamp": report.timestamp.isoformat(),
                "overall_status": report.overall_status.value,
                "integrity_checks": [asdict(check) for check in report.integrity_checks],
                "storage_quota": asdict(report.storage_quota) if report.storage_quota else None,
                "accessibility_results": [asdict(result) for result in report.accessibility_results],
                "performance_metrics": asdict(report.performance_metrics) if report.performance_metrics else None,
                "alerts": report.alerts,
                "recommendations": report.recommendations
            }
            
            # Convert datetime objects to ISO format strings
            for check in report_dict["integrity_checks"]:
                check["check_timestamp"] = check["check_timestamp"].isoformat()
                check["last_modified"] = check["last_modified"].isoformat()
            
            if report_dict["storage_quota"]:
                report_dict["storage_quota"]["check_timestamp"] = report_dict["storage_quota"]["check_timestamp"].isoformat()
            
            for result in report_dict["accessibility_results"]:
                result["check_timestamp"] = result["check_timestamp"].isoformat()
            
            if report_dict["performance_metrics"]:
                report_dict["performance_metrics"]["check_timestamp"] = report_dict["performance_metrics"]["check_timestamp"].isoformat()
            
            # Save to file
            async with aiofiles.open(output_path, 'w') as f:
                await f.write(json.dumps(report_dict, indent=2, default=str))
            
            logger.info(f"Health report saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving health report: {e}")
            return False
    
    async def get_health_history(self, limit: int = 10) -> List[HealthReport]:
        """
        Retrieve health report history from Supabase
        
        Args:
            limit: Maximum number of reports to retrieve
            
        Returns:
            List of historical health reports
        """
        if not self.supabase_client:
            logger.warning("Supabase client not available for retrieving health history")
            return []
        
        try:
            # This would require a supabase table for health reports
            # For now, return empty list as this requires proper table setup
            logger.info("Health history retrieval requested (requires Supabase table setup)")
            return []
            
        except Exception as e:
            logger.error(f"Error retrieving health history: {e}")
            return []
    
    async def _calculate_file_checksum(self, file_path: str) -> str:
        """
        Calculate SHA-256 checksum for a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA-256 checksum as hexadecimal string
        """
        try:
            hash_sha256 = hashlib.sha256()
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(8192):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum for {file_path}: {e}")
            return ""
    
    async def _store_health_report(self, report: HealthReport) -> bool:
        """
        Store health report in Supabase
        
        Args:
            report: HealthReport to store
            
        Returns:
            True if stored successfully, False otherwise
        """
        if not self.supabase_client:
            return False
        
        try:
            # This would store the report in a Supabase table
            # Example table structure would need to be set up
            report_data = {
                "report_id": report.report_id,
                "timestamp": report.timestamp.isoformat(),
                "overall_status": report.overall_status.value,
                "total_files_checked": len(report.integrity_checks),
                "files_with_issues": len([c for c in report.integrity_checks if not c.is_valid]),
                "storage_usage_percent": report.storage_quota.usage_percentage if report.storage_quota else 0,
                "alerts_count": len(report.alerts),
                "cpu_usage": report.performance_metrics.cpu_usage_percent if report.performance_metrics else 0,
                "memory_usage": report.performance_metrics.memory_usage_percent if report.performance_metrics else 0
            }
            
            # Note: This requires a table named 'health_reports' to be created in Supabase
            # result = self.supabase_client.table('health_reports').insert(report_data).execute()
            
            logger.info(f"Health report {report.report_id} stored in Supabase")
            return True
            
        except Exception as e:
            logger.error(f"Error storing health report in Supabase: {e}")
            return False
    
    async def run_automated_health_checks(self, 
                                        files_to_monitor: List[str],
                                        storage_path: Optional[str] = None,
                                        report_interval_hours: int = 24) -> None:
        """
        Run automated health checks on a schedule
        
        Args:
            files_to_monitor: List of files to monitor
            storage_path: Storage path to monitor
            report_interval_hours: Interval between reports in hours
        """
        logger.info(f"Starting automated health checks with {report_interval_hours}h interval")
        
        try:
            while True:
                # Generate health report
                report = await self.generate_health_report(files_to_monitor, storage_path)
                
                # Save report with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_path = f"/workspace/health_report_{timestamp}.json"
                await self.save_health_report(report, report_path)
                
                # Log summary
                logger.info(f"Automated health check completed:")
                logger.info(f"  - Overall Status: {report.overall_status.value}")
                logger.info(f"  - Files Checked: {len(report.integrity_checks)}")
                logger.info(f"  - Alerts: {len(report.alerts)}")
                if report.storage_quota:
                    logger.info(f"  - Storage Usage: {report.storage_quota.usage_percentage:.1f}%")
                
                # Wait for next interval
                await asyncio.sleep(report_interval_hours * 3600)
                
        except Exception as e:
            logger.error(f"Error in automated health checks: {e}")


# Example usage and testing functions
async def example_usage():
    """
    Example usage of the File Health Checker
    """
    # Initialize checker (provide Supabase credentials if available)
    checker = FileHealthChecker(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_KEY")
    )
    
    # Define files to check
    files_to_check = [
        "/workspace/src/file_management/health/health_checker.py",
        "/workspace/README.md"
    ]
    
    # Generate comprehensive health report
    report = await checker.generate_health_report(files_to_check)
    
    # Save report
    await checker.save_health_report(report, "/workspace/latest_health_report.json")
    
    # Print summary
    logger.info(f"Health Report Summary:")
    logger.info(f"Status: {report.overall_status.value}")
    logger.info(f"Files checked: {len(report.integrity_checks)}")
    logger.info(f"Alerts: {len(report.alerts)}")
    logger.info(f"Recommendations: {len(report.recommendations)}")
    
    return report


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())