#!/usr/bin/env python3
"""
Demo and Test Script for Audit Trail Logging System

This script demonstrates the comprehensive capabilities of the audit trail
logging system including file operations, user tracking, compliance reporting,
and security event detection.
"""

import sys
import logging
from datetime import datetime, timezone, timedelta
from typing import List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from audit_logger import (
    AuditLogger,
    AuditEventType,
    SecurityLevel,
    ComplianceStandard,
    log_file_operation,
    log_user_activity
)
from audit.config import (
    setup_development_audit_logger,
    AuditConfig,
    AuditLoggerFactory
)


logger = logging.getLogger(__name__)

class AuditLoggerDemo:
    """Demonstration class for audit logger capabilities"""
    
    def __init__(self):
        self.logger = None
        self.demo_users = [
            {"id": "user001", "email": "alice@company.com", "ip": "192.168.1.100"},
            {"id": "user002", "email": "bob@company.com", "ip": "192.168.1.101"},
            {"id": "user003", "email": "charlie@company.com", "ip": "192.168.1.102"},
        ]
        self.demo_files = [
            {"path": "/documents/quarterly_report.pdf", "size": 2048576, "type": "pdf"},
            {"path": "/finance/budget_2024.xlsx", "size": 5242880, "type": "xlsx"},
            {"path": "/customers/customer_data.csv", "size": 1048576, "type": "csv"},
            {"path": "/hr/employee_info.xlsx", "size": 2097152, "type": "xlsx"},
            {"path": "/legal/contracts.pdf", "size": 3145728, "type": "pdf"},
        ]
    
    async def run_comprehensive_demo(self):
        """Run comprehensive demonstration of all audit logger features"""
        
        logger.info("🚀 Starting Comprehensive Audit Logger Demo")
        logger.info("=" * 60)
        
        # Initialize audit logger
        logger.info("\n📋 Initializing Audit Logger...")
        self.logger = await setup_development_audit_logger()
        
        try:
            # Demo 1: Basic File Operations
            await self.demo_file_operations()
            
            # Demo 2: User Activity Tracking
            await self.demo_user_activities()
            
            # Demo 3: Security Event Simulation
            await self.demo_security_events()
            
            # Demo 4: Compliance Events
            await self.demo_compliance_events()
            
            # Demo 5: Context Manager Usage
            await self.demo_context_manager()
            
            # Demo 6: Real-time Streaming
            await self.demo_streaming()
            
            # Demo 7: Report Generation
            await self.demo_report_generation()
            
            # Demo 8: Database Queries
            await self.demo_database_queries()
            
            logger.info("\n✅ Demo completed successfully!")
            
        finally:
            await self.cleanup()
    
    async def demo_file_operations(self):
        """Demonstrate various file operation logging"""
        
        logger.info("\n📁 Demo 1: File Operations")
        logger.info("-" * 30)
        
        operations = ["upload", "download", "access", "modify", "delete"]
        
        for i, operation in enumerate(operations):
            user = self.demo_users[i % len(self.demo_users)]
            file_info = self.demo_files[i % len(self.demo_files)]
            
            await log_file_operation(
                audit_logger=self.logger,
                operation=operation,
                user_id=user["id"],
                file_path=file_info["path"],
                user_email=user["email"],
                ip_address=user["ip"],
                details={
                    "file_size": file_info["size"],
                    "file_type": file_info["type"],
                    "department": file_info["path"].split("/")[1] if "/" in file_info["path"] else "general"
                },
                compliance_tags=[
                    ComplianceStandard.GDPR,
                    ComplianceStandard.SOX if "finance" in file_info["path"] else None
                ].filter(None),
                security_level=SecurityLevel.HIGH if "finance" in file_info["path"] else SecurityLevel.MEDIUM
            )
            
            logger.info(f"  ✓ Logged {operation} operation for {file_info['path']} by {user['id']}")
    
    async def demo_user_activities(self):
        """Demonstrate user activity tracking"""
        
        logger.info("\n👤 Demo 2: User Activities")
        logger.info("-" * 30)
        
        activities = ["login", "logout", "activity"]
        
        for activity in activities:
            for user in self.demo_users:
                await log_user_activity(
                    audit_logger=self.logger,
                    activity=activity,
                    user_id=user["id"],
                    user_email=user["email"],
                    ip_address=user["ip"],
                    details={
                        "session_duration": "3600" if activity == "logout" else None,
                        "device_type": "desktop",
                        "browser": "Chrome 120.0"
                    }
                )
            
            logger.info(f"  ✓ Logged {activity} activities for all users")
    
    async def demo_security_events(self):
        """Demonstrate security event detection"""
        
        logger.info("\n🔒 Demo 3: Security Events")
        logger.info("-" * 30)
        
        # Simulate failed login attempts
        for i in range(6):  # This should trigger multiple failure detection
            await log_user_activity(
                audit_logger=self.logger,
                activity="login",
                user_id="intruder_user",
                user_email="intruder@unknown.com",
                ip_address="10.0.0.50",  # Different IP range
                details={
                    "login_method": "password",
                    "failure_reason": "invalid_credentials"
                },
                security_level=SecurityLevel.HIGH
            )
        
        logger.info("  ✓ Simulated brute force attack (should trigger security alert)")
        
        # Simulate unusual file access
        for i in range(15):  # Access many files to trigger unusual access detection
            await log_file_operation(
                audit_logger=self.logger,
                operation="access",
                user_id="suspicious_user",
                file_path=f"/documents/file_{i:03d}.pdf",
                details={"access_reason": "bulk_access"}
            )
        
        logger.info("  ✓ Simulated unusual file access pattern")
    
    async def demo_compliance_events(self):
        """Demonstrate compliance-specific logging"""
        
        logger.info("\n📊 Demo 4: Compliance Events")
        logger.info("-" * 30)
        
        # GDPR specific events
        gdpr_events = [
            ("data_subject_request", {"request_type": "data_export"}),
            ("consent_update", {"consent_status": "withdrawn"}),
            ("data_retention_check", {"data_category": "customer_data", "retention_period": "7_years"})
        ]
        
        for event_type, details in gdpr_events:
            await log_file_operation(
                audit_logger=self.logger,
                operation="access",
                user_id="privacy_officer",
                file_path="/compliance/gdpr_data/",
                details={**details, "compliance_reference": "GDPR_Article_15"},
                compliance_tags=[ComplianceStandard.GDPR],
                security_level=SecurityLevel.MEDIUM
            )
        
        logger.info("  ✓ Logged GDPR compliance events")
        
        # HIPAA specific events
        hipaa_events = [
            ("phi_access", {"patient_id": "PATIENT_123", "access_reason": "treatment"}),
            ("unauthorized_access_attempt", {"attempted_resource": "/medical_records/PATIENT_456"})
        ]
        
        for event_type, details in hipaa_events:
            await log_file_operation(
                audit_logger=self.logger,
                operation="access",
                user_id="medical_staff",
                file_path="/medical_records/",
                details={**details, "wha_category": "treatment"},
                compliance_tags=[ComplianceStandard.HIPAA],
                security_level=SecurityLevel.HIGH
            )
        
        logger.info("  ✓ Logged HIPAA compliance events")
        
        # SOX specific events
        sox_events = [
            ("financial_data_access", {"data_type": "quarterly_revenue"}),
            ("approval_required_action", {"action_type": "financial_report_modification"})
        ]
        
        for event_type, details in sox_events:
            await log_file_operation(
                audit_logger=self.logger,
                operation="modify",
                user_id="finance_manager",
                file_path="/finance/reports/",
                details={**details, "approval_status": "pending"},
                compliance_tags=[ComplianceStandard.SOX],
                security_level=SecurityLevel.HIGH
            )
        
        logger.info("  ✓ Logged SOX compliance events")
    
    async def demo_context_manager(self):
        """Demonstrate context manager usage"""
        
        logger.info("\n🔄 Demo 5: Context Manager")
        logger.info("-" * 30)
        
        # Simulate a complex business process
        async with self.logger.audit_context(
            user_id="user001",
            action="customer_data_processing",
            resource_path="/data/customers/process_2024/",
            event_type=AuditEventType.FILE_MODIFY,
            security_level=SecurityLevel.HIGH,
            compliance_tags=[ComplianceStandard.GDPR, ComplianceStandard.HIPAA]
        ) as event:
            # Simulate business logic
            logger.info("  📊 Processing customer data...")
            await asyncio.sleep(0.1)
            
            # Add processing details
            event.details['records_processed'] = 1250
            event.details['data_validation_passed'] = True
            event.details['sensitive_fields_encrypted'] = True
            event.details['processing_time_ms'] = 250
            
            logger.info("  ✓ Customer data processing completed")
        
        # Another context manager example
        async with self.logger.audit_context(
            user_id="user002",
            action="system_backup",
            resource_path="/backups/daily/",
            event_type=AuditEventType.SYSTEM_EVENT,
            security_level=SecurityLevel.MEDIUM
        ) as event:
            logger.info("  💾 Creating system backup...")
            await asyncio.sleep(0.05)
            
            event.details['backup_size_gb'] = 15.7
            event.details['backup_type'] = 'incremental'
            event.details['compression_ratio'] = 0.73
            event.details['verification_status'] = 'passed'
            
            logger.info("  ✓ System backup completed")
    
    async def demo_streaming(self):
        """Demonstrate real-time event streaming"""
        
        logger.info("\n🌊 Demo 6: Real-time Streaming")
        logger.info("-" * 30)
        
        # Define streaming callbacks
        async def file_operation_streamer(event):
            logger.info(f"    📡 STREAM: {event.action} - {event.resource_path}")
        
        async def security_event_streamer(event):
            if event.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                logger.info(f"    🚨 SECURITY STREAM: {event.action} - Level: {event.security_level.value}")
        
        async def compliance_streamer(event):
            if event.compliance_tags:
                tags = [tag.value for tag in event.compliance_tags]
                logger.info(f"    📋 COMPLIANCE STREAM: {event.action} - Tags: {tags}")
        
        # Register callbacks
        self.logger.register_streaming_callback(file_operation_streamer)
        self.logger.register_streaming_callback(security_event_streamer)
        self.logger.register_streaming_callback(compliance_streamer)
        
        logger.info("  📡 Registered streaming callbacks")
        
        # Trigger streaming events
        await log_file_operation(
            audit_logger=self.logger,
            operation="upload",
            user_id="user003",
            file_path="/documents/streaming_demo.pdf",
            details={"streaming_test": True},
            compliance_tags=[ComplianceStandard.GDPR],
            security_level=SecurityLevel.MEDIUM
        )
        
        logger.info("  ✓ Streaming events triggered")
    
    async def demo_report_generation(self):
        """Demonstrate compliance report generation"""
        
        logger.info("\n📈 Demo 7: Report Generation")
        logger.info("-" * 30)
        
        # Generate reports for different compliance standards
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(hours=2)  # Recent events only
        
        standards = [ComplianceStandard.GDPR, ComplianceStandard.SOX, ComplianceStandard.HIPAA]
        
        for standard in standards:
            logger.info(f"  📊 Generating {standard.value.upper()} compliance report...")
            
            report = await self.logger.generate_compliance_report(
                standard=standard,
                start_date=start_date,
                end_date=end_date
            )
            
            if report:
                metadata = report['report_metadata']
                logger.info(f"    ✓ {metadata['total_events']} events analyzed")
                logger.info(f"    ✓ {metadata['unique_users']} unique users")
                logger.info(f"    ✓ {metadata['period']['start'][:19]} to {metadata['period']['end'][:19]}")
                
                # Show summary statistics
                if 'summary' in report:
                    summary = report['summary']
                    if 'event_types' in summary:
                        top_event_type = max(summary['event_types'].items(), key=lambda x: x[1])
                        logger.info(f"    ✓ Most common event: {top_event_type[0]} ({top_event_type[1]} times)")
                
                # Show compliance-specific data
                compliance_key = f"{standard.value}_specific"
                if compliance_key in report:
                    logger.info(f"    ✓ {compliance_key} data included")
            else:
                logger.info(f"    ⚠️ No {standard.value.upper()} events found in time range")
    
    async def demo_database_queries(self):
        """Demonstrate database query capabilities"""
        
        logger.info("\n🗄️ Demo 8: Database Queries")
        logger.info("-" * 30)
        
        # Query recent events
        logger.info("  📅 Fetching recent events...")
        recent_events = await self.logger.get_recent_events(hours=1, limit=10)
        
        logger.info(f"    ✓ Found {len(recent_events)} events in last hour")
        
        # Query events by user
        if recent_events:
            sample_user = recent_events[0].user_id
            user_events = await self.logger.get_recent_events(user_id=sample_user, limit=5)
            logger.info(f"    ✓ Found {len(user_events)} events for user {sample_user}")
        
        # Query events by type
        file_events = await self.logger.get_recent_events(
            event_type=AuditEventType.FILE_UPLOAD, 
            limit=5
        )
        logger.info(f"    ✓ Found {len(file_events)} file upload events")
        
        # Show event details
        if recent_events:
            latest_event = recent_events[0]
            logger.info(f"    ✓ Latest event: {latest_event.event_type.value} by {latest_event.user_id}")
            logger.info(f"    ✓ Security level: {latest_event.security_level.value}")
            logger.info(f"    ✓ Compliance tags: {[tag.value for tag in latest_event.compliance_tags]}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.logger:
            await self.logger.close()
        logger.info("\n🧹 Cleanup completed")


async def main():
    """Main demo execution"""
    
    logger.info("🎯 Audit Trail Logging System - Comprehensive Demo")
    logger.info("=" * 60)
    logger.info("This demo showcases:")
    logger.info("• File operation logging")
    logger.info("• User activity tracking")
    logger.info("• Security event detection")
    logger.info("• Compliance event logging")
    logger.info("• Context manager usage")
    logger.info("• Real-time event streaming")
    logger.info("• Report generation")
    logger.info("• Database queries")
    logger.info("=" * 60)
    
    # Check if Supabase environment variables are set
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.info("\n⚠️ Warning: SUPABASE_URL and/or SUPABASE_SERVICE_ROLE_KEY not set")
        logger.info("   Demo will use development configuration")
        logger.info("   Set environment variables for full functionality:")
        logger.info("   export SUPABASE_URL='your-supabase-url'")
        logger.info("   export SUPABASE_SERVICE_ROLE_KEY='your-supabase-key'")
    
    try:
        demo = AuditLoggerDemo()
        await demo.run_comprehensive_demo()
        
    except Exception as e:
        logger.info(f"\n❌ Demo failed with error: {e}")
        logger.info(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
