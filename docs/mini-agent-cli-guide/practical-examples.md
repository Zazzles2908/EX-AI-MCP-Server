# Mini Agent CLI - Practical Examples

## 📚 Real-World Usage Scenarios

### 1. Project Onboarding & Understanding

**Scenario**: New team member needs to understand the EX-AI MCP Server

```
> "I'm new to this project. Give me a comprehensive overview of what the EX-AI MCP Server does, its main components, and how they work together"
> "Show me the key files I should understand first to get up to speed"
> "Create a visual architecture diagram and save it as a PDF"
> "Generate a quick-start guide for new developers joining this project"
```

**Expected Outcomes:**
- Clear project explanation in natural language
- Prioritized file list with descriptions
- Visual architecture diagram (using Mermaid)
- Developer onboarding document

---

### 2. Docker Service Management

**Scenario**: System health check and maintenance

```
> "Check the status of all Docker containers in this project"
> "View the last 50 lines of logs from the exai-mcp-stdio container"
> "If any containers are unhealthy, restart them and verify they come up properly"
> "Generate a system health report as PDF with current status and any issues found"
> "Monitor resource usage for the next 5 minutes and alert me if anything looks abnormal"
```

**Expected Outcomes:**
- Real-time container status report
- Log analysis with error identification
- Automated remediation for failed services
- Comprehensive health report document
- Resource monitoring with alerts

---

### 3. Documentation Generation & Management

**Scenario**: Create comprehensive project documentation

```
> "Analyze all Python files in src/ and extract function signatures, docstrings, and class definitions"
> "Create comprehensive API documentation as a searchable PDF"
> "Review the existing documentation in docs/ and identify gaps or outdated information"
> "Generate a user manual based on the README.md and configuration examples"
> "Create a deployment guide with step-by-step instructions from the Docker setup"
```

**Expected Outcomes:**
- Complete API reference documentation
- Automated PDF generation with table of contents
- Documentation completeness analysis
- User-friendly manual creation
- Step-by-step deployment instructions

---

### 4. Code Quality & Testing

**Scenario**: Code review and quality improvement

```
> "Analyze all Python modules for potential issues, code smells, and improvement opportunities"
> "Generate unit tests for all functions that currently lack test coverage"
> "Check the test coverage across the entire codebase and identify gaps"
> "Review the security aspects of the MCP server implementation"
> "Create a code quality report with specific recommendations for improvements"
```

**Expected Outcomes:**
- Detailed code analysis with specific recommendations
- Comprehensive unit test generation
- Test coverage metrics and gap analysis
- Security vulnerability assessment
- Actionable improvement plan

---

### 5. Performance Analysis & Optimization

**Scenario**: System performance evaluation

```
> "Analyze the WebSocket connection handling in the MCP server for performance bottlenecks"
> "Check memory and CPU usage patterns of all Docker containers"
> "Review the database query patterns and suggest optimizations"
> "Generate a performance report with current metrics and optimization recommendations"
> "Create a performance monitoring dashboard configuration"
```

**Expected Outcomes:**
- Bottleneck identification with specific solutions
- Resource utilization analysis
- Database performance optimization suggestions
- Performance metrics report
- Monitoring configuration templates

---

### 6. Feature Development & Planning

**Scenario**: New feature implementation

```
> "Analyze the current MCP server architecture to understand where I should add a new data processing tool"
> "Generate a template for a new MCP tool with proper structure and error handling"
> "Create unit tests for the proposed new functionality"
> "Document the API changes and update the project documentation"
> "Generate a development timeline and checklist for implementing this feature"
```

**Expected Outcomes:**
- Architecture analysis for integration points
- Custom MCP tool template generation
- Comprehensive test suite creation
- Updated documentation and API references
- Detailed implementation plan

---

### 7. Troubleshooting & Debugging

**Scenario**: Investigate reported issues

```
> "The MCP server seems slow. Can you analyze the logs and identify potential causes?"
> "Check if there are any memory leaks or resource issues in the running containers"
> "Review the recent code changes that might have introduced performance degradation"
> "Generate a debugging report with root cause analysis and solution recommendations"
> "Set up enhanced monitoring to track the specific issue we identified"
```

**Expected Outcomes:**
- Log analysis with issue identification
- Resource leak detection and analysis
- Change impact assessment
- Root cause analysis report
- Enhanced monitoring configuration

---

### 8. Compliance & Security

**Scenario**: Security audit and compliance check

```
> "Perform a security scan of all Python dependencies and identify any vulnerabilities"
> "Review the Docker container configurations for security best practices"
> "Check the API endpoints for proper authentication and authorization"
> "Generate a security compliance report with findings and remediation steps"
> "Create a security checklist for future development"
```

**Expected Outcomes:**
- Vulnerability assessment with specific CVEs
- Container security configuration review
- API security analysis
- Compliance report with actionable items
- Security development guidelines

---

### 9. Data Processing & Analysis

**Scenario**: Extract and analyze project data

