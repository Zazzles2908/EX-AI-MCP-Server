"""
Production-Level Metrics System with Sampling and Async Buffering.

This module provides a high-performance metrics collection system designed to
achieve <5% CPU overhead through:
- Sampling-based collection (1-5% configurable rate)
- Ring buffer with async flushing
- Adaptive sampling based on buffer pressure
- Critical event bypass
- Graceful degradation under load

Created: 2025-10-28
Phase: Emergency Metrics Redesign
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
Target: <5% CPU overhead, <100KB memory per 10K operations
"""

import os
import random
import threading
import time
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Deque, List
from enum import IntEnum

logger = logging.getLogger(__name__)


class MetricType(IntEnum):
    """Metric types using integers for memory efficiency."""
    CONNECTION = 1
    DISCONNECTION = 2
    MESSAGE_SENT = 3
    MESSAGE_QUEUED = 4
    MESSAGE_FAILED = 5
    RETRY_ATTEMPT = 6
    RETRY_SUCCESS = 7
    RETRY_FAILURE = 8
    CIRCUIT_BREAKER_OPEN = 9
    CIRCUIT_BREAKER_CLOSE = 10


@dataclass(slots=True)
class CompactMetric:
    """
    Lightweight metric object using slots for memory efficiency.
    
    Slots eliminate __dict__ overhead, reducing memory by ~40%.
    """
    timestamp: float
    metric_type: int  # MetricType enum value
    value: float
    client_id: str = ""
    
    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()


@dataclass
class MetricsConfig:
    """Configuration for production metrics system."""
    
    # Sampling configuration
    sample_rate: float = field(default_factory=lambda: float(os.getenv('METRICS_SAMPLE_RATE', '0.03')))
    max_sample_rate: float = field(default_factory=lambda: float(os.getenv('METRICS_MAX_SAMPLE_RATE', '0.15')))
    min_sample_rate: float = field(default_factory=lambda: float(os.getenv('METRICS_MIN_SAMPLE_RATE', '0.01')))
    
    # Buffer configuration
    buffer_size: int = field(default_factory=lambda: int(os.getenv('METRICS_BUFFER_SIZE', '2000')))
    flush_interval: float = field(default_factory=lambda: float(os.getenv('METRICS_FLUSH_INTERVAL', '2.0')))
    
    # Feature flags
    enable_adaptive_sampling: bool = field(default_factory=lambda: os.getenv('METRICS_ADAPTIVE_SAMPLING', 'true').lower() == 'true')
    enable_meta_metrics: bool = field(default_factory=lambda: os.getenv('METRICS_ENABLE_META', 'true').lower() == 'true')
    
    # Degradation thresholds
    buffer_high_watermark: float = 0.8  # 80% full
    buffer_critical_watermark: float = 0.95  # 95% full


class AdaptiveSampler:
    """
    Adaptive sampling that adjusts rate based on buffer pressure.
    
    EXAI Recommendation: Adaptive sampling provides better performance
    under varying load conditions.
    """
    
    def __init__(self, config: MetricsConfig):
        self.config = config
        self.current_rate = config.sample_rate
        self.random = random.Random()
        self._last_adjustment = time.time()
        self._adjustment_interval = 5.0  # Adjust every 5 seconds
    
    def should_sample(self, is_critical: bool = False) -> bool:
        """
        Determine if this metric should be sampled.
        
        Args:
            is_critical: If True, always sample (bypass sampling)
        
        Returns:
            True if metric should be collected
        """
        if is_critical:
            return True
        
        return self.random.random() < self.current_rate
    
    def adjust_sampling_rate(self, buffer_fill_ratio: float):
        """
        Adjust sampling rate based on buffer pressure.
        
        Args:
            buffer_fill_ratio: Current buffer fill ratio (0.0 to 1.0)
        """
        now = time.time()
        if now - self._last_adjustment < self._adjustment_interval:
            return
        
        self._last_adjustment = now
        
        if buffer_fill_ratio > self.config.buffer_high_watermark:
            # Buffer filling up - reduce sampling
            new_rate = max(self.current_rate * 0.7, self.config.min_sample_rate)
            if new_rate != self.current_rate:
                logger.warning(f"Reducing sampling rate: {self.current_rate:.3f} -> {new_rate:.3f} (buffer: {buffer_fill_ratio:.1%})")
                self.current_rate = new_rate
        
        elif buffer_fill_ratio < 0.3:
            # Buffer has capacity - increase sampling
            new_rate = min(self.current_rate * 1.2, self.config.max_sample_rate)
            if new_rate != self.current_rate:
                logger.info(f"Increasing sampling rate: {self.current_rate:.3f} -> {new_rate:.3f} (buffer: {buffer_fill_ratio:.1%})")
                self.current_rate = new_rate


