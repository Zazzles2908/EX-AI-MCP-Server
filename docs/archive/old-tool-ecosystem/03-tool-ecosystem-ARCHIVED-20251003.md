# Tool Ecosystem

**Version:** 1.1
**Last Updated:** 2025-10-03
**Related:** `01-system-overview.md`, `docs/guides/tool-selection-guide.md`, `docs/current/tools/`

---

## Overview

The EX-AI-MCP-Server provides a comprehensive **tool ecosystem** with two categories of tools: **Simple Tools** (request/response) and **Workflow Tools** (multi-step with pause enforcement). All workflow tools include **agentic enhancements** for self-assessment, early termination, and dynamic step adjustment.

**Key Capabilities:**
- **Multi-model support**: Use GLM (Z.ai), Kimi (Moonshot), or auto-selection
- **Web search integration**: Provider-native web browsing for current documentation
- **File and image context**: Absolute paths for code files and visual references
- **Conversation threading**: Continue investigations across sessions with `continuation_id`
- **Thinking modes**: Adjustable reasoning depth (minimal, low, medium, high, max)
- **Large context support**: Handle extensive codebases with 200K+ token models

---

## Tool Categories

### Simple Tools (Request/Response)

**Characteristics:**
- Single request/response cycle
- No multi-step workflow
- Immediate results
- No pause enforcement
- Optional web search and file context

**Available Tools:**
- `chat` - General conversation and collaborative thinking
- `thinkdeep` - Multi-stage investigation with expert validation
- `planner` - Sequential step-by-step planning
- `consensus` - Multi-model consensus workflow
- `challenge` - Critical analysis and truth-seeking
- `listmodels` - Display available models and capabilities
- `version` - Server version and configuration

### Workflow Tools (Multi-Step with Pause Enforcement)

**Characteristics:**
- Multi-step investigation process
- **Mandatory pause enforcement** between steps (no recursive calls)
- Agentic enhancements (self-assessment, early termination, dynamic steps)
- Structured findings and evidence tracking
- Optional expert analysis phase (can be disabled with `use_assistant_model=false`)

**Available Tools:**
- `analyze` - Comprehensive code analysis and architectural assessment
- `debug` - Root cause analysis and systematic debugging
- `codereview` - Professional code review with severity-based prioritization
- `precommit` - Pre-commit validation and change impact assessment
- `refactor` - Intelligent refactoring with top-down decomposition
- `testgen` - Comprehensive test generation with edge case coverage
- `tracer` - Code tracing and dependency mapping
- `secaudit` - Security audit and vulnerability assessment
- `docgen` - Documentation generation with complexity analysis

---

## Simple Tools

### chat_EXAI-WS

**Purpose:** Your collaborative thinking partner for development conversations

**Description:**
The `chat` tool is designed to help you brainstorm, validate ideas, get second opinions, and explore alternatives in a conversational format. It's your thinking partner for bouncing ideas, getting expert opinions, and collaborative problem-solving.

**Use Cases:**
- Collaborative thinking partner for analysis and planning
- Get second opinions on designs and approaches
- Brainstorm solutions and explore alternatives
- Validate checklists and implementation plans
- General development questions and explanations
- Technology comparisons and best practices
- Architecture and design discussions

**Key Features:**
- **File reference support**: Include code files for context-aware discussions
- **Image support**: Screenshots, diagrams, UI mockups for visual analysis
- **Dynamic collaboration**: Can request additional files or context during conversation
- **Web search capability**: Analyzes when web searches would be helpful and recommends specific searches

**Key Parameters:**
- `prompt` (required): Your question or discussion topic
- `model` (optional): auto|kimi-k2-0905-preview|glm-4.5|glm-4.5-flash (default: auto)
- `use_websearch` (optional): Enable web search (default: true)
- `temperature` (optional): Response creativity (0-1, default: 0.5)
- `thinking_mode` (optional): Thinking depth - minimal|low|medium|high|max (default: medium)
- `files` (optional): Files for context (absolute paths)
- `images` (optional): Images for visual context (absolute paths or base64)
- `continuation_id` (optional): Continue previous conversations

**Usage Examples:**

*Basic Development Chat:*
```
"Chat about the best approach for user authentication in my React app"
```

*Technology Comparison:*
```
"Discuss whether PostgreSQL or MongoDB would be better for my e-commerce platform"
```

*File Context Analysis:*
```
"Chat about the current authentication implementation in auth.py and suggest improvements"
```

*Visual Analysis:*
```
"Chat about this UI mockup screenshot - is the user flow intuitive?"
```

**Best Practices:**
- Be specific about context - include relevant files or describe your project scope
- Ask for trade-offs - request pros/cons for better decision-making
- Use conversation continuation - build on previous discussions with `continuation_id`
- Leverage visual context - include diagrams, mockups, or screenshots when discussing UI/UX
- Request web searches - ask for current best practices or recent developments

**When to Use:**
- Use `chat` for: Open-ended discussions, brainstorming, second opinions, technology comparisons
- Use `thinkdeep` for: Extending specific analysis, challenging assumptions, deeper reasoning
- Use `analyze` for: Understanding existing code structure and patterns
- Use `debug` for: Specific error diagnosis and troubleshooting

