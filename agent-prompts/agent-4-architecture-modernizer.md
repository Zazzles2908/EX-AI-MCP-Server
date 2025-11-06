# AGENT 4: ARCHITECTURE MODERNIZER
## Self-Aware Parallel Execution Agent

**⚠️ CRITICAL: 3 other agents are working simultaneously in separate terminals!**
- Agent 1: Performance optimization (you wait for this!)
- Agent 2: Error handling standardization (you can work in parallel!)
- Agent 3: Testing infrastructure (you can work in parallel!)

**Your work MUST NOT interfere with their work!**

## Agent Identity & Mission

**You are:** Architecture Modernization Specialist
**Your Goal:** Simplify over-engineered patterns (singletons, registries, Borg pattern)
**Priority:** P0 (Critical)
**Execution Order:** THIRD (After Agent 1 completes)

## Context: What You Need to Know

### The Problem
The EX-AI MCP Server has **excessive over-engineering** through patterns:
- **20+ singleton instances** throughout codebase
- **Monolithic registries** with 14+ methods each
- **Borg pattern** creating hidden shared state
- **Complex bootstrap chains** with circular dependencies

These patterns add complexity without benefits, creating:
- Tight coupling
- Hidden global state
- Difficult testing
- Hard to maintain

### Your Analysis Reports
Read these files for complete context:
- `docs/development/over-engineering-analysis-report.md` - Full analysis
- `docs/development/multi-agent-execution-plan.md` - Coordination plan

## Your Files (Safe to Modify)

### Singletons to Remove:
- `src/bootstrap/server_state.py` (Remove singleton pattern)
- `src/bootstrap/config_manager.py` (Remove singleton pattern)
- `src/tools/registry.py` (Remove singleton pattern)

### Registries to Split:
- `src/providers/registry.py` (Split into ProviderFactory, ProviderConfig, ProviderMetadata)

### Borg Pattern to Remove:
- `src/utils/conversation/history.py` (Replace with ConversationContext)

### Bootstrap to Simplify:
- `src/bootstrap/` directory (Implement DI container, simplify initialization)

### Configuration:
- Any config files using global state

## FORBIDDEN AREAS (DO NOT TOUCH!)

❌ **NEVER MODIFY:**
- `src/daemon/error_handling.py` (perfect framework - Agent 2 might update usage)
- `src/auth/` directory (security-critical)
- `src/security/` directory (security-critical)
- `tools/` directory (tool implementations)
- `tests/` directory (Agent 3 owns this)
- `docs/` directory (documentation)
- `src/providers/*.py` (only registry.py, not provider implementations)

## Your Work Sequence

### Phase 1: Wait for Agent 1 ✅
**Before you start, verify Agent 1 completed:**
```bash
# Check if monitoring_endpoint.py was refactored
ls -la src/daemon/monitoring/
# Should show: monitoring/ directory with multiple files
```

### Step 1: Remove ServerState Singleton
**File:** `src/bootstrap/server_state.py`

**Current (❌ Singleton):**
```python
class ServerState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
```

**Refactor to (✅ Dependency Injection):**
```python
class ServerState:
    def __init__(self):
        self._connections = []
        self._metrics = {}
        self._initialized = False

    def add_connection(self, conn):
        self._connections.append(conn)

    def get_connections(self):
        return self._connections.copy()
```

**Update all consumers:**
- Find all files importing ServerState
- Update to create instance and pass it
- Example: `state = ServerState(); handler = RequestHandler(state)`

### Step 2: Remove ConfigManager Singleton
**File:** `src/bootstrap/config_manager.py`

**Refactor to (✅ Instance-based):**
```python
class ConfigManager:
    def __init__(self, config_path: str):
        self._config_path = config_path
        self._config = {}
        self._load_config()

    def _load_config(self):
        # Load configuration from file
        pass

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def set(self, key: str, value):
        self._config[key] = value
```

### Step 3: Remove ToolRegistry Singleton
**File:** `src/tools/registry.py`

**Refactor to (✅ Per-context registry):**
```python
class ToolRegistry:
    def __init__(self):
        self._tools = {}
        self._loaded = False

    def register_tool(self, name: str, tool_class):
        self._tools[name] = tool_class

    def get_tool(self, name: str):
        return self._tools.get(name)

    def list_tools(self):
        return list(self._tools.keys())
```

### Step 4: Split ProviderRegistry
**File:** `src/providers/registry.py`

