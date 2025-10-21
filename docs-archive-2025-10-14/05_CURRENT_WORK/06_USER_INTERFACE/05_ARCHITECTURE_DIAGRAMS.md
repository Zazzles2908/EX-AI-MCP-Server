# EXAI Web UI - Architecture Diagrams

**Date:** 2025-10-17  
**Purpose:** Visual representation of recommended architecture

---

## 📊 **CURRENT STATE (BROKEN)**

### **Current Architecture - Three Competing Approaches**

```mermaid
graph TB
    subgraph "Approach 1: Single-File HTML"
        HTML[web_ui/index.html<br/>407 lines]
        HTML --> |Expects| T1[exai_sessions table]
        HTML --> |Expects| T2[exai_messages table]
    end
    
    subgraph "Approach 2: Next.js + Prisma"
        NEXTJS[Next.js App<br/>web_ui/app/]
        PRISMA[Prisma ORM]
        NEXTJS --> PRISMA
        PRISMA --> |Expects| T3[User table]
        PRISMA --> |Expects| T4[Conversation table]
        PRISMA --> |Expects| T5[Message table]
    end
    
    subgraph "Approach 3: Supabase Schema"
        SCHEMA[supabase/schema.sql]
        SCHEMA --> |Defines| T6[conversations table]
        SCHEMA --> |Defines| T7[messages table]
    end
    
    subgraph "Supabase Cloud Database"
        DB[(PostgreSQL)]
        DB -.-> |NOT DEPLOYED| EMPTY[Empty Database<br/>No Tables!]
    end
    
    T1 -.-> |❌ DOESN'T EXIST| DB
    T2 -.-> |❌ DOESN'T EXIST| DB
    T3 -.-> |❌ DOESN'T EXIST| DB
    T4 -.-> |❌ DOESN'T EXIST| DB
    T5 -.-> |❌ DOESN'T EXIST| DB
    T6 -.-> |❌ NOT DEPLOYED| DB
    T7 -.-> |❌ NOT DEPLOYED| DB
    
    style HTML fill:#ff6b6b
    style NEXTJS fill:#ff6b6b
    style SCHEMA fill:#ffd93d
    style DB fill:#ff6b6b
    style EMPTY fill:#ff6b6b
```

**Problem:** Three different schemas, none deployed, database is empty!

---

## ✅ **RECOMMENDED ARCHITECTURE**

### **High-Level System Architecture**

```mermaid
graph TB
    subgraph "User's Browser"
        UI[Next.js Web UI<br/>React Components]
        SUPABASE_CLIENT[Supabase Client SDK<br/>@supabase/supabase-js]
        UI --> SUPABASE_CLIENT
    end
    
    subgraph "Supabase Cloud Platform"
        AUTH[Supabase Auth<br/>Authentication & Authorization]
        DB[(PostgreSQL Database<br/>with RLS)]
        STORAGE[Supabase Storage<br/>File Buckets]
        EDGE[Edge Functions<br/>Deno Runtime]
        REALTIME[Supabase Realtime<br/>WebSocket Subscriptions]
        
        SUPABASE_CLIENT --> |HTTPS| AUTH
        SUPABASE_CLIENT --> |HTTPS| DB
        SUPABASE_CLIENT --> |HTTPS| STORAGE
        SUPABASE_CLIENT --> |HTTPS| EDGE
        SUPABASE_CLIENT --> |WebSocket| REALTIME
    end
    
    subgraph "EXAI Backend (Docker)"
        DAEMON[EXAI Daemon<br/>Port 8079]
        TOOLS[EXAI Tools<br/>chat, debug, analyze, etc.]
        DAEMON --> TOOLS
    end
    
    EDGE --> |WebSocket| DAEMON
    DB --> |Notify| REALTIME
    
    style UI fill:#4ecdc4
    style SUPABASE_CLIENT fill:#95e1d3
    style AUTH fill:#f38181
    style DB fill:#aa96da
    style STORAGE fill:#fcbad3
    style EDGE fill:#ffffd2
    style REALTIME fill:#a8e6cf
    style DAEMON fill:#ffd3b6
    style TOOLS fill:#ffaaa5
```

