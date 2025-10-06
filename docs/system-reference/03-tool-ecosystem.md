# Tool Ecosystem Overview

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [01-system-overview.md](01-system-overview.md), [04-features-and-capabilities.md](04-features-and-capabilities.md)

---

## Overview

The EX-AI-MCP-Server provides a comprehensive tool ecosystem designed for agentic AI workflows. Tools are organized into three categories: **Simple Tools** (request/response), **Workflow Tools** (multi-step investigation), and **Utility Tools** (system information).

---

## Tool Categories

### Simple Tools (Request/Response)

Quick, single-call tools for conversations, planning, and analysis:

- **[chat](tools/simple-tools/chat.md)** - Collaborative thinking partner for development conversations
- **[thinkdeep](tools/simple-tools/thinkdeep.md)** - Extended reasoning partner to challenge assumptions
- **[planner](tools/simple-tools/planner.md)** - Sequential step-by-step planning with branching
- **[consensus](tools/simple-tools/consensus.md)** - Multi-model consensus workflow for complex decisions
- **[challenge](tools/simple-tools/challenge.md)** - Critical analysis and truth-seeking

### Workflow Tools (Multi-Step Investigation)

Systematic investigation tools with pause enforcement between steps:

- **[analyze](tools/workflow-tools/analyze.md)** - Smart file analysis and code understanding
- **[debug](tools/workflow-tools/debug.md)** - Systematic investigation & expert debugging
- **[codereview](tools/workflow-tools/codereview.md)** - Professional code review with prioritized feedback
- **[refactor](tools/workflow-tools/refactor.md)** - Intelligent refactoring with top-down decomposition
- **[testgen](tools/workflow-tools/testgen.md)** - Comprehensive test generation with edge case coverage
- **[tracer](tools/workflow-tools/tracer.md)** - Code tracing and dependency mapping
- **[secaudit](tools/workflow-tools/secaudit.md)** - Comprehensive security audit with OWASP assessment
- **[docgen](tools/workflow-tools/docgen.md)** - Documentation generation with complexity analysis
- **[precommit](tools/workflow-tools/precommit.md)** - Pre-commit validation and change analysis

### Utility Tools

System information and diagnostics:

- **[listmodels](tools/simple-tools/listmodels.md)** - Display all available AI models by provider
- **[version](tools/simple-tools/version.md)** - Server version, configuration, and tool listing

---

## Tool Selection Guide

### For Understanding Code
- **New codebase?** → Use [analyze](tools/workflow-tools/analyze.md) for comprehensive exploration
- **Specific function?** → Use [tracer](tools/workflow-tools/tracer.md) to map execution flow
- **Architecture review?** → Use [analyze](tools/workflow-tools/analyze.md) with `analysis_type: architecture`

### For Finding Issues
- **Runtime error?** → Use [debug](tools/workflow-tools/debug.md) for systematic investigation
- **Code quality?** → Use [codereview](tools/workflow-tools/codereview.md) for comprehensive review
- **Security concerns?** → Use [secaudit](tools/workflow-tools/secaudit.md) for OWASP assessment
- **Before commit?** → Use [precommit](tools/workflow-tools/precommit.md) to validate changes

### For Improving Code
- **Need refactoring?** → Use [refactor](tools/workflow-tools/refactor.md) for decomposition analysis
- **Missing tests?** → Use [testgen](tools/workflow-tools/testgen.md) for comprehensive test generation
- **No documentation?** → Use [docgen](tools/workflow-tools/docgen.md) for automated docs

### For Planning & Discussion
- **Brainstorming?** → Use [chat](tools/simple-tools/chat.md) for open-ended discussions
- **Complex decision?** → Use [consensus](tools/simple-tools/consensus.md) for multi-model perspectives
- **Need deeper analysis?** → Use [thinkdeep](tools/simple-tools/thinkdeep.md) to challenge assumptions
- **Breaking down tasks?** → Use [planner](tools/simple-tools/planner.md) for step-by-step planning

---

## Agentic Enhancements (Phase 1)

All workflow tools support agentic capabilities:

