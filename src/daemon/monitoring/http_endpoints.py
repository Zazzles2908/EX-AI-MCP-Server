"""
HTTP Endpoints Module

Handles all HTTP API endpoints for the monitoring system.
Extracted from monitoring_endpoint.py to improve maintainability.

Components:
- Validation metrics endpoints
- Adapter metrics endpoints
- Flag status endpoints
- Metrics flush endpoints
- Auditor observation endpoints
- Cache metrics endpoints
- Timeout estimate endpoints
- Dashboard serving
"""

import asyncio
import json
import logging
from typing import Optional
from aiohttp import web
from pathlib import Path
from datetime import datetime, timedelta

from utils.timezone_helper import log_timestamp
from src.daemon.error_handling import log_error, ErrorCode
from src.monitoring.flags import get_flag_manager
from src.storage.supabase_client import get_storage_manager

logger = logging.getLogger(__name__)


async def serve_dashboard(request: web.Request) -> web.Response:
    """
    Serve the monitoring dashboard HTML file.

    Args:
        request: aiohttp request object

    Returns:
        HTML response
    """
    dashboard_path = Path(__file__).parent.parent.parent / "static" / "monitoring_dashboard.html"

    if not dashboard_path.exists():
        log_error(ErrorCode.INTERNAL_ERROR, f"Dashboard not found at {dashboard_path}", exc_info=True)
        return web.Response(text="Dashboard not found", status=404)

    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return web.Response(body=content, content_type='text/html')
    except Exception as e:
        log_error(ErrorCode.INTERNAL_ERROR, f"Error serving dashboard: {e}", exc_info=True)
        return web.Response(text=f"Error loading dashboard: {e}", status=500)


# PHASE 2.4.3: Dashboard Endpoints for Feature Flags and Metrics (2025-11-01)

async def get_validation_metrics(request: web.Request) -> web.Response:
    """
    Get current validation metrics.

    Returns validation metrics from the monitoring system.

    Args:
        request: aiohttp request object

    Returns:
        JSON response with validation metrics
    """
    try:
        # Get metrics from broadcaster
        from src.monitoring.broadcaster import get_broadcaster
        _broadcaster = get_broadcaster()
        
        metrics = {}
        if hasattr(_broadcaster, 'get_metrics'):
            metrics = await _broadcaster.get_metrics()

        return web.json_response({
            "status": "ok",
            "metrics": metrics,
            "timestamp": log_timestamp(),
        })
    except Exception as e:
        log_error(ErrorCode.INTERNAL_ERROR, f"Error getting validation metrics: {e}", exc_info=True)
        return web.json_response({
            "status": "error",
            "error": str(e),
            "timestamp": log_timestamp(),
        }, status=500)


async def get_adapter_metrics(request: web.Request) -> web.Response:
    """
    Get adapter performance metrics.

    Returns metrics about the monitoring adapter (WebSocket/Realtime).

    Args:
        request: aiohttp request object

    Returns:
        JSON response with adapter metrics
    """
    try:
        # Get adapter metrics from broadcaster
        from src.monitoring.broadcaster import get_broadcaster
        _broadcaster = get_broadcaster()
        
        adapter_metrics = {}
        if hasattr(_broadcaster, '_adapter') and _broadcaster._adapter:
            adapter_metrics = _broadcaster._adapter.get_metrics() if hasattr(_broadcaster._adapter, 'get_metrics') else {}

        return web.json_response({
            "status": "ok",
            "adapter_type": _broadcaster.adapter_type if hasattr(_broadcaster, 'adapter_type') else "unknown",
            "metrics": adapter_metrics,
            "timestamp": log_timestamp(),
        })
    except Exception as e:
        log_error(ErrorCode.INTERNAL_ERROR, f"Error getting adapter metrics: {e}", exc_info=True)
        return web.json_response({
            "status": "error",
            "error": str(e),
            "timestamp": log_timestamp(),
        }, status=500)


async def get_flags_status(request: web.Request) -> web.Response:
    """
    Get current feature flags configuration.

    Returns all feature flags and their current values.

    Args:
        request: aiohttp request object

    Returns:
        JSON response with flag configuration
    """
    try:
        flag_manager = get_flag_manager()
        flags = flag_manager.get_all()

        return web.json_response({
            "status": "ok",
            "flags": flags,
            "timestamp": log_timestamp(),
        })
    except Exception as e:
        log_error(ErrorCode.INTERNAL_ERROR, f"Error getting flags status: {e}", exc_info=True)
        return web.json_response({
            "status": "error",
            "error": str(e),
            "timestamp": log_timestamp(),
        }, status=500)


