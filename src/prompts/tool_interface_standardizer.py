"""
Tool Interface Standardizer

Ensures all AI tools follow consistent interface patterns, parameter structures,
and response formats. Provides validation and auto-correction capabilities.

Universal Design - Works with any project or AI provider.
"""

import ast
import inspect
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class InterfaceIssue(Enum):
    """Types of interface standardization issues."""
    MISSING_METHOD = "missing_method"
    INCONSISTENT_PARAMETER = "inconsistent_parameter"
    MISSING_DOCSTRING = "missing_docstring"
    INCORRECT_RETURN_TYPE = "incorrect_return_type"
    MISSING_FIELD_DESCRIPTION = "missing_field_description"
    INCONSISTENT_NAMING = "inconsistent_naming"
    MISSING_DEFAULT_VALUE = "missing_default_value"
    INCORRECT_SCHEMA_FORMAT = "incorrect_schema_format"


@dataclass
class StandardInterface:
    """Standard interface definition for AI tools."""
    required_methods: List[str]
    required_fields: List[str]
    standard_parameters: Dict[str, Any]
    response_format: Dict[str, Any]
    error_handling: Dict[str, Any]


@dataclass
class InterfaceValidationResult:
    """Result of interface validation."""
    tool_name: str
    is_compliant: bool
    issues: List[Tuple[InterfaceIssue, str, str]]  # (issue_type, field/method, message)
    recommendations: List[str]
    auto_fixes: List[str]