**Current (❌ Monolithic - 14+ methods):**
```python
class ProviderRegistry:
    def __init__(self):
        self._providers = {}
        self._factories = {}
        self._configs = {}
        # ... 11 more attributes
```

**Refactor to (✅ Specialized registries):**
```python
# providers/registry.py
class ProviderRegistry:
    def __init__(self):
        self.providers = {}

    def register(self, name: str, provider_class):
        self.providers[name] = provider_class

    def get(self, name: str):
        return self.providers.get(name)

# providers/factory.py
class ProviderFactory:
    def __init__(self, registry: ProviderRegistry):
        self.registry = registry

    def create(self, provider_name: str, **kwargs):
        provider_class = self.registry.get(provider_name)
        if provider_class:
            return provider_class(**kwargs)
        raise ValueError(f"Unknown provider: {provider_name}")

# providers/config.py
class ProviderConfig:
    def __init__(self, registry: ProviderRegistry):
        self.registry = registry

    def get_config(self, provider_name: str) -> dict:
        # Get configuration for provider
        pass
```

### Step 5: Replace Borg Pattern
**File:** `src/utils/conversation/history.py`

**Current (❌ Borg - shared state):**
```python
class ConversationHistory:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
```

**Refactor to (✅ Explicit context):**
```python
# utils/conversation/context.py
class ConversationContext:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages = []
        self.metadata = {}

# utils/conversation/history.py
class ConversationHistory:
    def __init__(self, contexts: dict[str, ConversationContext]):
        self.contexts = contexts

    def get_context(self, session_id: str) -> ConversationContext:
        if session_id not in self.contexts:
            self.contexts[session_id] = ConversationContext(session_id)
        return self.contexts[session_id]
```

### Step 6: Implement DI Container
**File:** `src/bootstrap/di_container.py` (NEW)
```python
class DIContainer:
    """Simple dependency injection container"""

    def __init__(self):
        self._services = {}
        self._singletons = {}

    def register(self, name: str, service_class, singleton=False):
        self._services[name] = {
            'class': service_class,
            'singleton': singleton
        }

    def get(self, name: str, *args, **kwargs):
        if name not in self._services:
            raise ValueError(f"Service {name} not registered")

        service_info = self._services[name]

        if service_info['singleton']:
            if name not in self._singletons:
                self._singletons[name] = service_info['class'](*args, **kwargs)
            return self._singletons[name]
        else:
            return service_info['class'](*args, **kwargs)
```

### Step 7: Simplify Bootstrap
**File:** `src/bootstrap/__init__.py`

**Refactor bootstrap to use DI:**
```python
def bootstrap():
    """Initialize the application with DI"""
    container = DIContainer()

    # Register services
    container.register('config', ConfigManager, singleton=True)
    container.register('server_state', ServerState, singleton=True)
    container.register('provider_registry', ProviderRegistry, singleton=True)

    # Initialize
    config = container.get('config')
    server_state = container.get('server_state')
    provider_registry = container.get('provider_registry')

    return container
```

## Validation: How to Verify Success

### Run These Checks:

1. **Singleton check:**
   ```python
   # Test that singletons are really removed
   python -c "
   from src.bootstrap.server_state import ServerState
   s1 = ServerState()
   s2 = ServerState()
   print(f'Same instance: {s1 is s2}')  # Should print: False
   "
   ```

2. **Registry check:**
   ```python
   # Test that registry is split
   python -c "
   from src.providers.factory import ProviderFactory
   from src.providers.registry import ProviderRegistry
   print('✅ Registry split successful')
   "
   ```

3. **Borg pattern check:**
   ```python
   # Test that shared state is removed
   python -c "
   from src.utils.conversation.context import ConversationContext
   from src.utils.conversation.history import ConversationHistory
   c1 = ConversationContext('user1')
   c2 = ConversationContext('user2')
   c1.messages.append('Hello')
   print(f'User2 sees message: {len(c2.messages)}')  # Should print: 0
   "
   ```

4. **DI container check:**
   ```python
   # Test DI container
   python -c "
   from src.bootstrap.di_container import DIContainer
   container = DIContainer()
   print('✅ DI container works')
   "
   ```

5. **Bootstrap check:**
   ```bash
   # Test bootstrap
   python -c "from src.bootstrap import bootstrap; container = bootstrap(); print('✅ Bootstrap successful')"
   ```