---

### thinkdeep_EXAI-WS

**Purpose:** Extended reasoning partner - get a second opinion to challenge assumptions

**Description:**
The `thinkdeep` tool provides extended reasoning capabilities, offering a second perspective to the AI client's analysis. It's designed to challenge assumptions, find edge cases, and provide alternative approaches to complex problems through multi-stage investigation.

**Use Cases:**
- Complex problem analysis with systematic investigation
- Architecture decisions requiring deep validation
- Performance challenges needing thorough analysis
- Security analysis with comprehensive threat modeling
- Systematic hypothesis testing and validation
- Expert validation of design patterns

**Key Features:**
- **Multi-stage workflow** with structured investigation steps
- **Provides second opinion** on AI client's analysis
- **Challenges assumptions** and identifies edge cases
- **Offers alternative perspectives** and approaches
- **Validates architectural decisions** and design patterns
- **File reference support**: Include code files for context
- **Image support**: Analyze architectural diagrams, flowcharts, design mockups
- **Web search capability**: Identifies areas where current documentation would strengthen analysis

**Key Parameters:**
- `step` (required): Current investigation step description
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Estimated total steps needed
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Important findings and evidence from this step
- `hypothesis` (optional): Current theory about the issue/goal
- `confidence` (optional): Confidence level (exploring, low, medium, high, very_high, almost_certain, certain)
- `model` (optional): Model to use (default: auto)
- `thinking_mode` (optional): Thinking depth - minimal|low|medium|high|max (default: high)
- `problem_context` (optional): Additional context about the problem or goal
- `focus_areas` (optional): Specific aspects to focus on (architecture, performance, security, etc.)
- `files` (optional): File paths for additional context (absolute paths)
- `images` (optional): Images for visual analysis (absolute paths)
- `use_websearch` (optional): Enable web search (default: true)
- `continuation_id` (optional): Continue previous investigations

**Workflow:**
1. **Step 1**: Describe investigation plan and begin forming systematic approach
2. **STOP** - Investigate using appropriate tools
3. **Step 2+**: Report findings with concrete evidence
4. **Continue** until investigation complete
5. **Expert Analysis**: Receive comprehensive analysis based on all findings

**Usage Examples:**

*Architecture Design:*
```
"Think deeper about my microservices authentication strategy using max thinking mode"
```

*With File Context:*
```
"Think deeper about my API design with reference to api/routes.py and models/user.py"
```

*Visual Analysis:*
```
"Think deeper about this system architecture diagram - identify potential bottlenecks"
```

*Problem Solving:*
```
"I'm considering using GraphQL vs REST for my API. Think deeper about the trade-offs using high thinking mode"
```

**Best Practices:**
- Provide detailed context - share your current thinking, constraints, and objectives
- Be specific about focus areas - mention what aspects need deeper analysis
- Include relevant files - reference code, documentation, or configuration files
- Use appropriate thinking modes - higher modes for complex problems, lower for quick validations
- Leverage visual context - include diagrams or mockups for architectural discussions
- Build on discussions - use continuation to extend previous analyses

**When to Use:**
- Use `thinkdeep` for: Extending specific analysis, challenging assumptions, architectural decisions
- Use `chat` for: Open-ended brainstorming and general discussions
- Use `analyze` for: Understanding existing code without extending analysis
- Use `codereview` for: Finding specific bugs and security issues

---

### planner_EXAI-WS

**Purpose:** Sequential step-by-step planning

**Use Cases:**
- Breaking down complex tasks
- Project planning
- Implementation roadmaps
- Task sequencing
- Dependency mapping

**Key Parameters:**
- `step` (required): Current planning step
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether another step is needed
- `is_step_revision` (optional): True if revising a previous step
- `revises_step_number` (optional): Which step is being revised
- `is_branch_point` (optional): True if branching from a previous step
- `branch_from_step` (optional): Which step is the branching point
- `branch_id` (optional): Identifier for the current branch

**Features:**
- Sequential thinking
- Deep reflection for complex plans
- Branching into alternative approaches
- Revisions of previous steps
- Dynamic step adjustment

**Example:**
```json
{
  "step": "Outline goals and constraints for zai-sdk upgrade",
  "step_number": 1,
  "total_steps": 5,
  "next_step_required": true
}
```

---

### consensus_EXAI-WS

**Purpose:** Multi-model consensus workflow

**Use Cases:**
- Complex decisions
- Architectural choices
- Feature proposals
- Technology evaluations
- Strategic planning

**Key Parameters:**
- `step` (required): Current consensus step
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Total steps (equals number of models)
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings from this step
- `models` (required): List of model configurations to consult

**Workflow:**
1. Step 1: Provide your own neutral analysis
2. Tool consults each model one by one
3. Track and synthesize perspectives
4. Final step: Present comprehensive consensus

**Example:**
```json
{
  "step": "Should we build a search component in SwiftUI for use in an AppKit app?",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Initial analysis suggests SwiftUI integration is feasible but has trade-offs",
  "models": [
    {"model": "kimi-k2-0905-preview", "stance": "for"},
    {"model": "glm-4.6", "stance": "against"},
    {"model": "kimi-k2-0905-preview", "stance": "neutral"}
  ]
}
```

