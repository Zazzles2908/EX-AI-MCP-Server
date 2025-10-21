# chat_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Simple Tool (Request/Response)  
**Related:** [thinkdeep.md](thinkdeep.md), [analyze.md](../workflow-tools/analyze.md)

---

## Purpose

Your collaborative thinking partner for development conversations

---

## Description

The `chat` tool is designed to help you brainstorm, validate ideas, get second opinions, and explore alternatives in a conversational format. It's your thinking partner for bouncing ideas, getting expert opinions, and collaborative problem-solving.

---

## Use Cases

- Collaborative thinking partner for analysis and planning
- Get second opinions on designs and approaches
- Brainstorm solutions and explore alternatives
- Validate checklists and implementation plans
- General development questions and explanations
- Technology comparisons and best practices
- Architecture and design discussions

---

## Key Features

- **File reference support**: Include code files for context-aware discussions
- **Image support**: Screenshots, diagrams, UI mockups for visual analysis
- **Dynamic collaboration**: Can request additional files or context during conversation
- **Web search capability**: Analyzes when web searches would be helpful and recommends specific searches

---

## Key Parameters

- `prompt` (required): Your question or discussion topic
- `model` (optional): auto|kimi-k2-0905-preview|glm-4.5|glm-4.5-flash (default: auto)
- `use_websearch` (optional): Enable web search (default: true)
- `temperature` (optional): Response creativity (0-1, default: 0.5)
- `thinking_mode` (optional): Thinking depth - minimal|low|medium|high|max (default: medium)
- `files` (optional): Files for context (absolute paths)
- `images` (optional): Images for visual context (absolute paths or base64)
- `continuation_id` (optional): Continue previous conversations

---

## Usage Examples

### Basic Development Chat
```
"Chat about the best approach for user authentication in my React app"
```

### Technology Comparison
```
"Discuss whether PostgreSQL or MongoDB would be better for my e-commerce platform"
```

### File Context Analysis
```
"Chat about the current authentication implementation in auth.py and suggest improvements"
```

### Visual Analysis
```
"Chat about this UI mockup screenshot - is the user flow intuitive?"
```

---

## Best Practices

- Be specific about context - include relevant files or describe your project scope
- Ask for trade-offs - request pros/cons for better decision-making
- Use conversation continuation - build on previous discussions with `continuation_id`
- Leverage visual context - include diagrams, mockups, or screenshots when discussing UI/UX
- Request web searches - ask for current best practices or recent developments

---

## When to Use

- **Use `chat` for:** Open-ended discussions, brainstorming, second opinions, technology comparisons
- **Use `thinkdeep` for:** Extending specific analysis, challenging assumptions, deeper reasoning
- **Use `analyze` for:** Understanding existing code structure and patterns
- **Use `debug` for:** Specific error diagnosis and troubleshooting

---

## Related Tools

- [thinkdeep.md](thinkdeep.md) - Extended reasoning with multi-stage investigation
- [analyze.md](../workflow-tools/analyze.md) - Comprehensive code analysis
- [debug.md](../workflow-tools/debug.md) - Root cause analysis and debugging

