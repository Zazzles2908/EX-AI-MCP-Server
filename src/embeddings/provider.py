"""
Embeddings provider adapter layer for EX MCP Server (Phase 5).

Goal: provider-agnostic embeddings with an external adapter option.

- EmbeddingsProvider: interface
- KimiEmbeddingsProvider: uses Kimi OpenAI-compatible embeddings API
- GLMEmbeddingsProvider: optional placeholder (can be implemented later)
- ExternalEmbeddingsProvider: POSTs to EXTERNAL_EMBEDDINGS_URL (JSON), expects {embeddings: [[...], ...]}
- get_embeddings_provider(): selects by EMBEDDINGS_PROVIDER env (external|kimi|glm)
"""
from __future__ import annotations

import logging
import os
from typing import List, Sequence, Optional, Any, Dict

logger = logging.getLogger(__name__)


class EmbeddingsProvider:
    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        raise NotImplementedError


class KimiEmbeddingsProvider(EmbeddingsProvider):
    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model or os.getenv("KIMI_EMBED_MODEL", "text-embedding-3-large")
        logger.info(f"Initializing KimiEmbeddingsProvider with model: {self.model}")

        # Resolve Kimi client either via provider registry or direct OpenAI-compatible client
        try:
            from src.providers.registry import ModelProviderRegistry  # lazy import
            from src.providers.kimi import KimiModelProvider  # type: ignore
        except ImportError as e:
            logger.error(f"Failed to import provider modules: {e}")
            raise RuntimeError("Provider modules not available for Kimi embeddings") from e

        try:
            prov = ModelProviderRegistry.get_provider_for_model(os.getenv("KIMI_DEFAULT_MODEL", "kimi-latest"))
        except Exception as e:
            logger.warning(f"Failed to get provider from registry: {e}; falling back to direct client")
            prov = None

        if not isinstance(prov, KimiModelProvider):
            api_key = os.getenv("KIMI_API_KEY", "").strip()
            if not api_key:
                logger.error("KIMI_API_KEY is not configured")
                raise RuntimeError("KIMI_API_KEY is not configured")
            base_url = os.getenv("KIMI_API_URL", "https://api.moonshot.ai/v1").strip()
            try:
                from openai import OpenAI  # type: ignore
                self.client = OpenAI(api_key=api_key, base_url=base_url)
                logger.info(f"Created direct OpenAI client for Kimi embeddings (base_url={base_url})")
            except ImportError as e:
                logger.error(f"OpenAI SDK not available: {e}")
                raise RuntimeError("OpenAI SDK not available for Kimi embeddings") from e
            except Exception as e:
                logger.error(f"Failed to create OpenAI client: {e}")
                raise RuntimeError(f"Failed to initialize Kimi embeddings client: {e}") from e
        else:
            client = getattr(prov, "client", None)
            if client is None or not hasattr(client, "embeddings"):
                logger.error("Kimi provider client does not expose embeddings API")
                raise RuntimeError("Kimi provider client does not expose embeddings API")
            self.client = client
            logger.info("Using Kimi provider client from registry")

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        if not texts:
            return []
        resp = self.client.embeddings.create(model=self.model, input=list(texts))
        data = getattr(resp, "data", None) or getattr(resp, "embeddings", None) or []
        out: List[List[float]] = []
        for item in data:
            vec = getattr(item, "embedding", None) or (item.get("embedding") if isinstance(item, dict) else None)
            if not isinstance(vec, list):
                raise RuntimeError("Unexpected embeddings item format from Kimi")
            out.append([float(x) for x in vec])
        return out


class GLMEmbeddingsProvider(EmbeddingsProvider):
    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model or os.getenv("GLM_EMBED_MODEL", "text-embedding-ada-002")
        # Placeholder: implement using ZhipuAI embeddings API if/when available.
        raise NotImplementedError("GLM embeddings not implemented yet; prefer external adapter or Kimi short-term")


class ExternalEmbeddingsProvider(EmbeddingsProvider):
    def __init__(self, url: Optional[str] = None, timeout: float = 30.0) -> None:
        self.url = (url or os.getenv("EXTERNAL_EMBEDDINGS_URL", "")).strip()
        if not self.url:
            logger.error("EXTERNAL_EMBEDDINGS_URL is not set for external provider")
            raise RuntimeError("EXTERNAL_EMBEDDINGS_URL is not set for external provider")
        self.timeout = timeout
        logger.info(f"Initialized ExternalEmbeddingsProvider (url={self.url}, timeout={timeout}s)")

        # Validate requests library is available
        try:
            import requests  # noqa: F401
        except ImportError as e:
            logger.error(f"requests library not available: {e}")
            raise RuntimeError("requests library required for ExternalEmbeddingsProvider") from e

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        if not texts:
            return []
        import requests
        payload: Dict[str, Any] = {"texts": list(texts)}
        r = requests.post(self.url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        j = r.json()
        embs = j.get("embeddings")
        if not isinstance(embs, list) or not all(isinstance(v, list) for v in embs):
            raise RuntimeError("External embeddings response missing 'embeddings' list")
        return [[float(x) for x in row] for row in embs]


def get_embeddings_provider() -> EmbeddingsProvider:
    choice = (os.getenv("EMBEDDINGS_PROVIDER", "").strip() or "external").lower()
    logger.info(f"Selecting embeddings provider: {choice}")

    try:
        if choice == "external":
            return ExternalEmbeddingsProvider()
        if choice == "kimi":
            return KimiEmbeddingsProvider()
        if choice == "glm":
            return GLMEmbeddingsProvider()
        # Fallback for safety
        logger.warning(f"Unknown embeddings provider '{choice}', falling back to external")
        return ExternalEmbeddingsProvider()
    except Exception as e:
        logger.error(f"Failed to initialize embeddings provider '{choice}': {e}")
        raise RuntimeError(f"Failed to initialize embeddings provider '{choice}': {e}") from e