async def post_metrics_flush(request: web.Request) -> web.Response:
    """
    Manually trigger metrics flush to database.

    Flushes in-memory metrics to Supabase database.

    Args:
        request: aiohttp request object

    Returns:
        JSON response with flush result
    """
    try:
        # Get metrics from broadcaster and flush
        from src.monitoring.broadcaster import get_broadcaster
        _broadcaster = get_broadcaster()
        
        if hasattr(_broadcaster, 'flush_metrics'):
            result = await _broadcaster.flush_metrics()
            return web.json_response({
                "status": "ok",
                "result": result,
                "timestamp": log_timestamp(),
            })
        else:
            return web.json_response({
                "status": "error",
                "error": "Metrics flush not available",
                "timestamp": log_timestamp(),
            }, status=501)
    except Exception as e:
        log_error(ErrorCode.INTERNAL_ERROR, f"Error flushing metrics: {e}", exc_info=True)
        return web.json_response({
            "status": "error",
            "error": str(e),
            "timestamp": log_timestamp(),
        }, status=500)
async def get_auditor_observations(request: web.Request) -> web.Response:
    """
    Get recent auditor observations from Supabase.

    Query params:
        limit: Number of observations to return (default: 50)
        severity: Filter by severity (critical, warning, info)
        category: Filter by category
        acknowledged: Filter by acknowledged status (true/false)

    Args:
        request: aiohttp request object

    Returns:
        JSON response with observations
    """
    try:
        from src.storage.supabase_client import get_storage_manager

        # Get query parameters
        limit = int(request.query.get('limit', 50))
        severity = request.query.get('severity')
        category = request.query.get('category')
        acknowledged = request.query.get('acknowledged')

        # FIXED (2025-10-24): Use singleton to avoid re-initializing client on every request
        supabase = get_storage_manager()
        client = supabase.get_client()

        # Build query
        query = client.table("auditor_observations").select("*")

        # Apply filters
        if severity:
            query = query.eq("severity", severity)
        if category:
            query = query.eq("category", category)
        if acknowledged is not None:
            query = query.eq("acknowledged", acknowledged.lower() == 'true')

        # Order by timestamp descending and limit
        query = query.order("timestamp", desc=True).limit(limit)

        # Execute query (Supabase client is sync, so run in thread pool)
        result = await asyncio.to_thread(lambda: query.execute())

        return web.json_response({
            "observations": result.data,
            "count": len(result.data),
            "timestamp": log_timestamp()
        })

    except Exception as e:
        log_error(ErrorCode.INTERNAL_ERROR, f"Error fetching auditor observations: {e}", exc_info=True)
        return web.json_response({
            "error": str(e),
            "observations": [],
            "count": 0
        }, status=500)
