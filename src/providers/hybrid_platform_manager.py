from __future__ import annotations

import os
import urllib.request
from time import sleep
from typing import Dict, Optional, Callable, Awaitable


class HybridPlatformManager:
    """Unified platform management for Moonshot (Kimi-compatible) and Z.ai (GLM).

    MVP goals (Phase E):
    - Do not import heavy SDKs here; defer to callers or optional imports
    - Provide environment-based configuration and a simple health_check stub
    - Establish a safe place to add retries/backoff/failure classification later
    """

    def __init__(
        self,
        moonshot_api_key: Optional[str] = None,
        zai_api_key: Optional[str] = None,
        moonshot_base_url: Optional[str] = None,
        zai_base_url: Optional[str] = None,
    ) -> None:
        self.moonshot_api_key = moonshot_api_key or os.getenv("MOONSHOT_API_KEY", "")
        self.zai_api_key = zai_api_key or os.getenv("ZAI_API_KEY", "")
        self.moonshot_base_url = (
            moonshot_base_url or os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1")
        )
        # Use z.ai proxy (3x faster than bigmodel.cn according to user testing)
        self.zai_base_url = zai_base_url or os.getenv("ZAI_BASE_URL", "https://api.z.ai/api/paas/v4")

        # NOTE: SDK client placeholders - intentionally None for MVP
        # Current implementation uses simple_ping() and health_check() without SDK clients
        # Used by: monitoring/health_monitor_factory.py for platform health probes
        # Future enhancement: Initialize SDK clients here if needed for advanced features
        self.moonshot_client = None
        self.zai_client = None

        # Ensure a default event loop exists in main thread for legacy callers/tests
        try:
            import asyncio
            asyncio.get_running_loop()
        except RuntimeError:
            try:
                import asyncio
                asyncio.set_event_loop(asyncio.new_event_loop())
            except Exception:
                pass

    async def health_check(self) -> Dict[str, bool]:
        """Return a simple health map based on minimal availability signals.

        This MVP avoids network calls. Later we can add small HEAD/GET pings with timeouts.
        """
        moonshot_ok = bool(self.moonshot_api_key)
        zai_ok = bool(self.zai_api_key)
        return {"moonshot": moonshot_ok, "zai": zai_ok}

    async def simple_ping(self, platform: str, timeout: float = 1.0) -> bool:
        """Attempt a minimal GET to the provider base URL root.
        No external deps; safe failure returns False.
        """
        base = self.moonshot_base_url if platform == "moonshot" else self.zai_base_url
        try:
            req = urllib.request.Request(base, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as _:
                return True
        except Exception:
            return False

    async def with_retry(self, func: Callable[[], Awaitable], retries: int = 2, backoff_s: float = 0.2):
        """Tiny async retry wrapper with linear backoff."""
        last_exc: Optional[Exception] = None
        for attempt in range(retries + 1):
            try:
                return await func()
            except Exception as e:  # pragma: no cover - behavior validated indirectly
                last_exc = e
                if attempt < retries:
                    sleep(backoff_s * (attempt + 1))
        if last_exc:
            raise last_exc