6. **Import check:**
   ```bash
   # Verify all imports work
   python -c "
   import src.bootstrap.server_state
   import src.bootstrap.config_manager
   import src.tools.registry
   import src.providers.registry
   import src.utils.conversation.history
   print('✅ All imports successful')
   "
   ```

7. **Test suite:**
   ```bash
   # Run tests
   python scripts/run_all_tests.py --type unit
   # Should pass
   ```

## What Success Looks Like

✅ **Before:**
- 20+ singleton instances
- Monolithic registries
- Hidden shared state (Borg pattern)
- Complex bootstrap chains

✅ **After:**
- 0 singleton instances (all removed)
- Specialized registries (split monoliths)
- Explicit context objects (no hidden state)
- Simple DI container initialization
- All singletons replaced with dependency injection
- All registries split into focused components
- All hidden state made explicit

## Code Templates

### Template 1: Remove Singleton
```python
# ❌ BEFORE: Singleton
class Service:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# ✅ AFTER: Dependency Injection
class Service:
    def __init__(self):
        # Initialization logic
        pass

# Usage:
service = Service()  # Create instance
consumer = Consumer(service)  # Inject dependency
```

### Template 2: Split Registry
```python
# ❌ BEFORE: Monolithic
class Registry:
    def __init__(self):
        self._things = {}
        self._other_things = {}
        self._more_things = {}

# ✅ AFTER: Specialized
class ThingRegistry:
    def __init__(self):
        self._things = {}

class OtherThingRegistry:
    def __init__(self):
        self._other_things = {}
```

### Template 3: Remove Borg
```python
# ❌ BEFORE: Borg pattern
class SharedState:
    _shared = {}
    def __init__(self):
        self.__dict__ = self._shared

# ✅ AFTER: Explicit context
class Context:
    def __init__(self, id):
        self.id = id
        self.data = {}

class Manager:
    def __init__(self):
        self.contexts = {}
```

## Risk Mitigation

**If you break something:**
1. Don't panic
2. Run: `git diff` to see your changes
3. Test: `python -c "import src.bootstrap.server_state"`
4. If broken: `git checkout -- <file>` and try again

**If Agent 1 is still working:**
- Wait! Do NOT start until Agent 1 completes
- Verify: `ls -la src/daemon/monitoring/`
- If monitoring/ exists, Agent 1 is done

**If Agent 2 changes provider code:**
- They might update imports after you split the registry
- No problem - you'll coordinate

**If Agent 3 breaks tests:**
- They shouldn't - you're not touching tests/
- If they do, they'll fix it

## Parallel Agent Awareness

**Agents working simultaneously:**
- Agent 1: Performance (WAIT FOR THIS FIRST!)
- Agent 2: Error handling (you can work in parallel)
- Agent 3: Testing infrastructure (you can work in parallel)

**Your coordination with them:**
- Wait for Agent 1 to complete
- Work independently from Agent 2 and 3
- No file overlap with Agent 1 (they own monitoring/, you avoid it)
- No file overlap with Agent 2 (they avoid bootstrap/)
- No file overlap with Agent 3 (they own tests/)

**What each agent is doing:**
- Agent 1: Decomposing monitoring_endpoint.py
- Agent 2: Standardizing error handling in providers/
- Agent 3: Setting up test coverage and CI/CD

**Your unique value:**
- You simplify the architecture
- You make the system more maintainable
- You enable better testing (no singletons!)

## Estimated Time

- **Effort:** 6-8 hours
- **Start:** After Agent 1 validates
- **Parallel with:** Agents 2 and 3

## Start Checklist

Before you begin:
- [ ] Agent 1 has completed (check: `ls src/daemon/monitoring/`)
- [ ] You've read over-engineering-analysis-report.md
- [ ] You understand all the patterns to remove
- [ ] You know your forbidden areas

## Start Now

Verify you can start:
```bash
# Check if Agent 1 is done
ls -la src/daemon/monitoring/ 2>/dev/null && echo "✅ Agent 1 complete - you can start!" || echo "⏳ Wait for Agent 1"

# Check current singletons
python -c "
from src.bootstrap.server_state import ServerState
s1 = ServerState()
s2 = ServerState()
print(f'Singleton exists: {s1 is s2}')  # Will show True before you fix it
"

# Find singleton files
find src/ -name "*.py" -exec grep -l "_instance.*__new__" {} \;
```

**Go!** Modernize the architecture and remove over-engineering! 🏗️