---

### **Data Flow - Sending a Message**

```mermaid
sequenceDiagram
    participant User
    participant UI as Next.js UI
    participant Auth as Supabase Auth
    participant Edge as Edge Function
    participant DB as PostgreSQL
    participant Daemon as EXAI Daemon
    participant Realtime as Supabase Realtime
    
    User->>UI: Type message & click Send
    UI->>Auth: Verify user session
    Auth-->>UI: Session valid ✓
    
    UI->>Edge: POST /exai-chat<br/>{prompt, tool, model}
    Edge->>DB: INSERT INTO messages<br/>(user message)
    DB-->>Edge: Message ID
    
    Edge->>Daemon: WebSocket: call_tool<br/>{tool, prompt, params}
    Daemon->>Daemon: Process with AI model
    Daemon-->>Edge: WebSocket: result<br/>{content, metadata}
    
    Edge->>DB: INSERT INTO messages<br/>(assistant response)
    DB-->>Edge: Message ID
    DB->>Realtime: Notify new message
    
    Edge-->>UI: HTTP Response<br/>{result, metadata}
    Realtime-->>UI: WebSocket: new message
    UI->>UI: Update chat interface
    UI-->>User: Display response
```

---

### **Database Schema - Unified Approach**

```mermaid
erDiagram
    CONVERSATIONS ||--o{ MESSAGES : contains
    CONVERSATIONS ||--o{ CONVERSATION_FILES : has
    FILES ||--o{ CONVERSATION_FILES : linked_to
    
    CONVERSATIONS {
        uuid id PK
        text continuation_id UK
        text title
        jsonb metadata
        timestamptz created_at
        timestamptz updated_at
    }
    
    MESSAGES {
        uuid id PK
        uuid conversation_id FK
        enum role
        text content
        jsonb metadata
        timestamptz created_at
    }
    
    FILES {
        uuid id PK
        text storage_path UK
        text original_name
        text mime_type
        integer size_bytes
        enum file_type
        jsonb metadata
        timestamptz created_at
    }
    
    CONVERSATION_FILES {
        uuid conversation_id FK
        uuid file_id FK
        timestamptz added_at
    }
```

---

### **Component Architecture - Next.js App**

```mermaid
graph TB
    subgraph "Next.js App Structure"
        ROOT[app/layout.tsx<br/>Root Layout]
        
        subgraph "Pages"
            HOME[app/page.tsx<br/>Home/Chat Page]
            LOGIN[app/login/page.tsx<br/>Login Page]
            SIGNUP[app/signup/page.tsx<br/>Signup Page]
        end
        
        subgraph "Components"
            CHAT[components/mcp-chat-interface.tsx<br/>Main Chat Interface]
            SIDEBAR[components/sidebar.tsx<br/>Conversation List]
            MESSAGE[components/message.tsx<br/>Message Component]
            INPUT[components/message-input.tsx<br/>Input Component]
            FILE[components/file-upload.tsx<br/>File Upload]
        end
        
        subgraph "UI Components (shadcn/ui)"
            BUTTON[ui/button.tsx]
            CARD[ui/card.tsx]
            INPUT_UI[ui/input.tsx]
            DIALOG[ui/dialog.tsx]
            DROPDOWN[ui/dropdown-menu.tsx]
        end
        
        subgraph "Libraries"
            SUPABASE[lib/supabase.ts<br/>Supabase Client]
            AUTH_LIB[lib/auth.ts<br/>Auth Helpers]
            TYPES[lib/types.ts<br/>TypeScript Types]
            UTILS[lib/utils.ts<br/>Utilities]
        end
        
        ROOT --> HOME
        ROOT --> LOGIN
        ROOT --> SIGNUP
        
        HOME --> CHAT
        CHAT --> SIDEBAR
        CHAT --> MESSAGE
        CHAT --> INPUT
        CHAT --> FILE
        
        CHAT --> BUTTON
        CHAT --> CARD
        CHAT --> INPUT_UI
        CHAT --> DIALOG
        CHAT --> DROPDOWN
        
        CHAT --> SUPABASE
        CHAT --> AUTH_LIB
        CHAT --> TYPES
        CHAT --> UTILS
    end
    
    style ROOT fill:#4ecdc4
    style HOME fill:#95e1d3
    style CHAT fill:#f38181
    style SUPABASE fill:#aa96da
```