---

### challenge_EXAI-WS

**Purpose:** Critical analysis and truth-seeking

**Use Cases:**
- Preventing reflexive agreement
- Critical evaluation
- Truth verification
- Assumption challenging
- Reasoning validation

**Key Parameters:**
- `prompt` (required): The user's message to analyze critically

**Automatic Invocation:**
Automatically triggered when user:
- Questions or disagrees with previous statements
- Challenges assumptions
- Expresses confusion
- Believes an error was made
- Seeks justification

**Example:**
```json
{
  "prompt": "But I don't think that approach will work because..."
}
```

---

## Workflow Tools

### analyze_EXAI-WS

**Purpose:** Smart file analysis - general-purpose code understanding and exploration

**Description:**
The `analyze` tool provides comprehensive code analysis and understanding capabilities through workflow-driven investigation. It helps you explore codebases, understand architecture, and identify patterns across files and directories. The tool guides the AI client through systematic investigation of code structure, patterns, and architectural decisions before providing expert analysis.

**Use Cases:**
- Analyze single files or entire directories
- Architectural assessment and system-level design
- Performance evaluation and bottleneck identification
- Security analysis and vulnerability assessment
- Code quality and maintainability review
- Pattern detection and anti-pattern identification
- Strategic planning and improvement recommendations

**Key Features:**
- **Analyzes single files or entire directories** with intelligent file filtering
- **Specialized analysis types**: architecture, performance, security, quality, general
- **Large codebase support**: Handle massive codebases with 200K+ token context models
- **Cross-file relationship mapping**: Understand dependencies and interactions
- **Architecture visualization**: Describe system structure and component relationships
- **Image support**: Analyze architecture diagrams, UML charts, flowcharts
- **Web search capability**: Enhance analysis with current documentation and best practices
- **Pattern recognition**: Identify design patterns, anti-patterns, and refactoring opportunities

**Key Parameters:**

*Workflow Investigation Parameters (used during step-by-step process):*
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

*Initial Configuration (used in step 1):*
- `model` (optional): Model to use (default: auto)
- `analysis_type` (optional): architecture|performance|security|quality|general (default: general)
- `output_format` (optional): summary|detailed|actionable (default: detailed)
- `temperature` (optional): Temperature for analysis (0-1, default: 0.2)
- `thinking_mode` (optional): Thinking depth - minimal|low|medium|high|max (default: medium)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true, set false for client-only)
- `continuation_id` (optional): Continue previous analysis sessions

**Workflow:**
1. **Step 1**: AI client describes analysis plan and begins examining code structure
2. **STOP** - Investigate architecture, patterns, dependencies, design decisions
3. **Step 2+**: Report findings with evidence from code examination
4. **Throughout**: Track findings, relevant files, insights, confidence levels
5. **Completion**: Once analysis is comprehensive, signal completion
6. **Expert Analysis**: Receive comprehensive analysis summary (unless confidence=certain)

**Analysis Types:**

- **General Analysis (default)**: Overall code structure, key components, data flow, design patterns
- **Architecture Analysis**: System-level design, module dependencies, separation of concerns, scalability
- **Performance Analysis**: Bottlenecks, algorithmic complexity, memory usage, I/O efficiency
- **Security Analysis**: Security patterns, vulnerabilities, input validation, authentication mechanisms
- **Quality Analysis**: Code quality metrics, testing coverage, documentation, best practices

**Usage Examples:**

*Single File Analysis:*
```
"Analyze user_controller.py to understand the authentication flow"
```

*Directory Architecture Analysis:*
```
"Analyze the src/ directory architecture and identify the main components"
```

*Performance-Focused Analysis:*
```
"Analyze backend/api/ for performance bottlenecks, focus on database queries"
```

*Large Codebase Analysis:*
```
"Analyze the entire project structure to understand how all components work together"
```

**Best Practices:**
- Be specific about goals - clearly state what you want to understand or discover
- Use appropriate analysis types - choose the type that matches your needs
- Include related files - analyze modules together for better context understanding
- Leverage large context models - use Kimi for comprehensive codebase analysis
- Combine with visual context - include architecture diagrams or documentation
- Use continuation - build on previous analysis for deeper understanding

**When to Use:**
- Use `analyze` for: Understanding code structure, exploring unfamiliar codebases, architecture assessment
- Use `codereview` for: Finding bugs and security issues with actionable fixes
- Use `debug` for: Diagnosing specific runtime errors or performance problems
- Use `refactor` for: Getting specific refactoring recommendations and implementation plans

---

### debug_EXAI-WS

**Purpose:** Systematic investigation & expert debugging assistance

**Description:**
The `debug` workflow guides the AI client through a systematic investigation process where the client performs methodical code examination, evidence collection, and hypothesis formation across multiple steps. Once the investigation is complete, the tool provides expert analysis based on all gathered findings (unless confidence is "certain").

**Use Cases:**
- Complex bugs requiring systematic investigation
- Mysterious errors with unclear root causes
- Performance issues and bottlenecks
- Race conditions and concurrency bugs
- Memory leaks and resource exhaustion
- Integration problems and API failures
- Runtime environment issues

