# Remaining Pyflakes Issues

**Date:** 2025-10-20 21:30 AEDT
**Status:** DOCUMENTED - Low Priority
**Total Issues:** 48 (all minor code quality)

## Summary

All CRITICAL bugs have been fixed (undefined logger in registry_selection.py). The remaining issues are minor code quality improvements that don't affect functionality:
- 20 unused imports
- 18 f-strings missing placeholders
- 5 unused local variables
- 5 unused global declarations

**Impact:** NONE - These are cosmetic issues only
**Priority:** LOW - Can be fixed incrementally during future refactoring

---

## Unused Imports (20 issues)

### Bootstrap & Core
- `src/bootstrap/logging_setup.py:15` - `pathlib.Path` imported but unused
- `src/bootstrap/singletons.py:23` - `os` imported but unused
- `src/core/config.py:7` - `pathlib.Path` imported but unused

### Daemon
- `src/daemon/conversation_queue.py:25` - `typing.Any` imported but unused
- `src/daemon/health_endpoint.py:13` - `json` imported but unused
- `src/daemon/health_endpoint.py:15` - `os` imported but unused
- `src/daemon/health_endpoint.py:17` - `datetime.datetime` imported but unused
- `src/daemon/session_semaphore_manager.py:18` - `datetime.datetime` imported but unused
- `src/daemon/ws_server.py:35` - `src.core.config.get_config` imported but unused

### Embeddings & Monitoring
- `src/embeddings/provider.py:194` - `requests` imported but unused
- `src/monitoring/metrics.py:13` - `os` imported but unused
- `src/monitoring/resilient_websocket.py:21` - `typing.Any` imported but unused

### Providers
- `src/providers/async_glm_chat.py:11` - `.base.ProviderType` imported but unused
- `src/providers/async_glm_chat.py:12` - `.glm_chat.build_payload` imported but unused
- `src/providers/glm_config.py:8` - `typing.Optional` imported but unused
- `src/providers/kimi.py:7` - `.base.ModelProvider` imported but unused
- `src/providers/kimi_config.py:8` - `typing.Optional` imported but unused
- `src/providers/moonshot/__init__.py:3` - `src.providers.kimi.*` imported but unused
- `src/providers/openai_compatible.py:7` - `time` imported but unused
- `src/providers/registry_config.py:20` - `typing.Optional` imported but unused
- `src/providers/registry_selection.py:222` - `src.providers.registry_core.ModelProviderRegistry as cls` imported but unused

---

## F-Strings Missing Placeholders (18 issues)

### Daemon
- `src/daemon/monitoring_endpoint.py:162` - f-string is missing placeholders
- `src/daemon/ws_server.py:99` - f-string is missing placeholders
- `src/daemon/ws_server.py:102` - f-string is missing placeholders
- `src/daemon/ws_server.py:657` - f-string is missing placeholders
- `src/daemon/ws_server.py:667` - f-string is missing placeholders
- `src/daemon/ws_server.py:668` - f-string is missing placeholders
- `src/daemon/ws_server.py:933` - f-string is missing placeholders
- `src/daemon/ws_server.py:943` - f-string is missing placeholders
- `src/daemon/ws_server.py:1000` - f-string is missing placeholders
- `src/daemon/ws_server.py:1006` - f-string is missing placeholders
- `src/daemon/ws_server.py:1007` - f-string is missing placeholders
- `src/daemon/ws_server.py:1102` - f-string is missing placeholders
- `src/daemon/ws_server.py:1108` - f-string is missing placeholders
- `src/daemon/ws_server.py:1148` - f-string is missing placeholders
- `src/daemon/ws_server.py:1154` - f-string is missing placeholders
- `src/daemon/ws_server.py:1155` - f-string is missing placeholders
- `src/daemon/ws_server.py:1212` - f-string is missing placeholders

### Embeddings & Providers
- `src/embeddings/provider.py:132` - f-string is missing placeholders
- `src/providers/async_base.py:134` - f-string is missing placeholders
- `src/providers/kimi_chat.py:211` - f-string is missing placeholders
- `src/providers/text_format_handler.py:202` - f-string is missing placeholders

---

## Unused Variables (5 issues)

- `src/daemon/health_endpoint.py:143` - local variable 'result' is assigned to but never used
- `src/daemon/warmup.py:57` - local variable 'result' is assigned to but never used

---

## Unused Global Declarations (5 issues)

- `src/daemon/conversation_queue.py:266` - `global _conversation_queue` is unused
- `src/daemon/semaphore_manager.py:269` - `global _provider_semaphore_managers` is unused
- `src/daemon/session_semaphore_manager.py:247` - `global _session_semaphore_manager` is unused
- `src/daemon/ws_server.py:486` - `global _resilient_ws` is unused
- `src/providers/kimi_cache.py:88` - `global _cache_tokens_order` is unused

---

## Recommended Fix Strategy

**Batch 1: Unused Imports (Quick Win)**
- Remove all unused imports
- Test after each file
- Commit incrementally

**Batch 2: F-Strings (Quick Win)**
- Change f"text" to "text" where no placeholders
- Test after each file
- Commit incrementally

**Batch 3: Unused Variables (Investigate First)**
- Check if these variables are needed for side effects
- If not, remove assignments
- Test carefully

**Batch 4: Unused Globals (Investigate First)**
- Check if these are used in other modules
- May be false positives from pyflakes
- Investigate before removing

---

## Notes

- All critical bugs already fixed (commit 9762c6d)
- These are cosmetic improvements only
- No functional impact
- Can be addressed during future refactoring
- Low priority compared to functional testing


