# Comprehensive Audit Trail Logging System

A production-ready, enterprise-grade audit trail logging system with Supabase integration, security event detection, and compliance reporting capabilities.

## Features

### Core Functionality
- **Detailed File Operation Logging**: Track upload, download, delete, modify, and access operations
- **User Action Tracking**: Comprehensive user activity monitoring with session management
- **Supabase Integration**: Persistent storage in PostgreSQL with connection pooling
- **Real-time Event Streaming**: Live audit event streaming with callback support
- **Security Event Detection**: Advanced security pattern recognition and alerting

### Compliance & Reporting
- **Multi-Standard Compliance**: GDPR, HIPAA, SOX, PCI-DSS, ISO 27001, CIS support
- **Audit Report Generation**: Automated compliance report creation
- **Analytics Dashboard**: Security trends and risk analysis
- **Data Retention Management**: Configurable retention policies (default: 7 years)

### Security Features
- **Event Integrity**: SHA-256 checksums for audit trail integrity
- **Anomaly Detection**: Multiple security event pattern recognition
- **Risk Scoring**: Automated risk assessment for security events
- **High-Risk Alerting**: Immediate notification for critical security events

## Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r src/file_management/audit/requirements.txt
```

2. Set up environment variables:
```bash
export SUPABASE_URL="your-supabase-url"
export SUPABASE_SERVICE_ROLE_KEY="your-supabase-key"
```

### Basic Usage

```python
import asyncio
from src.file_management.audit import AuditLogger, AuditEventType, SecurityLevel, ComplianceStandard
from src.file_management.audit.config import setup_production_audit_logger

async def main():
    # Initialize audit logger
    logger = await setup_production_audit_logger()
    
    try:
        # Log a file operation
        event = logger.create_audit_event(
            event_type=AuditEventType.FILE_UPLOAD,
            user_id="user123",
            action="upload_report",
            resource_path="/documents/quarterly_report.pdf",
            user_email="user@company.com",
            security_level=SecurityLevel.MEDIUM,
            compliance_tags=[ComplianceStandard.SOX],
            details={
                "file_size": 2048576,
                "department": "finance"
            }
        )
        
        await logger.log_event(event)
        
        # Generate compliance report
        from datetime import datetime, timezone, timedelta
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)
        
        report = await logger.generate_compliance_report(
            standard=ComplianceStandard.GDPR,
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"Generated report with {report['report_metadata']['total_events']} events")
        
    finally:
        await logger.close()

# Run the example
asyncio.run(main())
```

### Using Convenience Functions

```python
from src.file_management.audit import log_file_operation, log_user_activity

# Log file operations
await log_file_operation(
    audit_logger=logger,
    operation="upload",
    user_id="user123",
    file_path="/documents/important_file.pdf",
    user_email="user@company.com",
    ip_address="192.168.1.100",
    details={"file_size": 1024, "file_type": "pdf"},
    compliance_tags=[ComplianceStandard.GDPR, ComplianceStandard.SOX]
)

# Log user activities
await log_user_activity(
    audit_logger=logger,
    activity="login",
    user_id="user123",
    user_email="user@company.com",
    ip_address="192.168.1.100"
)
```

### Context Manager Usage

```python
async with logger.audit_context(
    user_id="user123",
    action="process_customer_data",
    resource_path="/data/customers/",
    event_type=AuditEventType.FILE_MODIFY,
    security_level=SecurityLevel.HIGH,
    compliance_tags=[ComplianceStandard.GDPR, ComplianceStandard.HIPAA]
) as event:
    # Your business logic here
    await process_customer_data()
    
    # Add custom details
    event.details['records_processed'] = 150
    event.details['data_classification'] = "customer_pii"
```

## Configuration

### Environment-Specific Setup

#### Production Environment
```python
from src.file_management.audit.config import setup_production_audit_logger

logger = await setup_production_audit_logger()
```

#### Development Environment
```python
from src.file_management.audit.config import setup_development_audit_logger