**Key Features:**
- **Multi-step investigation process** with evidence collection and hypothesis evolution
- **Systematic code examination** with file and method tracking throughout investigation
- **Confidence assessment and revision** capabilities for investigative steps
- **Backtracking support** to revise previous steps when new insights emerge
- **Expert analysis integration** that provides final debugging recommendations
- **Error context support**: Stack traces, logs, and runtime information
- **Visual debugging**: Include error screenshots, stack traces, console output
- **Conversation threading**: Continue investigations across multiple sessions
- **Large context analysis**: Handle extensive log files and multiple related code files
- **Multi-language support**: Debug issues across Python, JavaScript, Java, C#, Swift, and more
- **Web search integration**: Identifies when additional research would help solve problems

**Key Parameters:**

*Investigation Step Parameters:*
- `step` (required): Current investigation step description
- `step_number` (required): Current step number in investigation sequence
- `total_steps` (required): Estimated total investigation steps (adjustable as process evolves)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Discoveries and evidence collected in this step
- `hypothesis` (required): Current best guess about the underlying cause
- `files_checked` (optional): All files examined during investigation (tracks exploration path)
- `relevant_files` (optional): Files directly tied to the root cause or its effects (absolute paths)
- `relevant_context` (optional): Specific methods/functions involved in the issue
- `confidence` (optional): Confidence level (exploring, low, medium, high, very_high, almost_certain, certain)
- `backtrack_from_step` (optional): Step number to backtrack from (for revisions)
- `continuation_id` (optional): Thread ID for continuing investigations across sessions
- `images` (optional): Visual debugging materials (error screenshots, logs, etc.)

*Model Selection:*
- `model` (optional): Model to use (default: auto)
- `thinking_mode` (optional): Thinking depth - minimal|low|medium|high|max (default: medium)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true, set false for client-only)

**Workflow:**
1. **Step 1**: AI client describes the issue and begins thinking deeply about possible causes
2. **STOP** - Examine relevant code, trace errors, test hypotheses, gather evidence
3. **Step 2+**: Report findings with concrete evidence from code examination
4. **Throughout**: Track findings, files checked, methods involved, evolving hypotheses
5. **Backtracking**: Revise previous steps when new insights emerge
6. **Completion**: Once investigation is thorough, signal completion
7. **Expert Analysis**: Receive debugging recommendations (unless confidence=certain)

**Investigation Methodology:**

*Step-by-Step Investigation (Client-Led):*
1. **Initial Problem Description**: Describe issue and think about possible causes, side-effects, contributing factors
2. **Code Examination**: Systematically examine relevant files, trace execution paths, identify suspicious patterns
3. **Evidence Collection**: Gather findings, track files checked, identify methods/functions involved
4. **Hypothesis Formation**: Develop working theories about root cause with confidence assessments
5. **Iterative Refinement**: Backtrack and revise previous steps as understanding evolves
6. **Investigation Completion**: Signal when sufficient evidence has been gathered

*Expert Analysis Phase (When Used):*
- **Root Cause Analysis**: Deep analysis of all investigation findings and evidence
- **Solution Recommendations**: Specific fixes with implementation guidance
- **Prevention Strategies**: Measures to avoid similar issues in the future
- **Testing Approaches**: Validation methods for proposed solutions

**Debugging Categories:**

- **Runtime Errors**: Exceptions, crashes, null pointer errors, type errors, memory leaks
- **Logic Errors**: Incorrect algorithms, off-by-one errors, state management issues, race conditions
- **Integration Issues**: API failures, database connection problems, third-party service integration
- **Performance Problems**: Slow response times, memory spikes, CPU-intensive operations, I/O bottlenecks

**Valid Hypotheses:**
- "No bug found - possible user misunderstanding"
- "Symptoms appear unrelated to any code issue"
- Concrete theories about failures, incorrect assumptions, or violated constraints
- When no bug is found, consider: "Recommend discussing with thought partner for clarification"

**Usage Examples:**

*Error Debugging:*
```
"Debug this TypeError: 'NoneType' object has no attribute 'split' in my parser.py"
```

*With Stack Trace:*
```
"Debug why my API returns 500 errors with this stack trace: [paste full traceback]"
```

*Performance Debugging:*
```
"Debug to find out why the app is consuming excessive memory during bulk edit operations"
```

*Multi-File Investigation:*
```
"Debug the data processing pipeline issues across processor.py, validator.py, and output_handler.py"
```

**Best Practices:**

*For Investigation Steps:*
- Be thorough in step descriptions - explain what you're examining and why
- Track all files examined - include even files that don't contain the bug
- Document findings clearly - summarize discoveries, suspicious patterns, evidence
- Evolve hypotheses - update theories as investigation progresses
- Use backtracking wisely - revise previous steps when new insights emerge
- Include visual evidence - screenshots, error dialogs, console output

*For Initial Problem Description:*
- Provide complete error context - full stack traces, error messages, logs
- Describe expected vs actual behavior - clear symptom description
- Include environment details - runtime versions, configuration, deployment context
- Mention previous attempts - what debugging steps have already been tried
- Be specific about occurrence - when, where, and how the issue manifests

