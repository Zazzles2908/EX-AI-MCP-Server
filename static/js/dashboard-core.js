/**
 * Dashboard Core Module
 * PHASE 2 REFACTORING (2025-10-23)
 * 
 * Centralized state management and event coordination for the monitoring dashboard.
 * Implements pub/sub pattern for component communication.
 */

class DashboardCore {
    constructor() {
        // Event subscribers
        this.subscribers = {};
        
        // Dashboard state
        this.state = {
            connected: false,
            events: [],
            maxEvents: 100,
            statsData: {
                websocket: {},
                redis: {},
                supabase: {},
                kimi: {},
                glm: {}
            },
            healthData: {
                websocket: { status: 'unknown', score: 0 },
                redis: { status: 'unknown', score: 0 },
                supabase: { status: 'unknown', score: 0 },
                kimi: { status: 'unknown', score: 0 },
                glm: { status: 'unknown', score: 0 }
            },
            sessionMetrics: {
                active_sessions: 0,
                conversation_length: 0,
                tokens_used: 0,
                max_tokens: 0,
                current_model: '--'
            },
            // PHASE 1 DASHBOARD INTEGRATION (2025-10-31): Cache metrics
            cacheMetrics: {
                implementation: '--',
                hit_rate: 0,
                hits: 0,
                misses: 0,
                total_requests: 0,
                error_count: 0,
                size_rejections: 0,
                cache_size: 0,
                max_size: 0
            }
        };
        
        // Service colors
        this.serviceColors = {
            websocket: '#3B82F6',  // Blue
            redis: '#EF4444',       // Red
            supabase: '#10B981',    // Green
            kimi: '#8B5CF6',        // Purple
            glm: '#F59E0B'          // Orange
        };
    }
    
    /**
     * Subscribe to events
     */
    on(event, callback) {
        if (!this.subscribers[event]) {
            this.subscribers[event] = [];
        }
        this.subscribers[event].push(callback);
    }
    
    /**
     * Unsubscribe from events
     */
    off(event, callback) {
        if (!this.subscribers[event]) return;
        this.subscribers[event] = this.subscribers[event].filter(cb => cb !== callback);
    }
    
