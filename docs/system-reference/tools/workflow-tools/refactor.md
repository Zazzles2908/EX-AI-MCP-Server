# refactor_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [debug.md](debug.md)

---



**Purpose:** Intelligent code refactoring with top-down decomposition

**Description:**
The `refactor` tool provides intelligent code refactoring recommendations with a focus on top-down decomposition and systematic code improvement. This workflow tool enforces systematic investigation of code smells, decomposition opportunities, and modernization possibilities with precise implementation guidance.

**Use Cases:**
- Comprehensive refactoring analysis with prioritization
- Code smell detection and anti-pattern identification
- Decomposition planning for large files/classes/functions
- Modernization opportunities (language features, patterns)
- Organization improvements and structure optimization
- Maintainability enhancements and complexity reduction

**Key Features:**
- **Intelligent prioritization** - Refuses low-priority work if critical decomposition needed first
- **Top-down decomposition strategy** - Analyzes file → class → function levels systematically
- **Four refactor types**: codesmells, decompose, modernize, organization
- **Precise line-number references** - Exact line numbers for implementation
- **Language-specific guidance** - Tailored suggestions for each language
- **Style guide integration** - Uses existing project files as pattern references
- **Conservative approach** - Careful dependency analysis to prevent breaking changes
- **Multi-file analysis** - Understands cross-file relationships and dependencies
- **Priority sequencing** - Recommends implementation order for changes
- **Image support**: Analyze architecture diagrams, legacy system charts

**Refactor Types (Progressive Priority System):**

**1. `decompose` (CRITICAL PRIORITY)** - Context-aware decomposition:
- **AUTOMATIC decomposition** (CRITICAL severity - blocks all other refactoring):
  - Files >15,000 LOC, Classes >3,000 LOC, Functions >500 LOC
- **EVALUATE decomposition** (contextual severity - intelligent assessment):
  - Files >5,000 LOC, Classes >1,000 LOC, Functions >150 LOC
  - Only recommends if genuinely improves maintainability
  - Respects legacy stability, domain complexity, performance constraints

**2. `codesmells`** - Applied only after decomposition complete:
- Long methods, complex conditionals, duplicate code, magic numbers, poor naming

**3. `modernize`** - Applied only after decomposition complete:
- Update to modern language features (f-strings, async/await, etc.)

**4. `organization`** - Applied only after decomposition complete:
- Improve logical grouping, separation of concerns, module structure

**Key Parameters:**

*Workflow Investigation Parameters:*
- `step` (required): Current investigation step description
- `step_number` (required): Current step number in refactoring sequence
- `total_steps` (required): Estimated total investigation steps (adjustable)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Discoveries and refactoring opportunities in this step
- `files_checked` (optional): All files examined during investigation
- `relevant_files` (required in step 1): Files directly needing refactoring (absolute paths)
- `relevant_context` (optional): Methods/functions/classes requiring refactoring
- `issues_found` (optional): Refactoring opportunities with severity and type
- `confidence` (optional): Confidence level (exploring, incomplete, partial, complete)
- `backtrack_from_step` (optional): Step number to backtrack from

*Initial Configuration:*
- `model` (optional): Model to use (default: auto)
- `refactor_type` (optional): codesmells|decompose|modernize|organization (default: codesmells)
- `style_guide_examples` (optional): Existing code files as style reference (absolute paths)
- `temperature` (optional): Temperature (0-1, default: 0.2)
- `thinking_mode` (optional): Thinking depth (default: medium)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)

**Workflow:**
1. **Step 1**: Describe refactoring plan and pass files in `relevant_files`
2. **STOP** - Investigate code smells, decomposition needs, modernization opportunities
3. **Step 2+**: Report findings with evidence and precise line numbers
4. **Throughout**: Track findings, opportunities, confidence levels
5. **Completion**: Once investigation is thorough, signal completion
6. **Expert Analysis**: Receive refactoring recommendations (unless confidence=complete)

**Usage Examples:**

*Decompose Large Class:*
```
"Decompose my_crazy_big_class.m into smaller, maintainable extensions"
```

*Code Smell Detection:*
```
"Find code smells in the authentication module and suggest improvements"
```

*Modernization:*
```
"Modernize legacy_code.py to use current Python best practices and features"
```

**Best Practices:**
- Start with decomposition for large files/classes
- Provide style guide examples for consistency
- Use conservative approach for legacy code
- Consider dependencies before refactoring
- Implement changes in recommended order

**When to Use:**
- Use `refactor` for: Getting specific refactoring recommendations and implementation plans
- Use `codereview` for: Finding bugs and security issues
- Use `analyze` for: Understanding code structure without refactoring
- Use `debug` for: Diagnosing specific errors