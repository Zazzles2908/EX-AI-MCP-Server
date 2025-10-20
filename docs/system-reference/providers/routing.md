# Agentic Routing

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [glm.md](glm.md), [kimi.md](kimi.md), [../02-provider-architecture.md](../02-provider-architecture.md)

---

## Overview

The EX-AI-MCP-Server implements a **manager-first routing architecture** that intelligently routes requests between GLM and Kimi providers based on task complexity, cost optimization, and capability requirements.

---

## Manager-First Architecture

### Default Manager: GLM-4.5-flash

**Purpose:**
- Fast, cost-effective routing decisions
- Initial task classification
- Simple task handling

**Characteristics:**
- Low latency (~100ms response time)
- Cost-effective ($0.05/$0.15 per M tokens)
- Sufficient for 70% of tasks

---

## Routing Logic

### Task Classification

**Simple Tasks → GLM-4.5-flash:**
- General questions
- Basic code explanations
- Simple refactoring suggestions
- Quick documentation lookups

**Complex Tasks → GLM-4.6:**
- Detailed code analysis
- Architecture design
- Performance optimization
- Security audits
- **Advantage:** 200K context window (vs 128K for GLM-4.5)

**Specialized Tasks → Kimi:**
- Long context analysis (>100K tokens)
- Complex reasoning chains
- Agentic workflows
- Tool-heavy operations

---

## Escalation Strategy

**Level 1: GLM-4.5-flash (Manager)**
- Initial request handling
- Task complexity assessment
- Simple task completion

**Level 2: GLM-4.6**
- Complex analysis
- Detailed reasoning
- Multi-step workflows

**Level 3: Kimi**
- Long context processing
- Advanced reasoning
- Specialized capabilities

---

## Benefits

1. **Cost Optimization**: Use cheaper models for simple tasks
2. **Performance**: Fast routing decisions with GLM-4.5-flash
3. **Quality**: Route complex tasks to appropriate models
4. **Flexibility**: Dynamic routing based on task requirements

---

## Configuration

```env
# Manager model
GLM_MANAGER_MODEL=glm-4.5-flash

# Routing thresholds
ROUTING_COMPLEXITY_THRESHOLD=0.7
ROUTING_CONTEXT_THRESHOLD=100000
```

---

## Related Documentation

- [glm.md](glm.md) - GLM provider details
- [kimi.md](kimi.md) - Kimi provider details
- [../02-provider-architecture.md](../02-provider-architecture.md) - Provider architecture overview