**When to Use:**
- Use `debug` for: Specific runtime errors, exceptions, crashes, performance issues requiring systematic investigation
- Use `codereview` for: Finding potential bugs in code without specific errors or symptoms
- Use `analyze` for: Understanding code structure and flow without troubleshooting specific issues
- Use `precommit` for: Validating changes before commit to prevent introducing bugs

---

### codereview_EXAI-WS

**Purpose:** Professional code review with prioritized feedback

**Description:**
The `codereview` tool provides professional code review capabilities with actionable feedback, severity-based issue prioritization, and support for various review types from quick style checks to comprehensive security audits. This workflow tool guides the AI client through systematic investigation steps with forced pauses to ensure thorough code examination.

**Use Cases:**
- Comprehensive code review with actionable feedback
- Security audits and vulnerability assessment
- Performance analysis and optimization opportunities
- Architectural assessment and pattern evaluation
- Code quality evaluation and maintainability review
- Anti-pattern detection and refactoring recommendations

**Key Features:**
- **Issues prioritized by severity** (🔴 CRITICAL → 🟢 LOW)
- **Specialized review types**: full, security, performance, quick
- **Coding standards enforcement**: PEP8, ESLint, Google Style Guide, etc.
- **Severity filtering**: Report only critical/high/medium/low issues
- **Image support**: Review code from screenshots, error dialogs, visual bug reports
- **Multi-file analysis**: Comprehensive review of entire directories or codebases
- **Actionable feedback**: Specific recommendations with line numbers and code examples
- **Language-specific expertise**: Tailored analysis for Python, JavaScript, Java, C#, Swift, and more
- **Integration issue detection**: Cross-file dependencies and architectural problems
- **Security vulnerability scanning**: Common security patterns and anti-patterns

**Key Parameters:**

*Workflow Investigation Parameters:*
- `step` (required): Current investigation step description
- `step_number` (required): Current step number in review sequence
- `total_steps` (required): Estimated total investigation steps (adjustable)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Discoveries and evidence collected in this step
- `files_checked` (optional): All files examined during investigation
- `relevant_files` (required in step 1): Files directly relevant to review (absolute paths)
- `relevant_context` (optional): Methods/functions/classes central to review findings
- `issues_found` (optional): Issues identified with severity levels
- `confidence` (optional): Confidence level (exploring, low, medium, high, very_high, almost_certain, certain)
- `backtrack_from_step` (optional): Step number to backtrack from
- `images` (optional): Visual references for review context

*Initial Review Configuration:*
- `model` (optional): Model to use (default: auto)
- `review_type` (optional): full|security|performance|quick (default: full)
- `focus_on` (optional): Specific aspects to focus on (e.g., "security vulnerabilities", "performance bottlenecks")
- `standards` (optional): Coding standards to enforce (e.g., "PEP8", "ESLint")
- `severity_filter` (optional): critical|high|medium|low|all (default: all)
- `temperature` (optional): Temperature for consistency (0-1, default: 0.2)
- `thinking_mode` (optional): Thinking depth (default: medium)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)
- `continuation_id` (optional): Continue previous review discussions

**Review Types:**
- **Full Review (default)**: Comprehensive analysis including bugs, security, performance, maintainability
- **Security Review**: Focus on vulnerabilities, authentication, authorization, input validation
- **Performance Review**: Bottlenecks, algorithmic complexity, resource usage
- **Quick Review**: Style, naming conventions, basic code quality

**Workflow:**
1. **Step 1**: Describe review plan and pass files in `relevant_files`
2. **STOP** - Investigate code quality, security, performance, architecture
3. **Step 2+**: Report findings with evidence and severity classifications
4. **Throughout**: Track findings, issues, confidence levels
5. **Completion**: Once review is comprehensive, signal completion
6. **Expert Analysis**: Receive comprehensive review summary (unless confidence=certain)

**Usage Examples:**

*Security-Focused Review:*
```
"Perform a codereview on auth.py for security issues and potential vulnerabilities"
```

*Performance Review:*
```
"Review backend/api/ for performance bottlenecks and optimization opportunities"
```

*Full Codebase Review:*
```
"Comprehensive code review of src/ directory with actionable recommendations"
```

**Best Practices:**
- Be specific about review objectives and focus areas
- Include coding standards to enforce
- Use severity filtering for large codebases
- Leverage large context models for comprehensive analysis
- Include visual context when reviewing UI/UX code

**When to Use:**
- Use `codereview` for: Finding bugs and security issues with actionable fixes
- Use `analyze` for: Understanding code structure without finding specific issues
- Use `debug` for: Diagnosing specific runtime errors
- Use `refactor` for: Getting refactoring recommendations

---

### precommit_EXAI-WS

**Purpose:** Pre-commit validation

**Use Cases:**
- Comprehensive pre-commit validation
- Multi-repository analysis
- Security review
- Change impact assessment
- Completeness verification

**Key Parameters:**
- `step` (required): Current validation step
- `step_number` (required): Current step number
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings
- `path` (optional): Starting directory path (absolute)
- `compare_to` (optional): Git ref to compare against
- `include_staged` (optional): Include staged changes (default: true)
- `include_unstaged` (optional): Include unstaged changes (default: true)

