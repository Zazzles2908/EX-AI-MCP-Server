"""
Response Validator - Validate tool responses against success criteria

Validates:
- Response structure
- Response content
- Success criteria
- Error detection

Created: 2025-10-05
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ResponseValidator:
    """
    Validate tool responses against success criteria.
    
    Checks:
    - Response structure is valid
    - Required fields present
    - Response time within limits
    - No errors in response
    - Content quality
    """
    
    def __init__(self):
        """Initialize the response validator."""
        self.success_criteria = self._load_success_criteria()
        logger.info("Response validator initialized")
    
    def _load_success_criteria(self) -> Dict[str, Any]:
        """Load success criteria configuration."""
        # Default success criteria
        return {
            "execution": {
                "no_errors": True,
                "no_exceptions": True
            },
            "response_structure": {
                "has_content": True,
                "valid_json_or_text": True
            },
            "response_time": {
                "simple_tool_max_secs": 60,
                "workflow_tool_max_secs": 120,
                "provider_tool_max_secs": 90
            },
            "progress_heartbeat": {
                "required_for_long_ops": True,
                "min_interval_secs": 5
            },
            "logging": {
                "all_events_logged": True
            },
            "error_handling": {
                "graceful_errors": True
            }
        }
    
    def validate_response(
        self,
        response: Dict[str, Any],
        tool_type: str = "simple",
        expected_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate a tool response.
        
        Args:
            response: Response dictionary
            tool_type: Tool type (simple, workflow, provider)
            expected_fields: List of expected fields
        
        Returns:
            Validation result dictionary
        """
        validation_result = {
            "valid": True,
            "checks": {},
            "errors": [],
            "warnings": []
        }
        
        # Check 1: Execution (no errors)
        execution_check = self._check_execution(response)
        validation_result["checks"]["execution"] = execution_check
        if not execution_check["passed"]:
            validation_result["valid"] = False
            validation_result["errors"].extend(execution_check.get("errors", []))
        
        # Check 2: Response structure
        structure_check = self._check_structure(response, expected_fields)
        validation_result["checks"]["response_structure"] = structure_check
        if not structure_check["passed"]:
            validation_result["valid"] = False
            validation_result["errors"].extend(structure_check.get("errors", []))
        
        # Check 3: Response time
        time_check = self._check_response_time(response, tool_type)
        validation_result["checks"]["response_time"] = time_check
        if not time_check["passed"]:
            validation_result["warnings"].extend(time_check.get("warnings", []))
        
        # Check 4: Content quality
        content_check = self._check_content(response)
        validation_result["checks"]["content_quality"] = content_check
        if not content_check["passed"]:
            validation_result["warnings"].extend(content_check.get("warnings", []))
        
        return validation_result
    
    def _check_execution(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Check if execution was successful."""
        errors = []

        # Check for error status (including workflow-specific failure statuses)
        status = response.get("status", "")
        failure_statuses = [
            "error",
            "execution_error",
            "invalid_request",
            # Workflow-specific failure statuses
            "analyze_failed",
            "challenge_failed",
            "codereview_failed",
            "consensus_failed",
            "debug_failed",
            "docgen_failed",
            "planner_failed",
            "precommit_failed",
            "refactor_failed",
            "secaudit_failed",
            "testgen_failed",
            "thinkdeep_failed",
            "tracer_failed",
            # Timeout statuses
            "analyze_timeout",
            "challenge_timeout",
            "codereview_timeout",
            "consensus_timeout",
            "debug_timeout",
            "docgen_timeout",
            "planner_timeout",
            "precommit_timeout",
            "refactor_timeout",
            "secaudit_timeout",
            "testgen_timeout",
            "thinkdeep_timeout",
            "tracer_timeout"
        ]

        if status in failure_statuses:
            errors.append(f"Response has failure status: {status}")

        # Check for error field
        if "error" in response and response["error"]:
            errors.append(f"Response contains error: {response['error']}")

        # Check for exception
        if "exception" in response:
            errors.append(f"Response contains exception: {response['exception']}")

        return {
            "passed": len(errors) == 0,
            "errors": errors
        }
    
    def _check_structure(self, response: Dict[str, Any], expected_fields: Optional[List[str]]) -> Dict[str, Any]:
        """Check response structure."""
        errors = []
        
        # Check if response is a dictionary
        if not isinstance(response, dict):
            errors.append(f"Response is not a dictionary: {type(response)}")
            return {"passed": False, "errors": errors}
        
        # Check for content
        has_content = False
        content_fields = ["content", "choices", "message", "result", "output"]
        
        for field in content_fields:
            if field in response and response[field]:
                has_content = True
                break
        
        if not has_content:
            errors.append("Response has no content")
        
        # Check expected fields
        if expected_fields:
            missing_fields = [f for f in expected_fields if f not in response]
            if missing_fields:
                errors.append(f"Missing expected fields: {missing_fields}")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors
        }
    
    def _check_response_time(self, response: Dict[str, Any], tool_type: str) -> Dict[str, Any]:
        """Check response time."""
        warnings = []
        
        # Get response time from metadata
        metadata = response.get("_metadata", {})
        duration = metadata.get("duration_secs", 0)
        
        # Get max time for tool type
        max_times = {
            "simple": self.success_criteria["response_time"]["simple_tool_max_secs"],
            "workflow": self.success_criteria["response_time"]["workflow_tool_max_secs"],
            "provider": self.success_criteria["response_time"]["provider_tool_max_secs"]
        }
        
        max_time = max_times.get(tool_type, 120)
        
        if duration > max_time:
            warnings.append(f"Response time ({duration:.2f}s) exceeds limit ({max_time}s)")
        
        return {
            "passed": len(warnings) == 0,
            "warnings": warnings,
            "duration_secs": duration,
            "max_secs": max_time
        }
    
    def _check_content(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Check content quality."""
        warnings = []
        
        # Extract content
        content = None
        if "content" in response:
            content = response["content"]
        elif "choices" in response and len(response["choices"]) > 0:
            content = response["choices"][0].get("message", {}).get("content")
        elif "message" in response:
            content = response["message"].get("content")
        
        if content:
            # Check content length
            if isinstance(content, str):
                if len(content) < 10:
                    warnings.append("Content is very short (< 10 characters)")
                elif len(content) > 100000:
                    warnings.append("Content is very long (> 100k characters)")
        else:
            warnings.append("No content found in response")
        
        return {
            "passed": len(warnings) == 0,
            "warnings": warnings
        }
    
    def validate_batch(
        self,
        responses: List[Dict[str, Any]],
        tool_type: str = "simple"
    ) -> Dict[str, Any]:
        """
        Validate multiple responses.
        
        Args:
            responses: List of response dictionaries
            tool_type: Tool type
        
        Returns:
            Batch validation result
        """
        results = []
        
        for i, response in enumerate(responses):
            result = self.validate_response(response, tool_type)
            result["response_index"] = i
            results.append(result)
        
        # Calculate summary
        total = len(results)
        valid = sum(1 for r in results if r["valid"])
        invalid = total - valid
        
        return {
            "total_responses": total,
            "valid_responses": valid,
            "invalid_responses": invalid,
            "pass_rate": valid / total if total > 0 else 0,
            "results": results
        }


# Example usage
if __name__ == "__main__":
    validator = ResponseValidator()
    
    # Test valid response
    valid_response = {
        "status": "success",
        "content": "This is a valid response with good content.",
        "_metadata": {
            "duration_secs": 2.5,
            "provider": "kimi",
            "model": "kimi-k2-0905-preview"
        }
    }
    
    result = validator.validate_response(valid_response, tool_type="simple")
    print(json.dumps(result, indent=2))
    
    # Test invalid response
    invalid_response = {
        "status": "error",
        "error": "Something went wrong",
        "_metadata": {
            "duration_secs": 150.0
        }
    }
    
    result = validator.validate_response(invalid_response, tool_type="simple")
    print(json.dumps(result, indent=2))

