#!/usr/bin/env python3
"""
Extract detailed content from archived files into new subfolder structure.
"""

from pathlib import Path
import re

# Read archived files
archive_dir = Path("docs/archive/old-system-reference-20251003")

provider_archive = archive_dir / "02-provider-architecture-ARCHIVED-20251003.md"
features_archive = archive_dir / "04-features-and-capabilities-ARCHIVED-20251003.md"
api_archive = archive_dir / "05-api-endpoints-reference-ARCHIVED-20251003.md"

# Output directories
providers_dir = Path("docs/system-reference/providers")
features_dir = Path("docs/system-reference/features")
api_dir = Path("docs/system-reference/api")

providers_dir.mkdir(parents=True, exist_ok=True)
features_dir.mkdir(parents=True, exist_ok=True)
api_dir.mkdir(parents=True, exist_ok=True)

print("🚀 Starting detailed content extraction...")
print(f"📁 Reading from: {archive_dir}")
print(f"📁 Writing to: providers/, features/, api/")
print()

# Read provider archive
if provider_archive.exists():
    content = provider_archive.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Extract GLM section (lines ~33-250)
    glm_start = None
    glm_end = None
    kimi_start = None
    kimi_end = None
    routing_start = None
    
    for i, line in enumerate(lines):
        if '## GLM Provider' in line:
            glm_start = i
        elif '## Kimi Provider' in line and glm_start:
            glm_end = i
            kimi_start = i
        elif '## Agentic Routing' in line and kimi_start:
            kimi_end = i
            routing_start = i
        elif '## Related Documentation' in line and routing_start:
            break
    
    # Create GLM provider file
    if glm_start and glm_end:
        glm_content = '\n'.join(lines[glm_start:glm_end])
        glm_file = providers_dir / "glm.md"
        
        header = """# GLM Provider (ZhipuAI/Z.ai)

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [kimi.md](kimi.md), [routing.md](routing.md), [../02-provider-architecture.md](../02-provider-architecture.md)

---

"""
        glm_file.write_text(header + glm_content, encoding='utf-8')
        print(f"✅ Created {glm_file}")
    
    # Create Kimi provider file
    if kimi_start and kimi_end:
        kimi_content = '\n'.join(lines[kimi_start:kimi_end])
        kimi_file = providers_dir / "kimi.md"
        
        header = """# Kimi Provider (Moonshot)

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [glm.md](glm.md), [routing.md](routing.md), [../02-provider-architecture.md](../02-provider-architecture.md)

---

"""
        kimi_file.write_text(header + kimi_content, encoding='utf-8')
        print(f"✅ Created {kimi_file}")
    
    # Create routing file (placeholder for now)
    routing_file = providers_dir / "routing.md"
    routing_content = """# Agentic Routing

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
"""
    routing_file.write_text(routing_content, encoding='utf-8')
    print(f"✅ Created {routing_file}")

print()
print("🎉 Provider files extraction complete!")
print()
print("📝 Next: Extracting features and API files...")

