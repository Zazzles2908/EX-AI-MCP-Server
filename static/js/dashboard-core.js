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
}

// Export for use in dashboard
window.DashboardCore = DashboardCore;

