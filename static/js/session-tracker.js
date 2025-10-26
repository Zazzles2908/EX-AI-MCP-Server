/**
 * PHASE 2 REFACTORING (2025-10-23): Session Tracking Module
 * 
 * Manages session and conversation metrics for the monitoring dashboard.
 * Provides real-time tracking of active sessions, conversation length,
 * context window usage, and current model information.
 * 
 * Features:
 * - Session metric tracking and updates
 * - Context window usage monitoring with color-coded warnings
 * - Model information display
 * - Conversation length tracking
 * - Visual feedback for critical thresholds
 */

class SessionTracker {
    constructor() {
        this.metrics = {
            active_sessions: 0,
            conversation_length: 0,
            context_tokens_used: 0,
            context_tokens_max: 128000,  // Default, will be updated based on model
            current_model: '--'
        };
        
        // Warning thresholds for context window
        this.CONTEXT_WARNING_THRESHOLD = 80;  // 80% - yellow warning
        this.CONTEXT_CRITICAL_THRESHOLD = 90; // 90% - orange warning
        this.CONTEXT_DANGER_THRESHOLD = 95;   // 95% - red critical
    }
    
    /**
     * Update session metrics from backend data
     */
    updateMetrics(metrics) {
        if (!metrics) return;
        
        // Update internal state
        if (metrics.active_sessions !== undefined) {
            this.metrics.active_sessions = metrics.active_sessions;
        }
        if (metrics.conversation_length !== undefined) {
            this.metrics.conversation_length = metrics.conversation_length;
        }
        if (metrics.context_tokens_used !== undefined) {
            this.metrics.context_tokens_used = metrics.context_tokens_used;
        }
        if (metrics.context_tokens_max !== undefined) {
            this.metrics.context_tokens_max = metrics.context_tokens_max;
        }
        if (metrics.current_model !== undefined) {
            this.metrics.current_model = metrics.current_model;
        }
        
        // Update UI
        this.updateUI();
    }
    
    /**
     * Update UI elements with current metrics
     */
    updateUI() {
        // Update active sessions
        const activeSessionsEl = document.getElementById('activeSessionsValue');
        if (activeSessionsEl) {
            activeSessionsEl.textContent = this.metrics.active_sessions;
        }
        
        // Update conversation length
        const conversationLengthEl = document.getElementById('conversationLengthValue');
        if (conversationLengthEl) {
            const length = this.metrics.conversation_length;
            conversationLengthEl.textContent = length > 0 
                ? `${length} message${length !== 1 ? 's' : ''}`
                : '-- messages';
        }
        
        // Update context window with color coding
        const contextWindowEl = document.getElementById('contextWindowValue');
        if (contextWindowEl) {
            const used = this.metrics.context_tokens_used;
            const max = this.metrics.context_tokens_max;
            const percentage = max > 0 ? ((used / max) * 100).toFixed(1) : 0;
            
            // Format tokens (K for thousands)
            const formatTokens = (tokens) => {
                if (tokens >= 1000) {
                    return (tokens / 1000).toFixed(1) + 'K';
                }
                return tokens.toString();
            };
            
            contextWindowEl.textContent = `${formatTokens(used)} / ${formatTokens(max)} (${percentage}%)`;
            
            // Apply color coding based on usage percentage
            if (percentage >= this.CONTEXT_DANGER_THRESHOLD) {
                contextWindowEl.style.color = '#ef4444';  // Red - critical
            } else if (percentage >= this.CONTEXT_CRITICAL_THRESHOLD) {
                contextWindowEl.style.color = '#f59e0b';  // Orange - warning
            } else if (percentage >= this.CONTEXT_WARNING_THRESHOLD) {
                contextWindowEl.style.color = '#fbbf24';  // Yellow - caution
            } else {
                contextWindowEl.style.color = '#10b981';  // Green - healthy
            }
        }
        
        // Update current model
        const currentModelEl = document.getElementById('currentModelValue');
        if (currentModelEl) {
            currentModelEl.textContent = this.metrics.current_model || '--';
        }
    }
    
    /**
     * Get current metrics
     */
    getMetrics() {
        return { ...this.metrics };
    }
    
    /**
     * Get context window usage percentage
     */
    getContextUsagePercentage() {
        if (this.metrics.context_tokens_max === 0) return 0;
        return (this.metrics.context_tokens_used / this.metrics.context_tokens_max) * 100;
    }
    
    /**
     * Check if context window is approaching limit
     */
    isContextWindowWarning() {
        const percentage = this.getContextUsagePercentage();
        return percentage >= this.CONTEXT_WARNING_THRESHOLD;
    }
    
    /**
     * Check if context window is critical
     */
    isContextWindowCritical() {
        const percentage = this.getContextUsagePercentage();
        return percentage >= this.CONTEXT_CRITICAL_THRESHOLD;
    }
    
    /**
     * Check if context window is in danger zone
     */
    isContextWindowDanger() {
        const percentage = this.getContextUsagePercentage();
        return percentage >= this.CONTEXT_DANGER_THRESHOLD;
    }
    
    /**
     * Get context window status
     */
    getContextWindowStatus() {
        const percentage = this.getContextUsagePercentage();
        
        if (percentage >= this.CONTEXT_DANGER_THRESHOLD) {
            return {
                status: 'danger',
                color: '#ef4444',
                message: 'Context window critically full - consider starting new conversation'
            };
        } else if (percentage >= this.CONTEXT_CRITICAL_THRESHOLD) {
            return {
                status: 'critical',
                color: '#f59e0b',
                message: 'Context window approaching limit'
            };
        } else if (percentage >= this.CONTEXT_WARNING_THRESHOLD) {
            return {
                status: 'warning',
                color: '#fbbf24',
                message: 'Context window usage elevated'
            };
        } else {
            return {
                status: 'healthy',
                color: '#10b981',
                message: 'Context window usage normal'
            };
        }
    }
    
    /**
     * Reset metrics to defaults
     */
    reset() {
        this.metrics = {
            active_sessions: 0,
            conversation_length: 0,
            context_tokens_used: 0,
            context_tokens_max: 128000,
            current_model: '--'
        };
        this.updateUI();
    }
    
    /**
     * Format token count for display
     */
    formatTokens(tokens) {
        if (tokens >= 1000) {
            return (tokens / 1000).toFixed(1) + 'K';
        }
        return tokens.toString();
    }
}

