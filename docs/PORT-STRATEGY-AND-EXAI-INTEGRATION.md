# 🔌 Port Strategy & EXAI Integration Plan
## Avoiding Conflicts, Hierarchical Architecture, and Clear Separation

---

## Current State Analysis

### Your System (C:\Project\Orchestator)
```bash
Running Services:
├─ Port 8000: Orchestrator API
├─ Port 8001: Cognee API
├─ Port 8002: Local LLM API
├─ Port 8003: Voice AI API
├─ Port 8004: Supabase Sync API
└─ Port 8091: Auth Proxy (MiniMax)
```

### EXAI MCP Server (Your System)
```bash
Potential Ports:
├─ Port 3000: EXAI MCP Server (standard)
├─ Port 3001: EXAI Tools
└─ Port 3002: EXAI Web UI
```

**PORT CONFLICT**: If EXAI uses standard MCP ports (3000-3999) and your web UI also wants 3000, there's a conflict!

---

## The Solution: Hierarchical Port Strategy

### Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    HIERARCHICAL DESIGN                          │
│                                                                 │
│  Level 1: EXAI MCP SERVER (External)                            │
│  ├─ Port 3000-3999: EXAI Services                              │
│  ├─ Role: Advanced AI agent orchestration                      │
│  └─ Purpose: Heavy-lifting, complex workflows                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Connects TO ↓
                              │
┌─────────────────────────────────────────────────────────────────┐
│  Level 2: YOUR ORCHESTRATION SYSTEM (Core)                      │
│                                                                 │
│  Backend APIs (8000-8999):                                      │
│  ├─ Port 8000: Orchestrator (API Gateway)                      │
│  ├─ Port 8001: Cognee (Knowledge Graph)                        │
│  ├─ Port 8002: Local LLM (Qwen2.5 7B)                          │
│  ├─ Port 8003: Voice AI (STT/TTS)                              │
│  ├─ Port 8004: Supabase Sync (Cloud Backup)                    │
│  └─ Port 8091: Auth Proxy (MiniMax API)                        │
│                                                                 │
│  Web UIs (9000-9999):                                           │
│  ├─ Port 9000: System Dashboard (Main UI)                      │
│  ├─ Port 9010: Cognee Web UI                                   │
│  ├─ Port 9020: LLM Chat Interface                              │
│  ├─ Port 9030: Voice AI Interface                              │
│  └─ Port 9040: Admin Panel                                     │
│                                                                 │
│  Role: Data, knowledge, compute provider                       │
│  Purpose: Core infrastructure & AI services                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Connects TO ↓
                              │
┌─────────────────────────────────────────────────────────────────┐
│  Level 3: SUPABASE PORTAL (Cloud)                              │
│                                                                 │
│  Cloud Services:                                                │
│  ├─ Database: Visual data management                           │
│  ├─ Auth: User authentication                                  │
│  ├─ Storage: File management                                   │
│  ├─ Edge Functions: Serverless functions                       │
│  └─ Real-time: Live data updates                               │
│                                                                 │
│  Role: Cloud data & user management                            │
│  Purpose: Backup, auth, user accounts                          │
│  URL: https://supabase.com/dashboard                           │
└─────────────────────────────────────────────────────────────────┘
```

### Why This Hierarchy Makes Sense

1. **EXAI** connects to **YOUR SYSTEM**
   - EXAI is the "brain" - analyzes, plans, orchestrates
   - Your system is the "body" - stores data, runs models, provides compute

2. **YOUR SYSTEM** connects to **SUPABASE**
   - Your system provides data
   - Supabase provides cloud storage and auth
   - Users access via Supabase portal

3. **Clear Separation of Concerns**
   - EXAI: "I need to search a knowledge graph"
   - Your System: "Here's the data from Cognee"
   - EXAI: "Generate a report using this data"
   - Your System: "Qwen2.5 is processing..."
   - Supabase: "Store the result with user account X"

---

## Port Allocation Table

### EXAI MCP Server
```bash
EXAI Ports (3000-3999):
├─ 3000: EXAI Main MCP Server
├─ 3001: EXAI Research Tools
├─ 3002: EXAI Code Analysis Tools
├─ 3003: EXAI Web Scraping Tools
├─ 3004: EXAI Data Processing Tools
└─ 3005-3999: EXAI Additional Services
```

### Your System (Fixed Ports)
```bash
Backend APIs (8000-8999) - NEVER CHANGE:
├─ 8000: Orchestrator (API Gateway)
├─ 8001: Cognee (Knowledge Graph)
├─ 8002: Local LLM (Qwen2.5 7B)
├─ 8003: Voice AI (STT/TTS)
├─ 8004: Supabase Sync (Cloud Backup)
└─ 8091: Auth Proxy (MiniMax API)

