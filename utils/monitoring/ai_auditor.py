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
            # Use OpenAI SDK for GLM models (z.ai proxy for compatibility)
            self.client = AsyncOpenAI(
                api_key=os.getenv("GLM_API_KEY"),
                base_url="https://api.z.ai/api/paas/v4"
            )
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

        # PRIORITY 2 FIX (2025-10-27): Rate limiting to prevent excessive API calls
        self.hourly_calls = 0
        self.max_hourly_calls = 60  # Max 1 API call per minute
        self.hour_start = time.time()

        # PRIORITY 3 FIX (2025-10-27): Adaptive intervals and cost tracking
        self.recent_errors = 0  # Track recent error count for adaptive intervals
        self.error_window_start = time.time()
        self.total_cost = 0.0  # Track total API cost
        self.daily_cost_limit = 10.0  # Daily cost limit in USD

        # Statistics
        self.stats = {
            "events_processed": 0,
            "events_filtered": 0,  # PRIORITY 2: Track filtered events
            "analyses_performed": 0,
            "analyses_skipped_rate_limit": 0,  # PRIORITY 2: Track rate-limited analyses
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

        logger.info(f"[AI_AUDITOR] Initialized with model={model}, batch_size={batch_size}, max_hourly_calls={self.max_hourly_calls}")

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
    
    def _safe_numeric_compare(self, value, threshold, operation='>'):
        """
        Null-safe numeric comparison.
        Returns False if value is None.

        FIX (2025-10-29): Prevents NoneType comparison errors in AI Auditor
        """
        if value is None:
            return False

        if operation == '>':
            return value > threshold
        elif operation == '<':
            return value < threshold
        elif operation == '>=':
            return value >= threshold
        elif operation == '<=':
            return value <= threshold
        elif operation == '==':
            return value == threshold
        elif operation == '!=':
            return value != threshold
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def _should_buffer_event(self, event: Dict) -> bool:
        """PRIORITY 3: Smart event selection - determine if event should be buffered"""
        severity = event.get('severity', 'info').lower()
        event_type = event.get('type', '')

        # Always buffer errors and critical events
        if severity in ['error', 'critical']:
            return True

        # Sample routine events (10% sampling for health checks)
        if event_type == 'health_check':
            import random
            return random.random() < 0.1

        # Buffer performance anomalies (response time > 1 second)
        # FIX (2025-10-29): Use null-safe comparison to prevent NoneType errors
        if self._safe_numeric_compare(event.get('response_time_ms'), 1000, '>'):
            return True

        # Buffer warnings
        if severity == 'warning':
            return True

        return False

    async def _process_event(self, event: Dict):
        """Process incoming event with smart selection and severity filtering"""
        # PRIORITY 3 FIX (2025-10-27): Smart event selection
        if not self._should_buffer_event(event):
            self.stats["events_filtered"] += 1
            return  # Skip routine events

        # Add to buffer
        self.event_buffer.append(event)
        self.stats["events_processed"] += 1

        # PRIORITY 3: Track errors for adaptive intervals
        if event.get('severity', '').lower() in ['error', 'critical']:
            self.recent_errors += 1

        # Check if we should analyze
        if self._should_analyze():
            await self._analyze_batch()

    def _get_adaptive_interval(self) -> int:
        """PRIORITY 3: Calculate adaptive analysis interval based on system activity"""
        # Reset error counter every hour
        if time.time() - self.error_window_start > 3600:
            self.recent_errors = 0
            self.error_window_start = time.time()

        # Analyze frequently during issues
        if self.recent_errors > 5:
            return 60  # 1 minute during high error rate
        elif self.recent_errors > 0:
            return 300  # 5 minutes during moderate errors
        else:
            return 900  # 15 minutes during normal operation

    def _should_analyze(self) -> bool:
        """Determine if we should analyze now with minimum batch size and adaptive intervals"""
        time_elapsed = time.time() - self.last_analysis_time

        # PRIORITY 2 FIX: Require minimum 20 events AND time interval
        min_batch_size = max(self.batch_size, 20)

        # PRIORITY 3 FIX: Use adaptive interval based on system activity
        adaptive_interval = self._get_adaptive_interval()

        return (
            len(self.event_buffer) >= min_batch_size and
            time_elapsed >= adaptive_interval
        ) and not self.circuit_open
    
    async def _analyze_batch(self):
        """Analyze batch of events with AI and rate limiting"""
        if not self.event_buffer:
            return

        # PRIORITY 2 FIX (2025-10-27): Hourly rate limiting
        # Reset hourly counter if hour elapsed
        if time.time() - self.hour_start > 3600:
            self.hourly_calls = 0
            self.hour_start = time.time()
            logger.info("[AI_AUDITOR] Hourly rate limit counter reset")

        # Check rate limit
        if self.hourly_calls >= self.max_hourly_calls:
            logger.warning(f"[AI_AUDITOR] Hourly rate limit reached ({self.max_hourly_calls} calls/hour), skipping analysis")
            self.stats["analyses_skipped_rate_limit"] += 1

            # EXAI RECOMMENDATION: Buffer overflow protection during rate limiting
            if len(self.event_buffer) > 1000:
                logger.warning(f"[AI_AUDITOR] Buffer overflow during rate limit ({len(self.event_buffer)} events), dropping oldest events")
                self.event_buffer = self.event_buffer[-500:]  # Keep most recent 500

            # Keep events in buffer for next analysis window
            return

        # Get events to analyze
        events = self.event_buffer.copy()
        self.event_buffer.clear()
        self.last_analysis_time = time.time()

        logger.info(f"[AI_AUDITOR] Analyzing batch of {len(events)} events (hourly calls: {self.hourly_calls}/{self.max_hourly_calls})")

        try:
            # Build context
            context = self._build_context(events)

            # Get AI analysis
            observations = await self._get_ai_analysis(context, events)

            # PRIORITY 3 FIX: Track API cost
            cost = self._estimate_cost(context, observations)
            self.total_cost += cost
            logger.info(f"[AI_AUDITOR] API call cost: ${cost:.4f}, total: ${self.total_cost:.4f}")

            # Check daily cost limit
            if self.total_cost > self.daily_cost_limit:
                logger.warning(f"[AI_AUDITOR] Daily cost limit exceeded: ${self.total_cost:.2f} > ${self.daily_cost_limit:.2f}")

            # Store observations
            if observations:
                await self._store_observations(observations)
                self.stats["observations_created"] += len(observations)

            self.stats["analyses_performed"] += 1
            self.hourly_calls += 1  # PRIORITY 2: Increment rate limit counter
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

    def _estimate_cost(self, context: str, observations: List[Dict]) -> float:
        """PRIORITY 3: Estimate API call cost based on tokens used"""
        # Rough token estimation (1 token ≈ 4 characters)
        input_tokens = len(context) / 4
        output_tokens = sum(len(str(obs)) for obs in observations) / 4 if observations else 100

        # GLM-4.5-flash pricing (FREE tier, but track for monitoring)
        # Using nominal cost for tracking purposes
        if self.is_glm:
            # GLM-4.5-flash: FREE (but track as if $0.0001 per 1K tokens)
            cost_per_1k_input = 0.0001
            cost_per_1k_output = 0.0001
        else:
            # Kimi pricing (approximate)
            cost_per_1k_input = 0.001
            cost_per_1k_output = 0.002

        total_cost = (input_tokens / 1000 * cost_per_1k_input) + (output_tokens / 1000 * cost_per_1k_output)
        return total_cost
    
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

    def _parse_ai_response_safely(self, response_text: str) -> Optional[List[Dict]]:
        """
        Parse AI response with robust validation and fallback strategies.
        Returns None if parsing fails completely.
        """
        import re

        if not response_text or not response_text.strip():
            logger.warning(f"[AI_AUDITOR] Empty response received")
            return None

        # Strategy 1: Try direct JSON parse
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Extract from markdown code blocks
        if "```json" in response_text:
            try:
                content = response_text.split("```json")[1].split("```")[0].strip()
                return json.loads(content)
            except (IndexError, json.JSONDecodeError):
                pass

        if "```" in response_text:
            try:
                content = response_text.split("```")[1].split("```")[0].strip()
                return json.loads(content)
            except (IndexError, json.JSONDecodeError):
                pass

        # Strategy 3: Extract JSON array/object using regex
        try:
            # Try to find JSON array first
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            # Try to find JSON object
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                # If it's a single object, wrap in array
                return [parsed] if isinstance(parsed, dict) else parsed
        except json.JSONDecodeError:
            pass

        # All strategies failed - log for debugging
        logger.error(f"[AI_AUDITOR] All parsing strategies failed")
        logger.error(f"[AI_AUDITOR] Raw Response (first 1000 chars): {response_text[:1000]}...")
        return None

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
            # Both GLM and Kimi now use AsyncOpenAI
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

            # Parse JSON response with robust validation
            observations = self._parse_ai_response_safely(content)

            if observations is None:
                logger.warning(f"[AI_AUDITOR] Failed to parse response, returning empty list")
                return []

            # Add event IDs to each observation
            event_ids = [e.get("id", str(i)) for i, e in enumerate(events)]
            for obs in observations:
                obs["event_ids"] = event_ids

            return observations

        except json.JSONDecodeError as e:
            logger.error(f"[AI_AUDITOR] Failed to parse AI response as JSON: {e}")
            logger.error(f"[AI_AUDITOR] Raw Response (first 500 chars): {content[:500] if 'content' in locals() else 'N/A'}...")
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
        """Get auditor statistics with rate limiting and cost tracking"""
        return {
            **self.stats,
            "circuit_open": self.circuit_open,
            "buffer_size": len(self.event_buffer),
            "model": self.model,
            "batch_size": self.batch_size,
            "analysis_interval": self.analysis_interval,
            "hourly_calls": self.hourly_calls,  # PRIORITY 2: Rate limit tracking
            "max_hourly_calls": self.max_hourly_calls,
            "rate_limit_remaining": self.max_hourly_calls - self.hourly_calls,
            "recent_errors": self.recent_errors,  # PRIORITY 3: Adaptive intervals
            "adaptive_interval": self._get_adaptive_interval(),
            "total_cost": self.total_cost,  # PRIORITY 3: Cost tracking
            "daily_cost_limit": self.daily_cost_limit,
            "cost_remaining": max(0, self.daily_cost_limit - self.total_cost)
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

