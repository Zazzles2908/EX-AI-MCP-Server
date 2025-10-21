# thinkdeep_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Simple Tool (Multi-Stage Investigation)  
**Related:** [chat.md](chat.md), [analyze.md](../workflow-tools/analyze.md)

---

## Purpose

Extended reasoning partner - get a second opinion to challenge assumptions

---

## Description

The `thinkdeep` tool provides extended reasoning capabilities, offering a second perspective to the AI client's analysis. It's designed to challenge assumptions, find edge cases, and provide alternative approaches to complex problems through multi-stage investigation.

---

## Use Cases

- Complex problem analysis with systematic investigation
- Architecture decisions requiring deep validation
- Performance challenges needing thorough analysis
- Security analysis with comprehensive threat modeling
- Systematic hypothesis testing and validation
- Expert validation of design patterns

---

## Key Features

- **Multi-stage workflow** with structured investigation steps
- **Provides second opinion** on AI client's analysis
- **Challenges assumptions** and identifies edge cases
- **Offers alternative perspectives** and approaches
- **Validates architectural decisions** and design patterns
- **File reference support**: Include code files for context
- **Image support**: Analyze architectural diagrams, flowcharts, design mockups
- **Web search capability**: Identifies areas where current documentation would strengthen analysis

---

## Key Parameters

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

---

## Workflow

1. **Step 1**: Describe investigation plan and begin forming systematic approach
2. **STOP** - Investigate using appropriate tools
3. **Step 2+**: Report findings with concrete evidence
4. **Continue** until investigation complete
5. **Expert Analysis**: Receive comprehensive analysis based on all findings

---

## Usage Examples

### Architecture Design
```
"Think deeper about my microservices authentication strategy using max thinking mode"
```

### With File Context
```
"Think deeper about my API design with reference to api/routes.py and models/user.py"
```

### Visual Analysis
```
"Think deeper about this system architecture diagram - identify potential bottlenecks"
```

### Problem Solving
```
"I'm considering using GraphQL vs REST for my API. Think deeper about the trade-offs using high thinking mode"
```

---

## Best Practices

- Provide detailed context - share your current thinking, constraints, and objectives
- Be specific about focus areas - mention what aspects need deeper analysis
- Include relevant files - reference code, documentation, or configuration files
- Use appropriate thinking modes - higher modes for complex problems, lower for quick validations
- Leverage visual context - include diagrams or mockups for architectural discussions
- Build on discussions - use continuation to extend previous analyses

---

## When to Use

- **Use `thinkdeep` for:** Extending specific analysis, challenging assumptions, architectural decisions
- **Use `chat` for:** Open-ended brainstorming and general discussions
- **Use `analyze` for:** Understanding existing code without extending analysis
- **Use `codereview` for:** Finding specific bugs and security issues

---

## Related Tools

- [chat.md](chat.md) - Collaborative thinking partner
- [analyze.md](../workflow-tools/analyze.md) - Comprehensive code analysis
- [consensus.md](consensus.md) - Multi-model consensus workflow

