/**
 * PHASE 2 REFACTORING (2025-10-23): Chart Management Module
 * 
 * Manages all Chart.js instances for the monitoring dashboard.
 * Provides abstraction layer for chart creation, updates, and lifecycle management.
 * 
 * Features:
 * - Chart initialization with common configuration
 * - Buffered updates for performance
 * - Automatic data point limiting
 * - Throttled update loop
 * - Service-specific color coding
 */

class ChartManager {
    constructor(serviceColors) {
        this.charts = {};
        this.serviceColors = serviceColors;
        this.eventBuffer = [];
        this.lastChartUpdate = 0;
        this.MAX_CHART_POINTS = 50;
        this.CHART_UPDATE_INTERVAL = 1000; // 1 second
        
        // Start throttled update loop
        this.startUpdateLoop();
    }
    
    /**
     * Initialize all charts
     */
    initializeCharts() {
        try {
            console.log('[CHARTS] Starting chart initialization...');
            
            // Verify Chart.js is loaded
            if (typeof Chart === 'undefined') {
                console.error('[CHARTS] Chart.js not loaded!');
                return false;
            }
            console.log('[CHARTS] Chart.js loaded successfully');
            
            // Verify canvas elements exist
            const canvasCheck = {
                eventsChart: document.getElementById('eventsChart'),
                responseChart: document.getElementById('responseChart'),
                throughputChart: document.getElementById('throughputChart'),
                errorChart: document.getElementById('errorChart')
            };
            
            for (const [name, canvas] of Object.entries(canvasCheck)) {
                if (!canvas) {
                    console.error(`[CHARTS] Canvas element ${name} not found!`);
                    return false;
                }
            }
            console.log('[CHARTS] All canvas elements found');
            
            // Common chart options
            const commonOptions = {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 0 },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute',
                            displayFormats: {
                                minute: 'HH:mm'
                            }
                        },
                        grid: { color: '#2a2f4a' },
                        ticks: { color: '#a0a0a0' }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: '#2a2f4a' },
                        ticks: { color: '#a0a0a0' }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#e0e0e0' }
                    }
                }
            };
            
            console.log('[CHARTS] Creating charts...');
            
            // Events Over Time Chart
            try {
                this.charts.events = new Chart(document.getElementById('eventsChart'), {
                    type: 'line',
                    data: {
                        datasets: Object.keys(this.serviceColors).map(service => ({
                            label: service.charAt(0).toUpperCase() + service.slice(1),
                            data: [],
                            borderColor: this.serviceColors[service],
                            backgroundColor: this.serviceColors[service] + '20',
                            tension: 0.4,
                            fill: false
                        }))
                    },
                    options: { ...commonOptions }
                });
                console.log('[CHARTS] Events chart created successfully');
            } catch (error) {
                console.error('[CHARTS] Failed to create events chart:', error);
            }
            
            // Response Times Chart
            try {
                this.charts.response = new Chart(document.getElementById('responseChart'), {
                    type: 'line',
                    data: {
                        datasets: [
                            { label: 'p50', data: [], borderColor: '#10b981', tension: 0.4 },
                            { label: 'p95', data: [], borderColor: '#f59e0b', tension: 0.4 },
                            { label: 'p99', data: [], borderColor: '#ef4444', tension: 0.4 }
                        ]
                    },
                    options: { ...commonOptions }
                });
                console.log('[CHARTS] Response times chart created successfully');
            } catch (error) {
                console.error('[CHARTS] Failed to create response times chart:', error);
            }
            
            // Throughput Chart
            try {
                this.charts.throughput = new Chart(document.getElementById('throughputChart'), {
                    type: 'line',
                    data: {
                        datasets: [{
                            label: 'Requests/sec',
                            data: [],
                            borderColor: '#667eea',
                            backgroundColor: '#667eea20',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: { ...commonOptions }
                });
                console.log('[CHARTS] Throughput chart created successfully');
            } catch (error) {
                console.error('[CHARTS] Failed to create throughput chart:', error);
            }
            
            // Error Rate Chart
            try {
                this.charts.error = new Chart(document.getElementById('errorChart'), {
                    type: 'line',
                    data: {
                        datasets: [{
                            label: 'Error %',
                            data: [],
                            borderColor: '#ef4444',
                            backgroundColor: '#ef444420',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        ...commonOptions,
                        scales: {
                            ...commonOptions.scales,
                            y: {
                                ...commonOptions.scales.y,
                                max: 100,
                                ticks: {
                                    ...commonOptions.scales.y.ticks,
                                    callback: value => value + '%'
                                }
                            }
                        }
                    }
                });
                console.log('[CHARTS] Error rate chart created successfully');
            } catch (error) {
                console.error('[CHARTS] Failed to create error rate chart:', error);
            }

            // DAY 1 (2025-11-03): Adaptive Timeout Accuracy Chart
            try {
                this.charts.timeoutAccuracy = new Chart(document.getElementById('timeoutAccuracyChart'), {
                    type: 'scatter',
                    data: {
                        datasets: [{
                            label: 'Predicted vs Actual',
                            data: [],
                            backgroundColor: '#667eea80',
                            borderColor: '#667eea',
                            pointRadius: 5,
                            pointHoverRadius: 7
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: { duration: 0 },
                        scales: {
                            x: {
                                type: 'linear',
                                position: 'bottom',
                                title: {
                                    display: true,
                                    text: 'Predicted Timeout (s)',
                                    color: '#e0e0e0'
                                },
                                grid: { color: '#2a2f4a' },
                                ticks: { color: '#a0a0a0' }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: 'Actual Duration (s)',
                                    color: '#e0e0e0'
                                },
                                grid: { color: '#2a2f4a' },
                                ticks: { color: '#a0a0a0' }
                            }
                        },
                        plugins: {
                            legend: {
                                labels: { color: '#e0e0e0' }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const point = context.parsed;
                                        const accuracy = ((point.y / point.x) * 100).toFixed(1);
                                        return `Predicted: ${point.x}s, Actual: ${point.y}s (${accuracy}% accuracy)`;
                                    }
                                }
                            }
                        }
                    }
                });
                console.log('[CHARTS] Timeout accuracy chart created successfully');
            } catch (error) {
                console.error('[CHARTS] Failed to create timeout accuracy chart:', error);
            }

            console.log('[CHARTS] All charts initialized successfully');
            return true;
            
        } catch (error) {
            console.error('[CHARTS] Chart initialization failed:', error);
            return false;
        }
    }
    
    /**
     * Add event to buffer for batch processing
     */
    addEventToBuffer(event) {
        this.eventBuffer.push(event);
        
        // Force update if buffer gets too large
        if (this.eventBuffer.length > 100) {
            this.updateChartsFromBuffer();
        }
    }
    
    /**
     * Populate charts with historical events
     */
    populateChartsWithEvents(events) {
        if (!events || events.length === 0) return;
        
        console.log('[CHARTS] Populating charts with', events.length, 'historical events');
        
        // Group events by service
        const serviceEvents = {
            websocket: [],
            redis: [],
            supabase: [],
            kimi: [],
            glm: []
        };
        
        events.forEach(event => {
            const service = event.connection_type;
            if (serviceEvents[service]) {
                serviceEvents[service].push(event);
            }
        });
        
        // Populate Events Over Time chart
        Object.keys(this.serviceColors).forEach((service, idx) => {
            const count = serviceEvents[service].length;
            if (count > 0) {
                this.charts.events.data.datasets[idx].data.push({
                    x: Date.now(),
                    y: count
                });
            }
        });
        
        // Calculate response times
        const allResponseTimes = events
            .filter(e => e.response_time_ms)
            .map(e => e.response_time_ms)
            .sort((a, b) => a - b);
        
        if (allResponseTimes.length > 0) {
            const p50 = allResponseTimes[Math.floor(allResponseTimes.length * 0.5)];
            const p95 = allResponseTimes[Math.floor(allResponseTimes.length * 0.95)];
            const p99 = allResponseTimes[Math.floor(allResponseTimes.length * 0.99)];
            
            this.charts.response.data.datasets[0].data.push({ x: Date.now(), y: p50 });
            this.charts.response.data.datasets[1].data.push({ x: Date.now(), y: p95 });
            this.charts.response.data.datasets[2].data.push({ x: Date.now(), y: p99 });
        }
        
        // Update all charts
        Object.values(this.charts).forEach(chart => chart.update('none')); // 'none' = no animation
        console.log('[CHARTS] Charts populated successfully');
    }
    
    /**
     * Update charts from buffered events
     */
    updateChartsFromBuffer() {
        if (this.eventBuffer.length === 0) return;
        
        const now = Date.now();
        const events = [...this.eventBuffer];
        this.eventBuffer.length = 0;
        
        // Group events by service
        const serviceEvents = {
            websocket: [],
            redis: [],
            supabase: [],
            kimi: [],
            glm: []
        };
        
        events.forEach(event => {
            const service = event.connection_type;
            if (serviceEvents[service]) {
                serviceEvents[service].push(event);
            }
        });
        
        // Update Events Over Time chart
        Object.keys(this.serviceColors).forEach((service, idx) => {
            const count = serviceEvents[service].length;
            if (count > 0) {
                this.charts.events.data.datasets[idx].data.push({
                    x: now,
                    y: count
                });
                
                // Keep only last MAX_CHART_POINTS
                if (this.charts.events.data.datasets[idx].data.length > this.MAX_CHART_POINTS) {
                    this.charts.events.data.datasets[idx].data.shift();
                }
            }
        });
        
        // Calculate response times
        const allResponseTimes = events
            .filter(e => e.response_time_ms)
            .map(e => e.response_time_ms)
            .sort((a, b) => a - b);
        
        if (allResponseTimes.length > 0) {
            const p50 = allResponseTimes[Math.floor(allResponseTimes.length * 0.5)];
            const p95 = allResponseTimes[Math.floor(allResponseTimes.length * 0.95)];
            const p99 = allResponseTimes[Math.floor(allResponseTimes.length * 0.99)];
            
            this.charts.response.data.datasets[0].data.push({ x: now, y: p50 });
            this.charts.response.data.datasets[1].data.push({ x: now, y: p95 });
            this.charts.response.data.datasets[2].data.push({ x: now, y: p99 });
            
            // Keep only last MAX_CHART_POINTS
            this.charts.response.data.datasets.forEach(dataset => {
                if (dataset.data.length > this.MAX_CHART_POINTS) {
                    dataset.data.shift();
                }
            });
        }
        
        // Update Throughput chart
        const throughput = events.length; // Events in last second
        this.charts.throughput.data.datasets[0].data.push({ x: now, y: throughput });
        if (this.charts.throughput.data.datasets[0].data.length > this.MAX_CHART_POINTS) {
            this.charts.throughput.data.datasets[0].data.shift();
        }
        
        // Update Error Rate chart
        const errors = events.filter(e => e.error).length;
        const errorRate = events.length > 0 ? (errors / events.length) * 100 : 0;
        this.charts.error.data.datasets[0].data.push({ x: now, y: errorRate });
        if (this.charts.error.data.datasets[0].data.length > this.MAX_CHART_POINTS) {
            this.charts.error.data.datasets[0].data.shift();
        }

        // DAY 1 (2025-11-03): Update Adaptive Timeout Accuracy chart
        // Look for events with adaptive_timeout metadata
        const timeoutEvents = events.filter(e =>
            e.metadata &&
            e.metadata.adaptive_timeout &&
            e.metadata.adaptive_timeout_ms
        );

        timeoutEvents.forEach(event => {
            const metadata = event.metadata;
            const actualDuration = metadata.adaptive_timeout_ms / 1000; // Convert to seconds

            // Try to get predicted timeout from metadata
            // This would come from the estimate API or adaptive timeout engine
            let predictedTimeout = metadata.predicted_timeout_s || metadata.timeout_s;

            // If no predicted timeout, skip this event
            if (!predictedTimeout) return;

            // Add data point: {x: predicted, y: actual}
            this.charts.timeoutAccuracy.data.datasets[0].data.push({
                x: predictedTimeout,
                y: actualDuration
            });

            // Keep only last MAX_CHART_POINTS
            if (this.charts.timeoutAccuracy.data.datasets[0].data.length > this.MAX_CHART_POINTS) {
                this.charts.timeoutAccuracy.data.datasets[0].data.shift();
            }
        });

        // Update all charts
        Object.values(this.charts).forEach(chart => chart.update('none'));
        this.lastChartUpdate = now;
    }
    
    /**
     * Start throttled update loop
     */
    startUpdateLoop() {
        setInterval(() => {
            if (Date.now() - this.lastChartUpdate >= this.CHART_UPDATE_INTERVAL) {
                this.updateChartsFromBuffer();
            }
        }, 100);
    }

    /**
     * PHASE 2.5.2: Set data source for charts
     * Allows tracking which data source (WebSocket or Realtime) provided the data
     */
    setDataSource(source) {
        this.dataSource = source;
        this._updateDataSourceIndicator();
    }

    /**
     * PHASE 2.5.2: Get current data source
     */
    getDataSource() {
        return this.dataSource || 'websocket';
    }

    /**
     * PHASE 2.5.2: Update data source indicator in chart area
     */
    _updateDataSourceIndicator() {
        const indicator = document.getElementById('chartDataSourceIndicator');
        if (indicator) {
            const source = this.getDataSource();
            indicator.textContent = source === 'realtime' ? '🔄 Realtime' : '📡 WebSocket';
            indicator.style.color = source === 'realtime' ? '#10b981' : '#3b82f6';
        }
    }

    /**
     * PHASE 2.5.2: Clear all chart data
     * Useful when switching data sources
     */
    clearAllData() {
        Object.values(this.charts).forEach(chart => {
            chart.data.datasets.forEach(dataset => {
                dataset.data = [];
            });
            chart.update('none');
        });
        this.eventBuffer = [];
        console.log('[CHARTS] All chart data cleared');
    }
}

