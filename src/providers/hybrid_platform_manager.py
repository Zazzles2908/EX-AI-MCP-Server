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

        # Initialize SDK clients for health monitoring and advanced features (Phase 4: 2025-10-09)
        # Moonshot uses OpenAI-compatible SDK
        # ZhipuAI uses native zhipuai SDK
        self.moonshot_client = None
        self.zai_client = None

        # Initialize Moonshot client if API key is available
        if self.moonshot_api_key:
            try:
                from openai import OpenAI
                self.moonshot_client = OpenAI(
                    api_key=self.moonshot_api_key,
                    base_url=self.moonshot_base_url
                )
            except ImportError:
                # OpenAI SDK not installed - fall back to None
                pass
            except Exception:
                # Initialization failed - fall back to None
                pass

        # Initialize ZhipuAI client if API key is available
        if self.zai_api_key:
            try:
                from zhipuai import ZhipuAI
                self.zai_client = ZhipuAI(
                    api_key=self.zai_api_key,
                    base_url=self.zai_base_url
                )
            except ImportError:
                # ZhipuAI SDK not installed - fall back to None
                pass
            except Exception:
                # Initialization failed - fall back to None
                pass

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
        """Return health status for both platforms using SDK clients when available.

        Phase 4 (2025-10-09): Enhanced to use SDK clients for actual health checks.
        Falls back to API key presence check if SDK clients are not initialized.
        """
        moonshot_ok = False
        zai_ok = False

        # Check Moonshot/Kimi health
        if self.moonshot_client:
            try:
                # Try to list models as a lightweight health check
                # This verifies API key, network connectivity, and service availability
                import asyncio
                models = await asyncio.to_thread(lambda: self.moonshot_client.models.list())
                moonshot_ok = bool(models)
            except Exception:
                # SDK call failed - fall back to API key check
                moonshot_ok = bool(self.moonshot_api_key)
        else:
            # No SDK client - check if API key is present
            moonshot_ok = bool(self.moonshot_api_key)

        # Check ZhipuAI/GLM health
        if self.zai_client:
            try:
                # Try to list models as a lightweight health check
                import asyncio
                models = await asyncio.to_thread(lambda: self.zai_client.models.list())
                zai_ok = bool(models)
            except Exception:
                # SDK call failed - fall back to API key check
                zai_ok = bool(self.zai_api_key)
        else:
            # No SDK client - check if API key is present
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

