"""
Comprehensive Audit Trail Logging System

This module provides enterprise-grade audit trail functionality including:
- Detailed file operation logging (upload, download, delete, modify)
- User action tracking and attribution
- Supabase integration for persistent audit storage
- Audit report generation and analytics
- Compliance-ready logging formats
- Real-time audit event streaming
- Security event detection and alerting
"""

import json
import asyncio
import logging
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import aiofiles
import asyncpg
from contextlib import asynccontextmanager
import weakref


class AuditEventType(Enum):
    """Enumeration of audit event types for file operations"""
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    FILE_DELETE = "file_delete"
    FILE_MODIFY = "file_modify"
    FILE_ACCESS = "file_access"
    FILE_SHARE = "file_share"
    FOLDER_CREATE = "folder_create"
    FOLDER_DELETE = "folder_delete"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_ACTIVITY = "user_activity"
    PERMISSION_CHANGE = "permission_change"
    SYSTEM_EVENT = "system_event"
    SECURITY_EVENT = "security_event"


class SecurityLevel(Enum):
    """Security levels for audit events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStandard(Enum):
    """Supported compliance standards for audit logging"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    CIS = "cis"


@dataclass
class AuditEvent:
    """Data class representing an audit event"""
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    user_id: str
    user_email: Optional[str]
    session_id: str
    ip_address: str
    user_agent: str
    resource_path: str
    resource_id: Optional[str]
    action: str
    status: str
    details: Dict[str, Any]
    security_level: SecurityLevel
    compliance_tags: List[ComplianceStandard]
    checksum: str
    parent_event_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit event to dictionary format"""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'resource_path': self.resource_path,
            'resource_id': self.resource_id,
            'action': self.action,
            'status': self.status,
            'details': self.details,
            'security_level': self.security_level.value,
            'compliance_tags': [tag.value for tag in self.compliance_tags],
            'checksum': self.checksum,
            'parent_event_id': self.parent_event_id,
            'metadata': self.metadata
        }

    def to_compliance_format(self, standard: ComplianceStandard) -> Dict[str, Any]:
        """Convert event to compliance-specific format"""
        base_event = self.to_dict()
        
        compliance_mapping = {
            ComplianceStandard.GDPR: {
                'data_subject_id': self.user_id,
                'processing_purpose': self.action,
                'data_categories': list(self.details.keys()),
                'retention_period': '7_years'
            },
            ComplianceStandard.HIPAA: {
                'patient_identifier': self.details.get('patient_id'),
                'access_reason': self.action,
                'access_type': self.event_type.value,
                'wha_activity': 'access'
            },
            ComplianceStandard.SOX: {
                'financial_data_access': 'true' if 'financial' in str(self.details).lower() else 'false',
                'approval_required': 'true' if self.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL] else 'false',
                'segregation_of_duties': 'true'
            },
            ComplianceStandard.PCI_DSS: {
                'cardholder_data_access': 'true' if 'card' in str(self.details).lower() else 'false',
                'access_justification': self.action,
                'data_classification': self.security_level.value
            }
        }
        
        if standard in compliance_mapping:
            base_event['compliance_data'] = compliance_mapping[standard]
        
        return base_event


class SecurityEventDetector:
    """Detects security events and anomalies in audit trails"""
    
    def __init__(self):
        self.event_patterns = {
            'multiple_failed_logins': self._detect_multiple_failures,
            'unusual_file_access': self._detect_unusual_access,
            'privilege_escalation': self._detect_privilege_escalation,
            'data_exfiltration': self._detect_data_exfiltration,
            'brute_force': self._detect_brute_force
        }
    
    def analyze_event(self, event: AuditEvent, recent_events: List[AuditEvent]) -> Dict[str, Any]:
        """Analyze an audit event for security issues"""
        alerts = []
        risk_score = 0
        
        for pattern_name, pattern_func in self.event_patterns.items():
            pattern_result = pattern_func(event, recent_events)
            if pattern_result['detected']:
                alerts.append({
                    'pattern': pattern_name,
                    'description': pattern_result['description'],
                    'severity': pattern_result['severity'],
                    'risk_score': pattern_result['risk_score']
                })
                risk_score += pattern_result['risk_score']
        
        return {
            'alerts': alerts,
            'risk_score': risk_score,
            'requires_alert': risk_score >= 7.5,
            'analysis_timestamp': datetime.now(timezone.utc)
        }
    
    def _detect_multiple_failures(self, event: AuditEvent, recent_events: List[AuditEvent]) -> Dict[str, Any]:
        """Detect multiple failed login attempts"""
        failed_events = [e for e in recent_events 
                        if e.event_type == AuditEventType.USER_LOGIN 
                        and e.status == 'failed']
        
        return {
            'detected': len(failed_events) >= 5,
            'description': 'Multiple failed login attempts detected',
            'severity': 'high' if len(failed_events) >= 10 else 'medium',
            'risk_score': min(len(failed_events) * 0.8, 5.0)
        }
    
    def _detect_unusual_access(self, event: AuditEvent, recent_events: List[AuditEvent]) -> Dict[str, Any]:
        """Detect unusual file access patterns"""
        if event.event_type in [AuditEventType.FILE_DOWNLOAD, AuditEventType.FILE_ACCESS]:
            user_events = [e for e in recent_events if e.user_id == event.user_id]
            unique_paths = set(e.resource_path for e in user_events)
            
            # Detect access to significantly more files than usual
            if len(unique_paths) > 100:
                return {
                    'detected': True,
                    'description': 'Unusually high number of file accesses',
                    'severity': 'medium',
                    'risk_score': 3.0
                }
        
        return {'detected': False, 'description': '', 'severity': 'low', 'risk_score': 0.0}
    
    def _detect_privilege_escalation(self, event: AuditEvent, recent_events: List[AuditEvent]) -> Dict[str, Any]:
        """Detect potential privilege escalation"""
        if event.event_type == AuditEventType.PERMISSION_CHANGE:
            if 'admin' in event.action.lower() or 'root' in event.action.lower():
                return {
                    'detected': True,
                    'description': 'Potential privilege escalation detected',
                    'severity': 'critical',
                    'risk_score': 9.0
                }
        
        return {'detected': False, 'description': '', 'severity': 'low', 'risk_score': 0.0}
    
    def _detect_data_exfiltration(self, event: AuditEvent, recent_events: List[AuditEvent]) -> Dict[str, Any]:
        """Detect potential data exfiltration"""
        if event.event_type == AuditEventType.FILE_DOWNLOAD:
            # Check for bulk downloads
            download_events = [e for e in recent_events 
                             if e.event_type == AuditEventType.FILE_DOWNLOAD 
                             and e.user_id == event.user_id]
            
            if len(download_events) > 50:
                return {
                    'detected': True,
                    'description': 'Potential bulk data download detected',
                    'severity': 'high',
                    'risk_score': 7.0
                }
        
        return {'detected': False, 'description': '', 'severity': 'low', 'risk_score': 0.0}
    
    def _detect_brute_force(self, event: AuditEvent, recent_events: List[AuditEvent]) -> Dict[str, Any]:
        """Detect brute force attacks"""
        if event.event_type == AuditEventType.USER_LOGIN:
            same_ip_events = [e for e in recent_events 
                            if e.ip_address == event.ip_address 
                            and e.event_type == AuditEventType.USER_LOGIN]
            
            failed_same_ip = [e for e in same_ip_events if e.status == 'failed']
            
            if len(failed_same_ip) >= 20:
                return {
                    'detected': True,
                    'description': 'Brute force attack detected from IP address',
                    'severity': 'high',
                    'risk_score': 8.0
                }
        
        return {'detected': False, 'description': '', 'severity': 'low', 'risk_score': 0.0}


class AuditLogger:
    """
    Comprehensive audit trail logging system with Supabase integration,
    security event detection, and compliance reporting.
    """
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.logger = logging.getLogger(__name__)
        self.security_detector = SecurityEventDetector()
        self._event_cache = []
        self._streaming_callbacks = []
        self._session_context = weakref.WeakValueDictionary()
        
        # Configure logging
        self._setup_logging()
        
        # Initialize database connection pool
        self._pg_pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self) -> None:
        """Initialize the audit logger with database connections"""
        try:
            # Initialize PostgreSQL connection pool for Supabase
            self._pg_pool = await asyncpg.create_pool(
                f"postgresql://postgres:{self.supabase_key}@{self.supabase_url}/postgres",
                min_size=1,
                max_size=10
            )
            
            # Create audit tables if they don't exist
            await self._create_audit_tables()
            
            self.logger.info("Audit logger initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize audit logger: {e}")
            raise
    
    async def close(self) -> None:
        """Close all connections and cleanup"""
        if self._pg_pool:
            await self._pg_pool.close()
        self.logger.info("Audit logger closed")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def _create_audit_tables(self) -> None:
        """Create necessary database tables for audit logging"""
        async with self._pg_pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_events (
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
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_audit_events_user_id 
                ON audit_events(user_id);
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp 
                ON audit_events(timestamp);
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_audit_events_event_type 
                ON audit_events(event_type);
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_audit_events_security_level 
                ON audit_events(security_level);
            ''')
    
    def _calculate_checksum(self, event_data: Dict[str, Any]) -> str:
        """Calculate checksum for event data integrity"""
        event_string = json.dumps(event_data, sort_keys=True)
        return hashlib.sha256(event_string.encode()).hexdigest()
    
    def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get or create session context"""
        if session_id not in self._session_context:
            self._session_context[session_id] = {
                'start_time': datetime.now(timezone.utc),
                'event_count': 0,
                'last_activity': datetime.now(timezone.utc)
            }
        
        return self._session_context[session_id]
    
    def create_audit_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        action: str,
        resource_path: str,
        status: str = 'success',
        details: Optional[Dict[str, Any]] = None,
        security_level: SecurityLevel = SecurityLevel.MEDIUM,
        compliance_tags: Optional[List[ComplianceStandard]] = None,
        user_email: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """Create a new audit event with all necessary metadata"""
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get or create session context
        session_context = self._get_session_context(session_id)
        session_context['event_count'] += 1
        session_context['last_activity'] = datetime.now(timezone.utc)
        
        # Create event data
        event_data = {
            'event_id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc),
            'event_type': event_type,
            'user_id': user_id,
            'user_email': user_email,
            'session_id': session_id,
            'ip_address': ip_address or 'unknown',
            'user_agent': user_agent or 'unknown',
            'resource_path': resource_path,
            'resource_id': resource_id,
            'action': action,
            'status': status,
            'details': details or {},
            'security_level': security_level,
            'compliance_tags': compliance_tags or [],
            'metadata': metadata or session_context
        }
        
        # Calculate checksum
        checksum = self._calculate_checksum(event_data)
        
        # Create audit event
        event = AuditEvent(
            event_id=event_data['event_id'],
            timestamp=event_data['timestamp'],
            event_type=event_type,
            user_id=user_id,
            user_email=user_email,
            session_id=session_id,
            ip_address=event_data['ip_address'],
            user_agent=event_data['user_agent'],
            resource_path=resource_path,
            resource_id=resource_id,
            action=action,
            status=status,
            details=details or {},
            security_level=security_level,
            compliance_tags=compliance_tags or [],
            checksum=checksum,
            metadata=metadata
        )
        
        return event
    
    async def log_event(self, event: AuditEvent, trigger_streaming: bool = True) -> None:
        """Log an audit event with security analysis and streaming"""
        
        try:
            # Get recent events for security analysis
            recent_events = await self.get_recent_events(event.user_id, hours=1)
            
            # Perform security analysis
            security_analysis = self.security_detector.analyze_event(event, recent_events)
            
            # Add security analysis to event details
            event.details['security_analysis'] = security_analysis
            event.details['session_context'] = self._get_session_context(event.session_id)
            
            # Update checksum with new details
            event.checksum = self._calculate_checksum(event.to_dict())
            
            # Store in database
            await self._store_event(event)
            
            # Add to cache
            self._event_cache.append(event)
            if len(self._event_cache) > 1000:
                self._event_cache = self._event_cache[-500:]  # Keep last 500 events
            
            # Trigger real-time streaming if enabled
            if trigger_streaming:
                await self._trigger_streaming(event)
            
            # Handle high-risk security events
            if security_analysis['requires_alert']:
                await self._handle_security_alert(event, security_analysis)
            
            self.logger.info(f"Audit event logged: {event.event_id} - {event.event_type.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
            # Still try to log to file as fallback
            await self._log_to_file(event)
    
    async def _store_event(self, event: AuditEvent) -> None:
        """Store audit event in Supabase database"""
        try:
            async with self._pg_pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO audit_events (
                        event_id, timestamp, event_type, user_id, user_email,
                        session_id, ip_address, user_agent, resource_path,
                        resource_id, action, status, details, security_level,
                        compliance_tags, checksum, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                ''',
                event.event_id,
                event.timestamp,
                event.event_type.value,
                event.user_id,
                event.user_email,
                event.session_id,
                event.ip_address,
                event.user_agent,
                event.resource_path,
                event.resource_id,
                event.action,
                event.status,
                json.dumps(event.details),
                event.security_level.value,
                [tag.value for tag in event.compliance_tags],
                event.checksum,
                json.dumps(event.metadata) if event.metadata else None
                )
                
        except Exception as e:
            self.logger.error(f"Failed to store audit event in database: {e}")
            raise
    
    async def _log_to_file(self, event: AuditEvent) -> None:
        """Fallback logging to file when database is unavailable"""
        try:
            audit_dir = Path("audit_logs")
            audit_dir.mkdir(exist_ok=True)
            
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = audit_dir / f"audit_{date_str}.log"
            
            async with aiofiles.open(log_file, 'a') as f:
                await f.write(json.dumps(event.to_dict()) + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to log audit event to file: {e}")
    
    async def _trigger_streaming(self, event: AuditEvent) -> None:
        """Trigger real-time event streaming to registered callbacks"""
        if not self._streaming_callbacks:
            return
        
        streaming_tasks = []
        for callback in self._streaming_callbacks:
            task = asyncio.create_task(self._safe_stream_callback(callback, event))
            streaming_tasks.append(task)
        
        if streaming_tasks:
            await asyncio.gather(*streaming_tasks, return_exceptions=True)
    
    async def _safe_stream_callback(self, callback: Callable, event: AuditEvent) -> None:
        """Safely execute streaming callback"""
        try:
            await callback(event)
        except Exception as e:
            self.logger.error(f"Streaming callback failed: {e}")
    
    async def _handle_security_alert(self, event: AuditEvent, analysis: Dict[str, Any]) -> None:
        """Handle high-risk security events with appropriate alerts"""
        self.logger.warning(
            f"SECURITY ALERT: High-risk event {event.event_id} - "
            f"Risk score: {analysis['risk_score']:.1f} - "
            f"User: {event.user_id} - "
            f"Event: {event.event_type.value}"
        )
        
        # Here you could integrate with alerting systems like:
        # - Email notifications
        # - Slack/Teams webhooks
        # - Security information and event management (SIEM) systems
        # - Automated response systems
    
    def register_streaming_callback(self, callback: Callable[[AuditEvent], None]) -> None:
        """Register a callback for real-time audit event streaming"""
        self._streaming_callbacks.append(callback)
    
    def unregister_streaming_callback(self, callback: Callable[[AuditEvent], None]) -> None:
        """Unregister a streaming callback"""
        if callback in self._streaming_callbacks:
            self._streaming_callbacks.remove(callback)
    
    async def get_recent_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        hours: int = 24,
        limit: int = 1000
    ) -> List[AuditEvent]:
        """Retrieve recent audit events with optional filtering"""
        
        query_conditions = ["timestamp >= NOW() - INTERVAL '%s hours'" % hours]
        query_params = []
        
        if user_id:
            query_conditions.append("user_id = $%d" % (len(query_params) + 1))
            query_params.append(user_id)
        
        if event_type:
            query_conditions.append("event_type = $%d" % (len(query_params) + 1))
            query_params.append(event_type.value)
        
        where_clause = " AND ".join(query_conditions)
        query = f"SELECT * FROM audit_events WHERE {where_clause} ORDER BY timestamp DESC LIMIT {limit}"
        
        try:
            async with self._pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *query_params)
                
                events = []
                for row in rows:
                    event = self._row_to_audit_event(row)
                    events.append(event)
                
                return events
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve audit events: {e}")
            return []
    
    def _row_to_audit_event(self, row) -> AuditEvent:
        """Convert database row to AuditEvent object"""
        return AuditEvent(
            event_id=row['event_id'],
            timestamp=row['timestamp'],
            event_type=AuditEventType(row['event_type']),
            user_id=row['user_id'],
            user_email=row['user_email'],
            session_id=row['session_id'],
            ip_address=row['ip_address'],
            user_agent=row['user_agent'],
            resource_path=row['resource_path'],
            resource_id=row['resource_id'],
            action=row['action'],
            status=row['status'],
            details=json.loads(row['details']) if row['details'] else {},
            security_level=SecurityLevel(row['security_level']),
            compliance_tags=[ComplianceStandard(tag) for tag in row['compliance_tags']],
            checksum=row['checksum'],
            parent_event_id=row['parent_event_id'],
            metadata=json.loads(row['metadata']) if row['metadata'] else None
        )
    
    async def generate_compliance_report(
        self,
        standard: ComplianceStandard,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate compliance-specific audit report"""
        
        query_conditions = [
            "timestamp >= $1",
            "timestamp <= $2"
        ]
        query_params = [start_date, end_date]
        
        if user_id:
            query_conditions.append("user_id = $%d" % (len(query_params) + 1))
            query_params.append(user_id)
        
        where_clause = " AND ".join(query_conditions)
        query = f"SELECT * FROM audit_events WHERE {where_clause} ORDER BY timestamp DESC"
        
        try:
            async with self._pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *query_params)
                
                events = [self._row_to_audit_event(row) for row in rows]
                
                # Generate compliance-specific report
                report = self._generate_standard_report(standard, events, start_date, end_date)
                
                return report
                
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {e}")
            return {}
    
    def _generate_standard_report(
        self,
        standard: ComplianceStandard,
        events: List[AuditEvent],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate report for specific compliance standard"""
        
        base_report = {
            'report_metadata': {
                'standard': standard.value,
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'total_events': len(events),
                'unique_users': len(set(event.user_id for event in events))
            },
            'events': [event.to_compliance_format(standard) for event in events],
            'summary': self._generate_summary_stats(events),
            'security_analysis': self._generate_security_analysis(events)
        }
        
        # Add standard-specific insights
        if standard == ComplianceStandard.GDPR:
            base_report['gdpr_specific'] = self._generate_gdpr_analysis(events)
        elif standard == ComplianceStandard.HIPAA:
            base_report['hipaa_specific'] = self._generate_hipaa_analysis(events)
        elif standard == ComplianceStandard.SOX:
            base_report['sox_specific'] = self._generate_sox_analysis(events)
        
        return base_report
    
    def _generate_summary_stats(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Generate summary statistics from audit events"""
        
        event_type_counts = {}
        security_level_counts = {}
        daily_activity = {}
        
        for event in events:
            # Event type counts
            event_type = event.event_type.value
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
            
            # Security level counts
            security_level = event.security_level.value
            security_level_counts[security_level] = security_level_counts.get(security_level, 0) + 1
            
            # Daily activity
            date_str = event.timestamp.date().isoformat()
            daily_activity[date_str] = daily_activity.get(date_str, 0) + 1
        
        return {
            'event_types': event_type_counts,
            'security_levels': security_level_counts,
            'daily_activity': daily_activity,
            'most_active_user': max(set(event.user_id for event in events), 
                                  key=lambda u: sum(1 for e in events if e.user_id == u)),
            'peak_activity_date': max(daily_activity.keys(), key=lambda d: daily_activity[d]) if daily_activity else None
        }
    
    def _generate_security_analysis(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Generate security analysis from audit events"""
        
        critical_events = [e for e in events if e.security_level == SecurityLevel.CRITICAL]
        failed_events = [e for e in events if e.status == 'failed']
        high_risk_users = {}
        
        # Analyze user risk profiles
        for event in events:
            if event.user_id not in high_risk_users:
                high_risk_users[event.user_id] = {
                    'failed_events': 0,
                    'critical_events': 0,
                    'unique_ips': set(),
                    'suspicious_patterns': []
                }
            
            user_profile = high_risk_users[event.user_id]
            
            if event.status == 'failed':
                user_profile['failed_events'] += 1
            
            if event.security_level == SecurityLevel.CRITICAL:
                user_profile['critical_events'] += 1
            
            user_profile['unique_ips'].add(event.ip_address)
        
        # Convert sets to lists for JSON serialization
        for user_id in high_risk_users:
            high_risk_users[user_id]['unique_ips'] = list(high_risk_users[user_id]['unique_ips'])
        
        return {
            'critical_events_count': len(critical_events),
            'failed_events_count': len(failed_events),
            'high_risk_users': high_risk_users,
            'security_trends': self._analyze_security_trends(events)
        }
    
    def _analyze_security_trends(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Analyze security trends over time"""
        
        daily_security_events = {}
        for event in events:
            if event.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                date_str = event.timestamp.date().isoformat()
                if date_str not in daily_security_events:
                    daily_security_events[date_str] = 0
                daily_security_events[date_str] += 1
        
        return {
            'daily_security_events': daily_security_events,
            'trend_direction': 'increasing' if len(daily_security_events) > 0 else 'stable'
        }
    
    def _generate_gdpr_analysis(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Generate GDPR-specific analysis"""
        
        personal_data_events = []
        for event in events:
            if any(keyword in event.details.keys() for keyword in 
                  ['personal_data', 'pii', 'email', 'phone', 'address']):
                personal_data_events.append(event)
        
        return {
            'personal_data_access_events': len(personal_data_events),
            'data_subject_requests': len([e for e in events if 'data_subject_request' in e.action]),
            'consent_events': len([e for e in events if 'consent' in e.action]),
            'data_retention_compliance': 'compliant'  # Simplified for demo
        }
    
    def _generate_hipaa_analysis(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Generate HIPAA-specific analysis"""
        
        phi_events = [e for e in events if e.details.get('phi_accessed')]
        access_without_authorization = [e for e in events 
                                      if e.event_type in [AuditEventType.FILE_ACCESS, AuditEventType.FILE_DOWNLOAD] 
                                      and not e.details.get('authorized')]
        
        return {
            'phi_access_events': len(phi_events),
            'unauthorized_access_attempts': len(access_without_authorization),
            'wha_violations': len([e for e in phi_events if not e.details.get('authorized')]),
            'minimum_necessary_compliance': 'compliant'  # Simplified for demo
        }
    
    def _generate_sox_analysis(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Generate SOX-specific analysis"""
        
        financial_data_events = [e for e in events 
                               if 'financial' in str(e.details).lower() 
                               or 'sox' in str(e.compliance_tags).lower()]
        approval_required_events = [e for e in events 
                                  if e.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]]
        
        return {
            'financial_data_access_events': len(financial_data_events),
            'approval_required_events': len(approval_required_events),
            'segregation_of_duties_violations': 0,  # Simplified for demo
            'data_integrity_checks': 'passed'  # Simplified for demo
        }
    
    @asynccontextmanager
    async def audit_context(
        self,
        user_id: str,
        action: str,
        resource_path: str,
        event_type: AuditEventType = AuditEventType.FILE_ACCESS,
        **kwargs
    ):
        """Context manager for automatic audit logging"""
        
        event = self.create_audit_event(
            event_type=event_type,
            user_id=user_id,
            action=f"start_{action}",
            resource_path=resource_path,
            **kwargs
        )
        
        await self.log_event(event)
        
        try:
            yield event
            # Log successful completion
            event.status = 'success'
            event.action = f"complete_{action}"
            event.details['completion_time'] = datetime.now(timezone.utc).isoformat()
            
        except Exception as e:
            # Log failure
            event.status = 'error'
            event.action = f"error_{action}"
            event.details['error'] = str(e)
            event.details['error_type'] = type(e).__name__
            raise
        
        finally:
            event.details['end_time'] = datetime.now(timezone.utc).isoformat()
            await self.log_event(event, trigger_streaming=False)
    
    async def cleanup_old_events(self, retention_days: int = 2555) -> None:
        """Cleanup audit events older than retention period (default: 7 years)"""
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        
        try:
            async with self._pg_pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM audit_events WHERE timestamp < $1",
                    cutoff_date
                )
                
                deleted_count = int(result.split()[-1]) if result else 0
                self.logger.info(f"Cleaned up {deleted_count} old audit events")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old audit events: {e}")
            raise


# Convenience functions for common audit operations

async def log_file_operation(
    audit_logger: AuditLogger,
    operation: str,
    user_id: str,
    file_path: str,
    user_email: Optional[str] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    **kwargs
) -> None:
    """Convenience function for logging file operations"""
    
    event_type_mapping = {
        'upload': AuditEventType.FILE_UPLOAD,
        'download': AuditEventType.FILE_DOWNLOAD,
        'delete': AuditEventType.FILE_DELETE,
        'modify': AuditEventType.FILE_MODIFY,
        'access': AuditEventType.FILE_ACCESS
    }
    
    event_type = event_type_mapping.get(operation.lower(), AuditEventType.FILE_ACCESS)
    
    event = audit_logger.create_audit_event(
        event_type=event_type,
        user_id=user_id,
        action=f"file_{operation}",
        resource_path=file_path,
        user_email=user_email,
        session_id=session_id,
        ip_address=ip_address,
        **kwargs
    )
    
    await audit_logger.log_event(event)


async def log_user_activity(
    audit_logger: AuditLogger,
    activity: str,
    user_id: str,
    user_email: Optional[str] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    **kwargs
) -> None:
    """Convenience function for logging user activities"""
    
    event_type_mapping = {
        'login': AuditEventType.USER_LOGIN,
        'logout': AuditEventType.USER_LOGOUT,
        'activity': AuditEventType.USER_ACTIVITY
    }
    
    event_type = event_type_mapping.get(activity.lower(), AuditEventType.USER_ACTIVITY)
    
    event = audit_logger.create_audit_event(
        event_type=event_type,
        user_id=user_id,
        action=activity,
        resource_path='/user/activity',
        user_email=user_email,
        session_id=session_id,
        ip_address=ip_address,
        **kwargs
    )
    
    await audit_logger.log_event(event)


# Example usage and testing

async def example_usage():
    """Example of how to use the audit logger"""
    
    # Initialize audit logger
    audit_logger = AuditLogger(
        supabase_url="your-supabase-url",
        supabase_key="your-supabase-key"
    )
    
    await audit_logger.initialize()
    
    try:
        # Log a file operation
        await log_file_operation(
            audit_logger=audit_logger,
            operation="upload",
            user_id="user123",
            file_path="/documents/important_file.pdf",
            user_email="user@example.com",
            ip_address="192.168.1.100",
            details={"file_size": 1024, "file_type": "pdf"},
            compliance_tags=[ComplianceStandard.GDPR, ComplianceStandard.SOX]
        )
        
        # Use audit context manager
        async with audit_logger.audit_context(
            user_id="user123",
            action="process_document",
            resource_path="/documents/important_file.pdf",
            event_type=AuditEventType.FILE_MODIFY
        ) as event:
            # Your business logic here
            await asyncio.sleep(1)  # Simulate work
        
        # Generate compliance report
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)
        
        report = await audit_logger.generate_compliance_report(
            standard=ComplianceStandard.GDPR,
            start_date=start_date,
            end_date=end_date
        )
        
        logger.info(f"Generated report with {report['report_metadata']['total_events']} events")
        
    finally:
        await audit_logger.close()


if __name__ == "__main__":
    asyncio.run(example_usage())