#!/usr/bin/env python3
"""
Demonstration script for File Health Check System

This script demonstrates the main features and capabilities of the FileHealthChecker.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the health directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from health_checker import FileHealthChecker


async def demo_health_checker():
    """
    Demonstrate File Health Check System capabilities
    """
    print("🔍 File Health Check System - Demo")
    print("=" * 60)
    
    # Initialize the health checker
    print("\n📋 Initializing File Health Checker...")
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
        print("⚠️  No demo files found, creating a sample file...")
        demo_file = "/tmp/demo_health_check.txt"
        with open(demo_file, 'w') as f:
            f.write("This is a demo file for health checking.\n")
            f.write("It contains some sample content to test integrity.\n")
        demo_files = [demo_file]
    
    print(f"📁 Monitoring {len(demo_files)} file(s)")
    
    try:
        # 1. File Integrity Validation
        print("\n🔐 Testing File Integrity Validation...")
        for file_path in demo_files:
            result = await checker.validate_file_integrity(file_path)
            print(f"  📄 {Path(file_path).name}")
            print(f"     Size: {result.file_size:,} bytes")
            print(f"     Status: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
            print(f"     Checksum: {result.checksum[:32]}...")
        
        # 2. Storage Quota Monitoring
        print("\n💾 Testing Storage Quota Monitoring...")
        storage_result = await checker.monitor_storage_quota()
        status_icon = "🔴" if storage_result.usage_percentage >= storage_result.critical_threshold else "🟡" if storage_result.usage_percentage >= storage_result.warning_threshold else "🟢"
        print(f"  {status_icon} Storage Usage: {storage_result.usage_percentage:.1f}%")
        print(f"     Total: {storage_result.total_space / (1024**3):.2f} GB")
        print(f"     Used: {storage_result.used_space / (1024**3):.2f} GB")
        print(f"     Available: {storage_result.available_space / (1024**3):.2f} GB")
        
        # 3. File Accessibility Verification
        print("\n🔍 Testing File Accessibility Verification...")
        for file_path in demo_files:
            result = await checker.verify_file_accessibility(file_path)
            permissions = f"{result.permissions}"
            read_icon = "✅" if result.is_readable else "❌"
            write_icon = "✅" if result.is_writable else "❌"
            exec_icon = "✅" if result.is_executable else "❌"
            print(f"  📄 {Path(file_path).name}")
            print(f"     {read_icon} Read | {write_icon} Write | {exec_icon} Execute")
            print(f"     Permissions: {permissions}")
        
        # 4. Performance Metrics
        print("\n⚡ Testing Performance Metrics...")
        perf_result = await checker.measure_performance_metrics()
        print(f"  📈 Upload Speed: {perf_result.upload_speed_mbps:.2f} MB/s")
        print(f"  📉 Download Speed: {perf_result.download_speed_mbps:.2f} MB/s")
        print(f"  🧠 Memory Usage: {perf_result.memory_usage_percent:.1f}%")
        print(f"  💻 CPU Usage: {perf_result.cpu_usage_percent:.1f}%")
        print(f"  ⏱️  File Access Time: {perf_result.file_access_time_ms:.2f} ms")
        print(f"  🔢 Checksum Calculation: {perf_result.checksum_calculation_time_ms:.2f} ms")
        
        # 5. Comprehensive Health Report
        print("\n📊 Generating Comprehensive Health Report...")
        report = await checker.generate_health_report(demo_files)
        
        # Display report summary
        status_colors = {
            "healthy": "🟢",
            "warning": "🟡", 
            "critical": "🔴",
            "unknown": "⚪"
        }
        status_icon = status_colors.get(report.overall_status.value, "⚪")
        
        print(f"  {status_icon} Overall Status: {report.overall_status.value.upper()}")
        print(f"  📋 Report ID: {report.report_id}")
        print(f"  📅 Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  📁 Files Checked: {len(report.integrity_checks)}")
        print(f"  ⚠️  Alerts: {len(report.alerts)}")
        print(f"  💡 Recommendations: {len(report.recommendations)}")
        
        # Show alerts
        if report.alerts:
            print("\n  🚨 Alerts:")
            for alert in report.alerts:
                print(f"    • {alert}")
        
        # Show recommendations
        if report.recommendations:
            print("\n  💡 Recommendations:")
            for rec in report.recommendations:
                print(f"    • {rec}")
        
        # 6. Save Health Report
        print("\n💾 Saving Health Report...")
        report_path = "/workspace/demo_health_report.json"
        success = await checker.save_health_report(report, report_path)
        if success:
            print(f"  ✅ Report saved to: {report_path}")
            print(f"  📏 Report size: {Path(report_path).stat().st_size} bytes")
        else:
            print("  ❌ Failed to save report")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"📊 Check the generated report at: {report_path}")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
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