```
> "Extract all configuration values from the various .env files and create a configuration reference"
> "Analyze the git history to understand development patterns and major milestones"
> "Generate a metrics report showing project growth, code changes, and development velocity"
> "Create an Excel dashboard showing container performance over time"
> "Export all documentation content for external review or publication"
```

**Expected Outcomes:**
- Centralized configuration documentation
- Development pattern analysis
- Project metrics and growth visualization
- Interactive performance dashboard
- Portable documentation export

---

### 10. Integration & Migration

**Scenario**: System integration or migration planning

```
> "Analyze the current MCP server setup to understand integration points for external services"
> "Review the data models and suggest optimizations for better scalability"
> "Generate a migration plan for moving to a new infrastructure setup"
> "Create integration tests for verifying external service connectivity"
> "Document the integration requirements and deployment procedures"
```

**Expected Outcomes:**
- Integration architecture analysis
- Data model optimization recommendations
- Detailed migration strategy
- Comprehensive integration test suite
- Integration deployment documentation

---

## 🎯 Command Patterns for Different Scenarios

### Analysis Commands
```
"Analyze [component] for [specific criteria]"
"Review [system] and identify [issues/opportunities]" 
"Compare [current state] with [best practices]"
"Examine [data] and extract [insights]"
```

### Generation Commands
```
"Create [document/report] with [information from sources]"
"Generate [code/tests/documentation] for [specific purpose]"
"Build [tool/configuration] that [performs function]"
"Export [data] to [format] with [specifications]"
```

### Monitoring Commands
```
"Monitor [system] and alert on [conditions]"
"Track [metrics] and generate [reports]"
"Watch [services] and report [status]"
"Analyze [logs] for [patterns/issues]"
```

### Workflow Commands
```
"First [step 1], then [step 2], finally [step 3]"
"While [condition], [action], when [trigger], [alternative]"
"If [issue detected], then [remediate], else [continue monitoring]"
"Until [goal achieved], [iterate with improvements]"
```

---

## 🔄 Multi-Step Workflow Examples

### Complete Development Cycle
```
Step 1: Project Understanding
> "Analyze the current codebase and identify the main architectural components"
> "Review the existing tests and documentation for completeness"

Step 2: Feature Planning  
> "Based on the architecture, suggest where to add a new data validation tool"
> "Create a development plan with timeline and resource estimates"

Step 3: Implementation
> "Generate a template for the new validation tool with proper error handling"
> "Create comprehensive unit tests for the new functionality"
> "Update the project documentation to include the new tool"

Step 4: Validation
> "Run the test suite and verify everything works correctly"
> "Generate a final implementation report with deployment instructions"
```

### System Health Maintenance
```
Step 1: Status Check
> "Check the health status of all Docker containers"
> "Monitor system resources and identify any performance issues"

Step 2: Issue Resolution
> "For any failed services, attempt automatic recovery"
> "Analyze logs for root causes of any issues found"

Step 3: Prevention
> "Set up enhanced monitoring for identified weak points"
> "Generate a maintenance schedule with preventive actions"

Step 4: Reporting
> "Create a comprehensive health report with current status and recommendations"
> "Export the report as PDF for team distribution"
```

### Documentation Update Cycle
```
Step 1: Content Audit
> "Review all existing documentation for accuracy and completeness"
> "Identify areas that need updates based on recent changes"

Step 2: Content Generation
> "Generate API documentation from current source code"
> "Update user guides with new features and capabilities"

Step 3: Quality Assurance
> "Review generated documentation for accuracy and consistency"
> "Create cross-references and navigation aids"

Step 4: Publication
> "Export documentation in multiple formats (PDF, HTML, etc.)"
> "Generate a documentation change log and distribution plan"
```

---

## 💡 Pro Tips for Complex Scenarios

### 1. Start Broad, Then Narrow
```
❌ "Fix the WebSocket performance issue"
✅ "First analyze the overall system performance, then focus on WebSocket connections specifically"
```

### 2. Leverage Mini Agent's Context
```
✅ Reference your specific setup:
> "Check the exai-mcp-stdio container specifically"
> "Analyze the MCP tools in our 29-tool configuration"
> "Review our dual-protocol WebSocket + MCP setup"
```

### 3. Use Iterative Refinement
```
Start: > "Analyze our project architecture"
Then: > "Focus on the performance aspects you mentioned"
Finally: > "Create specific optimization recommendations"
```

### 4. Chain Related Operations
```
✅ Complex Workflow:
> "Check Docker status, analyze any issues, generate fixes, update monitoring, create report"
```

### 5. Request Specific Outputs
```
✅ Output-Specific Commands:
> "Create a PDF report suitable for management review"
> "Generate an Excel dashboard for technical team"
> "Build a PowerPoint presentation for stakeholder briefing"
```

---

*These examples demonstrate the full power and flexibility of Mini Agent CLI. Adapt these patterns to your specific needs and project requirements.*