    /**
     * Emit event to subscribers
     */
    emit(event, data) {
        if (!this.subscribers[event]) return;
        this.subscribers[event].forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`[DashboardCore] Error in ${event} subscriber:`, error);
            }
        });
    }
    
    /**
     * Update connection status
     */
    setConnected(connected) {
        if (this.state.connected === connected) return;
        
        this.state.connected = connected;
        this.emit('connection:change', connected);
        
        // Update UI
        const statusEl = document.getElementById('connectionStatus');
        if (statusEl) {
            if (connected) {
                statusEl.textContent = '🟢 Connected';
                statusEl.className = 'connection-status status-connected';
            } else {
                statusEl.textContent = '🔴 Disconnected';
                statusEl.className = 'connection-status status-disconnected';
            }
        }
    }
    
    /**
     * Add event to history
     */
    addEvent(event) {
        this.state.events.unshift(event);
        if (this.state.events.length > this.state.maxEvents) {
            this.state.events.pop();
        }
        this.emit('event:added', event);
    }
    
    /**
     * Update stats for a service
     */
    updateStats(service, stats) {
        if (!stats) return;
        
        this.state.statsData[service] = stats;
        this.emit('stats:updated', { service, stats });
    }
    
    /**
     * Update all stats
     */
    updateAllStats(stats) {
        Object.keys(stats).forEach(service => {
            this.updateStats(service, stats[service]);
        });
    }
    
    /**
     * Update health data for a service
     */
    updateHealth(service, status, score) {
        this.state.healthData[service] = { status, score: Math.max(0, score) };
        this.emit('health:updated', { service, status, score });
    }
    
    /**
     * Update session metrics
     */
    updateSessionMetrics(metrics) {
        if (!metrics) return;
        
        // Update state
        Object.keys(metrics).forEach(key => {
            if (metrics[key] !== undefined) {
                this.state.sessionMetrics[key] = metrics[key];
            }
        });
        
        this.emit('session:updated', this.state.sessionMetrics);
        
        // Update UI
        if (metrics.active_sessions !== undefined) {
            const el = document.getElementById('activeSessionsValue');
            if (el) el.textContent = metrics.active_sessions;
        }
        
        if (metrics.conversation_length !== undefined) {
            const el = document.getElementById('conversationLengthValue');
            if (el) {
                el.textContent = metrics.conversation_length === 0 
                    ? '-- messages' 
                    : `${metrics.conversation_length} message${metrics.conversation_length !== 1 ? 's' : ''}`;
            }
        }
        
        if (metrics.tokens_used !== undefined && metrics.max_tokens !== undefined) {
            const el = document.getElementById('contextWindowValue');
            if (el) {
                if (metrics.max_tokens === 0) {
                    el.textContent = '-- / --';
                } else {
                    const percentage = Math.round((metrics.tokens_used / metrics.max_tokens) * 100);
                    el.textContent = `${this.formatTokens(metrics.tokens_used)} / ${this.formatTokens(metrics.max_tokens)} (${percentage}%)`;
                }
            }
        }
        
        if (metrics.current_model !== undefined) {
            const el = document.getElementById('currentModelValue');
            if (el) el.textContent = metrics.current_model || '--';
        }
    }
    
    /**
     * Format tokens for display
     */
    formatTokens(tokens) {
        if (tokens >= 1000) {
            return `${(tokens / 1000).toFixed(1)}K`;
        }
        return tokens.toString();
    }
    
    /**
     * Get current state
     */
    getState() {
        return { ...this.state };
    }
    
    /**
     * Get service color
     */
    getServiceColor(service) {
        return this.serviceColors[service] || '#6B7280';
    }
    
    /**
     * Clear all events
     */
    clearEvents() {
        this.state.events = [];
        this.emit('events:cleared');
    }
    
    /**
     * Format bytes for display
     */
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Update cache metrics
     * PHASE 1 & 2 DASHBOARD INTEGRATION (2025-10-31)
     */
    updateCacheMetrics(metrics) {
        // Update state
        this.state.cacheMetrics = { ...metrics };

        // Emit event for subscribers
        this.emit('cache:update', metrics);

        // PHASE 1: Update health bar
        const hitRateEl = document.getElementById('cacheHitRate');
        const implEl = document.getElementById('cacheImplementation');
        const indicatorEl = document.getElementById('cacheHealthIndicator');

        if (hitRateEl) {
            hitRateEl.textContent = `${metrics.hit_rate.toFixed(1)}%`;
        }

        if (implEl) {
            const implText = metrics.implementation === 'new' ? 'New (L1+L2)' : 'Legacy (L1)';
            implEl.textContent = implText;
        }

        // Color code based on hit rate
        if (indicatorEl) {
            indicatorEl.className = 'health-indicator';
            if (metrics.hit_rate >= 80) {
                indicatorEl.classList.add('health-good');
            } else if (metrics.hit_rate >= 60) {
                indicatorEl.classList.add('health-warning');
            } else {
                indicatorEl.classList.add('health-critical');
            }
        }

        // PHASE 2: Update cache panel
        this.updateCachePanel(metrics);
    }

    /**
     * Update cache migration panel
     * PHASE 2 DASHBOARD INTEGRATION (2025-10-31)
     */
    updateCachePanel(metrics) {
        // Update migration progress
        const isNew = metrics.implementation === 'new';
        const progressPercent = isNew ? 100 : 0;

        const progressFill = document.getElementById('migrationProgressFill');
        const progressLabel = document.getElementById('migrationProgressLabel');

        if (progressFill) {
            progressFill.style.width = `${progressPercent}%`;
        }

        if (progressLabel) {
            progressLabel.textContent = `${progressPercent}% migrated to new implementation`;
        }

        // Update implementation-specific metrics
        if (isNew) {
            // New implementation is active
            this.updateImplMetrics('new', metrics);
            this.updateImplMetrics('legacy', { hit_rate: 0, hits: 0, misses: 0, total_requests: 0, cache_size: 0, error_count: 0 });
        } else {
            // Legacy implementation is active
            this.updateImplMetrics('legacy', metrics);
            this.updateImplMetrics('new', { hit_rate: 0, hits: 0, misses: 0, total_requests: 0, cache_size: 0, error_count: 0 });
        }

        // Update error tracking
        this.updateCacheErrors(metrics);
    }

    /**
     * Update implementation-specific metrics
     */
    updateImplMetrics(impl, metrics) {
        const hitRateEl = document.getElementById(`${impl}HitRate`);
        const requestsEl = document.getElementById(`${impl}Requests`);
        const cacheSizeEl = document.getElementById(`${impl}CacheSize`);
        const errorsEl = document.getElementById(`${impl}Errors`);

        if (hitRateEl) {
            hitRateEl.textContent = `${metrics.hit_rate.toFixed(1)}%`;
        }

        if (requestsEl) {
            requestsEl.textContent = metrics.total_requests || 0;
        }

        if (cacheSizeEl) {
            cacheSizeEl.textContent = `${metrics.cache_size || 0} / ${metrics.max_size || 0}`;
        }

        if (errorsEl) {
            errorsEl.textContent = metrics.error_count || 0;
        }
    }

    /**
     * Update cache error tracking
     */
    updateCacheErrors(metrics) {
        const errorsListEl = document.getElementById('cacheErrorsList');

        if (!errorsListEl) return;

        if (metrics.error_count === 0) {
            errorsListEl.innerHTML = '<div class="no-errors">No cache errors detected ✅</div>';
        } else {
            // Show error summary
            errorsListEl.innerHTML = `
                <div class="error-item">
                    <div class="error-time">${new Date().toLocaleString()}</div>
                    <div class="error-message">
                        ${metrics.error_count} total errors detected
                        ${metrics.size_rejections > 0 ? `<br>• ${metrics.size_rejections} size rejections` : ''}
                    </div>
                </div>
            `;
        }
    }
}

    /**
     * PHASE 2.5.2: Set data source adapter
     * Allows switching between WebSocket and Supabase Realtime
     */
    setDataSourceAdapter(adapter) {
        this.dataSourceAdapter = adapter;
        this.emit('datasource:changed', adapter);
        console.log('[DashboardCore] Data source adapter changed:', adapter);
    }

    /**
     * PHASE 2.5.2: Get current data source adapter
     */
    getDataSourceAdapter() {
        return this.dataSourceAdapter || 'websocket';
    }

    /**
     * PHASE 2.5.2: Enable dual-mode operation
     * Allows receiving data from both WebSocket and Realtime simultaneously
     */
    enableDualMode(enabled = true) {
        this.dualModeEnabled = enabled;
        this.emit('dualmode:changed', enabled);
        console.log('[DashboardCore] Dual mode:', enabled ? 'ENABLED' : 'DISABLED');
    }

    /**
     * PHASE 2.5.2: Check if dual mode is enabled
     */
    isDualModeEnabled() {
        return this.dualModeEnabled === true;
    }
}

// Export for use in dashboard
window.DashboardCore = DashboardCore;

