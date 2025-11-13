# Operations & Management Guide

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** 🟡 **In Progress**

## 🎯 Overview

This section contains operational documentation for deploying, monitoring, and managing the EX-AI MCP Server in production environments.

## 📚 Documentation Structure

### 🚀 Deployment Guide
**Location:** `01_deployment_guide.md`

Production deployment procedures:

**Environment Setup**
- Hardware requirements (2 CPU, 4GB RAM minimum)
- Operating system recommendations (Linux preferred)
- Network configuration (ports 3000, 3001, 3002)

**Installation Procedures**
- Docker deployment (recommended)
- Manual installation
- Kubernetes deployment
- Cloud deployment (AWS, Azure, GCP)

**Configuration**
- Environment variables setup
- Configuration files
- SSL/TLS setup
- Load balancing configuration

**Post-Deployment**
- Verification checks
- Health monitoring
- Performance testing
- Security validation

**Essential for** DevOps and infrastructure teams.

### 📊 Monitoring & Health Checks
**Location:** `02_monitoring_health_checks.md`

System monitoring and observability:

**Health Monitoring**
- WebSocket daemon health (port 3001)
- Database connectivity
- Provider availability (GLM/Kimi)
- API response times

**Metrics Collection**
- Request metrics (rate, latency, errors)
- Provider performance
- Database queries
- Resource utilization

**Alerting**
- Threshold configuration
- Alert channels (email, Slack, PagerDuty)
- Escalation procedures
- Incident response

**Dashboards**
- Grafana integration
- Custom dashboards
- Real-time monitoring
- Historical data

**Required for** production operations.

### 🛠️ Troubleshooting Guide
**Location:** `03_troubleshooting_guide.md`

Common issues and solutions:

**Connection Issues**
- WebSocket connection failures
- Database connection timeouts
- Provider connection errors

**Authentication Errors**
- JWT token issues
- API key problems
- Permission denied errors

**Provider Issues**
- GLM timeout errors
- Kimi file upload failures
- Rate limiting

**Database Errors**
- Query timeouts
- RLS policy violations
- Connection pool exhaustion

**Performance Issues**
- Slow responses
- High CPU/memory usage
- Database bottlenecks

**Recovery Procedures**
- Service restart
- Key rotation
- Database recovery
- Failover procedures

**Go-to guide** for debugging and incident response.

## 🏥 System Health

### Health Check Endpoint
```bash
# Check daemon health
curl http://localhost:3001/health

# Expected response
{
  "status": "healthy",
  "uptime": 3600,
  "version": "2.3.0",
  "tools": 29,
  "sessions": 5,
  "requests_per_minute": 45
}
```

### Health Metrics
- **Uptime**: Server availability (target: 99.9%+)
- **Active Sessions**: Current WebSocket connections
- **Requests/Minute**: Throughput
- **Error Rate**: Failures percentage (target: <1%)
- **Provider Health**: GLM/Kimi status
- **Database Latency**: Query performance (target: <100ms)

### Log Locations
- **WebSocket Daemon**: `logs/ws_daemon.log`
- **Health File**: `logs/ws_daemon.health.json`
- **Metrics**: `.logs/` directory (JSONL)
- **Errors**: `logs/error.log`
- **Audit**: Supabase `audit_logs` table

## 🚨 Alerting

### Alert Rules
- **High Error Rate**: >10% errors in 5 minutes
- **Provider Down**: Provider health = 0
- **High Latency**: >2s response time
- **Database Disconnect**: Connection failure

### Notification Channels
- **Email**: ops@company.com
- **Slack**: #alerts channel
- **PagerDuty**: On-call rotation
- **Webhooks**: Custom integrations

## 🔧 Maintenance

### Regular Tasks
- **Daily**: Check health metrics, review error logs
- **Weekly**: Performance review, security updates
- **Monthly**: API key rotation, SSL certificate check
- **Quarterly**: Security audit, infrastructure review

### Maintenance Windows
- **Scheduled**: Every Sunday 2:00 AM - 4:00 AM (UTC)
- **Emergency**: 24/7 with on-call rotation
- **Duration**: Typically 1-2 hours

## 🔄 Deployment

### Docker Deployment
```bash
# Pull latest
docker-compose pull

# Deploy
docker-compose up -d

# Verify
curl http://localhost:3001/health
```

### Rolling Update
```bash
# Update one container at a time
docker-compose up -d --no-deps exai-mcp-daemon

# Check health
sleep 10
curl http://localhost:3001/health
```

## 📈 Performance Tuning

### Database Optimization
- **Index Usage**: Review slow queries
- **Connection Pooling**: Adjust pool size (default: 10-100)
- **Query Optimization**: Use indexes
- **Vacuum**: Regular maintenance

### Application Tuning
- **Timeout Configuration**:
  - WebSocket: 30s
  - GLM: 60s
  - Kimi: 120s
  - Database: 30s

- **Rate Limiting**:
  - Per token: 100 requests
  - Global: 1000 requests/minute

## 📚 Related Documentation

- **System Architecture**: [../01-architecture-overview/01_system_architecture.md](../01-architecture-overview/01_system_architecture.md)
- **Database Integration**: [../02-database-integration/DATABASE_INTEGRATION_GUIDE.md](../02-database-integration/DATABASE_INTEGRATION_GUIDE.md)
- **Security & Authentication**: [../03-security-authentication/](../03-security-authentication/)

## 🔗 Quick Links

- **Deployment Guide**: [01_deployment_guide.md](01_deployment_guide.md)
- **Monitoring & Health**: [02_monitoring_health_checks.md](02_monitoring_health_checks.md)
- **Troubleshooting**: [03_troubleshooting_guide.md](03_troubleshooting_guide.md)
- **Main Documentation**: [../index.md](../index.md)

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server Operations Team
**Status:** 🟡 **In Progress - Operations documentation being created**
