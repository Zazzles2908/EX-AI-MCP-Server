# testgen_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [debug.md](debug.md)

---



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