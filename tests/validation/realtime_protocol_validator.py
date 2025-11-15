#!/usr/bin/env python3
"""
Real-time MCP Protocol Validator
Validates MCP protocol compliance in real-time
"""

import json
import re
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of a validation check"""
    valid: bool
    error_message: Optional[str] = None
    suggestions: List[str] = None

class RealtimeMCPValidator:
    """Real-time MCP protocol validator"""

    def __init__(self):
        self.validation_rules = {
            "jsonrpc_version": self._validate_jsonrpc_version,
            "id_present": self._validate_id_present,
            "method_present": self._validate_method_present,
            "params_present": self._validate_params_present,
            "tool_name": self._validate_tool_name,
            "required_fields": self._validate_required_fields,
            "argument_types": self._validate_argument_types,
        }

        self.known_tools = [
            "kimi_chat_with_tools",
            "analyze",
            "status",
            "listmodels",
            "glm_payload_preview"
        ]

        self.required_analyze_fields = [
            "step",
            "step_number",
            "total_steps",
            "next_step_required",
            "findings"
        ]

    def validate_message(self, message: str) -> Tuple[bool, List[str]]:
        """Validate an MCP message in real-time"""
        errors = []
        warnings = []

        try:
            # Parse JSON
            data = json.loads(message)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {str(e)}"]

        # Run validation rules
        for rule_name, rule_func in self.validation_rules.items():
            result = rule_func(data)
            if not result.valid:
                errors.append(result.error_message)
                if result.suggestions:
                    warnings.extend(result.suggestions)

        return len(errors) == 0, errors + warnings

    def validate_partial_message(self, partial: str) -> Dict[str, Any]:
        """Validate partial/incomplete message (for real-time feedback)"""
        feedback = {
            "complete": False,
            "valid_so_far": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "missing_fields": [],
            "completeness_percentage": 0
        }

        try:
            data = json.loads(partial)

            # Check completeness
            required_fields = ["jsonrpc", "id", "method"]
            missing = [f for f in required_fields if f not in data]
            feedback["missing_fields"] = missing

            if not missing and "params" not in data:
                feedback["missing_fields"].append("params")

            # Check if params is complete for tools/call
            if data.get("method") == "tools/call" and "params" in data:
                if "name" not in data["params"]:
                    feedback["missing_fields"].append("params.name (tool name)")
                if "arguments" not in data["params"]:
                    feedback["missing_fields"].append("params.arguments")

            # Calculate completeness
            total_required = len(required_fields) + 2  # + params + tool name
            completeness = (total_required - len(feedback["missing_fields"])) / total_required
            feedback["completeness_percentage"] = min(100, completeness * 100)

            if not feedback["missing_fields"]:
                feedback["complete"] = True

            # Provide suggestions
            if "jsonrpc" not in data:
                feedback["suggestions"].append('Add: "jsonrpc": "2.0"')

            if "id" not in data:
                feedback["suggestions"].append('Add: "id": "unique_id"')

            if data.get("method") == "tools/call" and "params" not in data:
                feedback["suggestions"].append('Add: "params": {...}')

        except json.JSONDecodeError as e:
            feedback["valid_so_far"] = False
            feedback["errors"].append(f"Invalid JSON so far: {str(e)}")
            feedback["suggestions"].append("Check JSON syntax - missing quote or comma?")

        return feedback

    def _validate_jsonrpc_version(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate JSON-RPC version"""
        if "jsonrpc" not in data:
            return ValidationResult(False, "Missing 'jsonrpc' field", [
                "Add: \"jsonrpc\": \"2.0\""
            ])

        if data["jsonrpc"] != "2.0":
            return ValidationResult(False, f"Invalid jsonrpc version: {data['jsonrpc']}", [
                "Use: \"jsonrpc\": \"2.0\""
            ])

        return ValidationResult(True)

    def _validate_id_present(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate ID field"""
        if "id" not in data:
            return ValidationResult(False, "Missing 'id' field", [
                "Add: \"id\": \"unique_request_id\""
            ])

        return ValidationResult(True)

    def _validate_method_present(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate method field"""
        if "method" not in data:
            return ValidationResult(False, "Missing 'method' field", [
                "Common methods: \"initialize\", \"tools/list\", \"tools/call\""
            ])

        return ValidationResult(True)

    def _validate_params_present(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate params field for tools/call"""
        if data.get("method") == "tools/call":
            if "params" not in data:
                return ValidationResult(False, "Missing 'params' for tools/call", [
                    "Add: \"params\": {\"name\": \"tool_name\", \"arguments\": {...}}"
                ])

        return ValidationResult(True)

    def _validate_tool_name(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate tool name"""
        if data.get("method") != "tools/call":
            return ValidationResult(True)

        if "params" not in data:
            return ValidationResult(False, "Missing params")

        tool_name = data["params"].get("name")

        if not tool_name:
            return ValidationResult(False, "Missing tool name in params.name", [
                'Add: "name": "tool_name"'
            ])

        if tool_name not in self.known_tools:
            return ValidationResult(False, f"Unknown tool: {tool_name}", [
                f"Known tools: {', '.join(self.known_tools)}",
                'Tip: Use "kimi_chat_with_tools" not "chat"'
            ])

        return ValidationResult(True)

    def _validate_required_fields(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate required fields for specific tools"""
        if data.get("method") != "tools/call":
            return ValidationResult(True)

        if "params" not in data:
            return ValidationResult(False, "Missing params")

        tool_name = data["params"].get("name")

        if tool_name == "analyze":
            return self._validate_analyze_required_fields(data["params"])

        return ValidationResult(True)

    def _validate_analyze_required_fields(self, params: Dict[str, Any]) -> ValidationResult:
        """Validate required fields for analyze tool"""
        missing = [field for field in self.required_analyze_fields if field not in params]

        if missing:
            return ValidationResult(
                False,
                f"Missing required fields for analyze: {', '.join(missing)}",
                [
                    f'Add: "{field}": <value>' for field in missing
                ]
            )

        return ValidationResult(True)

    def _validate_argument_types(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate argument types"""
        if data.get("method") != "tools/call":
            return ValidationResult(True)

        if "params" not in data:
            return ValidationResult(False, "Missing params")

        # Validate analyze types
        if data["params"].get("name") == "analyze":
            return self._validate_analyze_types(data["params"])

        return ValidationResult(True)

    def _validate_analyze_types(self, params: Dict[str, Any]) -> ValidationResult:
        """Validate analyze argument types"""
        errors = []
        suggestions = []

        # Check step_number
        if "step_number" in params:
            if not isinstance(params["step_number"], int):
                errors.append("step_number must be an integer")
                suggestions.append('Use: "step_number": 1')

        # Check total_steps
        if "total_steps" in params:
            if not isinstance(params["total_steps"], int):
                errors.append("total_steps must be an integer")
                suggestions.append('Use: "total_steps": 1')

        # Check next_step_required
        if "next_step_required" in params:
            if not isinstance(params["next_step_required"], bool):
                errors.append("next_step_required must be a boolean")
                suggestions.append('Use: "next_step_required": true or false')

        if errors:
            return ValidationResult(False, "; ".join(errors), suggestions)

        return ValidationResult(True)

    def get_tool_documentation(self, tool_name: str) -> str:
        """Get documentation for a specific tool"""
        docs = {
            "kimi_chat_with_tools": """
kimi_chat_with_tools:
  description: Chat with AI models (GLM, KIMI, MiniMax)
  parameters:
    prompt (string, required): The chat prompt
    model (string, optional): Model name
    tools (array, optional): List of tools to enable
    tool_choice (string, optional): Tool selection strategy
  example:
    {
      "jsonrpc": "2.0",
      "id": "chat_1",
      "method": "tools/call",
      "params": {
        "name": "kimi_chat_with_tools",
        "arguments": {
          "prompt": "Hello!",
          "model": "kimi-k2-thinking"
        }
      }
    }
            """,
            "analyze": """
analyze:
  description: Structured analysis workflow
  required_parameters:
    step (string): Analysis description
    step_number (int): Current step index
    total_steps (int): Total steps
    next_step_required (bool): Continue to next step?
    findings (string): Summary of discoveries
  optional_parameters:
    files_checked (array): Files examined
    relevant_files (array): Relevant files
    relevant_context (array): Context information
    issues_found (array): Issues identified
  example:
    {
      "jsonrpc": "2.0",
      "id": "analyze_1",
      "method": "tools/call",
      "params": {
        "name": "analyze",
        "arguments": {
          "step": "Analyze the code",
          "step_number": 1,
          "total_steps": 1,
          "next_step_required": false,
          "findings": "Analysis complete"
        }
      }
    }
            """
        }

        return docs.get(tool_name, f"No documentation available for {tool_name}")

def main():
    """Interactive validator"""
    validator = RealtimeMCPValidator()

    print(f"\n{'='*80}")
    print(f"🔍 REAL-TIME MCP PROTOCOL VALIDATOR")
    print(f"{'='*80}")
    print("Enter MCP messages (JSON) to validate.")
    print("Type 'quit' to exit, 'help' for tool docs.\n")

    while True:
        try:
            message = input("> ")

            if message.lower() == "quit":
                break
            elif message.lower() == "help":
                print(f"\nAvailable tools: {', '.join(validator.known_tools)}")
                print("Use: docs <tool_name> to see documentation")
                continue
            elif message.startswith("docs "):
                tool = message.split(" ", 1)[1]
                print(validator.get_tool_documentation(tool))
                continue
            elif not message.strip():
                continue

            # Validate message
            valid, issues = validator.validate_message(message)

            if valid:
                print("✅ Message is valid!")
            else:
                print("❌ Validation errors:")
                for issue in issues:
                    print(f"  - {issue}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
