"""
Enhanced progress messaging for better UX.

Provides standardized, user-friendly progress messages for different tool operations.
"""

from typing import Optional


class ProgressMessages:
    """Standardized progress messages for tool operations."""
    
    # ============================================================================
    # General Operations
    # ============================================================================
    
    @staticmethod
    def starting_analysis(tool_name: str, step: Optional[int] = None) -> str:
        """Message for starting analysis."""
        if step:
            return f"🔍 Starting {tool_name} analysis (Step {step})..."
        return f"🔍 Starting {tool_name} analysis..."
    
    @staticmethod
    def loading_files(count: int) -> str:
        """Message for loading files."""
        if count == 1:
            return "📂 Loading 1 file..."
        return f"📂 Loading {count} files..."
    
    @staticmethod
    def processing_context(size_kb: Optional[float] = None) -> str:
        """Message for processing context."""
        if size_kb:
            return f"⚙️  Processing context ({size_kb:.1f} KB)..."
        return "⚙️  Processing context..."
    
    @staticmethod
    def calling_model(model_name: str) -> str:
        """Message for calling AI model."""
        return f"🤖 Calling {model_name}..."
    
    @staticmethod
    def waiting_for_response() -> str:
        """Message for waiting for model response."""
        return "⏳ Waiting for response..."
    
    @staticmethod
    def processing_response() -> str:
        """Message for processing model response."""
        return "📝 Processing response..."
    
    # ============================================================================
    # Web Search Operations
    # ============================================================================
    
    @staticmethod
    def web_search_starting(query: Optional[str] = None) -> str:
        """Message for starting web search."""
        if query:
            return f"🔎 Searching the web: \"{query[:50]}...\""
        return "🔎 Performing web search..."
    
    @staticmethod
    def web_search_complete(results_count: int) -> str:
        """Message for completed web search."""
        if results_count == 0:
            return "⚠️  Web search returned no results"
        elif results_count == 1:
            return "✅ Found 1 search result"
        return f"✅ Found {results_count} search results"
    
    @staticmethod
    def web_search_failed(reason: Optional[str] = None) -> str:
        """Message for failed web search."""
        if reason:
            return f"❌ Web search failed: {reason}"
        return "❌ Web search failed"
    
    # ============================================================================
    # Tool Execution Operations
    # ============================================================================
    
    @staticmethod
    def tool_call_detected(tool_name: str, count: int = 1) -> str:
        """Message for detected tool calls."""
        if count == 1:
            return f"🔧 Model requested {tool_name} tool"
        return f"🔧 Model requested {count} tool calls"
    
    @staticmethod
    def executing_tool(tool_name: str) -> str:
        """Message for executing tool."""
        return f"⚡ Executing {tool_name}..."
    
    @staticmethod
    def tool_complete(tool_name: str) -> str:
        """Message for completed tool execution."""
        return f"✅ {tool_name} complete"
    
    # ============================================================================
    # Workflow Operations
    # ============================================================================
    
    @staticmethod
    def workflow_step(step_num: int, total_steps: int, description: str) -> str:
        """Message for workflow step progress."""
        return f"📊 Step {step_num}/{total_steps}: {description}"
    
    @staticmethod
    def workflow_complete(total_steps: int) -> str:
        """Message for completed workflow."""
        return f"✅ Workflow complete ({total_steps} steps)"
    
    @staticmethod
    def expert_analysis_starting(model: str) -> str:
        """Message for starting expert analysis."""
        return f"🎓 Requesting expert analysis from {model}..."
    
    @staticmethod
    def expert_analysis_complete() -> str:
        """Message for completed expert analysis."""
        return "✅ Expert analysis complete"
    
    # ============================================================================
    # File Operations
    # ============================================================================
    
    @staticmethod
    def reading_file(filename: str) -> str:
        """Message for reading file."""
        return f"📖 Reading {filename}..."
    
    @staticmethod
    def file_too_large(filename: str, size_mb: float) -> str:
        """Message for file too large."""
        return f"⚠️  {filename} is large ({size_mb:.1f} MB), this may take a moment..."
    
    @staticmethod
    def files_loaded(count: int, total_size_kb: float) -> str:
        """Message for files loaded."""
        if count == 1:
            return f"✅ Loaded 1 file ({total_size_kb:.1f} KB)"
        return f"✅ Loaded {count} files ({total_size_kb:.1f} KB)"
    
    # ============================================================================
    # Error and Warning Messages
    # ============================================================================
    
    @staticmethod
    def retrying_operation(attempt: int, max_attempts: int, reason: str) -> str:
        """Message for retrying operation."""
        return f"🔄 Retry {attempt}/{max_attempts}: {reason}"
    
    @staticmethod
    def operation_timeout(operation: str, timeout_seconds: int) -> str:
        """Message for operation timeout."""
        return f"⏱️  {operation} taking longer than expected ({timeout_seconds}s)..."
    
    @staticmethod
    def fallback_mode(reason: str) -> str:
        """Message for fallback mode."""
        return f"⚠️  Using fallback mode: {reason}"
    
    # ============================================================================
    # Completion Messages
    # ============================================================================
    
    @staticmethod
    def success(message: str) -> str:
        """Generic success message."""
        return f"✅ {message}"
    
    @staticmethod
    def warning(message: str) -> str:
        """Generic warning message."""
        return f"⚠️  {message}"
    
    @staticmethod
    def error(message: str) -> str:
        """Generic error message."""
        return f"❌ {message}"
    
    @staticmethod
    def info(message: str) -> str:
        """Generic info message."""
        return f"ℹ️  {message}"

