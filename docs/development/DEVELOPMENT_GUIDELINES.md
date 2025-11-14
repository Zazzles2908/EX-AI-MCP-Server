# Development Guidelines

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** 🟡 **In Progress**

## 🎯 Overview

This section contains development guidelines, coding standards, and best practices for contributing to the EX-AI MCP Server project.

## 📚 Documentation Structure

### 🤝 Contributing Guidelines
**Location:** `01_contributing_guidelines.md`

How to contribute to the project:

**Development Setup**
- Environment setup
- Dependencies installation
- IDE configuration (VSCode recommended)
- Pre-commit hooks

**Coding Standards**
- Python style guide (PEP 8)
- Type hints required
- Documentation standards
- Error handling patterns

**Git Workflow**
- Branch strategy (git flow)
- Commit message format
- Pull request process
- Code review requirements

**Testing Requirements**
- 80% code coverage minimum
- Unit tests for all functions
- Integration tests for workflows
- Test fixtures and mocks

**Required reading** for all contributors.

### ✅ Code Review Process
**Location:** `02_code_review_process.md`

How to conduct and receive code reviews:

**Review Checklist**
- Code quality
- Security review
- Performance check
- Documentation update
- Test coverage

**Review Criteria**
- Functionality correctness
- Code maintainability
- Security implications
- Performance impact
- Test completeness

**Review Process**
- PR submission
- Automated checks
- Human review
- Feedback cycles
- Approval and merge

**Reviewer Guidelines**
- Be constructive
- Focus on code, not person
- Ask questions
- Suggest improvements
- Approve when ready

**Essential for** maintaining code quality.

### 🧪 Testing Strategy
**Location:** `03_testing_strategy.md`

Comprehensive testing approach:

**Test Structure**
- Unit tests (80% coverage)
- Integration tests
- End-to-end tests
- Performance tests

**Test Organization**
- `tests/` directory structure
- `conftest.py` for fixtures
- `test_*.py` naming convention
- Mock external dependencies

**Test Tools**
- pytest for testing framework
- pytest-cov for coverage
- pytest-mock for mocking
- tox for multi-environment

**Continuous Integration**
- GitHub Actions
- Automated test runs
- Coverage reporting
- Quality gates

**Required for** all code changes.

## 💻 Development Environment

### Prerequisites
- **Python**: 3.11 or higher
- **Node.js**: 18+ (for WebSocket testing)
- **Git**: Latest version
- **Docker**: Latest version (for containerized testing)
- **VSCode**: Recommended IDE

### Quick Start
```bash
# Clone repository
git clone https://github.com/your-org/exai-mcp-server.git
cd exai-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest

# Start development server
python scripts/start_server.py
```

### Environment Variables
```env
# Required for development
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ACCESS_TOKEN=sbp_your-token
SUPABASE_JWT_SECRET=your-jwt-secret
GLM_API_KEY=your-glm-key
KIMI_API_KEY=your-kimi-key
```

## 📋 Coding Standards

### Python Style Guide
- **PEP 8**: Follow Python style guide
- **Line Length**: 88 characters (Black formatter)
- **Type Hints**: All public functions must have type hints
- **Docstrings**: Google-style docstrings
- **Imports**: Sort with isort

### Code Organization
- **One class per file** (when reasonable)
- **Clear separation of concerns**
- **Single responsibility principle**
- **Proper error handling**
- **Comprehensive logging**

### Error Handling
- ✅ **Use specific exceptions**
- ✅ **Log errors with context**
- ✅ **Provide actionable messages**
- ✅ **Never swallow exceptions**
- ✅ **Always handle file I/O errors**

## 🧪 Testing Standards