async def acknowledge_observation(request: web.Request) -> web.Response:
    """
    Acknowledge an auditor observation.

    Args:
        request: aiohttp request object with observation_id in path

    Returns:
        JSON response
    """
    try:
        from src.storage.supabase_client import get_storage_manager
        import asyncio

        observation_id = request.match_info['observation_id']

        # FIXED (2025-10-24): Use singleton to avoid re-initializing client on every request
        supabase = get_storage_manager()
        client = supabase.get_client()

        # Update observation (run in thread pool since Supabase client is sync)
        await asyncio.to_thread(
            lambda: client.table("auditor_observations").update({
                "acknowledged": True,
                "acknowledged_at": log_timestamp(),
                "acknowledged_by": "dashboard_user"  # TODO: Get actual user from auth
            }).eq("id", observation_id).execute()
        )

        return web.json_response({
            "success": True,
            "observation_id": observation_id,
            "timestamp": log_timestamp()
        })

    except Exception as e:
        log_error(ErrorCode.INTERNAL_ERROR, f"Error acknowledging observation: {e}", exc_info=True)
        return web.json_response({
            "error": str(e),
            "success": False
async def get_cache_metrics(request: web.Request) -> web.Response:
    """
    Get cache metrics from Supabase monitoring schema.

    Week 2-3 Monitoring Phase (2025-10-31): Cache Metrics Integration

    Query params:
        time_range: Time range in hours (default: 24)
        implementation_type: Filter by implementation type (legacy, new)
        aggregation: Aggregation level (raw, 1min, 1hour) (default: 1min)

    Args:
        request: aiohttp request object

    Returns:
        JSON response with cache metrics
    """
    try:
        from src.storage.supabase_client import get_storage_manager
        from datetime import datetime, timedelta

        # Get query parameters
        time_range_hours = int(request.query.get('time_range', 24))
        implementation_type = request.query.get('implementation_type')
        aggregation = request.query.get('aggregation', '1min')

        # Calculate time window
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=time_range_hours)

        # Get Supabase client
        supabase = get_storage_manager()
        client = supabase.get_client()

        # Determine table based on aggregation level
        table_map = {
            'raw': 'cache_metrics',
            '1min': 'cache_metrics_1min',
            '1hour': 'cache_metrics_1hour'
        }
        table_name = table_map.get(aggregation, 'cache_metrics_1min')

        # Build query for monitoring schema
        query = client.schema('monitoring').table(table_name).select("*")

        # Apply time filter
        if aggregation == 'raw':
            query = query.gte("timestamp", start_time.isoformat()).lte("timestamp", end_time.isoformat())
        else:
            # For aggregated tables, use minute_window or hour_window
            time_column = 'minute_window' if aggregation == '1min' else 'hour_window'
            query = query.gte(time_column, start_time.isoformat()).lte(time_column, end_time.isoformat())

        # Apply implementation type filter
        if implementation_type:
            query = query.eq("implementation_type", implementation_type)

        # Order by time descending and limit to 1000 records
        if aggregation == 'raw':
            query = query.order("timestamp", desc=True).limit(1000)
        else:
            time_column = 'minute_window' if aggregation == '1min' else 'hour_window'
            query = query.order(time_column, desc=True).limit(1000)

        # Execute query (run in thread pool since Supabase client is sync)
        result = await asyncio.to_thread(lambda: query.execute())

        # Calculate summary statistics
        metrics = result.data
        summary = {
            'total_records': len(metrics),
            'time_range_hours': time_range_hours,
            'aggregation': aggregation,
            'implementation_type': implementation_type or 'all'
        }

        if metrics and aggregation != 'raw':
            # Calculate aggregate statistics from the data
            total_ops = sum(m.get('total_operations', 0) for m in metrics)
            total_hits = sum(m.get('hits', 0) for m in metrics)
            total_misses = sum(m.get('misses', 0) for m in metrics)

            summary.update({
                'total_operations': total_ops,
                'total_hits': total_hits,
                'total_misses': total_misses,
                'overall_hit_rate': round((total_hits / (total_hits + total_misses) * 100), 2) if (total_hits + total_misses) > 0 else 0,
                'avg_response_time_ms': round(sum(m.get('avg_response_time_ms', 0) for m in metrics) / len(metrics), 2) if metrics else 0
            })

        return web.json_response({
            "metrics": metrics,
            "summary": summary,
            "timestamp": log_timestamp()
        })

    except Exception as e:
        log_error(ErrorCode.INTERNAL_ERROR, f"Error fetching cache metrics: {e}", exc_info=True)
        import traceback
        log_error(ErrorCode.INTERNAL_ERROR, f"Traceback: {traceback.format_exc()}", exc_info=True)
        return web.json_response({
            "error": str(e),
            "metrics": [],
            "summary": {},
            "timestamp": log_timestamp()
        }, status=500)
async def get_current_metrics(request: web.Request) -> web.Response:
    """
    Get current system metrics for testing baseline comparison.

    Phase 0.4 (2025-10-24): Testing Dashboard Support
    """
    try:
        # Calculate current metrics from recent events
        # For now, return mock data - will be replaced with actual metrics
        metrics = {
            "latency_p95": 150.0,  # ms
            "memory_mb": 85.0,     # MB
            "success_rate": 98.5,  # %
            "timestamp": log_timestamp()
        }

        return web.json_response(metrics)

    except Exception as e:
        log_error(ErrorCode.INTERNAL_ERROR, f"Error fetching current metrics: {e}", exc_info=True)
        return web.json_response({
            "error": str(e),
            "latency_p95": 0,
            "memory_mb": 0,
            "success_rate": 0
        }, status=500)
async def handle_timeout_estimate(request: web.Request) -> web.Response:
    """
    Estimate timeout for a model request using adaptive timeout engine.

    DAY 1 IMPLEMENTATION (2025-11-03): Adaptive Timeout Architecture
    K2 Decision: Call Moonshot /estimate API only when confidence < 0.5

    POST /api/v1/timeout/estimate
    Body: {
        "model": "kimi-k2",
        "messages": [...],  # Optional - for Moonshot estimate API
        "request_type": "text"  # text, file, image, audio
    }
    Response: {
        "timeout": 180,
        "confidence": 0.85,
        "source": "adaptive",  # adaptive, static, emergency, estimate
        "metadata": {
            "samples_used": 50,
            "estimated_tokens": 1500,  # If estimate API was called
            "provider": "kimi"
        }
    }
    """
    try:
        # Parse request body
        try:
            body = await request.json()
        except Exception as e:
            return web.json_response({
                "error": "Invalid JSON body",
                "details": str(e)
            }, status=400)

        model = body.get("model")
        messages = body.get("messages", [])
        request_type = body.get("request_type", "text")

        if not model:
            return web.json_response({
                "error": "Missing required field: model"
            }, status=400)

        # Import adaptive timeout engine
        from src.core.adaptive_timeout import get_engine, is_adaptive_timeout_enabled

        # Check if adaptive timeout is enabled
        if not is_adaptive_timeout_enabled():
            # Fallback to static timeout
            base_timeout = 180  # Default 3 minutes
            return web.json_response({
                "timeout": base_timeout,
                "confidence": 0.0,
                "source": "static",
                "metadata": {
                    "reason": "adaptive_timeout_disabled"
                }
            })

        # Get adaptive timeout engine
        engine = get_engine()

        # Get provider-specific config
        provider_config = engine.get_provider_specific_config(model)
        base_timeout = provider_config["base_timeout"]

        # Get adaptive timeout with metadata
        timeout, metadata = engine.get_adaptive_timeout_safe(model, base_timeout)

        # K2 Decision: Call Moonshot estimate API only when confidence < 0.5
        confidence = metadata.get("confidence", 0.0)

        if confidence < 0.5 and messages and ("kimi" in model.lower() or "k2" in model.lower()):
            # Low confidence - use Moonshot estimate API for better prediction
            try:
                # Import Moonshot client
                import os
                from openai import AsyncOpenAI

                api_key = os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")
                if api_key:
                    client = AsyncOpenAI(
                        api_key=api_key,
                        base_url="https://api.moonshot.ai/v1"
                    )

                    # Call estimate API (with timeout)
                    import asyncio
                    estimate_response = await asyncio.wait_for(
                        client.chat.completions.create(
                            model=model,
                            messages=messages,
                            max_tokens=1,  # Minimal tokens for estimate
                            stream=False
                        ),
                        timeout=5.0  # 5 second timeout for estimate call
                    )

                    # Extract token estimate from usage
                    if estimate_response.usage:
                        estimated_tokens = estimate_response.usage.total_tokens

                        # Calculate timeout based on tokens
                        # Assume ~10 tokens/second for K2 (conservative estimate)
                        tokens_per_second = 10
                        estimated_duration = estimated_tokens / tokens_per_second

                        # Add 50% buffer for safety
                        timeout = int(estimated_duration * 1.5)

                        # Update metadata
                        metadata["source"] = "estimate"
                        metadata["estimated_tokens"] = estimated_tokens
                        metadata["tokens_per_second"] = tokens_per_second

                        logger.info(f"[ESTIMATE_API] Used Moonshot estimate for {model}: {estimated_tokens} tokens → {timeout}s timeout")

            except asyncio.TimeoutError:
                logger.warning(f"[ESTIMATE_API] Moonshot estimate API timed out for {model}")
            except Exception as e:
                logger.warning(f"[ESTIMATE_API] Failed to call Moonshot estimate API: {e}")

        # Detect provider for metadata
        provider = engine.detect_provider(model)
        metadata["provider"] = provider

        return web.json_response({
            "timeout": timeout,
            "confidence": confidence,
            "source": metadata.get("source", "adaptive"),
            "metadata": metadata
        })

    except Exception as e:
        logger.error(f"[ESTIMATE_API] Error in timeout estimate handler: {e}", exc_info=True)
        return web.json_response({
            "error": "Internal server error",
            "details": str(e)
        }, status=500)
