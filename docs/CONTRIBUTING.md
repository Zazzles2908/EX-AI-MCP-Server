# Contributing to EX-AI-MCP-Server
**Last Updated:** 2025-10-04  
**Thank you for contributing!**

---

## 🎯 GETTING STARTED

### Prerequisites
- Python 3.8+
- Git
- API keys for testing (Kimi and/or GLM)
- Familiarity with async Python and MCP protocol

### Development Setup

**1. Fork and clone:**
```bash
git clone https://github.com/yourusername/EX-AI-MCP-Server.git
cd EX-AI-MCP-Server
```

**2. Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

**4. Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

**5. Run tests:**
```bash
pytest tests/
```

---

## 📋 CONTRIBUTION WORKFLOW

### 1. Create a Branch

**Branch naming convention:**
```
feature/description    # New features
fix/description        # Bug fixes
docs/description       # Documentation
refactor/description   # Code refactoring
test/description       # Test additions
chore/description      # Maintenance tasks
```

**Example:**
```bash
git checkout -b feature/add-gemini-provider
```

### 2. Make Changes

**Code standards:**
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all functions/classes
- Keep functions focused and small (<50 lines)
- Add logging for important operations

**Example:**
```python
def parse_query(text: str) -> Optional[str]:
    """
    Extract search query from text format.
    
    Args:
        text: Input text that may contain query
        
    Returns:
        Extracted query or None if not found
    """
    # Implementation
    pass
```

### 3. Write Tests

**Test requirements:**
- Unit tests for all new functions
- Integration tests for new features
- Test edge cases and error conditions
- Maintain >80% code coverage

**Example:**
```python
def test_parse_query_format_b():
    """Test parsing Format B query."""
    text = "<tool_call>web_search<arg_value>test query</tool_call>"
    result = parse_query(text)
    assert result == "test query"
```

### 4. Update Documentation

**Documentation requirements:**
- Update README.md if adding features
- Add docstrings to all code
- Update relevant guides in docs/guides/
- Add entry to DOCUMENTATION_INDEX.md
- Update CURRENT_STATUS.md if fixing bugs

### 5. Commit Changes

**Commit message format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

**Example:**
```
feat(providers): add Gemini provider support

- Implement GeminiProvider class
- Add configuration for Gemini API
- Add tests for Gemini integration
- Update documentation

Closes #123
```

### 6. Push and Create PR

```bash
git push origin feature/add-gemini-provider
```

**PR requirements:**
- Clear title and description
- Link to related issues
- Screenshots/examples if UI changes
- All tests passing
- Documentation updated

---

## 🔍 CODE REVIEW PROCESS

### What We Look For

**Code Quality:**
- [ ] Follows PEP 8 style guide
- [ ] Has type hints
- [ ] Has docstrings
- [ ] Is well-structured and readable
- [ ] Has appropriate error handling

**Testing:**
- [ ] Has unit tests
- [ ] Has integration tests if needed
- [ ] Tests pass locally
- [ ] Tests pass in CI

**Documentation:**
- [ ] Code is documented
- [ ] User-facing docs updated
- [ ] DOCUMENTATION_INDEX.md updated
- [ ] Examples provided if needed

**Functionality:**
- [ ] Solves the stated problem
- [ ] Doesn't break existing features
- [ ] Handles edge cases
- [ ] Has appropriate logging

### Review Timeline
- Initial review: Within 2-3 days
- Follow-up reviews: Within 1-2 days
- Merge: After approval and CI passes

---

## 🧪 TESTING GUIDELINES

### Running Tests

**All tests:**
```bash
pytest tests/
```

**Specific test file:**
```bash
pytest tests/test_text_format_handler.py
```

**With coverage:**
```bash
pytest --cov=src tests/
```

**Verbose output:**
```bash
pytest -v tests/
```

### Writing Tests

**Test structure:**
```python
import pytest
from src.module import function

class TestFunction:
    """Tests for function."""
    
    def test_normal_case(self):
        """Test normal operation."""
        result = function("input")
        assert result == "expected"
    
    def test_edge_case(self):
        """Test edge case."""
        result = function("")
        assert result is None
    
    def test_error_case(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            function(None)
```

**Test fixtures:**
```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"key": "value"}

def test_with_fixture(sample_data):
    """Test using fixture."""
    assert sample_data["key"] == "value"
```

---

## 📝 DOCUMENTATION GUIDELINES

### Code Documentation

**Module docstring:**
```python
"""
Module for handling text format responses.

This module provides functions to parse and execute web search
queries from text format tool calls.
"""
```

**Function docstring:**
```python
def function(arg1: str, arg2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed. Explain what the function does,
    when to use it, and any important considerations.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When arg1 is empty
        TypeError: When arg2 is not an integer
        
    Example:
        >>> function("test", 42)
        True
    """
```

### User Documentation

**Guide structure:**
```markdown
# Guide Title
**Last Updated:** YYYY-MM-DD
**For:** Target audience

## Overview
Brief introduction

## Prerequisites
What's needed

## Step-by-Step Instructions
1. First step
2. Second step

## Examples
Concrete examples

## Troubleshooting
Common issues

## Next Steps
What to do next
```

---

## 🐛 BUG REPORTS

### Before Reporting

1. Check existing issues
2. Verify it's reproducible
3. Test with latest version
4. Check logs for errors

### Bug Report Template

```markdown
**Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: Windows 10
- Python: 3.10
- Version: 1.0.0

**Logs:**
```
Relevant log output
```

**Additional Context:**
Any other relevant information
```

---

## 💡 FEATURE REQUESTS

### Feature Request Template

```markdown
**Problem:**
What problem does this solve?

**Proposed Solution:**
How should it work?

**Alternatives Considered:**
Other approaches you've thought about

**Additional Context:**
Examples, mockups, references
```

---

## 🎨 CODE STYLE

### Python Style

**Follow PEP 8:**
- 4 spaces for indentation
- Max line length: 100 characters
- Use snake_case for functions/variables
- Use PascalCase for classes
- Use UPPER_CASE for constants

**Type hints:**
```python
from typing import Optional, List, Dict

def process_data(
    items: List[str],
    config: Dict[str, Any]
) -> Optional[str]:
    """Process data with configuration."""
    pass
```

**Imports:**
```python
# Standard library
import os
import sys

# Third-party
import pytest
from typing import Optional

# Local
from src.module import function
```

---

## 🚀 RELEASE PROCESS

### Version Numbering
- Major: Breaking changes (1.0.0 → 2.0.0)
- Minor: New features (1.0.0 → 1.1.0)
- Patch: Bug fixes (1.0.0 → 1.0.1)

### Release Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Tagged in git
- [ ] Release notes written

---

## 📞 GETTING HELP

**Questions:**
- Check documentation first
- Ask in discussions
- Open an issue

**Stuck:**
- Review existing code
- Check test examples
- Ask for help in PR

---

## 🙏 THANK YOU!

Your contributions make this project better for everyone!

**Recognition:**
- Contributors listed in README.md
- Significant contributions highlighted in releases
- Community appreciation

---

**Happy Contributing!** 🎉