**Workflow:**
1. Step 1: Describe validation plan
2. STOP and investigate git changes
3. Step 2+: Report findings with evidence
4. Continue until validation complete
5. Receive expert analysis

---

### refactor_EXAI-WS

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

---

### testgen_EXAI-WS

**Purpose:** Comprehensive test generation with edge case coverage

**Description:**
The `testgen` tool creates comprehensive test suites by analyzing code paths, understanding intricate dependencies, and identifying realistic edge cases and failure scenarios. This workflow tool guides the AI client through systematic investigation of code functionality before generating thorough tests.

**Use Cases:**
- Generating tests for specific functions/classes/modules
- Creating test scaffolding for new features
- Improving test coverage with edge cases
- Edge case identification and boundary condition testing
- Framework-specific test generation
- Realistic failure mode analysis

**Key Features:**
- **Multi-step workflow** analyzing code paths and identifying realistic failure modes
- **Generates framework-specific tests** following project conventions
- **Supports test pattern following** when examples are provided
- **Dynamic token allocation** (25% for test examples, 75% for main code)
- **Prioritizes smallest test files** for pattern detection
- **Can reference existing test files** for style consistency
- **Specific code coverage** - target specific functions/classes rather than testing everything
- **Image support**: Test UI components, analyze visual requirements
- **Edge case identification**: Systematic discovery of boundary conditions and error states
- **Realistic failure mode analysis**: Understanding what can actually go wrong
- **Integration test support**: Tests covering component interactions

**Key Parameters:**

*Workflow Investigation Parameters:*
- `step` (required): Current investigation step description
- `step_number` (required): Current step number in test generation sequence
- `total_steps` (required): Estimated total investigation steps (adjustable)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Discoveries about functionality and test scenarios
- `files_checked` (optional): All files examined during investigation
- `relevant_files` (required in step 1): Files directly needing tests (absolute paths)
- `relevant_context` (optional): Methods/functions/classes requiring test coverage
- `confidence` (optional): Confidence level (exploring, low, medium, high, very_high, almost_certain, certain)
- `backtrack_from_step` (optional): Step number to backtrack from

*Initial Configuration:*
- `model` (optional): Model to use (default: auto)
- `test_examples` (optional): Existing test files as style/pattern reference (absolute paths)
- `thinking_mode` (optional): Thinking depth (default: medium)
- `use_assistant_model` (optional): Use expert test generation phase (default: true)

**Workflow:**
1. **Step 1**: Describe what to test and testing objectives (be specific!)
2. **STOP** - Investigate code functionality, critical paths, edge cases
3. **Step 2+**: Report findings with test scenarios and coverage gaps
4. **Throughout**: Track findings, test scenarios, confidence levels
5. **Completion**: Once investigation is thorough, signal completion
6. **Test Generation**: Receive comprehensive test suite

**Usage Examples:**

*Method-Specific Tests:*
```
"Generate tests for User.login() method covering authentication success, failure, and edge cases"
```

*Class Testing:*
```
"Generate comprehensive tests for PaymentProcessor class"
```

*Following Existing Patterns:*
```
"Generate tests for new authentication module following patterns from tests/unit/auth/"
```

*UI Component Testing:*
```
"Generate tests for this login form component using the UI mockup screenshot"
```

**Best Practices:**
- **Be specific about scope** - Target specific functions/classes/modules, not "test everything"
- **Provide test examples** - Include existing test files for pattern consistency
- **Describe expected behavior** - Explain what the code should do
- **Include edge cases** - Mention known boundary conditions or failure modes
- **Specify framework** - Indicate testing framework (pytest, jest, junit, etc.)

**When to Use:**
- Use `testgen` for: Generating comprehensive test suites with edge case coverage
- Use `codereview` for: Finding bugs in existing code
- Use `debug` for: Diagnosing specific test failures
- Use `analyze` for: Understanding code structure before writing tests

---

### tracer_EXAI-WS

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

---

### secaudit_EXAI-WS

**Purpose:** Comprehensive security audit with OWASP-based assessment

**Description:**
The `secaudit` tool provides comprehensive security auditing capabilities with systematic OWASP Top 10 assessment, compliance framework evaluation, and threat modeling. This workflow tool guides the AI client through methodical security investigation with forced pauses to ensure thorough vulnerability assessment.

**IMPORTANT**: AI models may not identify all security vulnerabilities. Always perform additional manual security reviews, penetration testing, and verification.

**Use Cases:**
- Comprehensive security assessment with OWASP Top 10 coverage
- Compliance evaluation (SOC2, PCI DSS, HIPAA, GDPR, FedRAMP)
- Vulnerability identification and threat modeling
- Security architecture review and attack surface mapping
- Authentication and authorization assessment
- Input validation and data security review

