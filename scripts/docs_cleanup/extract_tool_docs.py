#!/usr/bin/env python3
"""
Extract individual tool documentation from 03-tool-ecosystem.md
and create separate markdown files in tools/ subfolder.
"""

import re
from pathlib import Path

# Read the source file
source_file = Path("docs/system-reference/03-tool-ecosystem.md")
content = source_file.read_text(encoding='utf-8')

# Define tool sections to extract
tools = {
    'codereview': {'start': 583, 'end': 680, 'folder': 'workflow-tools'},
    'refactor': {'start': 715, 'end': 821, 'folder': 'workflow-tools'},
    'testgen': {'start': 825, 'end': 914, 'folder': 'workflow-tools'},
    'tracer': {'start': 918, 'end': 1025, 'folder': 'workflow-tools'},
    'secaudit': {'start': 1029, 'end': 1121, 'folder': 'workflow-tools'},
    'docgen': {'start': 1123, 'end': 1211, 'folder': 'workflow-tools'},
}

# Split content into lines
lines = content.split('\n')

# Extract and save each tool
for tool_name, info in tools.items():
    start_idx = info['start'] - 1  # Convert to 0-based index
    end_idx = info['end']
    
    # Extract lines for this tool
    tool_lines = lines[start_idx:end_idx]
    
    # Remove the ### heading and get the tool name
    if tool_lines[0].startswith('###'):
        tool_lines[0] = f"# {tool_lines[0][4:]}"  # Convert ### to #
    
    # Add header
    header = f"""**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [debug.md](debug.md)

---

"""
    
    # Insert header after the title
    tool_lines.insert(1, '')
    tool_lines.insert(2, header)
    
    # Create the file
    output_path = Path(f"docs/system-reference/tools/{info['folder']}/{tool_name}.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_path.write_text('\n'.join(tool_lines), encoding='utf-8')
    print(f"✅ Created {output_path}")

print("\n🎉 All tool files created successfully!")

