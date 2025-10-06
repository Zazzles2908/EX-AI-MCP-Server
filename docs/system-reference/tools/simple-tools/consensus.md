# consensus_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Simple Tool (Multi-Model Consensus)  
**Related:** [chat.md](chat.md), [thinkdeep.md](thinkdeep.md), [planner.md](planner.md)

---

## Purpose

Multi-model consensus workflow for complex decisions

---

## Use Cases

- Complex decisions requiring multiple perspectives
- Architectural choices with trade-offs
- Feature proposals needing validation
- Technology evaluations and comparisons
- Strategic planning with diverse viewpoints

---

## Key Features

- **Sequential model consultation** - One model at a time
- **Stance steering** - Models can argue for/against/neutral positions
- **Perspective synthesis** - Track and combine viewpoints
- **Structured debate** - Same model with different stances
- **Comprehensive consensus** - Final synthesis of all perspectives

---

## Key Parameters

- `step` (required): Current consensus step description
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Total steps (equals number of models)
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings from this step
- `models` (required): List of model configurations to consult
- `model` (optional): Model to use for synthesis (default: auto)
- `use_assistant_model` (optional): Use expert analysis (default: true)
- `continuation_id` (optional): Continue previous consensus discussions

---

## Model Configuration

Each model in the `models` list can have:
- `model` (required): Model name (e.g., "kimi-k2-0905-preview", "glm-4.6")
- `stance` (optional): for|against|neutral (default: neutral)
- `stance_prompt` (optional): Custom stance instructions

**Note:** Same model can be used multiple times with different stances, but each model + stance combination must be unique.

---

## Workflow

1. **Step 1**: Provide your own neutral analysis of the proposal
2. **Tool consults each model** one by one
3. **Track perspectives** as they accumulate
4. **Synthesize findings** from all models
5. **Final step**: Present comprehensive consensus and recommendations

---

## Usage Examples

### Basic Consensus
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

### Technology Evaluation
```json
{
  "step": "Evaluate the proposal to migrate our database from MySQL to PostgreSQL",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Migration would provide better JSON support but requires significant effort",
  "models": [
    {"model": "glm-4.6", "stance": "for"},
    {"model": "kimi-k2-0905-preview", "stance": "against"}
  ]
}
```

---

## Best Practices

- Phrase step 1 as a clear question or proposal
- Provide your own analysis first (step 1)
- Use diverse models for varied perspectives
- Leverage stance steering for structured debate
- Consider using same model with different stances for balanced view

---

## When to Use

- **Use `consensus` for:** Complex decisions needing multiple expert perspectives
- **Use `chat` for:** Open-ended discussions without formal consensus
- **Use `thinkdeep` for:** Deep analysis from a single perspective
- **Use `planner` for:** Breaking down implementation steps

---

## Related Tools

- [chat.md](chat.md) - Collaborative thinking partner
- [thinkdeep.md](thinkdeep.md) - Extended reasoning
- [planner.md](planner.md) - Sequential planning
- [challenge.md](challenge.md) - Critical analysis