### Self-Assessment
- Evaluate information sufficiency at each step
- Determine if enough evidence has been gathered
- Decide when to proceed vs. continue investigation

### Early Termination
- Stop investigation when goals are achieved
- Avoid unnecessary steps when confidence is high
- Configurable confidence thresholds

### Dynamic Step Adjustment
- Adjust total_steps mid-workflow as understanding evolves
- Add or remove steps based on findings
- Backtrack to revise previous steps when new insights emerge

### Configurable Sufficiency Thresholds
- Set minimum confidence levels for completion
- Customize investigation depth per use case
- Balance thoroughness vs. efficiency

---

## Common Parameters

### Workflow Tools
All workflow tools share these parameters:
- `step` (required): Current investigation step description
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Estimated total steps (adjustable)
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Discoveries and evidence from this step
- `confidence` (optional): Confidence level (exploring → certain)
- `continuation_id` (optional): Continue previous investigations

### Model Selection
All tools support:
- `model` (optional): Model to use (default: auto)
- `thinking_mode` (optional): Thinking depth (minimal|low|medium|high|max)
- `temperature` (optional): Response creativity (0-1)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)

---

## Best Practices

### Choosing the Right Tool
1. **Start with the most specific tool** - Use specialized tools (debug, codereview, secaudit) over general ones (analyze)
2. **Consider investigation depth** - Workflow tools for thorough analysis, simple tools for quick answers
3. **Leverage continuation** - Build on previous investigations with `continuation_id`
4. **Use appropriate models** - Large context models (Kimi) for comprehensive analysis, fast models (GLM-4.5-flash) for quick tasks

### Workflow Tool Usage
1. **Be thorough in step 1** - Clearly describe investigation plan and objectives
2. **Track all evidence** - Document findings, files checked, methods examined
3. **Evolve hypotheses** - Update theories as investigation progresses
4. **Use backtracking** - Revise previous steps when new insights emerge
5. **Signal completion** - Set `next_step_required: false` when investigation is complete

### File References
- **Always use absolute paths** - Relative paths may fail
- **Include relevant files** - Provide context for better analysis
- **Use images when helpful** - Screenshots, diagrams, error messages

---

## Related Documentation

- [01-system-overview.md](01-system-overview.md) - System architecture and components
- [02-provider-architecture.md](02-provider-architecture.md) - GLM and Kimi provider details
- [04-features-and-capabilities.md](04-features-and-capabilities.md) - Streaming, web search, multimodal
- [05-api-endpoints-reference.md](05-api-endpoints-reference.md) - API endpoints and authentication
- [06-deployment-guide.md](06-deployment-guide.md) - Installation and configuration
- [07-upgrade-roadmap.md](07-upgrade-roadmap.md) - Upgrade project status

---

## Quick Reference

| Need | Tool | Category |
|------|------|----------|
| Understand code | [analyze](tools/workflow-tools/analyze.md) | Workflow |
| Fix bug | [debug](tools/workflow-tools/debug.md) | Workflow |
| Review code | [codereview](tools/workflow-tools/codereview.md) | Workflow |
| Refactor code | [refactor](tools/workflow-tools/refactor.md) | Workflow |
| Generate tests | [testgen](tools/workflow-tools/testgen.md) | Workflow |
| Trace execution | [tracer](tools/workflow-tools/tracer.md) | Workflow |
| Security audit | [secaudit](tools/workflow-tools/secaudit.md) | Workflow |
| Generate docs | [docgen](tools/workflow-tools/docgen.md) | Workflow |
| Validate changes | [precommit](tools/workflow-tools/precommit.md) | Workflow |
| Brainstorm | [chat](tools/simple-tools/chat.md) | Simple |
| Deep analysis | [thinkdeep](tools/simple-tools/thinkdeep.md) | Simple |
| Plan tasks | [planner](tools/simple-tools/planner.md) | Simple |
| Get consensus | [consensus](tools/simple-tools/consensus.md) | Simple |
| Critical analysis | [challenge](tools/simple-tools/challenge.md) | Simple |
| List models | [listmodels](tools/simple-tools/listmodels.md) | Utility |
| Check version | [version](tools/simple-tools/version.md) | Utility |

