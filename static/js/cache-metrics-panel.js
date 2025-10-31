/**
 * Cache Metrics Panel - Supabase Integration
 * Week 2-3 Monitoring Phase (2025-10-31)
 * 
 * Displays real-time cache performance metrics from Supabase monitoring schema.
 * Integrates with existing monitoring dashboard architecture.
 */

class CacheMetricsPanel {
    constructor(options = {}) {
        this.refreshInterval = options.refreshInterval || 30000; // 30 seconds default
        this.timeRange = options.timeRange || 24; // 24 hours default
        this.aggregation = options.aggregation || '1min'; // 1min aggregation default
        this.charts = {};
        this.refreshTimer = null;
        this.isInitialized = false;
        
        console.log('[CACHE_METRICS] Panel initialized', {
            refreshInterval: this.refreshInterval,
            timeRange: this.timeRange,
            aggregation: this.aggregation
        });
    }

    /**
     * Initialize the panel
     */
    async init() {
        if (this.isInitialized) {
            console.warn('[CACHE_METRICS] Panel already initialized');
            return;
        }

        try {
            // Initial data fetch
            await this.fetchAndRender();

            // Start periodic refresh
            this.startAutoRefresh();

            this.isInitialized = true;
            console.log('[CACHE_METRICS] Panel initialized successfully');
        } catch (error) {
            console.error('[CACHE_METRICS] Initialization failed:', error);
            this.renderError('Failed to initialize cache metrics panel');
        }
    }

