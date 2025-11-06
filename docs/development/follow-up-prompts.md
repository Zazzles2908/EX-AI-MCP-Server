# Follow-Up Prompts for Next Phase
## Strategic Execution Guide for System Improvement

**Date:** 2025-11-06
**Context:** After completing Phase 2 (Agents 1-4) and cleanup planning (Agent 5)

---

## 🎯 EXAI TOOL USAGE GUIDELINES

### Cost-Optimized Model Selection:
- **`kimi` ( cheapest ):** File analysis, code patterns, simple reviews
- **`glm-4.6` ( expensive ):** Complex architecture decisions, critical bugs, multi-system integration
- **`glm-4.5-flash` ( moderate ):** Quick validations, simple debugging
- **`auto` ( default ):** Let EXAI decide based on task complexity

### When to Use Which EXAI Tool:
| Tool | Best For | Model | Cost Level |
|------|----------|-------|------------|
| `mcp__exai-mcp__analyze` | Code patterns, structure analysis | kimi | Low |
| `mcp__exai-mcp__chat` | Strategy discussions, brainstorming | auto | Medium |
| `mcp__exai-mcp__codereview` | Code review, security audit | glm-4.6 | High |
| `mcp__exai-mcp__debug` | Critical bugs, complex issues | glm-4.6 | High |
| `mcp__exai-mcp__testgen` | Test generation | glm-4.5-flash | Medium |
| Manual Bash | File discovery, git operations | N/A | FREE |

---

## 📋 AGENT SELECTION MATRIX

### Option 1: ARCHITECTURE ASSESSMENT AGENT
**When to Use:** If you want strategic planning before execution

**Prompt:**
```
ARCHITECTURE ASSESSMENT AGENT

MISSION: Assess the best execution strategy for system improvement

STEP 1: Strategic Discussion (use mcp__exai-mcp__chat with model='auto')
QUESTION: "We have 4 incomplete agent outputs (Agent 1: performance, Agent 2: error handling, Agent 3: testing, Agent 4: architecture) plus cleanup needed. Should we:
A) Run 4 parallel agents to complete their work
B) Use 1 focused Agent 5 to do everything
C) Hybrid approach (parallel for independent, sequential for dependent)
Which is most cost-effective and effective given our scattered files (424 cache dirs, 85 scripts, 4 .env files)?"

STEP 2: File Investigation (use manual Bash, NO EXAI calls)
- Check .env.docker (48KB config) impact
- Assess 85 scripts in scripts/ for redundancy
- Verify Docker rebuild necessity
- Document scattered file inventory

STEP 3: Cost-Benefit Analysis (use mcp__exai-mcp__debug with model='kimi' for cost awareness)
QUESTION: "Analyze: 4 parallel agents × 2-3 hours = vs 1 agent × 6-8 hours. Include EXAI call costs. Recommend optimal approach."

OUTPUT: Clear recommendation (A, B, or C) with rationale
```

### Option 2: FILE INVESTIGATION AGENT
**When to Use:** Deep dive into scattered files before cleanup

**Prompt:**
```
FILE INVESTIGATION AGENT

MISSION: Comprehensive audit of scattered files, .env, Docker, scripts

INVESTIGATION (use manual Bash commands, FREE):
1. .env files analysis:
   - Document .env vs .env.docker differences
   - Check which vars are actually used in code
   - Identify Docker-specific configurations

2. Script inventory:
   - Map 85 scripts in scripts/
   - Find duplicates in other directories
   - Identify dead/unused scripts
   - Check for conflicting implementations

3. Docker impact:
   - Review docker-compose.yml
   - Check Dockerfile for build context
   - Determine if rebuild needed post-cleanup

4. Cache pollution:
   - Find all 424 __pycache__ locations
   - Identify .pyc files
   - Plan cleanup strategy

EXAI CALLS (use sparingly, model='kimi'):
- mcp__exai-mcp__analyze: "Review this .env.docker file - identify critical vs optional configurations"
- mcp__exai-mcp__chat: "Best strategy to handle 85 scripts with potential duplicates"

OUTPUT:
- Inventory report
- Critical file list
- Cleanup priority order
- Docker rebuild recommendation
```

### Option 3: COST-OPTIMIZED CLEANUP AGENT
**When to Use:** Execute cleanup with maximum cost efficiency

**Prompt:**
```
COST-OPTIMIZED CLEANUP AGENT (Repurposed Agent 5)

MISSION: Execute cleanup with minimal EXAI cost

PHASE 1: Assessment (FREE - manual commands only)
```bash
# Quick checks, no EXAI
ls -la | grep -E "\.(py|md)$" | wc -l
find . -name "__pycache__" | wc -l
git status --short | head -5
```

PHASE 2: Strategic Questions (use EXAI sparingly)
- ONLY use mcp__exai-mcp__debug for critical decisions (model='glm-4.6')
- Use mcp__exai-mcp__analyze for code patterns (model='kimi')
- NEVER use EXAI for file operations or git commands

PHASE 3: Execution Plan
Priority Order (FREE execution):
1. Remove cache: `find . -name "__pycache__" -exec rm -rf {} +`
2. Move root files: Keep only 5 essential
3. Consolidate tests
4. Update .gitignore
5. Fix imports
6. Format code

EXAI GUARDRAILS:
- Max 3 EXAI calls per phase
- Prefer model='kimi' (90% cheaper than glm-4.6)
- Use mcp__exai-mcp__chat only for architecture questions
- NO EXAI calls for: file moves, git operations, cache cleanup

OUTPUT: Clean codebase with <5 EXAI calls total
```