---

### **Authentication Flow**

```mermaid
sequenceDiagram
    participant User
    participant UI as Next.js UI
    participant Auth as Supabase Auth
    participant DB as PostgreSQL
    
    Note over User,DB: Sign Up Flow
    User->>UI: Enter email & password
    UI->>Auth: signUp(email, password)
    Auth->>DB: Create user record
    Auth->>User: Send verification email
    User->>Auth: Click verification link
    Auth-->>UI: User verified ✓
    
    Note over User,DB: Login Flow
    User->>UI: Enter credentials
    UI->>Auth: signInWithPassword(email, password)
    Auth->>DB: Verify credentials
    Auth-->>UI: Session token (JWT)
    UI->>UI: Store session in localStorage
    UI-->>User: Redirect to chat
    
    Note over User,DB: Authenticated Request
    User->>UI: Send message
    UI->>Auth: Get session token
    Auth-->>UI: Valid token ✓
    UI->>DB: Query with RLS<br/>(user_id from JWT)
    DB-->>UI: User's data only
```

---

### **File Upload Flow**

```mermaid
sequenceDiagram
    participant User
    participant UI as Next.js UI
    participant Storage as Supabase Storage
    participant DB as PostgreSQL
    participant Edge as Edge Function
    participant Daemon as EXAI Daemon
    
    User->>UI: Select file
    UI->>UI: Validate file<br/>(size, type)
    UI->>Storage: Upload to bucket<br/>user-files/{user_id}/{file_id}
    Storage-->>UI: Storage path
    
    UI->>DB: INSERT INTO files<br/>(path, name, size, type)
    DB-->>UI: File ID
    
    UI->>DB: INSERT INTO conversation_files<br/>(conversation_id, file_id)
    DB-->>UI: Link created
    
    User->>UI: Send message with file
    UI->>Edge: POST /exai-chat<br/>{prompt, file_ids}
    Edge->>Storage: Download file
    Storage-->>Edge: File content
    
    Edge->>Daemon: call_tool with file context
    Daemon-->>Edge: Response
    Edge-->>UI: Result
```

---

### **Real-time Updates Flow**

```mermaid
sequenceDiagram
    participant User1 as User 1 Browser
    participant User2 as User 2 Browser
    participant Realtime as Supabase Realtime
    participant DB as PostgreSQL
    participant Edge as Edge Function
    
    User1->>Realtime: Subscribe to conversation
    User2->>Realtime: Subscribe to conversation
    
    User1->>Edge: Send message
    Edge->>DB: INSERT INTO messages
    DB->>Realtime: Notify: new message
    
    Realtime-->>User1: WebSocket: new message
    Realtime-->>User2: WebSocket: new message
    
    User1->>User1: Update UI (optimistic)
    User2->>User2: Update UI (real-time)
```

---

### **Deployment Architecture**