class MetricsRingBuffer:
    """
    Thread-safe ring buffer with automatic overflow handling.
    
    EXAI Recommendation: Ring buffers provide O(1) operations and
    fixed memory footprint, ideal for high-throughput metrics.
    """
    
    def __init__(self, capacity: int, flush_interval: float, flush_callback):
        self.buffer: Deque[CompactMetric] = deque(maxlen=capacity)
        self.capacity = capacity
        self.flush_interval = flush_interval
        self.flush_callback = flush_callback
        
        self.lock = threading.Lock()
        self._flush_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Meta-metrics
        self.metrics_added = 0
        self.metrics_dropped = 0
        self.flush_count = 0
        self.flush_duration_sum = 0.0
    
    def add_metric(self, metric: CompactMetric):
        """
        Add metric to buffer (thread-safe).
        
        If buffer is full, oldest metric is automatically dropped.
        """
        with self.lock:
            # Check if we're about to drop a metric
            if len(self.buffer) >= self.capacity:
                self.metrics_dropped += 1
            
            self.buffer.append(metric)
            self.metrics_added += 1
    
    def get_fill_ratio(self) -> float:
        """Get current buffer fill ratio (0.0 to 1.0)."""
        with self.lock:
            return len(self.buffer) / self.capacity if self.capacity > 0 else 0.0
    
    def start_flushing(self):
        """Start background flush thread."""
        if self._flush_thread is not None:
            logger.warning("Flush thread already running")
            return
        
        self._stop_event.clear()
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()
        logger.info(f"Started metrics flush thread (interval: {self.flush_interval}s)")
    
    def stop_flushing(self):
        """Stop background flush thread."""
        if self._flush_thread is None:
            return
        
        self._stop_event.set()
        self._flush_thread.join(timeout=5.0)
        self._flush_thread = None
        
        # Final flush
        self._flush_buffer()
        logger.info("Stopped metrics flush thread")
    
    def _flush_loop(self):
        """Background thread that periodically flushes buffer."""
        while not self._stop_event.is_set():
            time.sleep(self.flush_interval)
            self._flush_buffer()
    
    def _flush_buffer(self):
        """Flush buffer contents to callback."""
        start_time = time.perf_counter()
        
        # Get all metrics from buffer
        with self.lock:
            if not self.buffer:
                return
            
            metrics_to_flush = list(self.buffer)
            self.buffer.clear()
        
        # Call flush callback (outside lock)
        try:
            self.flush_callback(metrics_to_flush)
            self.flush_count += 1
            self.flush_duration_sum += (time.perf_counter() - start_time)
        except Exception as e:
            logger.error(f"Error flushing metrics: {e}")
    
    def get_meta_metrics(self) -> Dict[str, Any]:
        """Get meta-metrics about the buffer."""
        with self.lock:
            return {
                'buffer_size': len(self.buffer),
                'buffer_capacity': self.capacity,
                'buffer_fill_ratio': self.get_fill_ratio(),
                'metrics_added': self.metrics_added,
                'metrics_dropped': self.metrics_dropped,
                'drop_rate': self.metrics_dropped / max(1, self.metrics_added),
                'flush_count': self.flush_count,
                'avg_flush_duration_ms': (self.flush_duration_sum / max(1, self.flush_count)) * 1000
            }


