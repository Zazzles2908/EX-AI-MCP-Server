"""
AI Auditor Service - Real-time monitoring and analysis of system events

This service watches the WebSocket event stream and provides AI-powered
observations about system behavior, performance, security, and reliability.

Created: 2025-10-24
Model: Kimi Turbo (kimi-k2-turbo-preview)
"""

import asyncio
import json
import os
import time
import signal
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime
import websockets
from openai import AsyncOpenAI

from utils.timezone_helper import log_timestamp
from src.storage.supabase_client import SupabaseStorageManager
import logging

logger = logging.getLogger(__name__)


class AIAuditor:
    """Real-time AI auditor watching system events"""
    
    def __init__(
        self,
        model: str = "kimi-k2-turbo-preview",
        batch_size: int = 10,
        analysis_interval: int = 5,
        ws_url: str = "ws://localhost:8080/ws"
    ):
        """
        Initialize AI Auditor

        Args:
            model: AI model to use (supports both GLM and Kimi models)
            batch_size: Number of events to batch before analysis
            analysis_interval: Seconds between analyses
            ws_url: WebSocket URL to monitor
        """
        self.model = model
        self.batch_size = batch_size
        self.analysis_interval = analysis_interval
        self.ws_url = ws_url

        # Determine provider based on model name
        self.is_glm = model.startswith("glm-")

        # Initialize appropriate client
        if self.is_glm:
            # Use ZhipuAI SDK for GLM models
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=os.getenv("GLM_API_KEY"))
            self.client_type = "glm"
        else:
            # Use OpenAI SDK for Kimi models
            self.client = AsyncOpenAI(
                api_key=os.getenv("KIMI_API_KEY"),
                base_url="https://api.moonshot.ai/v1"
            )
            self.client_type = "kimi"
        
        # Initialize Supabase client
        self.supabase = SupabaseStorageManager()
        
        # Event buffer
        self.event_buffer: List[Dict] = []
        self.last_analysis_time = time.time()
        
        # Statistics
        self.stats = {
            "events_processed": 0,
            "analyses_performed": 0,
            "observations_created": 0,
            "observations_stored": 0,
            "storage_failures": 0,
            "websocket_reconnects": 0,
            "circuit_breaker_trips": 0,
            "duplicates_filtered": 0,
            "errors": 0
        }

        # Circuit breaker
        self.consecutive_failures = 0
        self.max_failures = 3
        self.circuit_open = False

        # Shutdown event for graceful termination
        self.shutdown_event = asyncio.Event()

        # Deduplication cache (observation hash -> timestamp)
        self.observation_cache: Dict[str, float] = {}
        self.cache_ttl = 3600  # 1 hour TTL for deduplication

        # Setup signal handlers for graceful shutdown
        try:
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
        except ValueError:
            # Signal handlers can only be set in main thread
            logger.warning("[AI_AUDITOR] Cannot set signal handlers (not in main thread)")

        logger.info(f"[AI_AUDITOR] Initialized with model={model}, batch_size={batch_size}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"[AI_AUDITOR] Shutdown signal received: {signum}")
        self.shutdown_event.set()
    
    async def start(self):
        """Start the AI auditor service with auto-reconnection"""
        logger.info(f"[AI_AUDITOR] Starting auditor service, connecting to {self.ws_url}")

        reconnect_delay = 5
        max_reconnect_delay = 60

        while True:
            try:
                await self._connect_and_watch()
                # Reset delay on successful connection
                reconnect_delay = 5
            except Exception as e:
                logger.error(f"[AI_AUDITOR] Connection error: {e}")
                logger.info(f"[AI_AUDITOR] Reconnecting in {reconnect_delay}s...")
                await asyncio.sleep(reconnect_delay)
                # Exponential backoff
                reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)
    
    async def _connect_and_watch(self):
        """Connect to WebSocket and watch events"""
        # PHASE 2.4 FIX (2025-10-26): EXAI COMPREHENSIVE FIX - Apply same ping timeout as main WebSocket
        # Root cause: AI Auditor WebSocket experiencing same keepalive timeout issues
        # EXAI recommended: Use same timeout values as main WebSocket (45s interval, 240s timeout)
        async with websockets.connect(
            self.ws_url,
            ping_interval=45,  # Increased from default 20s per EXAI recommendation
            ping_timeout=240   # Increased from default 20s per EXAI recommendation
        ) as websocket:
            logger.info("[AI_AUDITOR] Connected to monitoring WebSocket")
            
            async for message in websocket:
                try:
                    event = json.loads(message)
                    await self._process_event(event)
                except json.JSONDecodeError:
                    logger.warning(f"[AI_AUDITOR] Invalid JSON received: {message[:100]}")
                except Exception as e:
                    logger.error(f"[AI_AUDITOR] Error processing event: {e}")
    
    async def _process_event(self, event: Dict):
        """Process incoming event"""
        # Add to buffer
        self.event_buffer.append(event)
        self.stats["events_processed"] += 1
        
        # Check if we should analyze
        if self._should_analyze():
            await self._analyze_batch()
    
    def _should_analyze(self) -> bool:
        """Determine if we should analyze now"""
        time_elapsed = time.time() - self.last_analysis_time
        
        return (
            len(self.event_buffer) >= self.batch_size or
            time_elapsed >= self.analysis_interval
        ) and not self.circuit_open
    
    async def _analyze_batch(self):
        """Analyze batch of events with AI"""
        if not self.event_buffer:
            return
        
        # Get events to analyze
        events = self.event_buffer.copy()
        self.event_buffer.clear()
        self.last_analysis_time = time.time()
        
        logger.info(f"[AI_AUDITOR] Analyzing batch of {len(events)} events")
        
        try:
            # Build context
            context = self._build_context(events)
            
            # Get AI analysis
            observations = await self._get_ai_analysis(context, events)
            
            # Store observations
            if observations:
                await self._store_observations(observations)
                self.stats["observations_created"] += len(observations)
            
            self.stats["analyses_performed"] += 1
            self.consecutive_failures = 0
            
        except Exception as e:
            logger.error(f"[AI_AUDITOR] Analysis failed: {e}")
            self.stats["errors"] += 1
            self.consecutive_failures += 1
            
            # Open circuit breaker if too many failures
            if self.consecutive_failures >= self.max_failures:
                self.circuit_open = True
                logger.error("[AI_AUDITOR] Circuit breaker opened due to consecutive failures")
                # Schedule circuit breaker reset
                asyncio.create_task(self._reset_circuit_breaker())
    
    async def _reset_circuit_breaker(self):
        """Reset circuit breaker after cooldown period"""
        await asyncio.sleep(60)  # 1 minute cooldown
        self.circuit_open = False
        self.consecutive_failures = 0
        logger.info("[AI_AUDITOR] Circuit breaker reset")
    
    def _build_context(self, events: List[Dict]) -> str:
        """Build context string from events"""
        context_parts = []
        
        for event in events:
            event_type = event.get("type", "unknown")
            
            if event_type == "event":
                context_parts.append(
                    f"- {event.get('connection_type')} {event.get('direction')}: "
                    f"{event.get('script_name')}.{event.get('function_name')} "
                    f"({event.get('response_time_ms', 0)}ms)"
                )
                if event.get("error"):
                    context_parts.append(f"  ERROR: {event['error']}")
            
            elif event_type == "session_metrics":
                data = event.get("data", {})
                context_parts.append(
                    f"- Session: {data.get('active_sessions')} active, "
                    f"model={data.get('current_model')}, "
                    f"tokens={data.get('context_tokens_used')}/{data.get('context_tokens_max')}"
                )
        
        return "\n".join(context_parts)
    
    async def _get_ai_analysis(self, context: str, events: List[Dict]) -> List[Dict]:
        """Get AI analysis of events"""
        prompt = f"""You are an AI auditor monitoring a system testing process.

Analyze these recent events and provide observations:

{context}

For each significant finding, provide a JSON object with:
- observation: What you noticed (concise, specific)
- severity: "critical", "warning", or "info"
- category: "performance", "security", "reliability", "quality", or "general"
- confidence: 0-100 (your confidence in this observation)
- recommendation: What to do about it (optional)

Focus on:
- Performance anomalies (slow responses, timeouts)
- Error patterns (repeated failures, error spikes)
- Security concerns (authentication issues, data leaks)
- Reliability issues (connection failures, retries)
- Quality degradation (increasing error rates)

Only report significant findings. Return a JSON array of observations.
If nothing significant, return an empty array: []
"""

        try:
            if self.is_glm:
                # Use ZhipuAI SDK (synchronous) - run in thread pool
                import asyncio
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a system monitoring AI that provides concise, actionable observations."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
            else:
                # Use OpenAI SDK (async)
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a system monitoring AI that provides concise, actionable observations."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )

            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()
            
            observations = json.loads(content)
            
            # Add event IDs to each observation
            event_ids = [e.get("id", str(i)) for i, e in enumerate(events)]
            for obs in observations:
                obs["event_ids"] = event_ids
            
            return observations
            
        except json.JSONDecodeError as e:
            logger.error(f"[AI_AUDITOR] Failed to parse AI response as JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"[AI_AUDITOR] AI analysis failed: {e}")
            raise
    
    async def _store_observations(self, observations: List[Dict]):
        """Store observations in Supabase with retry logic"""
        for obs in observations:
            max_retries = 3
            retry_delay = 1

            for attempt in range(max_retries):
                try:
                    client = self.supabase.get_client()

                    # Prepare observation data
                    observation_data = {
                        "event_ids": obs.get("event_ids", []),
                        "observation": obs.get("observation", ""),
                        "severity": obs.get("severity", "info"),
                        "category": obs.get("category", "general"),
                        "confidence": obs.get("confidence", 50),
                        "recommendation": obs.get("recommendation"),
                        "timestamp": log_timestamp(),
                        "metadata": {
                            "model": self.model,
                            "batch_size": len(obs.get("event_ids", [])),
                            "auditor_version": "1.0.0"
                        }
                    }

                    # Execute insert in thread pool (Supabase client is sync)
                    await asyncio.to_thread(
                        lambda: client.table("auditor_observations").insert(observation_data).execute()
                    )

                    logger.info(
                        f"[AI_AUDITOR] Stored observation: "
                        f"severity={obs.get('severity')}, "
                        f"category={obs.get('category')}, "
                        f"confidence={obs.get('confidence')}%"
                    )
                    break  # Success, exit retry loop

                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"[AI_AUDITOR] Failed to store observation (attempt {attempt + 1}/{max_retries}): {e}"
                        )
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"[AI_AUDITOR] Failed to store observation after {max_retries} attempts: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get auditor statistics"""
        return {
            **self.stats,
            "circuit_open": self.circuit_open,
            "buffer_size": len(self.event_buffer),
            "model": self.model,
            "batch_size": self.batch_size,
            "analysis_interval": self.analysis_interval
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on auditor service"""
        health = {
            "status": "healthy",
            "checks": {}
        }

        # Check circuit breaker
        health["checks"]["circuit_breaker"] = {
            "status": "open" if self.circuit_open else "closed",
            "consecutive_failures": self.consecutive_failures
        }

        # Check event buffer
        buffer_size = len(self.event_buffer)
        health["checks"]["event_buffer"] = {
            "status": "ok" if buffer_size < self.batch_size * 2 else "warning",
            "size": buffer_size,
            "capacity": self.batch_size * 2
        }

        # Check Supabase connection
        try:
            await self.supabase.supabase.table("auditor_observations").select("id").limit(1).execute()
            health["checks"]["supabase"] = {"status": "ok"}
        except Exception as e:
            health["checks"]["supabase"] = {"status": "error", "error": str(e)}
            health["status"] = "unhealthy"

        # Check AI model
        try:
            # Simple ping to check if client is initialized
            if self.client:
                health["checks"]["ai_model"] = {"status": "ok", "model": self.model}
            else:
                health["checks"]["ai_model"] = {"status": "error", "error": "Client not initialized"}
                health["status"] = "unhealthy"
        except Exception as e:
            health["checks"]["ai_model"] = {"status": "error", "error": str(e)}
            health["status"] = "unhealthy"

        return health


async def main():
    """Main entry point for running auditor as standalone service"""
    auditor = AIAuditor()
    await auditor.start()


if __name__ == "__main__":
    asyncio.run(main())

