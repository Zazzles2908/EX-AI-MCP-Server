# Contributing to EX-AI MCP Server

Thank you for your interest in contributing to the EX-AI MCP Server project!

## Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see `.env.example`)
4. Run tests: `python scripts/tests/test_websocket_comprehensive.py`

## Code Standards

- Follow PEP 8 style guidelines
- Write type hints for all public APIs
- Maintain 80%+ test coverage
- Use meaningful variable and function names
- Document all public methods and classes

## Documentation

- Place all documentation in `docs/` directory
- No .md files should exist in the root except:
  - README.md
  - CONTRIBUTING.md (this file)
  - LICENSE
  - CHANGELOG.md
  - CLAUDE.md

## Testing

- Write unit tests for all new functionality
- Run the comprehensive test suite before submitting PRs
- Use mock objects for external dependencies

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with proper tests
3. Update documentation as needed
4. Run the validation suite: `python scripts/validation/unified_validator.py --all`
5. Submit a pull request with a clear description

## Questions?

Feel free to open an issue for questions or discussions.
