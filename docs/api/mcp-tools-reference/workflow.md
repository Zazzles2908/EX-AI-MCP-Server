# MCP Workflow Tools Reference

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** ✅ **Complete**

## 🎯 Overview

This section documents the 5 Workflow Tools available in the EX-AI MCP Server. These tools provide advanced automation, orchestration, and multi-step processing capabilities for complex AI-powered workflows.

---

## 📚 Tool Categories

### 🔄 Workflow Tools (5 Total)
- **expert_analysis** - Domain-specific expert analysis
- **conversation_integration** - Merge multiple conversations
- **workflow_orchestration** - Multi-step automation
- **batch_processing** - Process multiple items efficiently
- **task_queue** - Queue and execute tasks

---

## 🔬 Tool Details

### 1. expert_analysis

**Description:** Specialized domain analysis with expert-level AI

**Parameters:**
- `domain` (string, required) - Domain: 'security', 'architecture', 'performance', 'code_quality', 'devops'
- `input` (string/array, required) - Input data or file paths
- `expertise_level` (string, optional) - Level: 'basic', 'intermediate', 'expert', 'senior'
- `framework` (string, optional) - Framework: 'nist', 'owasp', 'iso27001', 'custom'
- `output_format` (string, optional) - Format: 'report', 'checklist', 'recommendations'

**Example Usage:**
```python
# Security audit
result = exai_mcp.expert_analysis(
    domain="security",
    input="/path/to/codebase",
    framework="owasp",
    expertise_level="expert"
)

# Architecture review
result = exai_mcp.expert_analysis(
    domain="architecture",
    input=["/docs/requirements.md", "/docs/design.md"],
    framework="c4_model",
    output_format="report"
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "domain": "security",
    "expertise_level": "expert",
    "framework": "owasp",
    "findings": [
      {
        "id": "SEC-001",
        "severity": "critical",
        "category": "injection",
        "title": "SQL Injection Vulnerability",
        "description": "User input is directly concatenated into SQL queries",
        "location": "auth.py:42",
        "impact": "Database compromise, data theft",
        "recommendation": "Use parameterized queries",
        "cwe": "CWE-89"
      }
    ],
    "summary": {
      "total_issues": 12,
      "critical": 3,
      "high": 5,
      "medium": 3,
      "low": 1
    },
    "recommendations": [
      "Implement parameterized queries",
      "Add input validation",
      "Enable SQL injection testing"
    ],
    "score": 72,
    "compliance": {
      "owasp_top10": "75%",
      "nist_framework": "68%"
    }
  }
}
```

**Supported Domains:**
- **Security**: OWASP Top 10, CWE, CVE analysis
- **Architecture**: C4 Model, microservices, scalability
- **Performance**: Bottlenecks, optimization, scaling
- **Code Quality**: Best practices, maintainability, patterns
- **DevOps**: CI/CD, monitoring, deployment

---

### 2. conversation_integration

**Description:** Merge and correlate multiple conversation sessions

**Parameters:**
- `session_ids` (array, required) - List of session IDs to merge
- `integration_type` (string, optional) - Type: 'timeline', 'topic', 'project', 'participant'
- `deduplication` (boolean, optional) - Remove duplicate messages (default: true)
- `timeline_sort` (boolean, optional) - Sort by timestamp (default: true)
- `output_format` (string, optional) - Format: 'merged', 'unified', 'cross_referenced'

**Example Usage:**
```python
# Merge by timeline
merged = exai_mcp.conversation_integration(
    session_ids=["sess_001", "sess_002", "sess_003"],
    integration_type="timeline",
    deduplication=True
)

# Merge by topic
topic_merged = exai_mcp.conversation_integration(
    session_ids=["sess_001", "sess_002"],
    integration_type="topic",
    output_format="cross_referenced"
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "merged_session_id": "merged_sess_abc",
    "source_sessions": ["sess_001", "sess_002", "sess_003"],
    "total_messages": 156,
    "deduplicated_count": 23,
    "integration_type": "timeline",
    "timeline": [
      {
        "timestamp": "2025-11-10T10:00:00Z",
        "session_id": "sess_001",
        "message_id": "msg_123",
        "content": "Started security audit",
        "topic": "security"
      }
    ],
    "topics": [
      {
        "name": "security",
        "message_count": 45,
        "participants": ["alice", "bob"],
        "first_mention": "2025-11-10T10:00:00Z",
        "last_mention": "2025-11-10T12:30:00Z"
      }
    ],
    "cross_references": [
      {
        "message_id": "msg_123",
        "referenced_by": ["msg_456", "msg_789"],
        "type": "quote"
      }
    ]
  }
}
```

---

### 3. workflow_orchestration

**Description:** Execute multi-step automated workflows

**Parameters:**
- `workflow_definition` (object, required) - Workflow configuration
- `inputs` (object, required) - Input parameters
- `parallel_steps` (array, optional) - Steps that can run in parallel
- `callback_url` (string, optional) - Webhook for completion notification

