# Mini Agent CLI - Complete Usage Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Basic CLI Usage](#basic-cli-usage)
3. [Command Syntax & Best Practices](#command-syntax--best-practices)
4. [Available Skills & Functions](#available-skills--functions)
5. [Special Characters & UI Features](#special-characters--ui-features)
6. [Advanced Workflows](#advanced-workflows)
7. [Workspace Management](#workspace-management)
8. [Integration Examples](#integration-examples)
9. [Troubleshooting](#troubleshooting)
10. [Cheat Sheet](#cheat-sheet)

---

## Quick Start

### 1. Starting Mini Agent
```bash
# Navigate to your project directory
cd /c/Project/EX-AI-MCP-Server

# Start Mini Agent with workspace access
mini-agent --workspace .

# Alternative: Use full path
mini-agent --workspace /c/Project/EX-AI-MCP-Server
```

### 2. Basic Interaction
Once Mini Agent starts, you'll see a prompt. Simply type your requests:

```
> Hello! Can you analyze this project?
> Create a PDF report from the README.md
> Check if all Docker containers are running
> Help me write unit tests for the MCP server
```

---

## Basic CLI Usage

### Starting Mini Agent
```bash
# Basic usage
mini-agent

# With specific workspace
mini-agent --workspace /path/to/your/project

# View version
mini-agent --version

# Check configuration
mini-agent --config
```

### Workspace Configuration
- **Current Setup**: Your EX-AI MCP Server at `/c/Project/EX-AI-MCP-Server`
- **Auto-detection**: Mini Agent automatically detects `.mcp.json` files
- **Path Resolution**: All relative paths are resolved from workspace root

### Session Management
- **Persistent Context**: Mini Agent maintains context throughout the session
- **File Awareness**: Always knows your current project structure
- **Docker Integration**: Monitors running containers and services

---

## Command Syntax & Best Practices

### 1. Natural Language Commands (Recommended)
Mini Agent excels with conversational, natural language:

```
✅ Good Examples:
> Analyze the main.py file and identify potential issues
> Create a comprehensive PDF report about this project's architecture
> Check if all Docker services are healthy and restart any failed ones
> Help me optimize the WebSocket connection handling in the MCP server
> Generate unit tests for the agent executor module
```

### 2. Direct Action Commands
For specific tasks, be explicit about what you want:

```
✅ Clear Examples:
> Read and summarize the CHANGELOG.md file
> Extract all configuration variables from .env.docker
> Create a new file called `api_docs.md` with project documentation
> Merge all PDF files in the docs/ directory into one master document
> Run a security scan on the Python dependencies
```

### 3. Multi-Step Workflows
Chain related tasks together:

```
✅ Workflow Examples:
> First check the Docker container status, then analyze any failed services, finally generate a system health report
> Read the README.md, check the test coverage, and create a development guide
> Analyze the source code structure, identify performance bottlenecks, and suggest optimizations
```

### 4. Command Structure Best Practices

#### Be Specific About Scope
```
❌ Vague: "Help with code"
✅ Specific: "Analyze the request_handler.py file for threading issues"

❌ Vague: "Create documentation"  
✅ Specific: "Create a PDF API documentation for all MCP server tools"
```

#### Reference Files & Directories
```
✅ File References:
> Analyze src/daemon/ws_server.py specifically
> Create a report from all files in the docs/ directory
> Review the test files in tests/unit/ for coverage gaps

✅ Directory References:
> Show me the structure of the src/ directory
> What Python files are in the web_ui/ module?
> Check all configuration files in config/
```

---

## Available Skills & Functions

### Document Processing Skills

#### PDF Operations
```
Available via 'pdf' skill:
- Extract text from PDFs
- Merge multiple PDFs
- Split PDF documents
- Create new PDFs
- Extract tables and images
- Add watermarks
- Password protection
- OCR for scanned documents

Example Usage:
> Extract all text from user_manual.pdf and save as user_manual.txt
> Merge installation_guide.pdf and setup_instructions.pdf into complete_guide.pdf
> Create a new PDF with project overview using data from README.md
```

#### Microsoft Office Integration
```
DOCX (Word Documents):
- Read and analyze Word documents
- Extract text and formatting
- Convert to other formats

PPTX (PowerPoint Presentations):
- Create presentation slides
- Extract content from existing presentations
- Generate slide decks from data

XLSX (Excel Spreadsheets):
- Process spreadsheet data
- Create reports and charts
- Import/export data formats

Example Usage:
> Convert the project requirements to a PowerPoint presentation
> Create an Excel report showing Docker container status over time
> Extract all text from the technical documentation.docx file
```

### Development & Testing Skills

#### Web Application Testing
```
Available via 'webapp-testing' skill:
- Functional testing
- Performance benchmarking
- Security scanning
- API endpoint testing
- User interface validation

Example Usage:
> Test all endpoints in the MCP server API
> Run security scans on the web UI components
> Benchmark the WebSocket connection performance
```

#### Code Analysis & Generation
```
Available via 'skill-creator' and 'mcp-builder':
- Generate unit tests
- Create new MCP servers
- Build custom skills
- Code refactoring assistance

Example Usage:
> Generate comprehensive unit tests for the ws_server module
> Create a new MCP server template for data processing
> Help me refactor the request handler for better performance
```

### System Integration Skills

#### Docker & Container Management
```
Access via Docker MCP integration:
- Container status monitoring
- Log analysis
- Service management
- Resource utilization tracking

Example Usage:
> Check health of all EX-AI MCP Server containers
> View real-time logs from the Redis service
> Restart failed containers and verify they come up properly
> Generate a system status report with container metrics
```

#### Git & Version Control
```
Available via Git MCP:
- Repository analysis
- Change tracking
- Branch management
- Conflict resolution

Example Usage:
> Show me the recent commits and what they changed
> Analyze the git history for the past month
> Create a release summary from git tags and commits
```

---

## Special Characters & UI Features

### 1. Prompt Symbols
```
> Standard prompt - for regular commands
> Special prompt indicators may appear for:
  - Long-running operations
  - Multi-step processes
  - Error states
  - Confirmation requests
```

### 2. Line Continuation
```
> For complex commands, you can continue on multiple lines:
> Create a comprehensive project analysis that includes:
  - Source code structure overview
  - Dependency analysis
  - Security vulnerability scan
  - Performance bottleneck identification
  - Documentation completeness review
```

### 3. Command History
```
> Use arrow keys to navigate command history
> Previous commands can be modified and re-executed
> Search history with Ctrl+R (if terminal supports it)
```

### 4. Special Input Patterns

#### File Path References
```
> Use relative paths from workspace:
  src/daemon/ws_server.py
  docs/api/
  tests/unit/test_mcp_*.py

> Use absolute paths when needed:
  C:/Project/EX-AI-MCP-Server/config/
  ~/.mini-agent/config/
```

#### Environment Variable References
```
> Reference environment variables:
  $MINIMAX_API_KEY
  $EXAI_CONFIG_PATH
  $DOCKER_HOST
```

### 5. Output Formatting

#### Structured Output
```
Mini Agent provides:
- Formatted tables for data
- Syntax-highlighted code blocks
- Progress indicators for long operations
- Error messages with suggested fixes
```

#### Export Options
```
> Many operations support export:
  - Save reports as PDF, DOCX, or text
  - Export data as CSV or Excel
  - Generate JSON or XML output
  - Create HTML reports
```

---

## Advanced Workflows

### 1. Project Analysis Workflow
```
Step 1: Repository Overview
> Analyze the overall project structure and identify main components

Step 2: Code Quality Assessment
> Run code analysis on all Python modules for potential issues
> Check test coverage and identify gaps

Step 3: Documentation Review
> Review all documentation files for completeness and accuracy
> Identify missing documentation areas

Step 4: Generate Report
> Create a comprehensive PDF report with findings and recommendations
```

### 2. Development Workflow
```
Step 1: Environment Setup
> Check Docker container status and ensure all services are running
> Verify environment configuration

Step 2: Development Tasks
> Create new feature branch analysis
> Generate unit tests for new functionality
> Review existing code for refactoring opportunities

Step 3: Testing & Validation
> Run test suites and analyze coverage
> Perform integration testing with Docker services
> Generate testing report
```

### 3. Documentation Workflow
```
Step 1: Content Gathering
> Extract information from source code comments
> Collect data from configuration files
> Gather usage examples from test files

Step 2: Documentation Generation
> Create structured documentation with proper formatting
> Generate PDF with table of contents and cross-references
> Export documentation in multiple formats

Step 3: Maintenance
> Update documentation when code changes
> Track documentation completeness metrics
```

### 4. Monitoring Workflow
```
Step 1: System Health Check
> Monitor all Docker container statuses
> Check resource utilization and performance metrics
> Analyze log files for errors or warnings

Step 2: Issue Resolution
> Identify and categorize any issues found
> Provide recommendations for fixes
> Generate maintenance report
```

---

## Workspace Management

### Understanding Your Current Setup

**Your Configuration:**
```
Workspace: /c/Project/EX-AI-MCP-Server
MCP Config: .mcp.json (auto-detected)
Docker Services: exai-mcp-stdio, exai-mcp-server, redis, redis-commander
Available Skills: PDF, DOCX, PPTX, XLSX, webapp-testing, skill-creator, mcp-builder
```

### Project Structure Access
```
✅ Full Access To:
  /c/Project/EX-AI-MCP-Server/* (your entire project)
  C:/Users/* (user directories)
  C:/Project/* (all project directories)
  Docker container internals via exec

❌ Access Limitations:
  System directories outside C:/
  Other users' private files
  Encrypted or password-protected resources
```

### Working Directory Context
```
> All file operations resolve relative to workspace root
> Docker commands execute in container context
> Git operations work on the repository
> Environment variables are accessible
```

---

## Integration Examples

### 1. Docker Integration
```
Example: Full Container Analysis
> Check status of all EX-AI MCP Server containers
> View last 100 lines of logs from exai-mcp-stdio
> Restart any unhealthy containers
> Verify all expected ports are listening
> Generate container health report as PDF
```

### 2. Development Workflow
```
Example: Feature Development
> Analyze current codebase for new feature integration points
> Generate unit tests for proposed functionality
> Create development timeline based on complexity assessment
> Document API changes needed
> Generate implementation checklist
```

### 3. Documentation Generation
```
Example: Technical Documentation
> Extract all function signatures and docstrings from src/
> Create comprehensive API reference
> Generate user manual from README and docs/
> Create deployment guide from Docker configurations
> Export everything as searchable PDF
```

### 4. Testing & Quality Assurance
```
Example: Comprehensive QA Process
> Analyze test coverage across all modules
> Identify performance bottlenecks in critical paths
> Run security scans on dependencies
> Generate quality metrics report
> Create test automation recommendations
```

---

## Troubleshooting

### Common Issues & Solutions

#### 1. API Key Problems
```
Problem: "NoneType" errors or authentication failures
Solution:
> Verify MINIMAX_API_KEY is set: echo $MINIMAX_API_KEY | head -c 20
> Check config file: cat ~/.mini-agent/config/config.yaml
> Test API directly: curl with your API key
```

#### 2. Docker Connection Issues
```
Problem: Cannot connect to Docker containers
Solution:
> Check Docker daemon is running
> Verify container names: docker ps | findstr exai
> Check container health status
> Restart services if needed
```

#### 3. File Access Problems
```
Problem: Cannot read/write files in workspace
Solution:
> Verify workspace path is correct
> Check file permissions
> Ensure you're running from correct directory
> Use absolute paths if needed
```

#### 4. Skill Availability Issues
```
Problem: "Skill not found" errors
Solution:
> List available skills: get_available_skills()
> Check skill documentation: get_skill("skill_name")
> Verify Mini Agent installation is complete
```

### Debug Commands
```
# Check Mini Agent configuration
mini-agent --config

# Verify workspace access
mini-agent --workspace . --verify

# Test Docker connectivity
docker ps

# Check environment variables
env | findstr MINIMAX
env | findstr EXAI

# Test API connectivity
curl -X POST "https://api.minimax.io/v1/text/chatcompletion_pro" \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"MiniMax-M2","messages":[{"role":"user","content":"test"}]}'
```

---

## Cheat Sheet

### Quick Commands

#### Project Analysis
```
> Explain what this project does
> Show me the main components and their purpose
> What are the key files I should understand first?
> Analyze the architecture and identify potential improvements
```

#### File Operations
```
> Read [filename] and summarize the key points
> Extract data from [PDF/Word/Excel file]
> Create a new file with [specific content]
> Convert [file format A] to [file format B]
> Merge all [file type] files in [directory]
```

#### System Management
```
> Check Docker container status
> View logs from [specific service]
> Restart failed containers
> Monitor system resources
> Generate system health report
```

#### Development Tasks
```
> Generate unit tests for [specific module/function]
> Help me optimize [specific code area]
> Create documentation for [API/module]
> Analyze code quality and suggest improvements
> Create new [feature/component] based on requirements
```

#### Document Generation
```
> Create PDF report about [topic]
> Convert [document] to [different format]
> Generate user manual from [source material]
> Create presentation slides about [subject]
> Export [data] to spreadsheet format
```

### Command Templates

#### Analysis Commands
```
"Analyze [file/directory] for [specific criteria]"
"Compare [item A] with [item B] and identify differences"
"Identify potential issues in [code section]"
"Review [document] for completeness and accuracy"
```

#### Generation Commands
```
"Create [document type] with information from [sources]"
"Generate [code/tests/documentation] for [specific purpose]"
"Build [tool/component] that does [specific task]"
"Convert [input] into [output format] with [specific requirements]"
```

#### Workflow Commands
```
"First [step 1], then [step 2], finally [step 3]"
"Check [condition], if [issue] then [action], else [alternative]"
"Monitor [system] and [action] if [problem detected]"
```

### Special Patterns

#### Multi-Step Processes
```
> Step 1: Analyze the current codebase
> Step 2: Identify improvement opportunities  
> Step 3: Generate implementation recommendations
> Step 4: Create project plan with timeline
```

#### Conditional Operations
```
> If the Redis container is down, restart it and verify connectivity
> Only analyze Python files that were modified in the last 30 days
> Generate documentation for all public functions except internal utilities
```

#### Batch Operations
```
> Process all files in [directory] with [operation]
> Apply [transformation] to all [file type] files
> Create [output] for every [input type] in the project
```

---

## Conclusion

Mini Agent CLI provides powerful, intelligent assistance for development, documentation, and system management tasks. The key to effective usage is:

1. **Be conversational** - Natural language works best
2. **Be specific** - Clear requests yield better results  
3. **Chain operations** - Build complex workflows step by step
4. **Use available skills** - Leverage specialized capabilities
5. **Reference your workspace** - Stay aware of your project context

### Getting Started Checklist
- [ ] Mini Agent installed and configured ✅
- [ ] Workspace path correctly set ✅
- [ ] Docker services running ✅
- [ ] API key verified ✅
- [ ] This guide reviewed ✅

**Ready to start?** Run:
```bash
cd /c/Project/EX-AI-MCP-Server
mini-agent --workspace .
```

Then try: **"Give me a comprehensive overview of this EX-AI MCP Server project and suggest 3 areas for improvement."**

---

*Last Updated: 2025-11-15*
*For the latest updates and examples, refer to the project documentation.*