class ProductionMetrics:
    """
    Production-level metrics system with sampling and async buffering.
    
    Designed to achieve <5% CPU overhead through:
    - Sampling at collection point (3% default rate)
    - Ring buffer with periodic flushing (2s interval)
    - Adaptive sampling based on buffer pressure
    - Critical event bypass
    
    EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
    """
    
    def __init__(self, config: Optional[MetricsConfig] = None):
        self.config = config or MetricsConfig()
        self.sampler = AdaptiveSampler(self.config)
        self.buffer = MetricsRingBuffer(
            capacity=self.config.buffer_size,
            flush_interval=self.config.flush_interval,
            flush_callback=self._process_metrics_batch
        )
        
        # Aggregated metrics (updated during flush)
        self.aggregated = {
            'connections': 0,
            'disconnections': 0,
            'messages_sent': 0,
            'messages_queued': 0,
            'messages_failed': 0,
            'retry_attempts': 0,
            'retry_successes': 0,
            'retry_failures': 0,
            'circuit_breaker_opens': 0,
            'circuit_breaker_closes': 0
        }
        
        self.start_time = time.time()
        self._started = False
    
    def start(self):
        """Start the metrics system."""
        if self._started:
            logger.warning("Metrics system already started")
            return
        
        self.buffer.start_flushing()
        self._started = True
        logger.info(f"Production metrics started (sample_rate: {self.config.sample_rate:.1%})")
    
    def stop(self):
        """Stop the metrics system and flush remaining metrics."""
        if not self._started:
            return
        
        self.buffer.stop_flushing()
        self._started = False
        logger.info("Production metrics stopped")
    
    def record_metric(self, metric_type: MetricType, value: float = 1.0, 
                     client_id: str = "", is_critical: bool = False):
        """
        Record a metric with sampling.
        
        Args:
            metric_type: Type of metric (MetricType enum)
            value: Metric value (default: 1.0 for counters)
            client_id: Optional client identifier
            is_critical: If True, bypass sampling
        """
        # Sampling decision
        if not self.sampler.should_sample(is_critical):
            return
        
        # Create compact metric
        metric = CompactMetric(
            timestamp=time.time(),
            metric_type=metric_type,
            value=value,
            client_id=client_id
        )
        
        # Add to buffer
        self.buffer.add_metric(metric)
        
        # Adaptive sampling adjustment
        if self.config.enable_adaptive_sampling:
            fill_ratio = self.buffer.get_fill_ratio()
            self.sampler.adjust_sampling_rate(fill_ratio)
    
    def _process_metrics_batch(self, metrics: List[CompactMetric]):
        """
        Process a batch of metrics during flush.
        
        This is where we aggregate sampled metrics back to full counts.
        """
        # Aggregate metrics with sampling correction
        sample_multiplier = 1.0 / max(0.001, self.sampler.current_rate)
        
        for metric in metrics:
            corrected_value = metric.value * sample_multiplier
            
            if metric.metric_type == MetricType.CONNECTION:
                self.aggregated['connections'] += corrected_value
            elif metric.metric_type == MetricType.DISCONNECTION:
                self.aggregated['disconnections'] += corrected_value
            elif metric.metric_type == MetricType.MESSAGE_SENT:
                self.aggregated['messages_sent'] += corrected_value
            elif metric.metric_type == MetricType.MESSAGE_QUEUED:
                self.aggregated['messages_queued'] += corrected_value
            elif metric.metric_type == MetricType.MESSAGE_FAILED:
                self.aggregated['messages_failed'] += corrected_value
            elif metric.metric_type == MetricType.RETRY_ATTEMPT:
                self.aggregated['retry_attempts'] += corrected_value
            elif metric.metric_type == MetricType.RETRY_SUCCESS:
                self.aggregated['retry_successes'] += corrected_value
            elif metric.metric_type == MetricType.RETRY_FAILURE:
                self.aggregated['retry_failures'] += corrected_value
            elif metric.metric_type == MetricType.CIRCUIT_BREAKER_OPEN:
                self.aggregated['circuit_breaker_opens'] += corrected_value
            elif metric.metric_type == MetricType.CIRCUIT_BREAKER_CLOSE:
                self.aggregated['circuit_breaker_closes'] += corrected_value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current aggregated metrics."""
        metrics = self.aggregated.copy()
        metrics['uptime_seconds'] = time.time() - self.start_time
        
        if self.config.enable_meta_metrics:
            metrics['meta'] = self.buffer.get_meta_metrics()
            metrics['meta']['current_sample_rate'] = self.sampler.current_rate
        
        return metrics

