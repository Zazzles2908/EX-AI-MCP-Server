#!/usr/bin/env python3
"""
Find the source of the _model_name error
"""

import re
import os

error_pattern = re.compile(r"f[^\n]*\{[^}]*_model_name[^}]*\}[^\n]*", re.MULTILINE)

# Search all Python files
for root, dirs, files in os.walk('c:/Project/EX-AI-MCP-Server/src'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = error_pattern.findall(content)
                    for match in matches:
                        # Check if _model_name is defined in the same scope
                        line_num = content[:content.find(match)].count('\n') + 1
                        print(f"{filepath}:{line_num}: {match.strip()}")
            except Exception as e:
                pass
