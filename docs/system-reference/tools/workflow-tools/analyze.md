# analyze_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [debug.md](debug.md), [codereview.md](codereview.md), [refactor.md](refactor.md)

---

## Purpose

Smart file analysis - general-purpose code understanding and exploration

---

## Description

The `analyze` tool provides comprehensive code analysis and understanding capabilities through workflow-driven investigation. It helps you explore codebases, understand architecture, and identify patterns across files and directories. The tool guides the AI client through systematic investigation of code structure, patterns, and architectural decisions before providing expert analysis.

---

## Use Cases

- Analyze single files or entire directories
- Architectural assessment and system-level design
- Performance evaluation and bottleneck identification
- Security analysis and vulnerability assessment
- Code quality and maintainability review
- Pattern detection and anti-pattern identification
- Strategic planning and improvement recommendations

---

## Key Features

- **Analyzes single files or entire directories** with intelligent file filtering
- **Specialized analysis types**: architecture, performance, security, quality, general
- **Large codebase support**: Handle massive codebases with 200K+ token context models
- **Cross-file relationship mapping**: Understand dependencies and interactions
- **Architecture visualization**: Describe system structure and component relationships
- **Image support**: Analyze architecture diagrams, UML charts, flowcharts
- **Web search capability**: Enhance analysis with current documentation and best practices
- **Pattern recognition**: Identify design patterns, anti-patterns, and refactoring opportunities

---

## Key Parameters

### Workflow Investigation Parameters
- `step` (required): Current investigation step description
- `step_number` (required): Current step number in analysis sequence
- `total_steps` (required): Estimated total investigation steps (adjustable)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Discoveries and insights collected in this step
- `files_checked` (optional): All files examined during investigation
- `relevant_files` (required in step 1): Files directly relevant to the analysis (absolute paths)
- `relevant_context` (optional): Methods/functions/classes central to analysis findings
- `issues_found` (optional): Issues or concerns identified with severity levels
- `confidence` (optional): Confidence level (exploring, low, medium, high, very_high, almost_certain, certain)
- `backtrack_from_step` (optional): Step number to backtrack from (for revisions)
- `images` (optional): Visual references for analysis context

### Initial Configuration
- `model` (optional): Model to use (default: auto)
- `analysis_type` (optional): architecture|performance|security|quality|general (default: general)
- `output_format` (optional): summary|detailed|actionable (default: detailed)
- `temperature` (optional): Temperature for analysis (0-1, default: 0.2)
- `thinking_mode` (optional): Thinking depth - minimal|low|medium|high|max (default: medium)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)
- `continuation_id` (optional): Continue previous analysis sessions

---

## Workflow

1. **Step 1**: AI client describes analysis plan and begins examining code structure
2. **STOP** - Investigate architecture, patterns, dependencies, design decisions
3. **Step 2+**: Report findings with evidence from code examination
4. **Throughout**: Track findings, relevant files, insights, confidence levels
5. **Completion**: Once analysis is comprehensive, signal completion
6. **Expert Analysis**: Receive comprehensive analysis summary (unless confidence=certain)

---

## Analysis Types

- **General Analysis (default)**: Overall code structure, key components, data flow, design patterns
- **Architecture Analysis**: System-level design, module dependencies, separation of concerns, scalability
- **Performance Analysis**: Bottlenecks, algorithmic complexity, memory usage, I/O efficiency
- **Security Analysis**: Security patterns, vulnerabilities, input validation, authentication mechanisms
- **Quality Analysis**: Code quality metrics, testing coverage, documentation, best practices

---

## Usage Examples

### Single File Analysis
```
"Analyze user_controller.py to understand the authentication flow"
```

### Directory Architecture Analysis
```
"Analyze the src/ directory architecture and identify the main components"
```

### Performance-Focused Analysis
```
"Analyze backend/api/ for performance bottlenecks, focus on database queries"
```

### Large Codebase Analysis
```
"Analyze the entire project structure to understand how all components work together"
```

---

## Best Practices

- Be specific about goals - clearly state what you want to understand or discover
- Use appropriate analysis types - choose the type that matches your needs
- Include related files - analyze modules together for better context understanding
- Leverage large context models - use Kimi for comprehensive codebase analysis
- Combine with visual context - include architecture diagrams or documentation
- Use continuation - build on previous analysis for deeper understanding

---

## When to Use

- **Use `analyze` for:** Understanding code structure, exploring unfamiliar codebases, architecture assessment
- **Use `codereview` for:** Finding bugs and security issues with actionable fixes
- **Use `debug` for:** Diagnosing specific runtime errors or performance problems
- **Use `refactor` for:** Getting specific refactoring recommendations and implementation plans

---

## Related Tools

- [debug.md](debug.md) - Root cause analysis and debugging
- [codereview.md](codereview.md) - Professional code review
- [refactor.md](refactor.md) - Intelligent refactoring analysis
- [tracer.md](tracer.md) - Code tracing and dependency mapping

