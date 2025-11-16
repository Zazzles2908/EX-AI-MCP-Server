# System Prompt Loading - Diagnostic & Fix Guide

## Issue Analysis

The Mini-Agent is showing `"System prompt not found, using default"` despite having `system_prompt.md` in the project root. This indicates a path resolution or configuration issue.

## Root Cause Investigation

### Current File Locations
```
C:\Project\EX-AI-MCP-Server\system_prompt.md          (Original - not being found)
C:\Project\EX-AI-MCP-Server\prompts.md                (New - alternative location)
C:\Project\EX-AI-MCP-Server\system_prompt.txt         (New - alternative format)
```

### Potential Causes
1. **Case Sensitivity**: Mini-Agent may expect specific casing
2. **File Extension**: May require `.txt` instead of `.md`
3. **Location**: May expect prompts in a different directory
4. **Configuration**: May need explicit configuration in Mini-Agent settings

## Immediate Fixes Applied

### 1. Multiple Fallback Locations Created
- ✅ `prompts.md` - Alternative markdown location
- ✅ `system_prompt.txt` - Plain text format

### 2. Configuration Updates
Added system prompt configuration to Mini-Agent config files if needed.

## Testing & Validation

To test if the system prompt is now loading:

```bash
cd C:\Project\EX-AI-MCP-Server
mini-agent "test prompt loading" --verbose
```

Look for:
- ❌ `[!] System prompt not found, using default` (ISSUE)
- ✅ `[OK] System prompt loaded from [location]` (SUCCESS)

## Advanced Troubleshooting

### Check Mini-Agent System Prompt Search Paths
The Mini-Agent likely searches in this order:
1. `./system_prompt.md` (current working directory)
2. `./prompts/system_prompt.md`
3. `./prompts.md`
4. Configuration-defined path

### Environment Variables Check
```bash
# Check if any environment variables affect system prompt loading
env | grep -i prompt
env | grep -i system
```

## Long-term Solution

### Recommended Structure
```
workspace/
├── system_prompt.md           # Primary system prompt
├── prompts.md                 # Fallback markdown
├── system_prompt.txt          # Fallback text
└── .mini-agent/               # Mini-Agent config
    └── config/
        └── system_prompt_path # Explicit path config (if supported)
```

### Configuration File Update
If Mini-Agent supports explicit system prompt paths, add to config:
```yaml
system_prompt:
  path: "./system_prompt.md"
  fallback_paths:
    - "./prompts.md"
    - "./system_prompt.txt"
```

## Verification Commands

### Quick Test
```bash
cd C:\Project\EX-AI-MCP-Server
echo "Testing system prompt..." > test_prompt.txt
mini-agent "respond with: SYSTEM_PROMPT_WORKING" 2>&1 | grep -i "system"
```

### Detailed Analysis
```bash
cd C:\Project\EX-AI-MCP-Server
# Run Mini-Agent with verbose output
mini-agent --verbose "check system prompt loading" 2>&1
```

## Expected Outcomes

### Before Fix
```
[!] System prompt not found, using default
[OK] Injected 15 skills metadata into system prompt
```

### After Fix
```
[OK] System prompt loaded from ./system_prompt.md
[OK] Injected 15 skills metadata into system prompt
```

## Next Steps

1. **Test the fixes** by running Mini-Agent again
2. **Monitor output** for system prompt loading messages
3. **If still failing**, check Mini-Agent version and documentation for exact expected locations
4. **Consider updating** Mini-Agent configuration if explicit paths are supported

---

*Created: 2025-11-16 19:58:00 AEDT*
*Purpose: Diagnose and resolve Mini-Agent system prompt loading issues*