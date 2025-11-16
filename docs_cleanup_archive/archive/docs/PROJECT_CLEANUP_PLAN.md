# EX-AI MCP Server - Project Cleanup Plan

## 📁 **CURRENT STATE ASSESSMENT**

The project contains **massive sprawl** with hundreds of directories and files:

### **🔴 MAJOR CLEANUP AREAS**

#### **1. Root Directory Pollution (CRITICAL)**
```
Root Directory Issues:
├── .agent_memory.json          # ❌ Agent state, not core functionality  
├── .cache/                     # ❌ Cache, should be in .gitignore
├── agent_outputs/             # ❌ Output pollution
├── agent-workspace/           # ❌ AI agent specific, not core
├── clean_later/               # ❌ Files marked for deletion
├── config.yaml                # ❌ Duplicate config
├── downloads_temp/            # ❌ Temporary files
├── EXAI_MEMORY_CONSOLIDATED.json  # ❌ Agent state
├── logs_temp/                 # ❌ Duplicate logs
├── session_memory/            # ❌ Session specific
├── smart_file_download_error_restarted.json  # ❌ Error pollution
├── tool_results/              # ❌ Output pollution
└── 20+ more scattered files   # ❌ Various tool outputs
```

#### **2. Documentation Overload (HIGH)**
```
Documentation Issues:
├── docs/ (100+ files)         # ❌ Massive duplication
├── docs/Fix_agents/           # ❌ Agent-specific docs
├── docs/mini-agent-cli-guide/ # ❌ Tool-specific docs  
├── docs/operations/           # ❌ Operations docs
└── Root-level .md files (15+) # ❌ Scattered documentation
```

#### **3. Testing Infrastructure Bloat (HIGH)**
```
Testing Issues:
├── tests/ (200+ files)        # ❌ Excessive test sprawl
├── tests/automation/          # ❌ Legacy test artifacts
├── tests/integration/         # ❌ Duplicate integration tests
├── tests/performance/         # ❌ Performance test bloat
└── scripts/ (100+ files)      # ❌ Massive script proliferation
```

#### **4. Development Artifacts (MEDIUM)**
```
Development Artifacts:
├── __pycache__/              # ❌ Python cache files
├── .pytest_cache/            # ❌ Test cache
├── venv/                     # ❌ Virtual environment
├── .vscode/                  # ❌ IDE-specific files
├── .github/                  # ❌ GitHub templates
└── Multiple backup directories # ❌ .backup files everywhere
```

### **✅ CORE INFRASTRUCTURE (KEEP)**

#### **Essential Files (NEEDS CLEANUP)**
```
Core Infrastructure:
├── src/                      # ✅ Core source code
├── tools/                    # ✅ MCP tools  
├── utils/                    # ✅ Utilities
├── config/                   # ✅ Configuration
├── static/                   # ✅ Static assets
├── Dockerfile               # ✅ Container build
├── docker-compose.yml       # ✅ Orchestration
├── .mcp.json               # ✅ MCP configuration
├── .env.docker             # ✅ Environment config
├── requirements.txt         # ✅ Dependencies
├── system_prompt.md         # ✅ System prompts
└── tools registry files     # ✅ Tool registrations
```

## 🧹 **CLEANUP STRATEGY**

### **Phase 1: Root Directory Cleanup**
1. Move agent-specific files to `archive/`
2. Consolidate documentation into `docs/`  
3. Remove output pollution
4. Clean up development artifacts

### **Phase 2: Documentation Consolidation**
1. Merge scattered .md files into organized docs structure
2. Remove duplicate and outdated documentation
3. Create single source of truth for setup/installation

### **Phase 3: Testing Infrastructure**
1. Consolidate tests into logical categories
2. Remove legacy/duplicate test files
3. Keep only essential integration and unit tests

### **Phase 4: Configuration Organization**
1. Consolidate configuration files
2. Remove duplicates and backup files
3. Create clear configuration hierarchy

## 🎯 **RECOMMENDED FINAL STRUCTURE**

```
EX-AI-MCP-Server/
├── src/                     # Core source code
├── tools/                   # MCP tools implementation  
├── utils/                   # Utility modules
├── config/                  # Configuration files
├── static/                  # Static assets
├── docs/                    # Organized documentation
├── tests/                   # Essential tests only
├── scripts/                 # Essential scripts only
├── docker-compose.yml       # Container orchestration
├── Dockerfile              # Container build
├── .mcp.json              # MCP configuration
├── requirements.txt        # Dependencies
└── system_prompt.md        # System prompts
```

## 📊 **CLEANUP PRIORITY**

1. **CRITICAL**: Root directory pollution
2. **HIGH**: Documentation consolidation  
3. **HIGH**: Testing infrastructure bloat
4. **MEDIUM**: Development artifacts
5. **LOW**: Database migrations (keep for now)