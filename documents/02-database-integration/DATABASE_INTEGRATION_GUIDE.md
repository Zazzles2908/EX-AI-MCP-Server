# Database Integration Guide

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** 🟡 **In Progress**

## 🎯 Overview

This section contains database integration documentation for the EX-AI MCP Server, including Supabase schema design, repository patterns, performance optimization, and data access patterns.

## 📚 Documentation Structure

### 📊 Schema to Code Mapping
**Location:** `schema-to-code-mapping/`

Complete database schema to application code mapping:
- **18 Tables Overview** - Complete schema documentation
- **Code Generation** - How tables map to Python models
- **Type Safety** - Type hints and validation
- **Migration Scripts** - Database versioning and updates
- **Relationships** - Foreign keys and joins
- **Index Strategy** - 78 indexes explained

**Essential for** developers working with database operations.

### 🔄 Repository Layer Guide
**Location:** `repository-layer-guide/`

Data access patterns and repository implementation:
- **Repository Pattern** - Abstraction over database
- **CRUD Operations** - Create, Read, Update, Delete
- **Query Optimization** - Best practices
- **Transaction Management** - ACID compliance
- **Error Handling** - Database-specific errors
- **Caching Strategy** - Redis integration
- **Test Data** - Fixtures and factories

**Essential for** developers implementing data access.

### ⚡ Performance Optimization
**Location:** `performance-optimization/`

Database performance tuning and optimization:
- **Index Usage** - How to use 78 indexes effectively
- **Query Performance** - Sub-100ms target
- **Connection Pooling** - Supabase connection management
- **Slow Query Analysis** - Identification and fixes
- **Database Monitoring** - Metrics and alerting
- **Scaling Strategies** - Read replicas, sharding
- **Backup & Recovery** - Point-in-time recovery

**Essential for** performance-critical operations.

## 🗄️ Database Architecture

### Supabase Configuration
- **Database**: PostgreSQL 15+
- **Version**: 15.x (latest stable)
- **Location**: Cloud-hosted (Supabase)
- **Connection**: Direct TCP with connection pooling

### Schema Statistics
```
Total Tables: 18
Total Indexes: 78
Total RLS Policies: 20
Total Functions: 15+
Estimated Size: ~2GB (with indexes)
```

### Key Tables
1. **messages** - Chat messages and conversations
2. **files** - File metadata and storage
3. **sessions** - User sessions and state
4. **audit_logs** - Security and compliance
5. **provider_uploads** - File tracking per provider
6. **truncation_events** - Message truncation history
7. **validation_metrics** - System health metrics
8. **monitoring_events** - Observability data

## 📊 Performance Targets

### Query Performance
- **Simple Queries**: <50ms (95th percentile)
- **Complex Queries**: <100ms (95th percentile)
- **Full-text Search**: <200ms (95th percentile)
- **Aggregations**: <500ms (95th percentile)

### Throughput
- **Read Operations**: 1000+ QPS
- **Write Operations**: 500+ QPS
- **Concurrent Connections**: 100 (pooled)
- **Connection Pool**: 10-100 connections

## 📚 Related Documentation

- **System Architecture**: [../01-architecture-overview/01_system_architecture.md](../01-architecture-overview/01_system_architecture.md)
- **Security & Authentication**: [../03-security-authentication/](../03-security-authentication/)

## 🔗 Quick Links

- **Schema Mapping**: [schema-to-code-mapping/](schema-to-code-mapping/)
- **Repository Guide**: [repository-layer-guide/](repository-layer-guide/)
- **Performance**: [performance-optimization/](performance-optimization/)
- **Main Documentation**: [../index.md](../index.md)

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server Database Team
**Status:** 🟡 **In Progress - Database documentation being created**
