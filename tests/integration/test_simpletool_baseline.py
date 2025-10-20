"""
Integration tests for SimpleTool - BASELINE BEFORE REFACTORING

This test suite establishes the baseline behavior of SimpleTool and its 3 subclasses
BEFORE any refactoring begins. All tests must pass before and after refactoring to
ensure 100% backward compatibility.

Tests cover:
- All 3 SimpleTool subclasses (ChatTool, ChallengeTool, ActivityTool)
- All 25 public methods
- Schema generation
- Request validation
- Execution flow
- Response formatting
"""

import pytest
import asyncio
from typing import Any, Dict
from pathlib import Path

# Import the tools
from tools.chat import ChatTool, ChatRequest
from tools.challenge import ChallengeTool, ChallengeRequest
from tools.activity import ActivityTool, ActivityRequest
from tools.simple.base import SimpleTool


class TestSimpleToolBaseline:
    """Baseline tests for SimpleTool base class"""

    @pytest.fixture
    def chat_tool(self):
        """Create ChatTool instance for testing"""
        return ChatTool()

    @pytest.fixture
    def challenge_tool(self):
        """Create ChallengeTool instance for testing"""
        return ChallengeTool()

    @pytest.fixture
    def activity_tool(self):
        """Create ActivityTool instance for testing"""
        return ActivityTool()

    # ===== Test Tool Instantiation =====

    def test_chat_tool_instantiation(self, chat_tool):
        """Test ChatTool can be instantiated"""
        assert isinstance(chat_tool, SimpleTool)
        assert isinstance(chat_tool, ChatTool)

    def test_challenge_tool_instantiation(self, challenge_tool):
        """Test ChallengeTool can be instantiated"""
        assert isinstance(challenge_tool, SimpleTool)
        assert isinstance(challenge_tool, ChallengeTool)

    def test_activity_tool_instantiation(self, activity_tool):
        """Test ActivityTool can be instantiated"""
        assert isinstance(activity_tool, SimpleTool)
        assert isinstance(activity_tool, ActivityTool)

    # ===== Test Public Methods (25 methods) =====

    def test_get_name(self, chat_tool, challenge_tool, activity_tool):
        """Test get_name() method"""
        assert chat_tool.get_name() == "chat"
        assert challenge_tool.get_name() == "challenge"
        assert activity_tool.get_name() == "activity"

    def test_get_description(self, chat_tool, challenge_tool, activity_tool):
        """Test get_description() method"""
        assert len(chat_tool.get_description()) > 0
        assert len(challenge_tool.get_description()) > 0
        assert len(activity_tool.get_description()) > 0

    def test_get_system_prompt(self, chat_tool, challenge_tool, activity_tool):
        """Test get_system_prompt() method"""
        assert isinstance(chat_tool.get_system_prompt(), str)
        assert isinstance(challenge_tool.get_system_prompt(), str)
        assert isinstance(activity_tool.get_system_prompt(), str)

    def test_get_default_temperature(self, chat_tool, challenge_tool, activity_tool):
        """Test get_default_temperature() method"""
        assert isinstance(chat_tool.get_default_temperature(), float)
        assert isinstance(challenge_tool.get_default_temperature(), float)
        assert 0.0 <= chat_tool.get_default_temperature() <= 1.0

    def test_get_model_category(self, chat_tool, challenge_tool, activity_tool):
        """Test get_model_category() method"""
        from tools.models import ToolModelCategory
        assert isinstance(chat_tool.get_model_category(), ToolModelCategory)
        assert isinstance(challenge_tool.get_model_category(), ToolModelCategory)
        assert isinstance(activity_tool.get_model_category(), ToolModelCategory)

    def test_get_request_model(self, chat_tool, challenge_tool, activity_tool):
        """Test get_request_model() method"""
        assert chat_tool.get_request_model() == ChatRequest
        assert challenge_tool.get_request_model() == ChallengeRequest
        # ActivityTool doesn't override get_request_model(), uses base ToolRequest
        from tools.shared.base_models import ToolRequest
        assert activity_tool.get_request_model() == ToolRequest

    def test_get_input_schema(self, chat_tool, challenge_tool, activity_tool):
        """Test get_input_schema() method"""
        chat_schema = chat_tool.get_input_schema()
        challenge_schema = challenge_tool.get_input_schema()
        activity_schema = activity_tool.get_input_schema()

        assert isinstance(chat_schema, dict)
        assert isinstance(challenge_schema, dict)
        assert isinstance(activity_schema, dict)

        # Verify schema structure
        assert "type" in chat_schema
        assert "properties" in chat_schema
        assert chat_schema["type"] == "object"

    def test_get_tool_fields(self, chat_tool, challenge_tool, activity_tool):
        """Test get_tool_fields() method (abstract method)"""
        chat_fields = chat_tool.get_tool_fields()
        challenge_fields = challenge_tool.get_tool_fields()
        activity_fields = activity_tool.get_tool_fields()

        assert isinstance(chat_fields, dict)
        assert isinstance(challenge_fields, dict)
        assert isinstance(activity_fields, dict)

        # Chat should have prompt, files, images
        assert "prompt" in chat_fields
        assert "files" in chat_fields
        assert "images" in chat_fields

    def test_get_required_fields(self, chat_tool, challenge_tool, activity_tool):
        """Test get_required_fields() method"""
        chat_required = chat_tool.get_required_fields()
        challenge_required = challenge_tool.get_required_fields()
        activity_required = activity_tool.get_required_fields()

        assert isinstance(chat_required, list)
        assert isinstance(challenge_required, list)
        assert isinstance(activity_required, list)

        # Chat requires prompt
        assert "prompt" in chat_required

    def test_get_annotations(self, chat_tool):
        """Test get_annotations() method"""
        annotations = chat_tool.get_annotations()
        assert isinstance(annotations, dict)

    def test_supports_custom_request_model(self, chat_tool):
        """Test supports_custom_request_model() method"""
        result = chat_tool.supports_custom_request_model()
        assert isinstance(result, bool)

    # ===== Test Request Accessor Methods (13 methods) =====

    def test_get_request_prompt(self, chat_tool):
        """Test get_request_prompt() method"""
        request = ChatRequest(prompt="Test prompt")
        prompt = chat_tool.get_request_prompt(request)
        assert prompt == "Test prompt"

    def test_get_request_files(self, chat_tool):
        """Test get_request_files() method"""
        request = ChatRequest(prompt="Test", files=["file1.py", "file2.py"])
        files = chat_tool.get_request_files(request)
        assert files == ["file1.py", "file2.py"]

    def test_get_request_images(self, chat_tool):
        """Test get_request_images() method"""
        request = ChatRequest(prompt="Test", images=["img1.png"])
        images = chat_tool.get_request_images(request)
        assert images == ["img1.png"]

    def test_get_request_continuation_id(self, chat_tool):
        """Test get_request_continuation_id() method"""
        request = ChatRequest(prompt="Test", continuation_id="test-id-123")
        cont_id = chat_tool.get_request_continuation_id(request)
        assert cont_id == "test-id-123"

    def test_get_request_model_name(self, chat_tool):
        """Test get_request_model_name() method"""
        request = ChatRequest(prompt="Test", model="glm-4.6")
        model = chat_tool.get_request_model_name(request)
        assert model == "glm-4.6"

    def test_get_request_temperature(self, chat_tool):
        """Test get_request_temperature() method"""
        request = ChatRequest(prompt="Test", temperature=0.7)
        temp = chat_tool.get_request_temperature(request)
        assert temp == 0.7

    def test_get_validated_temperature(self, chat_tool):
        """Test get_validated_temperature() method"""
        # Create a mock model_context object with required attributes
        class MockModelContext:
            def __init__(self):
                self.model_name = "test-model"
                self.capabilities = MockCapabilities()

        class MockCapabilities:
            def __init__(self):
                self.temperature_constraint = MockConstraint()

        class MockConstraint:
            def validate(self, temp):
                return 0.0 <= temp <= 1.0

            def get_corrected_value(self, temp):
                return max(0.0, min(1.0, temp))

            def get_description(self):
                return "Temperature must be between 0.0 and 1.0"

        request = ChatRequest(prompt="Test", temperature=0.7)
        model_context = MockModelContext()
        temp, warnings = chat_tool.get_validated_temperature(request, model_context)
        assert 0.0 <= temp <= 1.0
        assert isinstance(warnings, list)

    def test_get_request_thinking_mode(self, chat_tool):
        """Test get_request_thinking_mode() method"""
        request = ChatRequest(prompt="Test", thinking_mode="medium")
        mode = chat_tool.get_request_thinking_mode(request)
        assert mode == "medium"

    def test_get_request_use_websearch(self, chat_tool):
        """Test get_request_use_websearch() method"""
        request = ChatRequest(prompt="Test", use_websearch=True)
        websearch = chat_tool.get_request_use_websearch(request)
        assert websearch is True

    def test_get_request_stream_attribute(self, chat_tool):
        """Test stream attribute access on request"""
        request = ChatRequest(prompt="Test", stream=True)
        # SimpleTool doesn't have get_request_stream(), access directly
        assert hasattr(request, 'stream')
        assert request.stream is True

    def test_get_request_as_dict(self, chat_tool):
        """Test get_request_as_dict() method"""
        request = ChatRequest(prompt="Test", files=["file1.py"])
        req_dict = chat_tool.get_request_as_dict(request)
        assert isinstance(req_dict, dict)
        assert req_dict["prompt"] == "Test"
        assert "file1.py" in req_dict["files"]

    def test_set_request_files(self, chat_tool):
        """Test set_request_files() method"""
        request = ChatRequest(prompt="Test")
        chat_tool.set_request_files(request, ["new_file.py"])
        assert request.files == ["new_file.py"]

    def test_get_actually_processed_files(self, chat_tool):
        """Test get_actually_processed_files() method"""
        # get_actually_processed_files() takes no arguments (uses internal state)
        processed = chat_tool.get_actually_processed_files()
        assert isinstance(processed, list)

    # ===== Test Prompt Building Methods (3 methods) =====

    def test_build_standard_prompt(self, chat_tool):
        """Test build_standard_prompt() method"""
        request = ChatRequest(prompt="Test prompt")
        # build_standard_prompt requires system_prompt, user_content, request
        system_prompt = "You are a helpful assistant"
        user_content = "Test prompt"
        prompt = chat_tool.build_standard_prompt(system_prompt, user_content, request)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Test prompt" in prompt

    def test_handle_prompt_file_with_fallback(self, chat_tool):
        """Test handle_prompt_file_with_fallback() method"""
        request = ChatRequest(prompt="Test")
        # handle_prompt_file_with_fallback is synchronous
        result = chat_tool.handle_prompt_file_with_fallback(request)
        assert isinstance(result, str)
        assert result == "Test"  # Falls back to request prompt

    def test_prepare_chat_style_prompt(self, chat_tool):
        """Test prepare_chat_style_prompt() method"""
        request = ChatRequest(prompt="Test")
        # prepare_chat_style_prompt is synchronous
        prompt = chat_tool.prepare_chat_style_prompt(request)
        assert isinstance(prompt, str)

    # ===== Test Schema & Validation Methods (3 methods) =====

    def test_get_prompt_content_for_size_validation(self, chat_tool):
        """Test get_prompt_content_for_size_validation() method"""
        # get_prompt_content_for_size_validation takes user_content string, not request
        user_content = "Test prompt"
        content = chat_tool.get_prompt_content_for_size_validation(user_content)
        assert isinstance(content, str)
        assert content == "Test prompt"

    # ===== Test Execution Method (1 method) =====

    @pytest.mark.asyncio
    async def test_execute_challenge_tool(self, challenge_tool):
        """Test execute() method with ChallengeTool (doesn't require model)"""
        arguments = {"prompt": "Test challenge"}
        result = await challenge_tool.execute(arguments)
        assert isinstance(result, list)
        assert len(result) > 0

    # ===== Test Format Response Method (1 method) =====

    def test_format_response(self, chat_tool):
        """Test format_response() method"""
        request = ChatRequest(prompt="Test")
        # format_response requires response, request, and optional model_info
        response = chat_tool.format_response("Test response", request)
        assert isinstance(response, str)
        assert response == "Test response"  # Default implementation returns as-is


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

