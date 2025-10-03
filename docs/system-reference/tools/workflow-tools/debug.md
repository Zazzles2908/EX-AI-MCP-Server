# debug_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [codereview.md](codereview.md), [precommit.md](precommit.md)

---

## Purpose

Systematic investigation & expert debugging assistance

---

## Description

The `debug` workflow guides the AI client through a systematic investigation process where the client performs methodical code examination, evidence collection, and hypothesis formation across multiple steps. Once the investigation is complete, the tool provides expert analysis based on all gathered findings (unless confidence is "certain").

---

## Use Cases

- Complex bugs requiring systematic investigation
- Mysterious errors with unclear root causes
- Performance issues and bottlenecks
- Race conditions and concurrency bugs
- Memory leaks and resource exhaustion
- Integration problems and API failures
- Runtime environment issues

---

## Key Features

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

---

## Key Parameters

### Investigation Step Parameters
- `step` (required): Current investigation step description
- `step_number` (required): Current step number in investigation sequence
- `total_steps` (required): Estimated total investigation steps (adjustable)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Discoveries and evidence collected in this step
- `hypothesis` (required): Current best guess about the underlying cause
- `files_checked` (optional): All files examined during investigation
- `relevant_files` (optional): Files directly tied to the root cause (absolute paths)
- `relevant_context` (optional): Specific methods/functions involved in the issue
- `confidence` (optional): Confidence level (exploring, low, medium, high, very_high, almost_certain, certain)
- `backtrack_from_step` (optional): Step number to backtrack from
- `continuation_id` (optional): Thread ID for continuing investigations
- `images` (optional): Visual debugging materials (error screenshots, logs)

### Model Selection
- `model` (optional): Model to use (default: auto)
- `thinking_mode` (optional): Thinking depth - minimal|low|medium|high|max (default: medium)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)

---

## Workflow

1. **Step 1**: AI client describes the issue and begins thinking deeply about possible causes
2. **STOP** - Examine relevant code, trace errors, test hypotheses, gather evidence
3. **Step 2+**: Report findings with concrete evidence from code examination
4. **Throughout**: Track findings, files checked, methods involved, evolving hypotheses
5. **Backtracking**: Revise previous steps when new insights emerge
6. **Completion**: Once investigation is thorough, signal completion
7. **Expert Analysis**: Receive debugging recommendations (unless confidence=certain)

---

## Investigation Methodology

### Step-by-Step Investigation (Client-Led)
1. **Initial Problem Description**: Describe issue and think about possible causes
2. **Code Examination**: Systematically examine relevant files, trace execution paths
3. **Evidence Collection**: Gather findings, track files checked, identify methods involved
4. **Hypothesis Formation**: Develop working theories about root cause
5. **Iterative Refinement**: Backtrack and revise previous steps as understanding evolves
6. **Investigation Completion**: Signal when sufficient evidence has been gathered

### Expert Analysis Phase (When Used)
- **Root Cause Analysis**: Deep analysis of all investigation findings
- **Solution Recommendations**: Specific fixes with implementation guidance
- **Prevention Strategies**: Measures to avoid similar issues
- **Testing Approaches**: Validation methods for proposed solutions

---

## Debugging Categories

- **Runtime Errors**: Exceptions, crashes, null pointer errors, type errors, memory leaks
- **Logic Errors**: Incorrect algorithms, off-by-one errors, state management issues, race conditions
- **Integration Issues**: API failures, database connection problems, third-party service integration
- **Performance Problems**: Slow response times, memory spikes, CPU-intensive operations, I/O bottlenecks

---

## Valid Hypotheses

- "No bug found - possible user misunderstanding"
- "Symptoms appear unrelated to any code issue"
- Concrete theories about failures, incorrect assumptions, or violated constraints
- When no bug is found, consider: "Recommend discussing with thought partner for clarification"

---

## Usage Examples

### Error Debugging
```
"Debug this TypeError: 'NoneType' object has no attribute 'split' in my parser.py"
```

### With Stack Trace
```
"Debug why my API returns 500 errors with this stack trace: [paste full traceback]"
```

### Performance Debugging
```
"Debug to find out why the app is consuming excessive memory during bulk edit operations"
```

### Multi-File Investigation
```
"Debug the data processing pipeline issues across processor.py, validator.py, and output_handler.py"
```

---

## Best Practices

### For Investigation Steps
- Be thorough in step descriptions - explain what you're examining and why
- Track all files examined - include even files that don't contain the bug
- Document findings clearly - summarize discoveries, suspicious patterns, evidence
- Evolve hypotheses - update theories as investigation progresses
- Use backtracking wisely - revise previous steps when new insights emerge
- Include visual evidence - screenshots, error dialogs, console output

### For Initial Problem Description
- Provide complete error context - full stack traces, error messages, logs
- Describe expected vs actual behavior - clear symptom description
- Include environment details - runtime versions, configuration, deployment context
- Mention previous attempts - what debugging steps have already been tried
- Be specific about occurrence - when, where, and how the issue manifests

---

## When to Use

- **Use `debug` for:** Specific runtime errors, exceptions, crashes, performance issues requiring systematic investigation
- **Use `codereview` for:** Finding potential bugs in code without specific errors or symptoms
- **Use `analyze` for:** Understanding code structure and flow without troubleshooting specific issues
- **Use `precommit` for:** Validating changes before commit to prevent introducing bugs

---

## Related Tools

- [analyze.md](analyze.md) - Comprehensive code analysis
- [codereview.md](codereview.md) - Professional code review
- [precommit.md](precommit.md) - Pre-commit validation
- [tracer.md](tracer.md) - Code tracing and dependency mapping

