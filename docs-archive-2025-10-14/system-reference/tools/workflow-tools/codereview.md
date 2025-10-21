# codereview_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [debug.md](debug.md)

---



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