### Test Structure
```python
import pytest
from unittest.mock import Mock, patch

class TestMessageRepository:
    """Test suite for MessageRepository."""

    @pytest.fixture
    def database(self):
        """Create mock database."""
        return Mock()

    @pytest.fixture
    def repository(self, database):
        """Create repository instance."""
        return MessageRepository(database)

    def test_save_message_success(
        self,
        repository: MessageRepository,
        database: Mock
    ):
        """Test successful message save."""
        # Arrange
        database.insert.return_value = "msg_123"

        # Act
        message_id = repository.save_message(
            session_id="sess_456",
            content="Hello, world!",
            role="user"
        )

        # Assert
        assert message_id == "msg_123"
        database.insert.assert_called_once()
```

### Test Coverage
- **Minimum 80%** code coverage
- **100% coverage** for critical paths
- **Mock external dependencies** (HTTP, filesystem, processes)
- **Test edge cases** and error conditions

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_message_repository.py

# Run tests matching pattern
pytest -k "test_save_message"

# Run in parallel
pytest -n auto
```

## 🔍 Code Review Checklist

### Before Submitting PR
- [ ] Code follows style guide
- [ ] All functions have type hints
- [ ] Docstrings complete
- [ ] Error handling comprehensive
- [ ] Tests pass locally
- [ ] Test coverage >= 80%
- [ ] No TODO/FIXME comments
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Security review completed

### Reviewer Checklist
- [ ] **Functionality**: Code works as intended
- [ ] **Readability**: Code is clear and maintainable
- [ ] **Performance**: No obvious performance issues
- [ ] **Security**: No security vulnerabilities
- [ ] **Tests**: Adequate test coverage
- [ ] **Documentation**: Code is well-documented
- [ ] **Error Handling**: Errors are properly handled
- [ ] **Logging**: Appropriate logging added
- [ ] **Type Hints**: All public APIs typed
- [ ] **Dependencies**: No unnecessary dependencies

## 🔄 Git Workflow

### Branch Strategy
- **main**: Production-ready code
- **develop**: Integration branch
- **feature/***: Feature branches
- **bugfix/***: Bug fix branches
- **hotfix/***: Emergency fixes

### Commit Message Format
```
type(scope): subject

body (optional)

footer (optional)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Pull Request Process
1. **Create branch** from develop
2. **Make changes** and add tests
3. **Run test suite** - all must pass
4. **Update documentation** - if needed
5. **Create PR** with clear description
6. **Respond to feedback** - address all comments
7. **Squash and merge** - when approved

## 📦 Project Structure

### Directory Layout
```
exai-mcp-server/
├── src/                    # Source code
│   ├── auth/              # Authentication
│   ├── config/            # Configuration
│   ├── providers/         # AI providers
│   ├── storage/           # Database & files
│   ├── tools/             # MCP tools
│   └── daemon/            # WebSocket server
├── tests/                 # Test suite
│   ├── conftest.py        # Shared fixtures
│   ├── test_*.py          # Unit tests
│   ├── test_*.py          # Integration tests
│   └── fixtures/          # Test data
├── scripts/               # Utility scripts
├── docs/                  # Documentation
├── docker-compose.yml     # Docker config
├── requirements.txt      # Dependencies
└── CHANGELOG.md         # Version history
```

## 📚 Related Documentation

- **System Architecture**: [../01-architecture-overview/01_system_architecture.md](../01-architecture-overview/01_system_architecture.md)
- **Database Integration**: [../02-database-integration/DATABASE_INTEGRATION_GUIDE.md](../02-database-integration/DATABASE_INTEGRATION_GUIDE.md)
- **API & Tools Reference**: [../04-api-tools-reference/../04-api-tools-reference/)

## 🔗 Quick Links

- **Contributing**: [01_contributing_guidelines.md](01_contributing_guidelines.md)
- **Code Review**: [02_code_review_process.md](02_code_review_process.md)
- **Testing**: [03_testing_strategy.md](03_testing_strategy.md)
- **Main Documentation**: [../index.md](../index.md)

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server Development Team
**Status:** 🟡 **In Progress - Development guides being created**