**Key Features:**
- **OWASP Top 10 (2021) systematic assessment** with specific vulnerability identification
- **Multi-compliance framework support**: SOC2, PCI DSS, HIPAA, GDPR, FedRAMP
- **Threat-level aware analysis**: Critical, high, medium, low threat classifications
- **Technology-specific security patterns**: Web apps, APIs, mobile, cloud, enterprise systems
- **Risk-based prioritization**: Business impact and exploitability assessment
- **Audit focus customization**: Comprehensive, authentication, data protection, infrastructure
- **Image support**: Security analysis from architecture diagrams, network topology
- **Multi-file security analysis**: Cross-component vulnerability identification
- **Compliance gap analysis**: Specific framework requirements with remediation guidance
- **Attack surface mapping**: Entry points, data flows, privilege boundaries
- **Security control effectiveness**: Evaluation of existing security measures

**Key Parameters:**

*Workflow Investigation Parameters:*
- `step` (required): Current security investigation step description
- `step_number` (required): Current step number in audit sequence
- `total_steps` (required): Estimated total investigation steps (typically 4-6)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Security discoveries and evidence collected
- `files_checked` (optional): All files examined during security investigation
- `relevant_files` (required in step 1): Files directly relevant to security audit (absolute paths)
- `relevant_context` (optional): Methods/functions/classes with security implications
- `issues_found` (optional): Security issues with severity levels
- `confidence` (optional): Confidence level in audit completeness
- `images` (optional): Visual references (architecture diagrams, network topology)

*Initial Configuration:*
- `model` (optional): Model to use (default: auto)
- `audit_focus` (optional): owasp|compliance|infrastructure|dependencies|comprehensive (default: comprehensive)
- `threat_level` (optional): low|medium|high|critical (default: medium)
- `security_scope` (optional): Application context (web app, mobile app, API, enterprise system)
- `compliance_requirements` (optional): List of applicable frameworks (SOC2, PCI DSS, HIPAA, GDPR, ISO 27001)
- `severity_filter` (optional): critical|high|medium|low|all (default: all)
- `thinking_mode` (optional): Thinking depth (default: medium)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)

**Workflow:**
1. **Step 1**: Security scope analysis - identify application type, tech stack, attack surface
2. **Step 2**: Authentication & authorization assessment
3. **Step 3**: Input validation & data security review
4. **Step 4**: OWASP Top 10 (2021) systematic review
5. **Step 5**: Dependencies & infrastructure security
6. **Step 6**: Compliance & risk assessment
7. **Expert Analysis**: Comprehensive security assessment summary

**Usage Examples:**

*E-Commerce Security Audit:*
```
"Perform a secaudit on this e-commerce web application focusing on payment processing security and PCI DSS compliance"
```

*Authentication System Audit:*
```
"Conduct a comprehensive security audit of the authentication system, threat level high, focus on HIPAA compliance"
```

*API Security Assessment:*
```
"Security audit of REST API focusing on OWASP Top 10 and authentication vulnerabilities"
```

**Best Practices:**
- Define security scope and application context clearly
- Specify compliance requirements upfront
- Use appropriate threat level for risk prioritization
- Include architecture diagrams for better context
- Focus on specific audit areas for targeted assessment

**When to Use:**
- Use `secaudit` for: Comprehensive security assessment and vulnerability identification
- Use `codereview` for: General code quality with some security considerations
- Use `analyze` for: Understanding code structure without security focus
- Use `debug` for: Diagnosing specific security-related errors

---

### docgen_EXAI-WS

**Purpose:** Comprehensive documentation generation with complexity analysis

**Description:**
The `docgen` tool creates thorough documentation by analyzing code structure, understanding function complexity, and documenting gotchas and unexpected behaviors. This workflow tool guides the AI client through systematic investigation of code functionality before generating comprehensive documentation.

**Use Cases:**
- Comprehensive documentation generation for undocumented code
- Code documentation analysis and quality assessment
- Complexity assessment with Big O notation
- Documentation modernization and style updates
- API documentation with call flow information
- Gotchas and unexpected behavior documentation

**Key Features:**
- **Systematic file-by-file approach** - Complete documentation with progress tracking
- **Modern documentation styles** - Enforces /// for Objective-C/Swift, /** */ for Java/JavaScript
- **Complexity analysis** - Big O notation for algorithms and performance characteristics
- **Call flow documentation** - Dependencies and method relationships
- **Counter-based completion** - Prevents stopping until all files are documented
- **Large file handling** - Systematic portion-by-portion documentation
- **Final verification scan** - Mandatory check to ensure no functions are missed
- **Bug tracking** - Surfaces code issues without altering logic
- **Configuration parameters** - Control complexity analysis, call flow, inline comments

**Key Parameters:**

*Workflow Parameters:*
- `step` (required): Current step description - discovery (step 1) or documentation (step 2+)
- `step_number` (required): Current step number in documentation sequence
- `total_steps` (required): Dynamically calculated as 1 + total_files_to_document
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Discoveries about code structure and documentation needs
- `relevant_files` (optional): Files being actively documented in current step
- `num_files_documented` (required): Counter tracking completed files (starts at 0)
- `total_files_to_document` (required): Total count of files needing documentation

*Configuration Parameters (required fields):*
- `document_complexity` (required): Include Big O complexity analysis (default: true)
- `document_flow` (required): Include call flow and dependency information (default: true)
- `update_existing` (required): Update existing documentation when incorrect/incomplete (default: true)
- `comments_on_complex_logic` (required): Add inline comments for complex algorithmic steps (default: true)

