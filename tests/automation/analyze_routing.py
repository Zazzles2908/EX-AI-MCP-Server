#!/usr/bin/env python3
"""
Comprehensive Project Analysis for Smart Routing Documentation
"""

import os
import sys

def analyze_project():
    """Analyze the entire EX-AI MCP Server project structure"""

    print("=" * 80)
    print("EX-AI MCP SERVER - COMPREHENSIVE PROJECT ANALYSIS")
    print("=" * 80)

    # 1. Project Structure
    print("\n[PROJECT STRUCTURE]")
    print("-" * 80)

    structure = {
        "src/": ["providers/", "prompts/", "daemon/", "storage/", "config/"],
        "tools/": ["workflows/", "simple/", "shared/", "capabilities/"],
        "scripts/": ["dev/", "testing/", "database/"],
        "utils/": ["caching/", "observability/", "infrastructure/"],
        "docs/": ["architecture/", "development/", "getting-started/"],
        "documents/": ["01-architecture-overview/", "02-database-integration/",
                      "03-security-authentication/", "04-api-tools-reference/",
                      "05-operations-management/", "06-development-guides/"]
    }

    for folder, subfolders in structure.items():
        print(f"\n{folder}")
        for subfolder in subfolders:
            print(f"  └─ {subfolder}")

    # 2. Provider System
    print("\n\n[PROVIDER SYSTEM]")
    print("-" * 80)

    providers = {
        "GLM (ZhipuAI)": {
            "models": ["glm-4.6", "glm-4.5", "glm-4.5-flash", "glm-4.5v"],
            "capabilities": ["web_search", "streaming", "vision", "tool_calling"],
            "files": ["src/providers/glm.py", "src/providers/glm_provider.py",
                     "src/providers/async_glm.py"]
        },
        "Kimi (Moonshot)": {
            "models": ["kimi-k2-0905-preview", "kimi-k2-0711-preview", "kimi-thinking-preview"],
            "capabilities": ["file_uploads", "thinking", "vision", "tool_calling"],
            "files": ["src/providers/kimi.py", "src/providers/async_kimi.py",
                     "src/providers/kimi_cache.py"]
        }
    }

    for name, details in providers.items():
        print(f"\n{name}:")
        print(f"  Models: {', '.join(details['models'])}")
        print(f"  Capabilities: {', '.join(details['capabilities'])}")

    # 3. Routing System Analysis
    print("\n\n[ROUTING SYSTEM ANALYSIS]")
    print("-" * 80)

    print("\n[EXISTS BUT NOT USED] CapabilityRouter (src/providers/capability_router.py)")
    print("  ✓ CapabilityMatrix - Provider capability definitions")
    print("  ✓ ToolRequirements - Tool capability needs")
    print("  ✓ ExecutionPath - 7 routing strategies")
    print("  ✓ route_request() - Smart routing logic")
    print("  ✓ get_optimal_provider() - Provider recommendation")
    print("  ✗ ZERO integration with tool execution!")

    print("\n[ACTUALLY USED] Simple Category Routing (src/providers/registry_selection.py)")
    print("  • ToolModelCategory (3 types):")
    print("    - FAST_RESPONSE → GLM-4.6 only")
    print("    - EXTENDED_REASONING → Kimi K2 models only")
    print("    - BALANCED → GLM-4.5 series")
    print("  • Static fallback chains (no cross-provider)")
    print("  • No capability validation")

    # 4. Tools Analysis
    print("\n\n[MCP TOOLS ANALYSIS]")
    print("-" * 80)

    tools = {
        "Essential (3)": ["status", "chat", "planner"],
        "Core (8)": ["analyze", "codereview", "debug", "refactor", "testgen",
                    "thinkdeep", "smart_file_query", "smart_file_download"],
        "Advanced (7)": ["consensus", "docgen", "secaudit", "tracer", "precommit",
                        "kimi_chat_with_tools", "glm_payload_preview"],
        "Hidden (11)": ["provider_capabilities", "listmodels", "activity",
                       "version", "health", "toolcall_log_tail", "test_echo",
                       "kimi_capture_headers", "kimi_intent_analysis",
                       "kimi_manage_files", "glm_web_search"]
    }

    total_tools = sum(len(tools) for tools in tools.values())
    print(f"\nTotal MCP Tools: {total_tools}")
    print(f"Tool Organization: 4-tier visibility system")

    for tier, tool_list in tools.items():
        print(f"\n{tier}:")
        print(f"  {', '.join(tool_list)}")

    # 5. Capability Requirements
    print("\n\n[TOOL CAPABILITY REQUIREMENTS]")
    print("-" * 80)

    print("\nDefined in capability_router.py TOOL_REQUIREMENTS:")
    defined_tools = ["chat", "analyze", "codereview", "debug", "refactor", "secaudit",
                    "precommit", "testgen", "thinkdeep", "tracer", "planner", "docgen",
                    "consensus", "activity", "health", "listmodels", "version"]

    print(f"\nDefined tools: {len(defined_tools)}")
    print(f"Missing tools: {total_tools - len(defined_tools)} tools have NO capability requirements!")

    # 6. Key Findings
    print("\n\n[KEY FINDINGS]")
    print("-" * 80)

    findings = [
        "1. CAPABILITYROUTER IS ORPHANED - Sophisticated routing exists but unused",
        "2. TOOL REQUIREMENTS INCOMPLETE - 17 tools missing capability definitions",
        "3. STATIC CATEGORY ROUTING - Simple, but not intelligent",
        "4. NO RUNTIME VALIDATION - Provider capabilities not checked",
        "5. DOCUMENTATION GAPS - Architecture says 'intelligent' but implementation is basic",
        "6. WEB SEARCH BUG - Kimi doesn't support web_search but tools may try to use it",
        "7. HIGH IMPACT OPPORTUNITY - Connect existing CapabilityRouter for major improvement"
    ]

    for finding in findings:
        print(f"\n  {finding}")

    # 7. Integration Strategy
    print("\n\n[INTEGRATION STRATEGY]")
    print("-" * 80)

    strategy = {
        "Phase 1 (1-2 days)": [
            "Connect CapabilityRouter to SimpleTool base class",
            "Add validation before provider selection",
            "Test with chat tool (web search + files)"
        ],
        "Phase 2 (3-5 days)": [
            "Add get_capability_requirements() to BaseTool",
            "Update CapabilityRouter for runtime requirements",
            "Migrate core tools to dynamic requirements"
        ],
        "Phase 3 (5-7 days)": [
            "Refactor provider selection to use get_optimal_provider()",
            "Add cost-aware routing",
            "Implement comprehensive fallbacks"
        ],
        "Phase 4 (2-3 days)": [
            "Cache routing decisions",
            "Add performance monitoring",
            "Fine-tune provider preferences"
        ]
    }

    for phase, tasks in strategy.items():
        print(f"\n{phase}:")
        for task in tasks:
            print(f"  • {task}")

    # 8. Documentation Structure for 07-smart-routing
    print("\n\n[DOCUMENTATION STRUCTURE]")
    print("-" * 80)

    doc_structure = [
        "07-smart-routing/",
        "  ├─ index.md (Main navigation)",
        "  ├─ 01_routing_architecture.md (Design and components)",
        "  ├─ 02_capability_matrix.md (Provider capabilities table)",
        "  ├─ 03_tool_requirements.md (Tool capability needs)",
        "  ├─ 04_routing_decisions.md (How routing works)",
        "  ├─ 05_implementation_guide.md (How to add new routing)",
        "  ├─ 06_troubleshooting.md (Common issues and fixes)",
        "  └─ 07_best_practices.md (Guidelines and examples)"
    ]

    for line in doc_structure:
        print(f"  {line}")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    analyze_project()
