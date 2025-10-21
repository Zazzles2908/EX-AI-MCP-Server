# planner_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Simple Tool (Sequential Planning)  
**Related:** [chat.md](chat.md), [thinkdeep.md](thinkdeep.md), [consensus.md](consensus.md)

---

## Purpose

Sequential step-by-step planning with branching and revision support

---

## Use Cases

- Breaking down complex tasks into manageable steps
- Project planning and implementation roadmaps
- Task sequencing and dependency mapping
- Exploring alternative approaches through branching
- Revising plans as understanding evolves

---

## Key Features

- **Sequential thinking** - Build plans step-by-step
- **Deep reflection** for complex planning scenarios
- **Branching** into alternative approaches
- **Revisions** of previous steps when new insights emerge
- **Dynamic step adjustment** - Add or modify steps as needed

---

## Key Parameters

- `step` (required): Current planning step description
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Estimated total steps needed
- `next_step_required` (required): Whether another step is needed
- `is_step_revision` (optional): True if revising a previous step
- `revises_step_number` (optional): Which step number is being revised
- `is_branch_point` (optional): True if branching from a previous step
- `branch_from_step` (optional): Which step is the branching point
- `branch_id` (optional): Identifier for the current branch (e.g., 'approach-A')
- `model` (optional): Model to use (default: auto)
- `use_assistant_model` (optional): Use expert analysis (default: true)

---

## Usage Examples

### Basic Planning
```json
{
  "step": "Outline goals and constraints for zai-sdk upgrade",
  "step_number": 1,
  "total_steps": 5,
  "next_step_required": true
}
```

### Branching Approach
```json
{
  "step": "Explore microservices approach as alternative",
  "step_number": 4,
  "total_steps": 6,
  "next_step_required": true,
  "is_branch_point": true,
  "branch_from_step": 3,
  "branch_id": "microservices-path"
}
```

### Revising Previous Step
```json
{
  "step": "Revise authentication strategy based on new security requirements",
  "step_number": 3,
  "total_steps": 5,
  "next_step_required": true,
  "is_step_revision": true,
  "revises_step_number": 2
}
```

---

## Best Practices

- Start with high-level goals and constraints
- Break down complex tasks into smaller, manageable steps
- Use branching to explore alternative approaches
- Revise steps when new information emerges
- Be flexible with total_steps - adjust as planning evolves

---

## When to Use

- **Use `planner` for:** Breaking down complex tasks, creating implementation roadmaps
- **Use `chat` for:** Open-ended brainstorming without structured planning
- **Use `thinkdeep` for:** Deep analysis of specific problems
- **Use `consensus` for:** Getting multiple perspectives on decisions

---

## Related Tools

- [chat.md](chat.md) - Collaborative thinking partner
- [thinkdeep.md](thinkdeep.md) - Extended reasoning
- [consensus.md](consensus.md) - Multi-model consensus

