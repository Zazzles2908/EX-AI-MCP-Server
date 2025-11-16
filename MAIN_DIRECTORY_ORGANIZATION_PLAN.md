# EX-AI MCP Server - Main Directory Organization Plan

## **📋 CURRENT FILES IN MAIN DIRECTORY (44 files)**

### **✅ KEEP IN ROOT (Essential Files)**
```
ROOT/
├── README.md                           # Main project documentation
├── CONTRIBUTING.md                     # Development guidelines
├── CHANGELOG.md                        # Version history  
├── LICENSE                             # License file
├── requirements.txt                    # Python dependencies
├── docker-compose.yml                  # Container orchestration
├── Dockerfile                          # Container definition
└── .gitignore                          # Git ignore rules
```

### **📁 MOVE TO /config/ (Configuration Files)**
```
config/
├── .env                               # Environment variables
├── .env.docker                        # Docker environment (HIDDEN FILE CONFIRMED)
├── .env.example                       # Environment template
├── .mcp.json                          # MCP server configuration
├── .mcp.json.example                  # MCP template
├── config.yaml                        # Application configuration
├── mini-agent-config.yaml             # Mini-Agent configuration
└── .dockerignore                      # Docker ignore rules
```

### **📁 MOVE TO /docs/ (Documentation)**
```
docs/
├── ARCHITECTURAL_CLEANUP_REPORT.md
├── COMPLETE_RESOLUTION_REPORT.md
├── COMPREHENSIVE_RESOLUTION_SUMMARY.md
├── DOCUMENTATION_CONSOLIDATION.md
├── ENHANCED_AI_CAPABILITIES_ASSESSMENT.md
├── ENVIRONMENT_MANAGEMENT.md
├── EXAI_MCP_STREAMLINING_COMPLETE.md
├── FINAL_ASSESSMENT.md
├── GIT_STATUS_QUICK_SUMMARY.md
├── GIT_STATUS_REPORT.md
├── MYSTERY_SOLVED.md
├── PARAMETER_OPTIMIZATION_GUIDE.md
├── PROJECT_CLEANUP_EXECUTOR.md
├── PROVIDER_ANALYSIS.md
├── PROVIDER_INVESTIGATION_README.md
├── REPOSITORY_CLEANUP_PLAN.md
├── STDIO_BRIDGE_WORK_BRANCH_INFO.md
├── TEST_ORGANIZATION_COMPLETE.md
├── TOOL_OPTIMIZATION_GUIDE.md
├── VALIDATION_COMPLETE_REPORT.md
├── COMPLETE_IMPROVEMENT_GAME_PLAN.md
├── prompts.md                         # System prompts
└── system_prompt.md                   # System prompts
└── system_prompt.txt                  # System prompts
```

### **📁 MOVE TO /scripts/ (Scripts & Tools)**
```
scripts/
├── fix_file_organization.sh           # File organization script
├── validate_deployment.sh             # Deployment validation
├── provider_diagnostic.py             # Provider diagnostic tool
├── verify_ai_capabilities.py          # AI capabilities verification
└── EXAI_MEMORY_CONSOLIDATED.json      # Memory/conversation data
```

### **📁 MOVE TO /.git/ (Git Files - Hidden)**
```
.git/
└── .gitattributes                     # Git attributes (move to .git folder)
```

### **📁 MOVE TO /.agent/ (Agent Data - Hidden)**
```
.agent/
└── .agent_memory.json                 # Agent memory data
```

## **🚨 HIDDEN FILES CONFIRMED:**
- `.env.docker` - Yes, this is a hidden file (starts with dot)
- All other .dot files are hidden as well

## **⚠️ PERMISSION REQUIRED:**

Before proceeding with any file movements, I need your explicit permission for:

1. **Moving configuration files** from root to /config/
2. **Consolidating documentation** from root to /docs/
3. **Organizing scripts** from root to /scripts/
4. **Relocating agent data** to /agent/ (hidden directory)
5. **Moving git attributes** to .git/ folder

## **🎯 EXPECTED RESULT:**
```
BEFORE: 44 files scattered in main directory
AFTER: 8 essential files in root + organized structure
REDUCTION: 82% reduction in main directory clutter
```

## **🔒 IMPORTANT NOTES:**
- **Hidden files preserved**: .env.docker and other dot-files maintained
- **Git integrity maintained**: No changes to repository structure
- **Configuration centralized**: All configs in /config/ directory
- **Documentation organized**: All docs in /docs/ directory
- **Scripts separated**: All utility scripts in /scripts/ directory

**May I proceed with this organization plan?**
