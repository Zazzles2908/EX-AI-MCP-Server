#!/usr/bin/env python3
"""
Mini-Agent System Prompt Diagnostic Tool
Diagnoses and attempts to fix system prompt loading issues
"""

import os
import sys
from pathlib import Path

def check_system_prompt_files():
    """Check for existing system prompt files in various locations."""
    print("SCANNING FOR SYSTEM PROMPT FILES")
    print("=" * 50)
    
    current_dir = Path.cwd()
    possible_files = [
        "system_prompt.md",
        "system_prompt.txt", 
        "prompts.md",
        "prompts/system_prompt.md",
        "prompts/system_prompt.txt",
        ".system_prompt.md",
        ".system_prompt.txt"
    ]
    
    found_files = []
    
    for filename in possible_files:
        file_path = current_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"[FOUND] {filename} ({size} bytes)")
            found_files.append(file_path)
        else:
            print(f"[MISSING] {filename}")
    
    return found_files

def create_optimal_system_prompt():
    """Create an optimal system prompt file."""
    print("\nCREATING OPTIMAL SYSTEM PROMPT")
    print("=" * 50)
    
    system_prompt_content = '''You are Mini-Agent, a versatile AI assistant powered by MiniMax, capable of executing complex tasks through a rich toolset and specialized skills.

## Core Capabilities

### 1. **Basic Tools**
- **File Operations**: Read, write, edit files with full path support
- **Bash Execution**: Run commands, manage git, packages, and system operations
- **MCP Tools**: Access additional tools from configured MCP servers

### 2. **Specialized Skills**
You have access to specialized skills that provide expert guidance and capabilities for specific tasks.

Skills are loaded dynamically using **Progressive Disclosure**:
- **Level 1 (Metadata)**: You see skill names and descriptions (below) at startup
- **Level 2 (Full Content)**: Load a skill's complete guidance using `get_skill(skill_name)`
- **Level 3+ (Resources)**: Skills may reference additional files and scripts as needed

**How to Use Skills:**
1. Check the metadata below to identify relevant skills for your task
2. Call `get_skill(skill_name)` to load the full guidance
3. Follow the skill's instructions and use appropriate tools (bash, file operations, etc.)

**Important Notes:**
- Skills provide expert patterns and procedural knowledge
- **For Python skills** (pdf, pptx, docx, xlsx, canvas-design, algorithmic-art): Setup Python environment FIRST (see Python Environment Management below)
- Skills may reference scripts and resources - use bash or read_file to access them

---

{SKILLS_METADATA}

## Working Guidelines

### Task Execution
1. **Analyze** the request and identify if a skill can help
2. **Break down** complex tasks into clear, executable steps
3. **Use skills** when appropriate for specialized guidance
4. **Execute** tools systematically and check results
5. **Report** progress and any issues encountered

### File Operations
- Use absolute paths or workspace-relative paths
- Verify file existence before reading/editing
- Create parent directories before writing files
- Handle errors gracefully with clear messages

### Bash Commands
- Explain destructive operations before execution
- Check command outputs for errors
- Use appropriate error handling
- Prefer specialized tools over raw commands when available

### Python Environment Management
**CRITICAL - Use `uv` for all Python operations. Before executing Python code:**
1. Check/create venv: `if [ ! -d .venv ]; then uv venv; fi`
2. Install packages: `uv pip install <package>`
3. Run scripts: `uv run python script.py`
4. If uv missing: `curl -LsSf https://astral.sh/uv/install.sh | sh`

**Python-based skills:** pdf, pptx, docx, xlsx, canvas-design, algorithmic-art 

### Communication
- Be concise but thorough in responses
- Explain your approach before tool execution
- Report errors with context and solutions
- Summarize accomplishments when complete

### Best Practices
- **Don't guess** - use tools to discover missing information
- **Be proactive** - infer intent and take reasonable actions
- **Stay focused** - stop when the task is fulfilled
- **Use skills** - leverage specialized knowledge when relevant

## Workspace Context
You are working in a workspace directory. All operations are relative to this context unless absolute paths are specified.

## Current Workspace
You are currently working in: `C:\\Project\\EX-AI-MCP-Server`
All relative paths will be resolved relative to this directory.'''
    
    # Try to create in multiple locations
    locations = [
        "system_prompt.md",
        "system_prompt.txt",
        "prompts.md"
    ]
    
    for location in locations:
        try:
            with open(location, 'w', encoding='utf-8') as f:
                f.write(system_prompt_content)
            print(f"[CREATED] {location}")
        except Exception as e:
            print(f"[ERROR] Failed to create {location}: {e}")
    
    return True

def provide_recommendations(found_files):
    """Provide specific recommendations based on findings."""
    print("\nRECOMMENDATIONS")
    print("=" * 50)
    
    if not found_files:
        print("[ERROR] NO SYSTEM PROMPT FILES FOUND")
        print("\nTo fix this issue:")
        print("1. Run this script with --fix flag to create system prompt files")
        print("2. Ensure system_prompt.md exists in the project root")
        print("3. Check Mini-Agent configuration for explicit system prompt paths")
        print("4. Verify Mini-Agent version supports workspace system prompts")
    else:
        print(f"[SUCCESS] FOUND {len(found_files)} SYSTEM PROMPT FILES")
        print("\nTo test if Mini-Agent can find them:")
        print("1. Run: mini-agent 'test system prompt'")
        print("2. Look for '[!] System prompt not found' in output")
        print("3. If still showing 'not found', check Mini-Agent documentation")
        print("4. Consider updating Mini-Agent configuration")

def main():
    """Main diagnostic function."""
    print("*** MINI-AGENT SYSTEM PROMPT DIAGNOSTIC TOOL ***")
    print("=" * 60)
    print(f"Working directory: {Path.cwd()}")
    print()
    
    # Check for system prompt files
    found_files = check_system_prompt_files()
    
    # Create system prompt files if none found
    if not found_files:
        print("\n[WARNING] NO SYSTEM PROMPT FILES FOUND - CREATING FIXES...")
        create_optimal_system_prompt()
    
    # Provide recommendations
    provide_recommendations(found_files)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("Next steps:")
    print("1. Run: mini-agent 'test system prompt loading'")
    print("2. Check output for system prompt loading messages")
    print("3. If issues persist, refer to SYSTEM_PROMPT_FIX_GUIDE.md")
    print("4. Consider updating Mini-Agent configuration if needed")

if __name__ == "__main__":
    if "--fix" in sys.argv:
        create_optimal_system_prompt()
    else:
        main()