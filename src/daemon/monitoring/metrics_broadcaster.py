"""
Metrics Broadcaster Module

Handles metrics collection, change detection, and broadcasting to dashboard clients.
Extracted from monitoring_endpoint.py to improve maintainability.

Components:
- broadcast_monitoring_event: Main event broadcasting function
- _broadcast_session_metrics: Session metrics broadcasting
- _should_broadcast_metrics_change: Change detection logic
- prepare_stats_for_dashboard: Stats preparation utilities
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from utils.timezone_helper import log_timestamp

logger = logging.getLogger(__name__)

# Track last broadcast metrics for change detection
_last_broadcast_metrics: Optional[dict] = None


async def _broadcast_session_metrics(metrics: dict, _dashboard_clients) -> None:
    """
    Broadcast session metrics to all connected dashboard clients.

    Args:
        metrics: Session metrics dictionary from SessionTracker.get_metrics()
        _dashboard_clients: Set of connected WebSocket clients
    """
    if not _dashboard_clients:
        return

    session_metrics_update = {
        "type": "session_metrics",
        "data": metrics,
        "timestamp": log_timestamp(),
    }

    # Log metrics broadcast for debugging
    logger.debug(f"Broadcasting session metrics: active_sessions={metrics.get('active_sessions')}, "
                f"conversation_length={metrics.get('conversation_length')}, "
                f"current_model={metrics.get('current_model')}")

    for client in _dashboard_clients:
        try:
            await client.send_str(json.dumps(session_metrics_update))
        except Exception as e:
            logger.debug(f"Failed to send session metrics to client: {e}")


def _should_broadcast_metrics_change(current: dict, last: Optional[dict]) -> bool:
    """
    Determine if session metrics have changed enough to warrant broadcasting.

    Args:
        current: Current session metrics
        last: Last broadcast session metrics (None if first broadcast)

    Returns:
        True if metrics should be broadcast
    """
    if last is None:
        return True  # Always broadcast first time

    # Check for meaningful changes
    if current.get("conversation_length") != last.get("conversation_length"):
        return True
    if current.get("current_model") != last.get("current_model"):
        return True
    if current.get("active_sessions") != last.get("active_sessions"):
        return True

    # Check for significant token usage change (>10%)
    current_tokens = current.get("context_tokens_used", 0)
    last_tokens = last.get("context_tokens_used", 0)
    if last_tokens > 0:
        change_pct = abs(current_tokens - last_tokens) / last_tokens
        if change_pct > 0.1:  # 10% change
            return True

    return False


def prepare_stats_for_dashboard(stats_dict):
    """
    Add computed fields for dashboard display.

    Args:
        stats_dict: Statistics dictionary from ConnectionMonitor

    Returns:
        Enhanced statistics dictionary with computed fields
    """
    if stats_dict:
        # PHASE 3 (2025-10-23): Add total_bytes as sum of sent and received
        stats_dict['total_bytes'] = (
            (stats_dict.get('total_sent_bytes') or 0) +
            (stats_dict.get('total_received_bytes') or 0)
        )
    return stats_dict


async def broadcast_monitoring_event(event_data: dict, _dashboard_clients, _session_tracker) -> None:
    """
    Broadcast monitoring event to all connected dashboard clients.

    Args:
        event_data: Event data to broadcast
        _dashboard_clients: Set of connected WebSocket clients
        _session_tracker: Session tracker instance
    """
    global _last_broadcast_metrics

    # CRITICAL FIX (2025-10-23): Change to DEBUG level to reduce log spam
    # BUG: These INFO logs were creating excessive noise in production logs
    logger.debug(f"[BROADCAST_DEBUG] Function called with event_data keys: {list(event_data.keys())}")
    logger.debug(f"[BROADCAST_DEBUG] Dashboard clients connected: {len(_dashboard_clients)}")

    if not _dashboard_clients:
        logger.debug(f"[BROADCAST_DEBUG] No dashboard clients, skipping broadcast")
        return

    # PHASE 3.5 (2025-10-23): Update session tracker from event
    _session_tracker.update_from_event(event_data)

    # Add timestamp
    event_data["broadcast_time"] = log_timestamp()

    # Broadcast to all clients
    disconnected = set()
    for client in _dashboard_clients:
        try:
            await client.send_str(json.dumps(event_data))
        except Exception as e:
            logger.debug(f"Failed to send to dashboard client: {e}")
            disconnected.add(client)

    # Remove disconnected clients
    _dashboard_clients.difference_update(disconnected)

    # PHASE 4 (2025-10-23): Hybrid session metrics broadcasting (EXAI consultation: 6f02b31b-865d-4077-898f-dea9445b3c4a)
    # Development mode: send immediately when continuation_id detected
    # Production mode: send only on meaningful changes
    if len(_dashboard_clients) > 0:
        import os
        dev_mode = os.getenv('EXAI_DEV_MODE', 'true').lower() == 'true'  # Default to dev mode

        current_metrics = _session_tracker.get_metrics()

        # Check if this event has continuation_id
        metadata = event_data.get("metadata", {})
        has_continuation_id = bool(metadata.get("continuation_id") or metadata.get("conversation_id"))

        should_broadcast = False
        if dev_mode and has_continuation_id:
            # Development: immediate updates when continuation_id present
            should_broadcast = True
            logger.debug(f"[DEV MODE] Broadcasting session metrics immediately (continuation_id detected)")
        elif not dev_mode and _should_broadcast_metrics_change(current_metrics, _last_broadcast_metrics):
            # Production: only on meaningful changes
            should_broadcast = True
            logger.debug(f"[PROD MODE] Broadcasting session metrics (change detected)")

        if should_broadcast:
            await _broadcast_session_metrics(current_metrics, _dashboard_clients)
            _last_broadcast_metrics = current_metrics.copy()
