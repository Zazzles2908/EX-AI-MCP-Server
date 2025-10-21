# tracer_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [debug.md](debug.md)

---



**Purpose:** Code tracing and dependency mapping through systematic investigation

**Description:**
The `tracer` tool provides comprehensive code tracing capabilities for understanding execution flows and dependency relationships. This workflow tool guides the AI client through systematic investigation of call chains, usage patterns, and structural dependencies.

**Use Cases:**
- Method execution flow analysis and call chain tracing
- Dependency mapping and structural relationship analysis
- Call chain tracing for debugging and understanding
- Architectural understanding and component relationships
- Code comprehension for unfamiliar codebases
- Impact analysis for code changes

**Key Features:**
- **Two analysis modes**: precision (execution flow) and dependencies (structural relationships)
- **Systematic investigation** with step-by-step evidence collection
- **Call chain analysis**: Where methods are defined, called, and how they flow
- **Execution flow mapping**: Step-by-step execution paths with branching
- **Usage pattern analysis**: Frequency, context, parameter patterns
- **Dependency mapping**: Bidirectional dependencies and coupling analysis
- **Image support**: Analyze visual call flow diagrams, sequence diagrams
- **Multi-language support**: Works with any programming language

**Trace Modes:**

**`precision` Mode** - For methods/functions:
- Traces execution flow, call chains, and usage patterns
- Detailed branching analysis and side effects
- Shows when and how functions are called throughout the system
- Call hierarchy and depth analysis
- Return value usage and parameter passing patterns

**`dependencies` Mode** - For classes/modules/protocols:
- Maps bidirectional dependencies and structural relationships
- Identifies coupling and architectural dependencies
- Shows how components interact and depend on each other
- Inheritance hierarchies and protocol conformance
- Module-level dependency graphs

**`ask` Mode** - Interactive mode:
- Prompts you to choose between precision or dependencies
- Provides guidance on which mode is appropriate
- Explains trade-offs between modes

**Key Parameters:**

*Workflow Investigation Parameters:*
- `step` (required): Current tracing step description
- `step_number` (required): Current step number in tracing sequence
- `total_steps` (required): Estimated total investigation steps
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Discoveries about execution flow or dependencies
- `target_description` (required): What to trace and WHY you need this analysis
- `trace_mode` (required): precision|dependencies|ask
- `files_checked` (optional): All files examined during investigation
- `relevant_files` (optional): Files directly relevant to the trace
- `relevant_context` (optional): Methods/functions/classes involved
- `confidence` (optional): Confidence level in trace completeness
- `images` (optional): Visual references (call flow diagrams, sequence diagrams)

*Model Selection:*
- `model` (optional): Model to use (default: auto)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)

**Workflow:**
1. **Step 1**: Describe what to trace and WHY (context is critical!)
2. **STOP** - Investigate code structure, call chains, dependencies
3. **Step 2+**: Report findings with concrete evidence
4. **Throughout**: Track findings, relevant files, execution paths
5. **Completion**: Once trace is comprehensive, signal completion
6. **Expert Analysis**: Receive detailed trace analysis

**Usage Examples:**

*Method Execution Tracing:*
```
"Trace how UserAuthManager.authenticate is used throughout the system"
```

*Class Dependency Mapping:*
```
"Generate a dependency trace for the PaymentProcessor class to understand its relationships"
```

*With Visual Context:*
```
"Trace the authentication flow using this sequence diagram to validate the implementation"
```

*Complex System Analysis:*
```
"Trace how OrderProcessor.processPayment flows through the entire system including all side effects"
```

**Best Practices:**
- **Provide context** - Explain WHY you need the trace (debugging, refactoring, understanding)
- **Be specific** - Target specific methods/classes rather than entire modules
- **Choose appropriate mode** - Use precision for execution flow, dependencies for structure
- **Include visual context** - Sequence diagrams or call flow charts help validate findings
- **Explain the goal** - Understanding, debugging, impact analysis, or refactoring planning

**When to Use:**
- Use `tracer` for: Understanding execution flow and dependencies
- Use `analyze` for: General code structure understanding
- Use `debug` for: Diagnosing specific runtime errors
- Use `codereview` for: Finding bugs and security issues