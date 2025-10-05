# Batch 12 Code Review

## Files Reviewed
- `__init__.py` (tool management)
- `file_context_resolver.py`
- `__init__.py` (moonshot provider shim)
- `streaming_flags.py`
- `websearch_adapter.py`

## Findings

### CRITICAL: Missing error handling in streaming_flags.py
**File:** `streaming_flags.py`
**Lines:** 15-16
**Category:** security
**Issue:** The function `is_streaming_enabled` returns `bool(enabled)` which could expose internal state if `enabled` is not a boolean. The environment variable parsing could return unexpected types.
**Recommendation:** Add explicit type conversion and validation:
```python
if p == "glm" and t == "chat":
    return str(enabled).lower() in ("1", "true", "yes")
return False
```

### HIGH: Unsafe path resolution in file_context_resolver.py
**File:** `file_context_resolver.py`
**Lines:** 35-40, 48-53
**Category:** security
**Issue:** The `_is_under_any_root` and `_is_under_root` functions use `path.resolve()` without proper error handling for symlink attacks or circular references. This could allow directory traversal if TEST_FILES_DIR is misconfigured.
**Recommendation:** Add symlink validation and use `path.absolute()` instead of `resolve()` for safety:
```python
def _is_under_root(path: Path, root: Path) -> bool:
    try:
        # Validate no symlinks outside root
        if path.is_symlink():
            target = path.readlink()
            if target.is_absolute() and not str(target).startswith(str(root)):
                return False
        path_abs = path.absolute()
        root_abs = root.absolute()
        return root_abs in path_abs.parents or path_abs == root_abs
    except Exception:
        return False
```

### HIGH: Missing input validation in websearch_adapter.py
**File:** `websearch_adapter.py`
**Lines:** 20-25
**Category:** architecture
**Issue:** The function doesn't validate the `provider_type` parameter before passing to `get_capabilities_for_provider`. This could cause unexpected errors if None or invalid types are passed.
**Recommendation:** Add provider type validation:
```python
if not provider_type:
    return provider_kwargs, None
# Validate provider_type is a valid Provider enum or string
valid_providers = {"glm", "kimi"}
if str(provider_type).lower() not in valid_providers:
    return provider_kwargs, None
```

### MEDIUM: Inconsistent error handling patterns
**File:** `file_context_resolver.py`
**Lines:** 85-95, 115-125
**Category:** best_practices
**Issue:** The error handling uses broad exception catching (`except Exception`) which could mask important errors. Different functions handle similar errors differently.
**Recommendation:** Use more specific exception handling:
```python
except (OSError, ValueError, TypeError) as e:
    # Log specific error types
    logger.debug(f"Specific error in glob pattern '{g}': {type(e).__name__}: {e}")
except PermissionError as e:
    logger.warning(f"Permission denied accessing '{p}': {e}")
    continue
```

### MEDIUM: Missing type hints in __init__.py files
**File:** Both `__init__.py` files
**Lines:** All
**Category:** best_practices
**Issue:** The `__init__.py` files lack proper type hints and documentation. The moonshot provider shim uses wildcard imports which could pollute the namespace.
**Recommendation:** Add explicit imports and type hints:
```python
# In tool management __init__.py
from typing import List

__all__: List[str] = [
    "parse_disabled_tools_env",
    "validate_disabled_tools",
    # ... etc
]
```

### LOW: Inefficient glob pattern handling
**File:** `file_context_resolver.py`
**Lines:** 78-84
**Category:** performance
**Issue:** The `_collect_from_globs` function converts the input to a list twice and uses inefficient slicing.
**Recommendation:** Optimize the pattern processing:
```python
def _collect_from_globs(globs: Iterable[str], roots: List[Path], max_each: int = 50) -> List[Path]:
    out: List[Path] = []
    # Convert once and limit early
    patterns = list(islice(globs, 8))
    for g in patterns:
        try:
            matches = glob.glob(g, recursive=True)[:max_each]
            for m in matches:
                if isinstance(m, str):
                    p = Path(m).resolve()
                    if p.is_file() and _is_under_any_root(p, roots):
                        out.append(p)
        except (OSError, ValueError, TypeError) as e:
            logger.debug(f"Glob pattern '{g}' failed: {e}")
            continue
    return out
```

### LOW: