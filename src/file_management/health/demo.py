#!/usr/bin/env python3
"""
Demonstration script for File Health Check System

This script demonstrates the main features and capabilities of the FileHealthChecker.
"""

import sys
import logging
from pathlib import Path

# Add the health directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from health_checker import FileHealthChecker


async def demo_health_checker():
    """
    Demonstrate File Health Check System capabilities
    """
    logger.info("🔍 File Health Check System - Demo")
    logger.info("=" * 60)
    
    # Initialize the health checker
    logger.info("\n📋 Initializing File Health Checker...")
    checker = FileHealthChecker(
        supabase_url=os.getenv("SUPABASE_URL"),  # Optional
        supabase_key=os.getenv("SUPABASE_KEY")  # Optional
    )
    
    # Define some files to monitor (using the health checker itself as an example)
    files_to_monitor = [
        "/workspace/src/file_management/health/health_checker.py",
        "/workspace/src/file_management/health/__init__.py",
        "/workspace/src/file_management/health/requirements.txt"
    ]
    
    # Create some test files for demonstration
    demo_files = []
    for i, file_path in enumerate(files_to_monitor):
        if Path(file_path).exists():
            demo_files.append(file_path)
    
    if not demo_files:
        logger.info("⚠️  No demo files found, creating a sample file...")
        demo_file = "/tmp/demo_health_check.txt"
        with open(demo_file, 'w') as f:
            f.write("This is a demo file for health checking.\n")
            f.write("It contains some sample content to test integrity.\n")
        demo_files = [demo_file]
    
    logger.info(f"📁 Monitoring {len(demo_files)} file(s)")
    
    try:
        # 1. File Integrity Validation
        logger.info("\n🔐 Testing File Integrity Validation...")
        for file_path in demo_files:
            result = await checker.validate_file_integrity(file_path)
            logger.info(f"  📄 {Path(file_path).name}")
            logger.info(f"     Size: {result.file_size:,} bytes")
            logger.info(f"     Status: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
            logger.info(f"     Checksum: {result.checksum[:32]}...")
        
        # 2. Storage Quota Monitoring
        logger.info("\n💾 Testing Storage Quota Monitoring...")
        storage_result = await checker.monitor_storage_quota()
        status_icon = "🔴" if storage_result.usage_percentage >= storage_result.critical_threshold else "🟡" if storage_result.usage_percentage >= storage_result.warning_threshold else "🟢"
        logger.info(f"  {status_icon} Storage Usage: {storage_result.usage_percentage:.1f}%")
        logger.info(f"     Total: {storage_result.total_space / (1024**3):.2f} GB")
        logger.info(f"     Used: {storage_result.used_space / (1024**3):.2f} GB")
        logger.info(f"     Available: {storage_result.available_space / (1024**3):.2f} GB")
        
        # 3. File Accessibility Verification
        logger.info("\n🔍 Testing File Accessibility Verification...")
        for file_path in demo_files:
            result = await checker.verify_file_accessibility(file_path)
            permissions = f"{result.permissions}"
            read_icon = "✅" if result.is_readable else "❌"
            write_icon = "✅" if result.is_writable else "❌"
            exec_icon = "✅" if result.is_executable else "❌"
            logger.info(f"  📄 {Path(file_path).name}")
            logger.info(f"     {read_icon} Read | {write_icon} Write | {exec_icon} Execute")
            logger.info(f"     Permissions: {permissions}")
        
        # 4. Performance Metrics
        logger.info("\n⚡ Testing Performance Metrics...")
        perf_result = await checker.measure_performance_metrics()
        logger.info(f"  📈 Upload Speed: {perf_result.upload_speed_mbps:.2f} MB/s")
        logger.info(f"  📉 Download Speed: {perf_result.download_speed_mbps:.2f} MB/s")
        logger.info(f"  🧠 Memory Usage: {perf_result.memory_usage_percent:.1f}%")
        logger.info(f"  💻 CPU Usage: {perf_result.cpu_usage_percent:.1f}%")
        logger.info(f"  ⏱️  File Access Time: {perf_result.file_access_time_ms:.2f} ms")
        logger.info(f"  🔢 Checksum Calculation: {perf_result.checksum_calculation_time_ms:.2f} ms")
        
        # 5. Comprehensive Health Report
        logger.info("\n📊 Generating Comprehensive Health Report...")
        report = await checker.generate_health_report(demo_files)
        
        # Display report summary
        status_colors = {
            "healthy": "🟢",
            "warning": "🟡", 
            "critical": "🔴",
            "unknown": "⚪"
        }
        status_icon = status_colors.get(report.overall_status.value, "⚪")
        
        logger.info(f"  {status_icon} Overall Status: {report.overall_status.value.upper()}")
        logger.info(f"  📋 Report ID: {report.report_id}")
        logger.info(f"  📅 Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"  📁 Files Checked: {len(report.integrity_checks)}")
        logger.info(f"  ⚠️  Alerts: {len(report.alerts)}")
        logger.info(f"  💡 Recommendations: {len(report.recommendations)}")
        
        # Show alerts
        if report.alerts:
            logger.info("\n  🚨 Alerts:")
            for alert in report.alerts:
                logger.info(f"    • {alert}")
        
        # Show recommendations
        if report.recommendations:
            logger.info("\n  💡 Recommendations:")
            for rec in report.recommendations:
                logger.info(f"    • {rec}")
        
        # 6. Save Health Report
        logger.info("\n💾 Saving Health Report...")
        report_path = "/workspace/demo_health_report.json"
        success = await checker.save_health_report(report, report_path)
        if success:
            logger.info(f"  ✅ Report saved to: {report_path}")
            logger.info(f"  📏 Report size: {Path(report_path).stat().st_size} bytes")
        else:
            logger.info("  ❌ Failed to save report")
        
        logger.info(f"\n🎉 Demo completed successfully!")
        logger.info(f"📊 Check the generated report at: {report_path}")
        
    except Exception as e:
        logger.info(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup demo files
        for demo_file in demo_files:
            if demo_file.startswith("/tmp/demo_"):
                try:
                    os.remove(demo_file)
                except:
                    pass


async def main():
    """Main demo function"""
    await demo_health_checker()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())