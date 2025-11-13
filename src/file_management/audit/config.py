"""
Audit Logger Configuration and Setup Examples

This module provides configuration templates and examples for setting up
the audit trail logging system in different environments and use cases.
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

from .audit_logger import (
    AuditLogger, 
    AuditEventType, 
    SecurityLevel, 
    ComplianceStandard,
    log_file_operation,
    log_user_activity
)


logger = logging.getLogger(__name__)

class AuditConfig:
    """Configuration class for audit logger settings"""
    
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        environment: str = "development",
        compliance_standards: List[ComplianceStandard] = None,
        retention_days: int = 2555,
        enable_streaming: bool = True,
        enable_security_detection: bool = True
    ):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.environment = environment
        self.compliance_standards = compliance_standards or [ComplianceStandard.GDPR]
        self.retention_days = retention_days
        self.enable_streaming = enable_streaming
        self.enable_security_detection = enable_security_detection


logger = logging.getLogger(__name__)

class AuditLoggerFactory:
    """Factory class for creating configured audit loggers"""
    
    @staticmethod
    def create_file_management_logger(config: AuditConfig) -> AuditLogger:
        """Create audit logger specifically for file management operations"""
        
        logger = AuditLogger(config.supabase_url, config.supabase_key)
        
        # Configure for file management specific events
        if config.enable_streaming:
            logger.register_streaming_callback(AuditLoggerFactory._file_operation_streamer)
        
        if config.enable_security_detection:
            logger.register_streaming_callback(AuditLoggerFactory._security_event_handler)
        
        return logger
    
    @staticmethod
    def create_compliance_logger(config: AuditConfig, standards: List[ComplianceStandard]) -> AuditLogger:
        """Create audit logger configured for specific compliance standards"""
        
        logger = AuditLogger(config.supabase_url, config.supabase_key)
        
        # Add compliance-specific streaming callbacks
        for standard in standards:
            callback_name = f"_compliance_streamer_{standard.value}"
            if hasattr(AuditLoggerFactory, callback_name):
                callback = getattr(AuditLoggerFactory, callback_name)
                logger.register_streaming_callback(callback)
        
        return logger
    
    @staticmethod
    async def _file_operation_streamer(event) -> None:
        """Real-time streaming callback for file operations"""
        logger.info(f"FILE OPERATION: {event.action} on {event.resource_path} by {event.user_id}")
        
        # Here you could integrate with:
        # - Real-time monitoring dashboards
        # - Slack/Teams notifications
        # - Email alerts for critical operations
    
    @staticmethod
    async def _security_event_handler(event) -> None:
        """Handle security events in real-time"""
        if event.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            logger.info(f"SECURITY ALERT: {event.action} by {event.user_id} - Level: {event.security_level.value}")
            
            # Here you could integrate with:
            # - SIEM systems
            # - Incident response platforms
            # - Automated security controls
    
    @staticmethod
    async def _compliance_streamer_gdpr(event) -> None:
        """GDPR-specific event streaming"""
        if ComplianceStandard.GDPR in event.compliance_tags:
            logger.info(f"GDPR EVENT: {event.action} - Data subject: {event.user_id}")
    
    @staticmethod
    async def _compliance_streamer_hipaa(event) -> None:
        """HIPAA-specific event streaming"""
        if ComplianceStandard.HIPAA in event.compliance_tags:
            logger.info(f"HIPAA EVENT: {event.action} - PHI access by: {event.user_id}")
    
    @staticmethod
    async def _compliance_streamer_sox(event) -> None:
        """SOX-specific event streaming"""
        if ComplianceStandard.SOX in event.compliance_tags:
            logger.info(f"SOX EVENT: {event.action} - Financial data access by: {event.user_id}")


async def setup_production_audit_logger() -> AuditLogger:
    """Setup audit logger for production environment"""
    
    config = AuditConfig(
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        environment="production",
        compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.SOX],
        retention_days=2555,  # 7 years
        enable_streaming=True,
        enable_security_detection=True
    )
    
    logger = AuditLoggerFactory.create_file_management_logger(config)
    await logger.initialize()
    
    return logger


async def setup_compliance_audit_logger(standards: List[ComplianceStandard]) -> AuditLogger:
    """Setup audit logger for specific compliance requirements"""
    
    config = AuditConfig(
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        environment="compliance",
        compliance_standards=standards
    )
    
    logger = AuditLoggerFactory.create_compliance_logger(config, standards)
    await logger.initialize()
    
    return logger


async def setup_development_audit_logger() -> AuditLogger:
    """Setup audit logger for development environment"""
    
    config = AuditConfig(
        supabase_url="http://localhost:54321",  # Local Supabase
        supabase_key="your-local-key",
        environment="development",
        compliance_standards=[ComplianceStandard.GDPR],
        retention_days=90,  # Shorter retention for dev
        enable_streaming=False,  # Disable streaming in dev
        enable_security_detection=True
    )
    
    logger = AuditLoggerFactory.create_file_management_logger(config)
    await logger.initialize()
    
    return logger


async def demo_comprehensive_logging():
    """Demonstrate comprehensive audit logging capabilities"""
    
    logger = await setup_development_audit_logger()
    
    try:
        # Log various types of file operations
        await log_file_operation(
            audit_logger=logger,
            operation="upload",
            user_id="user123",
            file_path="/documents/report.pdf",
            user_email="user@example.com",
            ip_address="192.168.1.100",
            details={
                "file_size": 2048576,
                "file_type": "pdf",
                "department": "finance"
            },
            compliance_tags=[ComplianceStandard.GDPR, ComplianceStandard.SOX],
            security_level=SecurityLevel.MEDIUM
        )
        
        await log_file_operation(
            audit_logger=logger,
            operation="download",
            user_id="user456",
            file_path="/documents/sensitive_data.xlsx",
            user_email="user2@example.com",
            ip_address="192.168.1.101",
            details={
                "file_size": 5242880,
                "file_type": "xlsx",
                "sensitivity": "high"
            },
            compliance_tags=[ComplianceStandard.GDPR, ComplianceStandard.HIPAA],
            security_level=SecurityLevel.HIGH
        )
        
        # Log user activities
        await log_user_activity(
            audit_logger=logger,
            activity="login",
            user_id="user123",
            user_email="user@example.com",
            ip_address="192.168.1.100",
            details={
                "login_method": "sso",
                "device_type": "desktop"
            }
        )
        
        # Use context manager for complex operations
        async with logger.audit_context(
            user_id="user123",
            action="process_customer_data",
            resource_path="/data/customers/",
            event_type=AuditEventType.FILE_MODIFY,
            security_level=SecurityLevel.HIGH,
            compliance_tags=[ComplianceStandard.GDPR, ComplianceStandard.HIPAA]
        ) as event:
            # Simulate business logic
            await asyncio.sleep(0.1)
            event.details['records_processed'] = 150
            event.details['data_classification'] = "customer_pii"
        
        # Generate compliance reports
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)
        
        gdpr_report = await logger.generate_compliance_report(
            standard=ComplianceStandard.GDPR,
            start_date=start_date,
            end_date=end_date
        )
        
        sox_report = await logger.generate_compliance_report(
            standard=ComplianceStandard.SOX,
            start_date=start_date,
            end_date=end_date
        )
        
        logger.info(f"GDPR Report: {gdpr_report['report_metadata']['total_events']} events")
        logger.info(f"SOX Report: {sox_report['report_metadata']['total_events']} events")
        
        # Demonstrate real-time streaming
        def streaming_callback(event):
            logger.info(f"STREAM: {event.event_type.value} - {event.action}")
        
        logger.register_streaming_callback(streaming_callback)
        
        # Trigger streaming with a new event
        await log_file_operation(
            audit_logger=logger,
            operation="access",
            user_id="user789",
            file_path="/documents/public_info.txt",
            details={"access_reason": "reference"}
        )
        
    finally:
        await logger.close()


# Integration examples for different frameworks

logger = logging.getLogger(__name__)

class FlaskAuditMiddleware:
    """Audit middleware for Flask applications"""
    
    def __init__(self, app, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        app.before_request(self._before_request)
        app.after_request(self._after_request)
    
    def _before_request(self):
        """Log request start"""
        from flask import request, session, g
        
        g.audit_start_time = datetime.now(timezone.utc)
        
        if 'user_id' in session:
            event = self.audit_logger.create_audit_event(
                event_type=AuditEventType.USER_ACTIVITY,
                user_id=session['user_id'],
                action=f"request_{request.method}",
                resource_path=request.path,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                details={
                    'endpoint': request.endpoint,
                    'args': dict(request.args),
                    'form': dict(request.form) if request.form else {}
                }
            )
            g.audit_event = event
    
    def _after_request(self, response):
        """Log request completion"""
        from flask import request, g
        
        if hasattr(g, 'audit_event'):
            g.audit_event.status = 'success' if response.status_code < 400 else 'error'
            g.audit_event.details['response_status'] = response.status_code
            g.audit_event.details['duration_ms'] = (
                datetime.now(timezone.utc) - g.audit_start_time
            ).total_seconds() * 1000
            
            # Note: This should be done asynchronously in production
            asyncio.create_task(self.audit_logger.log_event(g.audit_event))
        
        return response


async def setup_fastapi_audit_middleware():
    """Example of FastAPI audit middleware setup"""
    
    logger = await setup_production_audit_logger()
    
    # In FastAPI, you would implement middleware like this:
    """
    from fastapi import Request, Response
    import time
    
    @app.middleware("http")
    async def audit_middleware(request: Request, call_next):
        start_time = time.time()
        
        # Log request start
        user_id = request.headers.get("X-User-ID", "anonymous")
        event = logger.create_audit_event(
            event_type=AuditEventType.USER_ACTIVITY,
            user_id=user_id,
            action="fastapi_request",
            resource_path=request.url.path,
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("User-Agent", "unknown"),
            details={
                "method": request.method,
                "headers": dict(request.headers),
                "query_params": dict(request.query_params)
            }
        )
        
        response = await call_next(request)
        
        # Log completion
        event.status = "success"
        event.details["response_status"] = response.status_code
        event.details["duration_ms"] = (time.time() - start_time) * 1000
        
        await logger.log_event(event)
        
        return response
    """
    
    return logger


if __name__ == "__main__":
    asyncio.run(demo_comprehensive_logging())