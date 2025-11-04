"""
Audit Trail Logging System Package

Provides comprehensive audit trail functionality including:
- Detailed file operation logging
- User action tracking and attribution
- Supabase integration for persistent storage
- Audit report generation and analytics
- Compliance-ready logging formats
- Real-time audit event streaming
- Security event detection and alerting

Usage:
    from src.file_management.audit import AuditLogger, AuditEventType, SecurityLevel
    
    audit_logger = AuditLogger(supabase_url, supabase_key)
    await audit_logger.initialize()
    
    # Log events
    await audit_logger.log_event(event)
    
    # Generate reports
    report = await audit_logger.generate_compliance_report(...)
"""

from .audit_logger import (
    AuditLogger,
    AuditEvent,
    AuditEventType,
    SecurityLevel,
    ComplianceStandard,
    SecurityEventDetector,
    log_file_operation,
    log_user_activity
)

__version__ = "1.0.0"
__all__ = [
    "AuditLogger",
    "AuditEvent", 
    "AuditEventType",
    "SecurityLevel",
    "ComplianceStandard",
    "SecurityEventDetector",
    "log_file_operation",
    "log_user_activity"
]