**Example Usage:**
```python
# Define workflow
workflow = {
    "name": "security_audit",
    "steps": [
        {
            "id": "scan",
            "type": "analyze",
            "tool": "expert_analysis",
            "params": {
                "domain": "security",
                "input": "${input.codebase}"
            }
        },
        {
            "id": "report",
            "type": "process",
            "tool": "process_file",
            "depends_on": ["scan"],
            "params": {
                "file_id": "${scan.file_id}",
                "analysis_type": "summary"
            }
        },
        {
            "id": "notify",
            "type": "action",
            "tool": "send_notification",
            "depends_on": ["report"],
            "params": {
                "message": "Security audit complete: ${report.summary}"
            }
        }
    ]
}

# Execute workflow
result = exai_mcp.workflow_orchestration(
    workflow_definition=workflow,
    inputs={
        "codebase": "/path/to/code"
    }
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "workflow_id": "wf_abc123",
    "status": "running",
    "current_step": "report",
    "steps": [
      {
        "id": "scan",
        "status": "completed",
        "start_time": "2025-11-10T10:00:00Z",
        "end_time": "2025-11-10T10:05:00Z",
        "duration": 300,
        "result": {
          "file_id": "file_scan_001"
        }
      },
      {
        "id": "report",
        "status": "running",
        "start_time": "2025-11-10T10:05:00Z",
        "result": null
      }
    ],
    "estimated_completion": "2025-11-10T10:10:00Z"
  }
}
```

**Workflow Features:**
- **Step dependencies**: Define execution order
- **Parallel execution**: Run independent steps concurrently
- **Error handling**: Retry failed steps
- **State persistence**: Resume interrupted workflows
- **Webhooks**: Async completion notifications

---

### 4. batch_processing

**Description:** Efficiently process multiple items in batches

**Parameters:**
- `items` (array, required) - List of items to process
- `processor` (string, required) - Tool to use for processing
- `batch_size` (int, optional) - Items per batch (default: 10)
- `max_parallel` (int, optional) - Max parallel batches (default: 3)
- `on_error` (string, optional) - Error handling: 'skip', 'retry', 'fail'
- `progress_callback` (function, optional) - Progress update callback

**Example Usage:**
```python
# Process multiple files
results = exai_mcp.batch_processing(
    items=[
        "/path/to/file1.py",
        "/path/to/file2.py",
        "/path/to/file3.py"
    ],
    processor="process_file",
    batch_size=5,
    max_parallel=2
)

# With progress callback
def progress_handler(progress):
    print(f"Progress: {progress.completed}/{progress.total}")

results = exai_mcp.batch_processing(
    items=list_of_files,
    processor="expert_analysis",
    progress_callback=progress_handler
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "total_items": 50,
    "processed": 48,
    "failed": 2,
    "batches": 10,
    "total_duration": 45.6,
    "results": [
      {
        "item": "/path/to/file1.py",
        "status": "success",
        "result": {
          "file_id": "file_abc",
          "analysis": "complete"
        },
        "duration": 2.3
      }
    ],
    "errors": [
      {
        "item": "/path/to/file20.py",
        "error": "File not found",
        "code": "404"
      }
    ],
    "statistics": {
      "avg_duration": 0.95,
      "max_duration": 3.2,
      "min_duration": 0.3,
      "success_rate": "96%"
    }
  }
}
```

---

### 5. task_queue

**Description:** Queue tasks for asynchronous execution

**Parameters:**
- `task` (object, required) - Task definition
- `priority` (string, optional) - Priority: 'low', 'normal', 'high', 'urgent'
- `schedule` (object, optional) - Schedule configuration
- `callbacks` (object, optional) - Completion callbacks

**Example Usage:**
```python
# Queue simple task
task_id = exai_mcp.task_queue.queue_task(
    task={
        "type": "analysis",
        "tool": "expert_analysis",
        "params": {
            "domain": "security",
            "input": "/path/to/code"
        }
    },
    priority="high"
)

# Queue scheduled task
task_id = exai_mcp.task_queue.queue_task(
    task={
        "type": "maintenance",
        "tool": "cleanup_files",
        "params": {
            "older_than_days": 30
        }
    },
    schedule={
        "run_at": "2025-11-10T02:00:00Z",
        "timezone": "UTC"
    }
)

# Get task status
status = exai_mcp.task_queue.get_task_status(task_id)

# Cancel task
exai_mcp.task_queue.cancel_task(task_id)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123",
    "status": "queued",
    "priority": "high",
    "created_at": "2025-11-10T10:00:00Z",
    "estimated_start": "2025-11-10T10:01:00Z",
    "queue_position": 5,
    "task": {
      "type": "analysis",
      "tool": "expert_analysis"
    }
  }
}

{
  "success": true,
  "data": {
    "task_id": "task_abc123",
    "status": "running",
    "started_at": "2025-11-10T10:01:00Z",
    "progress": {
      "current_step": "scanning",
      "completed_steps": 2,
      "total_steps": 5,
      "percentage": 40
    }
  }
}

{
  "success": true,
  "data": {
    "task_id": "task_abc123",
    "status": "completed",
    "started_at": "2025-11-10T10:01:00Z",
    "completed_at": "2025-11-10T10:05:30Z",
    "duration": 270,
    "result": {
      "file_id": "file_result_001"
    }
  }
}
```