### Option 4: PARALLEL COMPLETION AGENTS
**When to Use:** If architecture assessment recommends parallel approach

**For Agent 2 (Error Handling):**
```
AGENT 2 COMPLETION AGENT

MISSION: Complete error handling standardization (12 direct exceptions remain)

STEPS:
1. Find remaining exceptions: `grep -r "raise Exception" src/ --include="*.py"`
2. Use mcp__exai-mcp__codereview (model='glm-4.5-flash', not 4.6):
   "Review these exception patterns and suggest standardized replacements"
3. Apply fixes manually
4. Verify framework adoption: `grep -r "error_handling" src/ --include="*.py" | wc -l`

COST: ~$0.20-0.40 (glm-4.5-flash vs glm-4.6)
```

**For Agent 3 (Testing):**
```
AGENT 3 ENHANCEMENT AGENT

MISSION: Complete test infrastructure, verify 220 tests

STEPS:
1. Test runner verification: `python scripts/run_all_tests.py --help`
2. Use mcp__exai-mcp__analyze (model='kimi', cheapest):
   "Review test runner implementation, suggest improvements"
3. Run quick tests: `python scripts/run_all_tests.py --type unit --quick`
4. Fix any failures

COST: ~$0.10-0.20 (kimi model)
```

**For Agent 4 (Architecture):**
```
AGENT 4 COMPLETION AGENT

MISSION: Complete singleton removal, finalize architecture

STEPS:
1. Check progress: `ls -la src/bootstrap/`
2. Use mcp__exai-mcp__debug (model='glm-4.5-flash'):
   "Review bootstrap/singletons.py and architecture changes needed"
3. Complete singleton removal
4. Verify architecture: `python -c "test imports"`

COST: ~$0.20-0.30
```

**For Agent 5 (Cleanup):**
```
AGENT 5 CLEANUP AGENT

MISSION: Execute comprehensive cleanup

STEPS:
1. Use mcp__exai-mcp__analyze (model='kimi') ONCE:
   "Analyze root directory pollution, suggest cleanup order"
2. Execute all cleanup manually (FREE)
3. Final validation: `python scripts/check-project-status.py`

COST: ~$0.10
```

---

## 💰 TOTAL COST COMPARISON

### Option 1 (Architecture First):
- Strategic EXAI calls: ~$0.30-0.50
- Investigation: FREE
- Execution: ~$0.50-0.80
- **Total: ~$0.80-1.30**

### Option 2 (File Investigation First):
- Investigation: FREE
- Analysis: ~$0.20-0.40
- **Total: ~$0.20-0.40**

### Option 3 (Direct Cleanup):
- Minimal EXAI: ~$0.30-0.50
- **Total: ~$0.30-0.50**

### Option 4 (Parallel Agents):
- 4 agents × ~$0.20 = ~$0.80
- **Total: ~$0.80**

---

## 🚀 RECOMMENDED APPROACH

**Based on cost and effectiveness:**

### IMMEDIATE (Next 2 hours):
1. **Use Option 2 (File Investigation Agent)** to understand the scope
2. Cost: ~$0.20-0.40
3. Output: Clear inventory and priorities

### THEN (Next 4-6 hours):
2. **Based on findings, choose:**
   - If files critical: Use Option 4 (Parallel Agents)
   - If cleanup safe: Use Option 3 (Direct Cleanup)
   - If complex: Use Option 1 (Architecture First)

### REASONING:
- Option 2 has lowest cost and highest information value
- Tells us exactly what we're dealing with
- Guides all subsequent decisions
- Prevents expensive mistakes

---

## 📝 QUICK START COMMANDS

**To launch the recommended approach:**

```bash
# Create the file investigation prompt
cat > /tmp/file-investigation-prompt.txt << 'EOF'
[Insert Option 2 prompt here]
EOF

# Start the agent
# (You would execute this prompt with Claude)
```

**Cost Tracking:**
```bash
# Track your EXAI spending
echo "EXAI calls made:" > /tmp/exai-cost.log
date >> /tmp/exai-cost.log
```

---

## ⚠️ CRITICAL REMINDERS

1. **Always start with Bash commands** for file discovery (FREE)
2. **Use model='kimi' by default** for 90% cost savings
3. **Reserve glm-4.6 for critical architecture only**
4. **Never use EXAI for file operations, git, or simple commands**
5. **Track EXAI calls** to stay within budget

---

## 🎯 SUCCESS METRICS

**After execution:**
- [ ] Root directory: 5 files max
- [ ] Cache files: 0 __pycache__
- [ ] Git status: Clean
- [ ] All imports: Working
- [ ] Tests: Passing
- [ ] Total EXAI cost: <$1.00

**Agent 5 will deliver:** Professional, enterprise-grade codebase ✨