    /**
     * Fetch cache metrics from backend API
     */
    async fetchData() {
        try {
            const params = new URLSearchParams({
                time_range: this.timeRange,
                aggregation: this.aggregation
            });

            const response = await fetch(`/api/cache-metrics?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            console.log('[CACHE_METRICS] Data fetched successfully', {
                records: data.metrics?.length || 0,
                summary: data.summary
            });

            return data;
        } catch (error) {
            console.error('[CACHE_METRICS] Fetch error:', error);
            throw error;
        }
    }

    /**
     * Fetch and render data
     */
    async fetchAndRender() {
        try {
            const data = await this.fetchData();
            this.render(data);
        } catch (error) {
            console.error('[CACHE_METRICS] Fetch and render failed:', error);
            this.renderError('Failed to load cache metrics');
        }
    }

    /**
     * Render cache metrics
     */
    render(data) {
        if (!data || !data.metrics) {
            this.renderNoData();
            return;
        }

        // Update summary statistics
        this.renderSummary(data.summary);

        // Update charts
        this.renderCharts(data.metrics);

        // Update last refresh timestamp
        this.updateLastRefresh();
    }

    /**
     * Render summary statistics
     */
    renderSummary(summary) {
        const container = document.getElementById('cacheMetricsSummary');
        if (!container) {
            console.warn('[CACHE_METRICS] Summary container not found');
            return;
        }

        const hitRate = summary.overall_hit_rate || 0;
        const hitRateClass = hitRate >= 80 ? 'success' : hitRate >= 50 ? 'warning' : 'error';

        container.innerHTML = `
            <div class="metric">
                <span class="metric-label">Total Operations</span>
                <span class="metric-value">${(summary.total_operations || 0).toLocaleString()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Cache Hits</span>
                <span class="metric-value success">${(summary.total_hits || 0).toLocaleString()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Cache Misses</span>
                <span class="metric-value error">${(summary.total_misses || 0).toLocaleString()}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Hit Rate</span>
                <span class="metric-value ${hitRateClass}">${hitRate.toFixed(2)}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Avg Response Time</span>
                <span class="metric-value">${(summary.avg_response_time_ms || 0).toFixed(2)} ms</span>
            </div>
            <div class="metric">
                <span class="metric-label">Time Range</span>
                <span class="metric-value">${summary.time_range_hours || 0}h</span>
            </div>
        `;
    }

    /**
     * Render charts
     */
    renderCharts(metrics) {
        if (!metrics || metrics.length === 0) {
            console.warn('[CACHE_METRICS] No metrics data to render charts');
            return;
        }

        // Render hit rate chart
        this.renderHitRateChart(metrics);

        // Render response time chart
        this.renderResponseTimeChart(metrics);

        // Render operations chart
        this.renderOperationsChart(metrics);
    }

    /**
     * Render hit rate chart
     */
    renderHitRateChart(metrics) {
        const canvas = document.getElementById('cacheHitRateChart');
        if (!canvas) {
            console.warn('[CACHE_METRICS] Hit rate chart canvas not found');
            return;
        }

        // Destroy existing chart
        if (this.charts.hitRate) {
            this.charts.hitRate.destroy();
        }

        const ctx = canvas.getContext('2d');
        const labels = metrics.map(m => new Date(m.minute_window || m.hour_window || m.timestamp));
        const hitRates = metrics.map(m => m.hit_rate || 0);

        this.charts.hitRate = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Hit Rate (%)',
                    data: hitRates,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: this.aggregation === '1min' ? 'minute' : 'hour'
                        },
                        ticks: { color: '#a0a0a0' },
                        grid: { color: '#2a2f4a' }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#a0a0a0' },
                        grid: { color: '#2a2f4a' }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#e0e0e0' }
                    }
                }
            }
        });
    }

    /**
     * Render response time chart
     */
    renderResponseTimeChart(metrics) {
        const canvas = document.getElementById('cacheResponseTimeChart');
        if (!canvas) {
            console.warn('[CACHE_METRICS] Response time chart canvas not found');
            return;
        }

        // Destroy existing chart
        if (this.charts.responseTime) {
            this.charts.responseTime.destroy();
        }

        const ctx = canvas.getContext('2d');
        const labels = metrics.map(m => new Date(m.minute_window || m.hour_window || m.timestamp));
        const avgTimes = metrics.map(m => m.avg_response_time_ms || 0);
        const p95Times = metrics.map(m => m.p95_response_time_ms || 0);

        this.charts.responseTime = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Avg Response Time (ms)',
                        data: avgTimes,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'P95 Response Time (ms)',
                        data: p95Times,
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        tension: 0.4,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: this.aggregation === '1min' ? 'minute' : 'hour'
                        },
                        ticks: { color: '#a0a0a0' },
                        grid: { color: '#2a2f4a' }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#a0a0a0' },
                        grid: { color: '#2a2f4a' }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#e0e0e0' }
                    }
                }
            }
        });
    }

    /**
     * Render operations chart
     */
    renderOperationsChart(metrics) {
        const canvas = document.getElementById('cacheOperationsChart');
        if (!canvas) {
            console.warn('[CACHE_METRICS] Operations chart canvas not found');
            return;
        }

        // Destroy existing chart
        if (this.charts.operations) {
            this.charts.operations.destroy();
        }

        const ctx = canvas.getContext('2d');
        const labels = metrics.map(m => new Date(m.minute_window || m.hour_window || m.timestamp));
        const hits = metrics.map(m => m.hits || 0);
        const misses = metrics.map(m => m.misses || 0);
        const sets = metrics.map(m => m.sets || 0);

        this.charts.operations = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Hits',
                        data: hits,
                        backgroundColor: 'rgba(16, 185, 129, 0.8)',
                        borderColor: '#10b981',
                        borderWidth: 1
                    },
                    {
                        label: 'Misses',
                        data: misses,
                        backgroundColor: 'rgba(239, 68, 68, 0.8)',
                        borderColor: '#ef4444',
                        borderWidth: 1
                    },
                    {
                        label: 'Sets',
                        data: sets,
                        backgroundColor: 'rgba(102, 126, 234, 0.8)',
                        borderColor: '#667eea',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: this.aggregation === '1min' ? 'minute' : 'hour'
                        },
                        stacked: true,
                        ticks: { color: '#a0a0a0' },
                        grid: { color: '#2a2f4a' }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        ticks: { color: '#a0a0a0' },
                        grid: { color: '#2a2f4a' }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#e0e0e0' }
                    }
                }
            }
        });
    }

    /**
     * Render no data message
     */
    renderNoData() {
        const container = document.getElementById('cacheMetricsSummary');
        if (container) {
            container.innerHTML = `
                <div class="no-data-message">
                    <p>No cache metrics data available</p>
                    <p class="hint">Cache operations will appear here once the system starts collecting metrics</p>
                </div>
            `;
        }
    }

    /**
     * Render error message
     */
    renderError(message) {
        const container = document.getElementById('cacheMetricsSummary');
        if (container) {
            container.innerHTML = `
                <div class="error-message">
                    <p>⚠️ ${message}</p>
                    <p class="hint">Check console for details</p>
                </div>
            `;
        }
    }

    /**
     * Update last refresh timestamp
     */
    updateLastRefresh() {
        const element = document.getElementById('cacheMetricsLastRefresh');
        if (element) {
            const now = new Date();
            element.textContent = `Last updated: ${now.toLocaleTimeString()}`;
        }
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }

        this.refreshTimer = setInterval(() => {
            this.fetchAndRender();
        }, this.refreshInterval);

        console.log(`[CACHE_METRICS] Auto-refresh started (${this.refreshInterval}ms)`);
    }

    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
            console.log('[CACHE_METRICS] Auto-refresh stopped');
        }
    }

    /**
     * Destroy panel and cleanup
     */
    destroy() {
        this.stopAutoRefresh();
        
        // Destroy all charts
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        
        this.charts = {};
        this.isInitialized = false;
        
        console.log('[CACHE_METRICS] Panel destroyed');
    }
}

// Export for use in dashboard
window.CacheMetricsPanel = CacheMetricsPanel;

