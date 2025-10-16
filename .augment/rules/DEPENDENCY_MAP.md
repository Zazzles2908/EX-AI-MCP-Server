---
type: "agent_requested"
description: "EXAI-MCP Layered Architecture and Docker Deployment"
---

# IDE Augmentation Guidelines: Layered Architecture Organization

## 🐳 EXAI-MCP Architecture Overview

**Deployment Model:**
- EXAI runs in a **Docker container** (not direct terminal execution)
- Access via **WebSocket daemon** at `ws://127.0.0.1:8079`
- MCP integration through **stdio transport** to `scripts/run_ws_shim.py`
- Configuration: `Daemon/mcp-config.augmentcode.json`

**Key Components:**
1. **Docker Container**: Isolated EXAI environment with all dependencies
2. **WebSocket Shim**: `scripts/run_ws_shim.py` - bridges MCP stdio ↔ WebSocket
3. **MCP Server**: Augment Code connects via stdio to shim
4. **EXAI Daemon**: Runs inside Docker, handles tool execution
5. **Supabase Integration**: Persistent storage for conversations, issues, files

**Restart Workflow:**
```powershell
# Restart EXAI daemon after code changes
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

## Core Principle: Unidirectional Dependency Flow

Your code should follow a strict layered architecture where dependencies flow in one direction only, from higher-level layers to lower-level layers. This prevents circular dependencies and maintains a clean separation of concerns.

## Layer Structure Guidelines

### 1. Foundation Layer (Utilities)
- **Purpose**: Pure utility functions with no project-specific imports
- **Dependency Rule**: Must not import from any other project modules
- **Characteristics**: 
  - Small, focused functions
  - No business logic
  - Reusable across the entire project
- **Example Patterns**: `utils/` directory with modules like `progress.py`, `observability.py`, `file_utils.py`

### 2. Shared Infrastructure Layer
- **Purpose**: Base classes, mixins, and common components
- **Dependency Rule**: May only import from the Foundation Layer and external libraries
- **Characteristics**:
  - Abstract base classes
  - Shared interfaces
  - Common implementations used across multiple modules
- **Example Patterns**: `shared/` or `base/` directory with base classes and mixins

### 3. Intermediate Layer (Base Components)
- **Purpose**: Specialized base classes that build upon shared infrastructure
- **Dependency Rule**: May import from Foundation and Shared Infrastructure layers only
- **Characteristics**:
  - More specific than shared infrastructure
  - Still abstract enough to be reused
  - Contains common patterns for specific domains
- **Example Patterns**: Domain-specific base classes like `simple/base.py`, `workflow/base.py`

### 4. Implementation Layer
- **Purpose**: Concrete implementations of functionality
- **Dependency Rule**: May import from all lower layers but not from other implementations at the same level
- **Characteristics**:
  - Concrete classes and functions
  - Business logic implementation
  - Application-specific code
- **Example Patterns**: Implementation files like `activity.py`, `chat.py`, `analyze.py`

## Cross-Layer Dependency Guidelines

### Allowed Cross-Layer Dependencies
1. **Registry/Discovery Pattern**: Higher layers may import from lower layers for component discovery
2. **Type Hinting**: Use `TYPE_CHECKING` imports for type hints to prevent runtime circular dependencies
3. **Dynamic Imports**: Use dynamic imports when needed to break potential cycles
4. **Configuration**: Configuration may be imported across layers as needed

### Discouraged Cross-Layer Dependencies
1. **Implementation-to-Implementation**: Direct imports between modules at the same implementation level
2. **Upward Dependencies**: Lower layers importing from higher layers
3. **Circular Dependencies**: Any situation where A imports B and B imports A

## Organization Strategies

### 1. Directory Structure
```
project/
├── utils/              # Foundation Layer
├── shared/             # Shared Infrastructure
├── components/         # Intermediate Layer
│   ├── simple/
│   └── workflow/
└── implementations/    # Implementation Layer
    ├── simple/
    └── workflow/
```

### 2. Import Ordering
1. Standard library imports
2. Third-party library imports
3. Foundation layer imports (utils)
4. Shared infrastructure imports
5. Intermediate layer imports
6. Implementation layer imports (if necessary)

### 3. Mixin Composition
- Keep mixins focused on a single responsibility
- Avoid circular dependencies between mixins
- Place mixins in the appropriate layer based on their dependencies

## Implementation Strategies

### 1. Dependency Management
- Regularly analyze dependency graphs to detect violations
- Use linting rules to enforce layer boundaries
- Implement automated checks for circular dependencies

### 2. Refactoring Guidelines
- When a file grows too large (>30KB), consider splitting it
- Move commonly used components to lower layers
- Extract shared functionality to appropriate layers

### 3. Change Impact Analysis
- Identify high-impact components that affect many files
- Exercise extra caution when modifying foundation layer components
- Consider the dependency radius when planning changes

## IDE Augmentation Features

### 1. Visual Layer Indicators
- Color-code files based on their layer
- Show dependency direction in the project explorer
- Highlight potential layer violations

### 2. Import Assistance
- Suggest appropriate imports based on current layer
- Warn when importing from higher layers
- Recommend TYPE_CHECKING imports for type hints

### 3. Dependency Visualization
- Show dependency graphs for selected files
- Highlight potential circular dependencies
- Display impact radius for changes

### 4. Refactoring Tools
- Suggest layer-appropriate locations for new code
- Identify components that could be moved to lower layers
- Recommend splitting large files

By following these guidelines, your IDE augmentation can help maintain a clean, layered architecture that minimizes circular dependencies and maximizes code maintainability.