logger = await setup_development_audit_logger()
```

#### Compliance-Focused Setup
```python
from src.file_management.audit.config import setup_compliance_audit_logger
from src.file_management.audit import ComplianceStandard

logger = await setup_compliance_audit_logger([
    ComplianceStandard.GDPR,
    ComplianceStandard.HIPAA,
    ComplianceStandard.SOX
])
```

### Custom Configuration

```python
from src.file_management.audit.config import AuditConfig, AuditLoggerFactory

config = AuditConfig(
    supabase_url="your-supabase-url",
    supabase_key="your-supabase-key",
    environment="production",
    compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.SOX],
    retention_days=2555,  # 7 years
    enable_streaming=True,
    enable_security_detection=True
)

logger = AuditLoggerFactory.create_file_management_logger(config)
await logger.initialize()
```

## Real-time Event Streaming

### Register Streaming Callbacks

```python
async def my_streaming_callback(event):
    print(f"Real-time event: {event.event_type.value} - {event.action}")
    
    # Send to monitoring systems
    await send_to_monitoring_dashboard(event)
    
    # Send alerts for critical events
    if event.security_level == SecurityLevel.CRITICAL:
        await send_security_alert(event)

# Register callback
logger.register_streaming_callback(my_streaming_callback)
```

### Webhook Integration

```python
async def webhook_callback(event):
    if event.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
        webhook_data = {
            "alert_type": "security_event",
            "event_id": event.event_id,
            "user_id": event.user_id,
            "action": event.action,
            "security_level": event.security_level.value,
            "timestamp": event.timestamp.isoformat()
        }
        
        await send_webhook("https://alerts.company.com/security", webhook_data)

logger.register_streaming_callback(webhook_callback)
```

## Security Event Detection

The system automatically detects various security patterns:

### Detected Patterns
- **Multiple Failed Logins**: 5+ failed login attempts
- **Unusual File Access**: Accessing 100+ files in short period
- **Privilege Escalation**: Administrative permission changes
- **Data Exfiltration**: Bulk downloads (50+ files)
- **Brute Force Attacks**: 20+ failed attempts from same IP

### Risk Scoring
Events are automatically scored (0-10 scale):
- **Low Risk (0-3)**: Routine operations
- **Medium Risk (3-7)**: Monitor closely
- **High Risk (7-9)**: Immediate attention required
- **Critical Risk (10)**: Emergency response needed

### Alert Management
```python
async def handle_security_alert(event, analysis):
    risk_score = analysis['risk_score']
    
    if risk_score >= 9.0:
        await send_emergency_alert(event, analysis)
        await lock_user_account(event.user_id)
    elif risk_score >= 7.0:
        await send_security_team_notification(event, analysis)
        await increase_monitoring(event.user_id)

# Register alert handler
logger.register_streaming_callback(handle_security_alert)
```

## Compliance Reporting

### Supported Standards

#### GDPR (General Data Protection Regulation)
```python
report = await logger.generate_compliance_report(
    standard=ComplianceStandard.GDPR,
    start_date=start_date,
    end_date=end_date,
    user_id="specific_user"  # Optional
)

# Report includes:
# - Personal data access events
# - Data subject requests
# - Consent tracking
# - Data retention compliance
```

#### HIPAA (Health Insurance Portability and Accountability Act)
```python
report = await logger.generate_compliance_report(
    standard=ComplianceStandard.HIPAA,
    start_date=start_date,
    end_date=end_date
)

# Report includes:
# - PHI access events
# - Unauthorized access attempts
# - WHA violations
# - Minimum necessary compliance
```

#### SOX (Sarbanes-Oxley Act)
```python
report = await logger.generate_compliance_report(
    standard=ComplianceStandard.SOX,
    start_date=start_date,
    end_date=end_date
)

# Report includes:
# - Financial data access
# - Approval requirements
# - Segregation of duties
# - Data integrity checks
```

## Framework Integration

### Flask Integration

```python
from flask import Flask
from src.file_management.audit.config import FlaskAuditMiddleware, setup_production_audit_logger