**Task Statuses:**
- **queued**: Waiting in queue
- **running**: Currently executing
- **completed**: Successfully finished
- **failed**: Execution failed
- **cancelled**: Manually cancelled
- **timeout**: Exceeded time limit

---

## 🔄 Workflow Examples

### Example 1: Complete Security Audit Workflow
```python
# 1. Queue comprehensive security audit
task_id = exai_mcp.task_queue.queue_task(
    task={
        "type": "security_audit",
        "steps": [
            {
                "tool": "expert_analysis",
                "params": {
                    "domain": "security",
                    "framework": "owasp"
                }
            },
            {
                "tool": "batch_processing",
                "params": {
                    "processor": "process_file",
                    "items": "${files}"
                }
            },
            {
                "tool": "workflow_orchestration",
                "params": {
                    "workflow_definition": "generate_report"
                }
            }
        ]
    },
    priority="urgent"
)

# 2. Monitor progress
while True:
    status = exai_mcp.task_queue.get_task_status(task_id)
    if status.data.status in ["completed", "failed"]:
        break
    print(f"Progress: {status.data.progress.percentage}%")
    time.sleep(5)

# 3. Get results
result = exai_mcp.task_queue.get_task_result(task_id)
```

### Example 2: Multi-Conversation Analysis
```python
# 1. Identify related sessions
sessions = exai_mcp.list_sessions(
    filter={
        "project": "security_audit"
    }
)

# 2. Merge conversations
merged = exai_mcp.conversation_integration(
    session_ids=[s.id for s in sessions],
    integration_type="project",
    deduplication=True
)

# 3. Analyze merged conversation
analysis = exai_mcp.expert_analysis(
    domain="code_quality",
    input=merged.data.merged_session_id
)

# 4. Generate consolidated report
report = exai_mcp.process_file(
    file_id=analysis.data.report_file_id,
    analysis_type="summary"
)
```

---

## ⚙️ Advanced Configuration

### Custom Workflows
```python
custom_workflow = {
    "name": "CI/CD Pipeline",
    "version": "1.0",
    "steps": [
        {
            "id": "lint",
            "tool": "expert_analysis",
            "params": {"domain": "code_quality"},
            "retry": {"max_attempts": 3}
        },
        {
            "id": "test",
            "tool": "batch_processing",
            "params": {"processor": "run_tests"},
            "parallel": True
        },
        {
            "id": "security_scan",
            "tool": "expert_analysis",
            "params": {"domain": "security"},
            "depends_on": ["lint"]
        }
    ],
    "error_handling": {
        "on_failure": "stop",
        "rollback_steps": ["deploy"]
    }
}
```

---

## 📊 Performance Metrics

### Execution Times (95th percentile)
- **expert_analysis**: 5-15 seconds
- **conversation_integration**: 2-8 seconds
- **workflow_orchestration**: 10-60 seconds
- **batch_processing**: Varies by item count
- **task_queue**: <1 second (queuing)

### Throughput
- **Batch processing**: 1000 items/hour
- **Task queue**: 10000 tasks/hour
- **Workflow orchestration**: 100 workflows/hour
- **Max parallel workflows**: 10

---

## 🔍 Troubleshooting

### Common Issues

**Issue: "Workflow timeout"**
- Maximum workflow duration: 1 hour
- Solution: Break into smaller steps or increase timeout
- Use task_queue for long-running processes

**Issue: "Batch processing stuck"**
- Check max_parallel setting
- Verify provider rate limits
- Monitor queue size

**Issue: "Task queue full"**
- Maximum queue size: 1000 tasks
- Clear completed tasks
- Increase processing capacity

### Error Codes
- `400`: Invalid workflow definition
- `409`: Resource conflict
- `422`: Validation failed
- `429`: Rate limit exceeded
- `503`: Service unavailable

---

## 📚 Related Documentation

- **Chat Tools**: [01_chat_tools.md](01_chat_tools.md)
- **File Management**: [02_file_management.md](02_file_management.md)
- **Provider APIs**: [../../provider-apis/](../../provider-apis/)
- **System Architecture**: [../../../../01-architecture-overview/01_system_architecture.md](../../../../01-architecture-overview/01_system_architecture.md)

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server API Team
**Status:** ✅ **Complete - Workflow Tools Reference**