Web UIs (9000-9999) - YOUR CHOICE:
├─ 9000: System Dashboard (Main UI)
├─ 9010: Cognee Web UI
├─ 9020: LLM Chat Interface
├─ 9030: Voice AI Interface
├─ 9040: Admin Panel
└─ 9050-9999: Additional UIs
```

### Result
```
NO PORT CONFLICTS! ✅
- EXAI uses 3000-3999
- Your system uses 8000-8999 (APIs) and 9000-9999 (Web UIs)
- Completely separate ranges
```

---

## How EXAI Connects to Your System

### EXAI Configuration

```python
# EXAI connects to your endpoints
EXAI_CONFIG = {
    "cognee_endpoint": "http://your-system:8001",
    "local_llm_endpoint": "http://your-system:8002",
    "orchestrator_endpoint": "http://your-system:8000",
    "supabase_endpoint": "https://your-project.supabase.co",
    "dashboard_endpoint": "http://your-system:9000"
}
```

### Example Integration

**EXAI wants to research "AI in healthcare"**

```python
# EXAI workflow:
# 1. Query your Cognee knowledge graph
response = requests.post("http://your-system:8001/search", json={
    "query": "AI in healthcare"
})
cognee_results = response.json()

# 2. Use your Local LLM to generate insights
response = requests.post("http://your-system:8002/generate", json={
    "prompt": f"Based on this data: {cognee_results}, analyze AI in healthcare",
    "max_tokens": 1000
})
llm_analysis = response.json()

# 3. Store result in Supabase
response = requests.post("https://your-project.supabase.co/rest/v1/research", json={
    "topic": "AI in healthcare",
    "analysis": llm_analysis,
    "user_id": "user_123"
})
```

**Your system provides**: Data, compute, models
**EXAI provides**: Intelligence, analysis, orchestration

### EXAI Can Use Your Services

```python
# Available to EXAI:
1. Cognee Knowledge Graph (Port 8001)
   - Search documents
   - Explore entities
   - Query relationships

2. Local LLM - Qwen2.5 7B (Port 8002)
   - Generate text
   - Answer questions
   - Analyze data

3. Orchestrator (Port 8000)
   - Coordinate services
   - Route requests
   - Aggregate results

4. Supabase (Cloud)
   - Store data
   - User management
   - Cloud backup
```

---

## Documenting Your System for EXAI

### API Documentation File

**Create**: `docs/integration/EXAI-API-REFERENCE.md`

```markdown
# EXAI Integration API Reference

## Available Endpoints

### Cognee Knowledge Graph (Port 8001)

#### Search Knowledge Graph
```http
POST http://your-system:8001/search
Content-Type: application/json

{
  "query": "Your search question"
}
```

**Response**:
```json
{
  "results": [
    {
      "text": "Document chunk text...",
      "relevance_score": 0.95,
      "document_id": "doc_123"
    }
  ],
  "entity_count": 42,
  "relationship_count": 156
}
```

#### Add Document
```http
POST http://your-system:8001/add
Content-Type: application/json

{
  "text": "Your document text"
}
```

### Local LLM - Qwen2.5 7B (Port 8002)

#### Generate Text
```http
POST http://your-system:8002/generate
Content-Type: application/json

{
  "prompt": "Your prompt",
  "max_tokens": 500,
  "temperature": 0.7
}
```

**Response**:
```json
{
  "generated_text": "AI-generated response...",
  "tokens_used": 150,
  "time_taken": 2.3
}
```

### Orchestrator (Port 8000)

#### Query Any LLM
```http
POST http://your-system:8000/query
Content-Type: application/json

{
  "prompt": "Your question",
  "use_local": true  // true = Qwen2.5, false = MiniMax
}
```

### Supabase (Cloud)

#### Database
- URL: https://your-project.supabase.co
- API: Auto-generated REST/GraphQL
- Auth: JWT tokens

## Authentication

### For Cognee/Local LLM/Orchestrator
- No auth required (internal services)
- Use Docker network: `http://cognee:8000` (not localhost)

### For Supabase
- Auth: JWT token in header
- Format: `Authorization: Bearer <token>`
- Get token: https://supabase.com/dashboard

## Rate Limits
- Cognee: 100 requests/minute
- Local LLM: 10 requests/minute (GPU intensive)
- Supabase: Per plan limits

## Error Handling
```json
{
  "error": "error_type",
  "message": "Human readable message",
  "details": {}
}
```
```

---

## Checking for Port Conflicts

### Script: check_ports.py

```python
# Check if ports are in use
import socket

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0  # 0 = port is open, 1 = port is closed

# Check your ports
your_ports = [8000, 8001, 8002, 8003, 8004, 8091]
exai_ports = [3000, 3001, 3002, 3003, 3004]
web_ports = [9000, 9010, 9020, 9030, 9040]

print("Your System Ports:")
for port in your_ports:
    status = "OPEN" if check_port(port) else "CLOSED"
    print(f"  Port {port}: {status}")

print("\nEXAI Ports (potential):")
for port in exai_ports:
    status = "OPEN" if check_port(port) else "CLOSED"
    print(f"  Port {port}: {status}")

print("\nYour Web UI Ports (planned):")
for port in web_ports:
    status = "OPEN" if check_port(port) else "CLOSED"
    print(f"  Port {port}: {status}")