app = Flask(__name__)

# Setup audit logging
logger = asyncio.run(setup_production_audit_logger())

# Add Flask middleware
audit_middleware = FlaskAuditMiddleware(app, logger)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Your file upload logic here
    return {'status': 'uploaded'}
```

### FastAPI Integration

```python
from fastapi import FastAPI, Request
from src.file_management.audit.config import setup_production_audit_logger

app = FastAPI()
logger = asyncio.run(setup_production_audit_logger())

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
```

## Database Schema

The system creates the following PostgreSQL tables:

### audit_events
```sql
CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id VARCHAR(255) UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255),
    session_id VARCHAR(255) NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    resource_path TEXT NOT NULL,
    resource_id VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    details JSONB NOT NULL,
    security_level VARCHAR(50) NOT NULL,
    compliance_tags TEXT[] NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    parent_event_id UUID,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Indexes
```sql
CREATE INDEX idx_audit_events_user_id ON audit_events(user_id);
CREATE INDEX idx_audit_events_timestamp ON audit_events(timestamp);
CREATE INDEX idx_audit_events_event_type ON audit_events(event_type);
CREATE INDEX idx_audit_events_security_level ON audit_events(security_level);
```

## Best Practices

### 1. Environment Separation
- Use different configurations for development, staging, and production
- Set appropriate retention periods for each environment
- Enable/disable features based on environment requirements

### 2. Security Considerations
- Always use HTTPS for Supabase connections
- Implement proper access controls for audit data
- Regular backups of audit logs
- Monitor for unauthorized access to audit logs

### 3. Performance Optimization
- Use connection pooling for database operations
- Implement batch operations for high-volume scenarios
- Regular cleanup of old events
- Monitor database performance and optimize queries

### 4. Compliance Alignment
- Map audit events to specific compliance requirements
- Regular compliance report generation
- Document data retention policies
- Regular audit trail integrity verification

### 5. Monitoring and Alerting
- Set up monitoring for audit system health
- Implement alerting for security events
- Regular review of security patterns
- Monitor system performance and resource usage

## Troubleshooting

### Common Issues

#### Database Connection Issues
```python
# Check Supabase connection
try:
    await logger.initialize()
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")
```

#### Performance Issues
```python
# Enable query logging
import logging
logging.getLogger('asyncpg').setLevel(logging.DEBUG)

# Monitor connection pool
print(f"Pool size: {logger._pg_pool.get_size()}")
```

#### Memory Usage
```python
# Monitor event cache
print(f"Event cache size: {len(logger._event_cache)}")

# Manually cleanup cache
logger._event_cache = []
```

## API Reference

### AuditLogger

#### Methods
- `initialize()`: Initialize database connections
- `close()`: Close all connections and cleanup
- `create_audit_event()`: Create a new audit event
- `log_event(event, trigger_streaming=True)`: Log an audit event
- `get_recent_events()`: Retrieve recent audit events
- `generate_compliance_report()`: Generate compliance report
- `cleanup_old_events()`: Cleanup old events

#### Event Types
- `FILE_UPLOAD`, `FILE_DOWNLOAD`, `FILE_DELETE`, `FILE_MODIFY`
- `FILE_ACCESS`, `FILE_SHARE`, `FOLDER_CREATE`, `FOLDER_DELETE`
- `USER_LOGIN`, `USER_LOGOUT`, `USER_ACTIVITY`
- `PERMISSION_CHANGE`, `SYSTEM_EVENT`, `SECURITY_EVENT`

#### Security Levels
- `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`

#### Compliance Standards
- `GDPR`, `HIPAA`, `SOX`, `PCI_DSS`, `ISO_27001`, `CIS`

## License

This audit trail logging system is provided as-is for enterprise use. Ensure compliance with your organization's security and privacy policies when implementing audit logging systems.
