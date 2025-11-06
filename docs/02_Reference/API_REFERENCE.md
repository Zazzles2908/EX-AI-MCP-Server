# API Reference - EX-AI MCP Server v2.3

> **Comprehensive API Documentation**
> Generated: 2025-11-05
> Version: 1.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [Base URL & Authentication](#base-url--authentication)
3. [Health Check Endpoints](#health-check-endpoints)
4. [Monitoring Endpoints](#monitoring-endpoints)
5. [WebSocket APIs](#websocket-apis)
6. [Provider APIs](#provider-apis)
7. [File Management APIs](#file-management-apis)
8. [Error Handling](#error-handling)
9. [Rate Limits](#rate-limits)
10. [SDK Integration](#sdk-integration)

---

## Overview

The EX-AI MCP Server v2.3 provides a unified interface for AI model access with intelligent routing, multi-provider support, and real-time monitoring. The system uses a thin orchestrator pattern with modular architecture.

**Key Features:**
- Multi-provider support (OpenAI, GLM, Kimi, MiniMax, etc.)
- Intelligent request routing
- WebSocket real-time communication
- File upload/management
- Health monitoring and metrics
- Circuit breaker resilience patterns

---

## Base URL & Authentication

### Base URL
```
http://localhost:8080
```

### Authentication
Most endpoints use JWT-based authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

**Alternative**: For internal service-to-service communication:
- API Key in header: `X-API-Key: <key>`
- Service tokens in request body

---

## Health Check Endpoints

### GET /health

Standard health check endpoint for external monitoring systems (Prometheus, Datadog, Kubernetes).

**Endpoint:** `GET /health`

**Response:**
```json
{
    "status": "healthy",
    "timestamp_utc": "2025-11-05T10:30:00Z",
    "timestamp_melbourne": "2025-11-05T21:30:00+11:00",
    "version": "1.0.0",
    "components": {
        "database": {
            "status": "healthy",
            "response_time_ms": 12
        },
        "cache": {
            "status": "healthy",
            "response_time_ms": 3
        },
        "ai_providers": {
            "status": "healthy",
            "available_providers": ["openai", "glm", "kimi"]
        }
    },
    "uptime_seconds": 3600
}
```

**Status Codes:**
- `200 OK`: All systems healthy
- `503 Service Unavailable`: One or more systems degraded

**Query Parameters:**
- `detailed=true`: Include component-level health information (default: false)

---

## Monitoring Endpoints

### GET /metrics

Prometheus-formatted metrics endpoint.

**Endpoint:** `GET /metrics`

**Response:**
```
# HELP exai_requests_total Total number of requests
# TYPE exai_requests_total counter
exai_requests_total{provider="openai"} 1250
exai_requests_total{provider="glm"} 980

# HELP exai_request_duration_ms Request duration in milliseconds
# TYPE exai_request_duration_ms histogram
exai_request_duration_ms_bucket{provider="openai",le="100"} 500
exai_request_duration_ms_bucket{provider="openai",le="500"} 1200
exai_request_duration_ms_bucket{provider="openai",le="1000"} 1245
exai_request_duration_ms_bucket{provider="openai",le="+Inf"} 1250
exai_request_duration_ms_sum{provider="openai"} 125000
exai_request_duration_ms_count{provider="openai"} 1250
```

### WebSocket: /ws/monitoring

Real-time monitoring stream for dashboard visualization.

**WebSocket URL:** `ws://localhost:8080/ws/monitoring`

**Message Format:**
```json
{
    "event_type": "connection_status",
    "timestamp": "2025-11-05T10:30:00Z",
    "data": {
        "active_connections": 5,
        "total_requests": 2230,
        "error_rate": 0.02
    }
}
```

**Event Types:**
- `connection_status`: Active connections, queue depth
- `provider_metrics`: Per-provider request counts, latency
- `error_alert`: System errors and warnings
- `performance_update`: Throughput, response times

---

## WebSocket APIs

### WebSocket: /ws

Main WebSocket endpoint for AI model interactions.

**WebSocket URL:** `ws://localhost:8080/ws`

**Connection Flow:**
1. Establish WebSocket connection
2. Send authentication message
3. Send model request message
4. Receive streaming response
5. Send acknowledgment

**Authentication Message:**
```json
{
    "type": "auth",
    "token": "your_jwt_token"
}
```

**Model Request Message:**
```json
{
    "type": "request",
    "request_id": "req_12345",
    "provider": "openai",  // optional: auto-route if omitted
    "model": "gpt-4",
    "messages": [
        {
            "role": "user",
            "content": "Hello, world!"
        }
    ],
    "stream": true,
    "parameters": {
        "temperature": 0.7,
        "max_tokens": 1000
    }
}
```

**Response Message:**
```json
{
    "type": "response",
    "request_id": "req_12345",
    "content": {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I help you?"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 8,
            "total_tokens": 18
        }
    }
}
```

**Streaming Response:**
```json
{
    "type": "stream",
    "request_id": "req_12345",
    "delta": {
        "content": "Hello"
    }
}
```

---

## Provider APIs

### POST /api/chat/completions

Unified chat completions endpoint with intelligent provider routing.

**Endpoint:** `POST /api/chat/completions`

**Headers:**
```http
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body:**
```json
{
    "model": "auto",  // or specific model: "gpt-4", "glm-4", "kimi-chat"
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Explain quantum computing."
        }
    ],
    "stream": false,
    "parameters": {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 1000
    },
    "provider_hints": {
        "preferred": "openai",  // optional: hint for routing
        "capabilities": ["code", "reasoning"]
    }
}
```

**Response:**
```json
{
    "id": "chatcmpl_12345",
    "object": "chat.completion",
    "created": 1701234567,
    "model": "gpt-4",
    "provider": "openai",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Quantum computing is..."
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 45,
        "completion_tokens": 120,
        "total_tokens": 165
    },
    "metadata": {
        "routing": {
            "selected_provider": "openai",
            "confidence": 0.95
        },
        "performance": {
            "response_time_ms": 850,
            "total_time_ms": 920
        }
    }
}
```

### POST /api/embeddings

Generate embeddings for text.

**Endpoint:** `POST /api/embeddings`

**Request Body:**
```json
{
    "model": "text-embedding-ada-002",
    "input": [
        "The quick brown fox",
        "Jumps over the lazy dog"
    ],
    "encoding_format": "float"
}
```

**Response:**
```json
{
    "object": "list",
    "data": [
        {
            "object": "embedding",
            "embedding": [0.002, 0.003, ...],
            "index": 0
        },
        {
            "object": "embedding",
            "embedding": [0.001, 0.004, ...],
            "index": 1
        }
    ],
    "model": "text-embedding-ada-002",
    "usage": {
        "prompt_tokens": 10,
        "total_tokens": 10
    }
}
```

### POST /api/files/upload

Upload files for processing or RAG.

**Endpoint:** `POST /api/files/upload`

**Headers:**
```http
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: The file to upload (max 100MB)
- `purpose`: "agent" (default) or "fine-tune"
- `metadata`: Optional JSON metadata

**Response:**
```json
{
    "id": "file_12345",
    "object": "file",
    "created_at": 1701234567,
    "filename": "document.pdf",
    "purpose": "agent",
    "size": 1024000,
    "status": "uploaded",
    "metadata": {
        "mime_type": "application/pdf",
        "pages": 15
    }
}
```

---

## File Management APIs

### GET /api/files

List uploaded files.

**Endpoint:** `GET /api/files`

**Query Parameters:**
- `purpose`: Filter by purpose (agent, fine-tune, etc.)
- `limit`: Maximum number of files (default: 100, max: 1000)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
    "object": "list",
    "data": [
        {
            "id": "file_12345",
            "filename": "document.pdf",
            "size": 1024000,
            "created_at": 1701234567,
            "status": "uploaded"
        }
    ],
    "has_more": false
}
```

### DELETE /api/files/{file_id}

Delete a file.

**Endpoint:** `DELETE /api/files/{file_id}`

**Response:**
```json
{
    "deleted": true,
    "file_id": "file_12345"
}
```

---

## Error Handling

All endpoints return errors in a consistent format:

**Error Response:**
```json
{
    "error": {
        "code": "PROVIDER_ERROR",
        "message": "OpenAI API rate limit exceeded",
        "details": {
            "provider": "openai",
            "rate_limit_reset": 1701234667
        },
        "request_id": "req_12345"
    }
}
```

**Error Codes:**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Invalid or missing authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `PROVIDER_ERROR` | 502 | Upstream provider error |
| `TIMEOUT` | 504 | Request timeout |
| `INTERNAL_ERROR` | 500 | Internal server error |

---

## Rate Limits

**Default Limits:**
- General API: 1000 requests/hour per token
- File uploads: 100 uploads/hour per token
- Streaming: 500 concurrent streams per token

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1701234667
```

**Rate Limit Exceeded Response:**
```json
{
    "error": {
        "code": "RATE_LIMITED",
        "message": "Rate limit exceeded",
        "details": {
            "limit": 1000,
            "reset_time": 1701234667
        }
    }
}
```

---

## SDK Integration

### Python SDK

```python
from exai_mcp import EXAIClient

# Initialize client
client = EXAIClient(
    api_key="your_api_key",
    base_url="http://localhost:8080"
)

# Chat completion
response = client.chat.completions.create(
    model="auto",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

### JavaScript SDK

```javascript
import { EXAIClient } from '@exai/mcp-client';

// Initialize client
const client = new EXAIClient({
  apiKey: 'your_api_key',
  baseURL: 'http://localhost:8080'
});

// Chat completion
const response = await client.chat.completions.create({
  model: 'auto',
  messages: [
    { role: 'user', content: 'Hello!' }
  ]
});

console.log(response.choices[0].message.content);
```

---

## WebSocket Client Example

```python
import asyncio
import websockets
import json

async def chat_completion():
    uri = "ws://localhost:8080/ws"

    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            "type": "auth",
            "token": "your_jwt_token"
        }))

        # Send request
        await websocket.send(json.dumps({
            "type": "request",
            "request_id": "req_12345",
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": "Hello!"}
            ]
        }))

        # Receive response
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "response":
                print(data["content"])
                break

# Run
asyncio.run(chat_completion())
```

---

## Circuit Breaker & Resilience

The system implements circuit breaker patterns for all external providers:

**States:**
- `CLOSED`: Normal operation
- `OPEN`: Failing fast, no requests sent
- `HALF_OPEN`: Testing if service recovered

**Configuration:**
```json
{
    "circuit_breaker": {
        "failure_threshold": 5,
        "recovery_timeout": 30,
        "half_open_max_calls": 3
    }
}
```

**Monitoring:**
- Circuit state available via `/metrics` endpoint
- Events streamed via `/ws/monitoring`

---

## Versioning

API versioning is managed through the `Accept` header:

```http
Accept: application/vnd.exai.v1+json
```

**Supported Versions:**
- `v1`: Current version (default)
- Future versions will maintain backward compatibility

---

## Changelog

### v1.0.0 (2025-11-05)
- Initial API release
- Multi-provider support
- WebSocket streaming
- File management
- Health monitoring

---

**Last Updated:** 2025-11-05
**API Version:** 1.0.0