```mermaid
graph TB
    subgraph "Vercel Edge Network"
        EDGE_NODES[Edge Nodes<br/>Global CDN]
        NEXTJS_SERVER[Next.js Server<br/>Serverless Functions]
        EDGE_NODES --> NEXTJS_SERVER
    end
    
    subgraph "Supabase Cloud"
        SUPABASE_EDGE[Edge Functions<br/>Deno Runtime]
        SUPABASE_DB[(PostgreSQL<br/>Primary + Replicas)]
        SUPABASE_STORAGE[Object Storage<br/>S3-compatible]
        SUPABASE_AUTH[Auth Service]
        SUPABASE_REALTIME[Realtime Service<br/>WebSocket]
    end
    
    subgraph "User's Infrastructure"
        DOCKER[Docker Container<br/>EXAI Daemon]
        DOCKER_NETWORK[host.docker.internal:8079]
        DOCKER --> DOCKER_NETWORK
    end
    
    USERS[Users Worldwide] --> EDGE_NODES
    NEXTJS_SERVER --> SUPABASE_EDGE
    NEXTJS_SERVER --> SUPABASE_DB
    NEXTJS_SERVER --> SUPABASE_STORAGE
    NEXTJS_SERVER --> SUPABASE_AUTH
    NEXTJS_SERVER --> SUPABASE_REALTIME
    
    SUPABASE_EDGE --> DOCKER_NETWORK
    
    style EDGE_NODES fill:#4ecdc4
    style NEXTJS_SERVER fill:#95e1d3
    style SUPABASE_EDGE fill:#f38181
    style SUPABASE_DB fill:#aa96da
    style DOCKER fill:#ffd3b6
```

---

### **Security Architecture - Row Level Security (RLS)**

```mermaid
graph TB
    subgraph "User Request"
        USER[Authenticated User<br/>JWT Token]
    end
    
    subgraph "Supabase Auth"
        AUTH[Extract user_id from JWT]
    end
    
    subgraph "PostgreSQL with RLS"
        RLS_POLICY[RLS Policy Check]
        QUERY[SQL Query]
        
        RLS_POLICY --> |user_id matches| ALLOW[Allow Access]
        RLS_POLICY --> |user_id mismatch| DENY[Deny Access]
        
        ALLOW --> QUERY
        DENY --> ERROR[Return Error]
    end
    
    subgraph "Data"
        USER_DATA[User's Data Only]
        OTHER_DATA[Other Users' Data<br/>❌ Not Accessible]
    end
    
    USER --> AUTH
    AUTH --> RLS_POLICY
    QUERY --> USER_DATA
    
    style USER fill:#4ecdc4
    style AUTH fill:#95e1d3
    style RLS_POLICY fill:#f38181
    style ALLOW fill:#a8e6cf
    style DENY fill:#ff6b6b
    style USER_DATA fill:#a8e6cf
    style OTHER_DATA fill:#ff6b6b
```

---

## 📊 **COMPARISON: BEFORE vs AFTER**

### **Before (Current Broken State)**

```mermaid
graph LR
    A[Single HTML File<br/>407 lines] --> B[❌ No Deployment]
    A --> C[❌ No Auth]
    A --> D[❌ No Scalability]
    A --> E[❌ No Security]
    
    style A fill:#ff6b6b
    style B fill:#ff6b6b
    style C fill:#ff6b6b
    style D fill:#ff6b6b
    style E fill:#ff6b6b
```

### **After (Recommended Architecture)**

```mermaid
graph LR
    A[Next.js App<br/>Modular Components] --> B[✅ Vercel Deployment]
    A --> C[✅ Supabase Auth]
    A --> D[✅ Horizontal Scaling]
    A --> E[✅ RLS Security]
    A --> F[✅ Real-time Updates]
    A --> G[✅ File Storage]
    A --> H[✅ Type Safety]
    
    style A fill:#a8e6cf
    style B fill:#a8e6cf
    style C fill:#a8e6cf
    style D fill:#a8e6cf
    style E fill:#a8e6cf
    style F fill:#a8e6cf
    style G fill:#a8e6cf
    style H fill:#a8e6cf
```

---

## 🎯 **NEXT STEPS**

See the following documents for implementation:

1. `00_EXECUTIVE_SUMMARY.md` - Overview and action plan
2. `01_ARCHITECTURAL_ANALYSIS.md` - Detailed technical analysis
3. `02_UNIFIED_SCHEMA.md` - Complete database schema (to be created)
4. `03_MIGRATION_PLAN.md` - Step-by-step migration guide (to be created)
5. `04_DEPLOYMENT_GUIDE.md` - Deployment instructions (to be created)

---

**Diagrams Complete** ✅  
**Ready for Implementation**