class ToolInterfaceStandardizer:
    """
    Validates and standardizes tool interfaces across all AI tools.

    Ensures consistency in:
    - Method signatures
    - Parameter naming and types
    - Field descriptions
    - Response formats
    - Error handling
    """

    # Standard interface specification
    STANDARD_INTERFACE = StandardInterface(
        required_methods=[
            "get_name",
            "get_description",
            "get_system_prompt",
            "get_default_temperature",
            "get_model_category",
            "get_request_model",
            "get_tool_fields",
            "get_required_fields",
            "get_annotations"
        ],
        required_fields=[
            "prompt",
            "files",
            "images",
            "model",
            "temperature",
            "use_websearch",
            "stream"
        ],
        standard_parameters={
            "prompt": {
                "type": "string",
                "description": "Required: Task description with detailed context"
            },
            "files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional: File paths for context (<5KB each)"
            },
            "images": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional: Image paths for visual context"
            },
            "model": {
                "type": "string",
                "description": "Optional: Specific model to use (auto-selects if not specified)"
            },
            "temperature": {
                "type": "number",
                "description": "Optional: Randomness level (0.0-1.0, default varies by tool)"
            },
            "use_websearch": {
                "type": "boolean",
                "description": "Optional: Enable web search (default: true)"
            },
            "stream": {
                "type": "boolean",
                "description": "Optional: Enable streaming response (default: false)"
            }
        },
        response_format={
            "format": "markdown",
            "includes_metadata": True,
            "includes_timing": True,
            "includes_model_info": True
        },
        error_handling={
            "validation_errors": "return_formatted_error",
            "execution_errors": "return_formatted_error",
            "timeout_errors": "return_formatted_error",
            "provider_errors": "return_formatted_error"
        }
    )

    # Known tool implementations
    KNOWN_TOOLS = {
        "chat": "tools/chat.py",
        "debug": "tools/debug.py",
        "analyze": "tools/analyze.py",
        "codereview": "tools/codereview.py",
        "thinkdeep": "tools/thinkdeep.py",
        "refactor": "tools/refactor.py",
        "testgen": "tools/testgen.py",
        "docgen": "tools/docgen.py",
        "planner": "tools/planner.py",
        "tracer": "tools/tracer.py",
        "consensus": "tools/consensus.py",
        "secaudit": "tools/secaudit.py",
        "precommit": "tools/precommit.py"
    }

    def validate_tool_interface(self, tool_path: str, tool_name: str) -> InterfaceValidationResult:
        """
        Validate a tool's interface against the standard.

        Args:
            tool_path: Path to the tool file
            tool_name: Name of the tool

        Returns:
            Validation result with issues and recommendations
        """
        issues = []
        recommendations = []
        auto_fixes = []

        try:
            with open(tool_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            # Parse AST
            tree = ast.parse(source_code)

            # Find tool class
            tool_class = self._find_tool_class(tree, tool_name)
            if not tool_class:
                issues.append((
                    InterfaceIssue.MISSING_METHOD,
                    "class",
                    f"Tool class '{tool_name}' not found"
                ))
                return InterfaceValidationResult(
                    tool_name=tool_name,
                    is_compliant=False,
                    issues=issues,
                    recommendations=recommendations,
                    auto_fixes=auto_fixes
                )

            # Validate required methods
            methods = {node.name: node for node in ast.walk(tool_class)
                      if isinstance(node, ast.FunctionDef)}

            for required_method in self.STANDARD_INTERFACE.required_methods:
                if required_method not in methods:
                    issues.append((
                        InterfaceIssue.MISSING_METHOD,
                        required_method,
                        f"Missing required method: {required_method}"
                    ))
                    recommendations.append(f"Implement {required_method}() method")
                    auto_fixes.append(f"Add stub for {required_method}()")

            # Validate field definitions
            field_definitions = self._extract_field_definitions(source_code)
            for required_field in self.STANDARD_INTERFACE.required_fields:
                if required_field not in field_definitions:
                    issues.append((
                        InterfaceIssue.MISSING_FIELD_DESCRIPTION,
                        required_field,
                        f"Missing field definition: {required_field}"
                    ))
                    recommendations.append(f"Add {required_field} field to tool schema")
                    auto_fixes.append(f"Define {required_field} field")

            # Check for consistent naming
            if not tool_name.endswith('Tool'):
                issues.append((
                    InterfaceIssue.INCONSISTENT_NAMING,
                    "class_name",
                    f"Tool class should be named '{tool_name}Tool'"
                ))

            # Check docstrings
            if not (tool_class.body and isinstance(tool_class.body[0], ast.Expr) and
                   isinstance(tool_class.body[0].value, ast.Constant)):
                issues.append((
                    InterfaceIssue.MISSING_DOCSTRING,
                    "class_docstring",
                    "Missing class docstring"
                ))

        except Exception as e:
            issues.append((
                InterfaceIssue.INCORRECT_RETURN_TYPE,
                "parsing",
                f"Error parsing tool file: {str(e)}"
            ))

        is_compliant = len(issues) == 0

        return InterfaceValidationResult(
            tool_name=tool_name,
            is_compliant=is_compliant,
            issues=issues,
            recommendations=recommendations,
            auto_fixes=auto_fixes
        )

    def _find_tool_class(self, tree: ast.AST, tool_name: str) -> Optional[ast.ClassDef]:
        """Find the tool class in the AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.lower() == tool_name.lower():
                    return node
                if node.name == f"{tool_name}Tool":
                    return node
        return None

    def _extract_field_definitions(self, source_code: str) -> Dict[str, str]:
        """Extract field definitions from source code."""
        fields = {}

        # Look for FIELD_DESCRIPTIONS or field definitions
        import re

        # Pattern 1: FIELD_DESCRIPTIONS = {...}
        pattern1 = r'(\w+)_FIELD_DESCRIPTIONS\s*=\s*\{([^}]+)\}'
        matches1 = re.finditer(pattern1, source_code, re.MULTILINE | re.DOTALL)
        for match in matches1:
            field_name = match.group(1).lower()
            fields[field_name] = "defined"

        # Pattern 2: Field definitions in class
        pattern2 = r'(\w+):\s*(?:[^=]+)=\s*Field\('
        matches2 = re.finditer(pattern2, source_code)
        for match in matches2:
            field_name = match.group(1).lower()
            fields[field_name] = "pydantic_field"

        return fields

    def validate_all_tools(self) -> List[InterfaceValidationResult]:
        """
        Validate all known AI tools.

        Returns:
            List of validation results for all tools
        """
        results = []

        for tool_name, tool_path in self.KNOWN_TOOLS.items():
            result = self.validate_tool_interface(tool_path, tool_name)
            results.append(result)

        return results

    def generate_standard_interface_template(self, tool_name: str) -> str:
        """
        Generate a standard interface template for a new tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Template code for the tool
        """
        template = f'''"""
{tool_name.title()} Tool - [Brief description of tool purpose]

[Detailed description of what the tool does, when to use it,
and what kind of results it provides.]

Universal Design - Works with any project or AI provider.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Field descriptions
{tool_name.upper()}_FIELD_DESCRIPTIONS = {{
    "prompt": (
        "You MUST provide a thorough, expressive [task description] with as much context as possible. "
        "IMPORTANT: [Specific instructions for this tool]. "
        "Remember: [Key reminders about context, file usage, or response format]."
    ),
    "files": (
        "Optional files for context - EMBEDS CONTENT AS TEXT in prompt (not uploaded to platform). "
        "Use for small files (<5KB). For large files or persistent reference, use appropriate file handling tool. "
        "(must be FULL absolute paths to real files / folders - DO NOT SHORTEN)"
    ),
    "images": (
        "Optional images for visual context. Useful for [use cases]. "
        "(must be FULL absolute paths to real files / folders - DO NOT SHORTEN - OR these can be base64 data)"
    ),
}}


# Standard tool interface
class {tool_name.title()}Request:
    """Request model for {tool_name.title()} tool - customize for your framework"""

    prompt: str
    files: Optional[List[str]] = None
    images: Optional[List[str]] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    use_websearch: Optional[bool] = None


class {tool_name.title()}Tool:
    """
    [Tool description - what it does, when to use it]

    This tool provides [functionality] and is designed for [use cases].
    Customize this class for your specific framework.

    Universal Design - Works with any project or AI provider.
    """

    def get_name(self) -> str:
        """Return the name of the tool."""
        return "{tool_name}"

    def get_description(self) -> str:
        """Return description of the tool."""
        return (
            "[ONE LINE DESCRIPTION]\\n\\n"
            "✅ USE THIS FOR:\\n"
            "- [Use case 1]\\n"
            "- [Use case 2]\\n"
            "- [Use case 3]\\n\\n"
            "❌ DON'T USE THIS FOR:\\n"
            "- [What not to use it for]\\n\\n"
            "HOW IT WORKS:\\n"
            "- [Explanation of workflow]\\n"
            "- [Key capabilities]\\n\\n"
            "🔧 CAPABILITIES:\\n"
            "- [Capability 1]\\n"
            "- [Capability 2]\\n\\n"
            "📊 WORKFLOW ESCALATION:\\n"
            "[tool] → [next_tool] → [next_tool]\\n"
        )

    def _get_related_tools(self) -> dict[str, list[str]]:
        """Return related tools for escalation patterns"""
        return {{
            "escalation": ["[related_tool1]", "[related_tool2]"],
            "alternatives": ["[alternative_tool]"]
        }}

    def get_system_prompt(self) -> str:
        return {tool_name.upper()}_PROMPT

    def get_default_temperature(self) -> float:
        return TEMPERATURE_BALANCED

    def get_model_category(self) -> "ToolModelCategory":
        """[Tool model category rationale]"""
        from tools.models import ToolModelCategory

        return ToolModelCategory.[CATEGORY]

    def get_request_model(self):
        """Return the {tool_name.title()}-specific request model"""
        return {tool_name.title()}Request
'''

        return template

    def generate_interface_report(self, results: List[InterfaceValidationResult]) -> str:
        """
        Generate a comprehensive interface standardization report.

        Args:
            results: List of validation results

        Returns:
            Formatted report
        """
        report = []
        report.append("="*70)
        report.append("TOOL INTERFACE STANDARDIZATION REPORT")
        report.append("="*70)
        report.append("")

        # Summary
        compliant_count = sum(1 for r in results if r.is_compliant)
        total_count = len(results)

        report.append(f"Total Tools: {total_count}")
        report.append(f"Compliant: {compliant_count} ({compliant_count/total_count*100:.0f}%)")
        report.append(f"Non-Compliant: {total_count - compliant_count} ({(total_count - compliant_count)/total_count*100:.0f}%)")
        report.append("")

        # Detailed results
        report.append("="*70)
        report.append("DETAILED RESULTS")
        report.append("="*70)
        report.append("")

        for result in results:
            status = "✓ COMPLIANT" if result.is_compliant else "✗ NON-COMPLIANT"
            report.append(f"{result.tool_name:20} | {status}")

            if result.issues:
                for issue_type, field, message in result.issues:
                    report.append(f"  - [{issue_type.value}] {field}: {message}")

            if result.recommendations:
                report.append("  Recommendations:")
                for rec in result.recommendations:
                    report.append(f"    • {rec}")

            report.append("")

        # Standard interface spec
        report.append("="*70)
        report.append("STANDARD INTERFACE SPECIFICATION")
        report.append("="*70)
        report.append("")
        report.append("Required Methods:")
        for method in self.STANDARD_INTERFACE.required_methods:
            report.append(f"  - {method}()")

        report.append("")
        report.append("Required Fields:")
        for field in self.STANDARD_INTERFACE.required_fields:
            report.append(f"  - {field}")

        report.append("")
        report.append("Standard Parameters:")
        for param, spec in self.STANDARD_INTERFACE.standard_parameters.items():
            report.append(f"  - {param}: {spec['type']} - {spec['description']}")

        return "\n".join(report)


def validate_tool_interfaces():
    """Main entry point for interface validation."""
    standardizer = ToolInterfaceStandardizer()
    results = standardizer.validate_all_tools()
    report = standardizer.generate_interface_report(results)

    # Print report
    print(report)

    # Save report
    with open("docs/reports/tool_interface_standardization_report.md", "w") as f:
        f.write("# Tool Interface Standardization Report\n\n")
        f.write(report)

    return results


if __name__ == "__main__":
    validate_tool_interfaces()