**Critical Counters:**
- `num_files_documented`: Increment by 1 ONLY when file is 100% documented
- `total_files_to_document`: Set in step 1 after discovering all files
- **Cannot set `next_step_required=false` unless `num_files_documented == total_files_to_document`**

**Workflow:**
1. **Step 1 (Discovery)**: Discover ALL files needing documentation and report exact count
2. **Step 2+ (Documentation)**: Document files one-by-one with complete coverage validation
3. **Throughout**: Track progress with counters and enforce modern documentation styles
4. **Completion**: Only when all files are documented (counters match)
5. **Documentation Generation**: Complete documentation with style consistency

**Usage Examples:**

*Class Documentation:*
```
"Generate comprehensive documentation for the PaymentProcessor class including complexity analysis"
```

*Module Documentation:*
```
"Document all functions in the authentication module with call flow information"
```

*API Documentation:*
```
"Create API documentation for the REST endpoints with complexity and flow analysis"
```

**Best Practices:**
- Let the tool discover all files first (step 1)
- Document one file at a time for thoroughness
- Include complexity analysis for algorithms
- Document call flows for better understanding
- Update existing docs when incorrect
- Add inline comments for complex logic

**When to Use:**
- Use `docgen` for: Generating comprehensive documentation with complexity analysis
- Use `codereview` for: Finding bugs and improving code quality
- Use `analyze` for: Understanding code structure
- Use `refactor` for: Improving code organization

---

## Agentic Enhancements (Phase 1)

### Self-Assessment

**Purpose:** Evaluate information sufficiency

**Implementation:**
```python
def assess_information_sufficiency(self) -> dict:
    """Assess if enough information has been gathered."""
    
    findings_sufficient = len(self.findings) >= self.MINIMUM_FINDINGS_LENGTH
    files_sufficient = len(self.relevant_files) >= self.MINIMUM_RELEVANT_FILES
    
    return {
        "sufficient": findings_sufficient and files_sufficient,
        "findings_length": len(self.findings),
        "files_count": len(self.relevant_files)
    }
```

**Configurable Thresholds:**
```python
MINIMUM_FINDINGS_LENGTH = 100  # Minimum characters in findings
MINIMUM_RELEVANT_FILES = 0     # Minimum relevant files
```

---

### Early Termination

**Purpose:** Complete investigation early when goals achieved

**Implementation:**
```python
def should_terminate_early(self) -> dict:
    """Determine if investigation can terminate early."""
    
    if self.confidence == "certain":
        return {"should_terminate": True, "reason": "High confidence achieved"}
    
    if self.step_number >= self.total_steps:
        return {"should_terminate": True, "reason": "All steps completed"}
    
    return {"should_terminate": False}
```

**Confidence Levels:**
- `exploring` - Just starting
- `low` - Early investigation
- `medium` - Some evidence
- `high` - Strong evidence
- `very_high` - Very strong evidence
- `almost_certain` - Nearly confirmed
- `certain` - 100% confidence (triggers early termination)

---

### Dynamic Step Adjustment

**Purpose:** Request additional steps mid-workflow

**Implementation:**
```python
def request_additional_steps(self, additional_steps: int, reason: str) -> dict:
    """Request additional investigation steps."""
    
    if additional_steps <= 0:
        raise ValueError("additional_steps must be positive")
    
    self.total_steps += additional_steps
    self.step_adjustment_history.append({
        "step_number": self.step_number,
        "additional_steps": additional_steps,
        "reason": reason
    })
    
    return {
        "new_total_steps": self.total_steps,
        "adjustment_history": self.step_adjustment_history
    }
```

**Usage:**
```json
{
  "step": "Need more investigation into authentication flow",
  "step_number": 3,
  "total_steps": 5,
  "next_step_required": true,
  "findings": "Discovered additional complexity requiring 2 more steps",
  "request_additional_steps": 2,
  "adjustment_reason": "Authentication flow more complex than initially estimated"
}
```

---

## Tool Selection Guide

### When to Use Which Tool

**General Questions:**
- Use `chat` for quick questions, brainstorming, explanations

**Complex Investigation:**
- Use `thinkdeep` for multi-stage investigation with expert validation

**Planning:**
- Use `planner` for breaking down complex tasks into steps

**Decision Making:**
- Use `consensus` for multi-model perspectives on decisions

**Code Analysis:**
- Use `analyze` for comprehensive code analysis
- Use `codereview` for systematic code review
- Use `refactor` for refactoring recommendations

**Debugging:**
- Use `debug` for root cause analysis and bug hunting

**Testing:**
- Use `testgen` for generating tests with edge case coverage

**Security:**
- Use `secaudit` for security audits and vulnerability assessment

**Documentation:**
- Use `docgen` for generating comprehensive documentation

**Code Understanding:**
- Use `tracer` for understanding execution flow and dependencies

**Pre-Commit:**
- Use `precommit` for validating changes before committing

---

**Next:** Read `04-features-and-capabilities.md` for detailed feature documentation