```

**Run it**:
```bash
python check_ports.py
```

**Output**:
```
Your System Ports:
  Port 8000: OPEN
  Port 8001: OPEN
  Port 8002: OPEN
  Port 8003: CLOSED
  Port 8004: CLOSED
  Port 8091: OPEN

EXAI Ports (potential):
  Port 3000: CLOSED  ← EXAI can use this!
  Port 3001: CLOSED  ← EXAI can use this!
  Port 3002: CLOSED  ← EXAI can use this!

Your Web UI Ports (planned):
  Port 9000: CLOSED  ← You can use this!
  Port 9010: CLOSED  ← You can use this!
  Port 9020: CLOSED  ← You can use this!
```

**Result**: NO CONFLICTS! ✅

---

## Docker Compose Configuration

### Updated docker-compose.yml

```yaml
version: '3.8'

services:
  # Backend APIs (8000-8999)
  orchestrator:
    ports: ["8000:8000"]
    # ... existing config

  cognee:
    ports: ["8001:8000"]
    # ... existing config

  local_llm:
    ports: ["8002:8000"]
    # ... existing config

  voice_ai:
    ports: ["8003:8000"]
    # ... existing config

  supabase_sync:
    ports: ["8004:8000"]
    # ... existing config

  auth_proxy:
    ports: ["8091:8091"]
    # ... existing config

  # NEW: System Dashboard (9000)
  system-dashboard:
    build: ./services/system-dashboard
    ports: ["9000:8000"]
    depends_on:
      - orchestrator
      - cognee
      - local_llm
    environment:
      - COGNEE_URL=http://cognee:8000
      - LLM_URL=http://local_llm:8000
      - ORCHESTRATOR_URL=http://orchestrator:8000
    # No GPU needed
    # ... other config

  # NEW: Cognee Web UI (9010)
  cognee-ui:
    build: ./services/cognee-ui
    ports: ["9010:8000"]
    depends_on:
      - cognee
    environment:
      - COGNEE_API_URL=http://cognee:8000
    # No GPU needed

  # NEW: LLM Chat UI (9020)
  llm-chat:
    build: ./services/llm-chat
    ports: ["9020:8000"]
    depends_on:
      - local_llm
    environment:
      - LLM_API_URL=http://local_llm:8000
    # No GPU needed

  # NEW: Voice AI UI (9030)
  voice-ui:
    build: ./services/voice-ui
    ports: ["9030:8000"]
    depends_on:
      - voice_ai
    environment:
      - VOICE_API_URL=http://voice_ai:8000
    # No GPU needed

  # NEW: Admin Panel (9040)
  admin-panel:
    build: ./services/admin
    ports: ["9040:8000"]
    environment:
      - ALL_SERVICES_URL=http://orchestrator:8000
    # No GPU needed
```

---

## Implementation Checklist

### Phase 1: Port Documentation
- [ ] Document all current ports (8000-8004, 8091)
- [ ] Reserve port ranges (EXAI: 3000-3999, Web: 9000-9999)
- [ ] Create port allocation table
- [ ] Update docker-compose.yml with clear comments

### Phase 2: Web UI Layer
- [ ] Create system-dashboard service (port 9000)
- [ ] Create cognee-ui service (port 9010)
- [ ] Create llm-chat service (port 9020)
- [ ] Create voice-ui service (port 9030)
- [ ] Create admin-panel service (port 9040)

### Phase 3: EXAI Integration
- [ ] Document API endpoints for EXAI
- [ ] Create EXAI configuration file
- [ ] Test EXAI connection to your services
- [ ] Implement EXAI workflow examples

### Phase 4: Supabase Integration
- [ ] Configure Supabase auth
- [ ] Set up cloud sync
- [ ] Create user management
- [ ] Build dashboard with Supabase portal

---

## Quick Commands

### Check Ports
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Linux/Mac
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000
```

### Test EXAI Connection
```bash
# Simulate EXAI calling your system
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test from EXAI"}'

curl -X POST http://localhost:8002/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test from EXAI", "max_tokens": 50}'
```

### Your System → Supabase
```bash
# Access Supabase portal
# https://supabase.com/dashboard

# API endpoint (from your dashboard)
# https://your-project.supabase.co/rest/v1/
```

---

## Summary

### The Architecture
```
EXAI (3000-3999)
    ↓ Uses
Your System (8000-8999 APIs, 9000-9999 UIs)
    ↓ Stores Data In
Supabase (Cloud)
```

### Port Allocation
```
EXAI: 3000-3999 (free to use)
Your APIs: 8000-8999 (fixed)
Your Web UIs: 9000-9999 (your choice)
```

### No Conflicts!
- EXAI and your system use completely different port ranges
- Each has its own space
- Clear separation of concerns

### Next Steps
1. **Document your API endpoints** for EXAI
2. **Build web UIs** on ports 9000-9999
3. **Test EXAI integration** with your services
4. **Use Supabase Portal** for user management

**The hierarchy is clear**: EXAI → Your System → Supabase

---

**Document Version**: 1.0
**Created**: 2025-11-08
**Status**: Ready for Implementation
**Priority**: HIGH - Prevents future port conflicts
