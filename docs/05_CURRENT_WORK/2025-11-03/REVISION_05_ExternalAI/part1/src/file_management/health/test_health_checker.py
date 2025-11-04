#!/usr/bin/env python3
"""
Test script for File Health Check System

This script tests the basic functionality of the FileHealthChecker.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the health directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from health_checker import FileHealthChecker, example_usage


async def test_basic_functionality():
    """Test basic functionality of the health checker"""
    print("Testing File Health Check System...")
    
    # Initialize checker (no Supabase credentials for basic test)
    checker = FileHealthChecker()
    
    # Create a test file
    test_file_path = "/tmp/test_health_check.txt"
    test_content = "This is a test file for health checking.\n"
    
    try:
        # Write test file
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        print(f"✓ Created test file: {test_file_path}")
        
        # Test file integrity check
        integrity_result = await checker.validate_file_integrity(test_file_path)
        print(f"✓ File integrity check: {'PASS' if integrity_result.is_valid else 'FAIL'}")
        print(f"  - File size: {integrity_result.file_size} bytes")
        print(f"  - Checksum: {integrity_result.checksum[:16]}...")
        
        # Test accessibility check
        accessibility_result = await checker.verify_file_accessibility(test_file_path)
        print(f"✓ Accessibility check: {'PASS' if accessibility_result.is_readable else 'FAIL'}")
        print(f"  - Permissions: {accessibility_result.permissions}")
        print(f"  - Readable: {accessibility_result.is_readable}")
        print(f"  - Writable: {accessibility_result.is_writable}")
        
        # Test storage quota check
        storage_result = await checker.monitor_storage_quota("/tmp")
        print(f"✓ Storage quota check completed")
        print(f"  - Usage: {storage_result.usage_percentage:.1f}%")
        print(f"  - Available: {storage_result.available_space / (1024*1024*1024):.2f} GB")
        
        # Test performance metrics
        performance_result = await checker.measure_performance_metrics(test_file_path)
        print(f"✓ Performance metrics completed")
        print(f"  - Upload speed: {performance_result.upload_speed_mbps:.2f} MB/s")
        print(f"  - Download speed: {performance_result.download_speed_mbps:.2f} MB/s")
        print(f"  - Memory usage: {performance_result.memory_usage_percent:.1f}%")
        
        # Test comprehensive health report
        report = await checker.generate_health_report([test_file_path])
        print(f"✓ Health report generated")
        print(f"  - Overall status: {report.overall_status.value}")
        print(f"  - Files checked: {len(report.integrity_checks)}")
        print(f"  - Alerts: {len(report.alerts)}")
        print(f"  - Recommendations: {len(report.recommendations)}")
        
        # Save report
        report_path = "/tmp/test_health_report.json"
        success = await checker.save_health_report(report, report_path)
        if success:
            print(f"✓ Health report saved to: {report_path}")
        else:
            print("✗ Failed to save health report")
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup test file
        try:
            os.remove(test_file_path)
            os.remove("/tmp/performance_test_file.tmp")  # Remove if it exists
            print(f"✓ Cleaned up test files")
        except:
            pass


async def test_example_usage():
    """Test the example usage function"""
    print("\nTesting example usage...")
    
    try:
        report = await example_usage()
        print(f"✓ Example usage completed successfully")
        print(f"  - Report ID: {report.report_id}")
        print(f"  - Overall status: {report.overall_status.value}")
        return True
    except Exception as e:
        print(f"✗ Example usage failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("File Health Check System - Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    await test_basic_functionality()
    
    # Test example usage
    success = await test_example_usage()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests completed successfully!")
    else:
        print("✗ Some tests failed")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())