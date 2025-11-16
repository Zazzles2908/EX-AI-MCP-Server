# EX-AI MCP Server Repository Cleanup Plan

## **CURRENT STATE**
- **200+ markdown files** scattered across multiple directories
- **4,562 Python files** (including 4,145 .pyc cache files)
- Duplicate documentation in multiple locations
- No clear documentation structure

## **CLEANUP STRATEGY**

### **Step 1: Remove Redundant Documentation (TARGET: 80% reduction)**
```
KEEP (Essential 15 files):
├── README.md                           # Main project overview
├── CONTRIBUTING.md                     # Development guidelines
├── ARCHITECTURE.md                     # System architecture
├── API_REFERENCE.md                    # Tool API documentation
├── DEPLOYMENT.md                       # Deployment guide
├── TROUBLESHOOTING.md                  # Common issues and solutions
├── CHANGELOG.md                        # Version history
├── LICENSE                             # License file
├── .env.example                        # Environment template
├── docker-compose.yml                  # Container orchestration
├── Dockerfile                          # Container definition
├── .mcp.json                          # MCP configuration
├── requirements.txt                    # Python dependencies
└── SECURITY.md                         # Security guidelines
└── ROADMAP.md                          # Future development plan

REMOVE (All others - 180+ files):
├── archive/                           # All archived docs
├── clean_later/                       # All files marked for later
├── docs/ (multiple subdirs)           # Duplicate documentation
├── tests/ (docs)                      # Move to main README
├── agent-workspace/ (docs files)      # Consolidate to main
├── web_ui/ (docs)                     # Integrate into main
├── venv/ (docs)                       # Remove virtual env docs
├── All duplicate README files         # Keep only main README
└── All analysis and progress reports  # Move to Git history
```

### **Step 2: Consolidate Python Structure**
```
TARGET STRUCTURE:
exai-mcp-server/
├── src/                               # Core implementation
│   ├── server.py                      # Main MCP server
│   ├── tools/                         # Tool implementations
│   ├── providers/                     # AI provider integrations
│   ├── router/                        # Smart routing logic
│   └── utils/                         # Shared utilities
├── tests/                             # Test suite
├── docs/                              # Essential documentation only
├── scripts/                           # Deployment/utility scripts
├── config/                            # Configuration files
├── docker-compose.yml                 # Container orchestration
├── Dockerfile                         # Container definition
├── requirements.txt                   # Dependencies
└── README.md                          # Project overview
```

### **Step 3: Remove Cache and Build Files**
```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# Remove build artifacts
find . -name "*.pyc" -delete
find . -name "*.pyd" -delete
find . -name "*.pyx" -delete

# Remove temporary files
find . -name ".coverage" -delete
find . -name "*.pid" -delete
find . -name "*.backup" -delete
```

### **Step 4: Create Single Source of Truth**
- Consolidate all setup instructions into one DEPLOYMENT.md
- Single API reference in API_REFERENCE.md
- Unified troubleshooting guide
- Single architecture overview

## **EXPECTED RESULTS**
- **80% reduction** in documentation files (200 → 15)
- **50% reduction** in total files (accounting for cache removal)
- **Clear project structure** with obvious locations for everything
- **Reduced maintenance burden** with single source of truth

## **IMPLEMENTATION PRIORITY**
1. **HIGH**: Remove duplicate/redundant documentation
2. **HIGH**: Clean up cache and build files
3. **MEDIUM**: Consolidate Python structure
4. **LOW**: Optimize directory organization
