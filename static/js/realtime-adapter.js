/**
 * Supabase Realtime Adapter
 * 
 * Phase 2.5.1: Supabase Client Infrastructure
 * Date: 2025-11-01
 * 
 * Wraps Supabase Realtime subscriptions with connection management,
 * error handling, and automatic reconnection.
 */

class RealtimeAdapter {
    constructor(eventType, options = {}) {
        this.eventType = eventType;
        this.options = {
            autoReconnect: true,
            reconnectDelay: 1000,
            maxReconnectAttempts: 5,
            ...options,
        };

        this.subscription = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.callbacks = [];
        this.errorCallbacks = [];
    }

    /**
     * Start listening to Realtime events
     * 
     * @returns {Promise<void>}
     */
    async start() {
        try {
            console.log(`[REALTIME] Starting adapter for ${this.eventType}`);

            const subscription = window.SupabaseClient.subscribeToMonitoringEvents(
                this.eventType,
                (event) => this._handleEvent(event)
            );

            this.subscription = subscription;
            this.isConnected = true;
            this.reconnectAttempts = 0;

            console.log(`[REALTIME] ✅ Adapter started for ${this.eventType}`);
        } catch (error) {
            console.error(`[REALTIME] ❌ Failed to start adapter:`, error);
            this._handleError(error);

            if (this.options.autoReconnect) {
                this._scheduleReconnect();
            }
        }
    }

    /**
     * Stop listening to Realtime events
     * 
     * @returns {Promise<void>}
     */
    async stop() {
        try {
            if (this.subscription) {
                const client = window.SupabaseClient.getSupabaseClient();
                await client.removeChannel(this.subscription);
                this.subscription = null;
            }

            this.isConnected = false;
            console.log(`[REALTIME] ✅ Adapter stopped for ${this.eventType}`);
        } catch (error) {
            console.error(`[REALTIME] ❌ Failed to stop adapter:`, error);
        }
    }

    /**
     * Register callback for new events
     * 
     * @param {Function} callback - Callback function
     */
    onEvent(callback) {
        this.callbacks.push(callback);
    }

    /**
     * Register callback for errors
     * 
     * @param {Function} callback - Error callback function
     */
    onError(callback) {
        this.errorCallbacks.push(callback);
    }

    /**
     * Handle incoming event
     * 
     * @private
     * @param {Object} event - Event data
     */
    _handleEvent(event) {
        console.log(`[REALTIME] Event received for ${this.eventType}:`, event);

        // Call all registered callbacks
        this.callbacks.forEach((callback) => {
            try {
                callback(event);
            } catch (error) {
                console.error('[REALTIME] Error in callback:', error);
            }
        });
    }

    /**
     * Handle error
     * 
     * @private
     * @param {Error} error - Error object
     */
    _handleError(error) {
        console.error(`[REALTIME] Error in adapter:`, error);

        // Call all registered error callbacks
        this.errorCallbacks.forEach((callback) => {
            try {
                callback(error);
            } catch (err) {
                console.error('[REALTIME] Error in error callback:', err);
            }
        });
    }

    /**
     * Schedule reconnection attempt
     * 
     * @private
     */
    _scheduleReconnect() {
        if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
            console.error(`[REALTIME] Max reconnection attempts reached for ${this.eventType}`);
            return;
        }

        this.reconnectAttempts++;
        const delay = this.options.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

        console.log(`[REALTIME] Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);

        setTimeout(() => {
            this.start();
        }, delay);
    }

    /**
     * Get connection status
     * 
     * @returns {Object} Status object
     */
    getStatus() {
        return {
            eventType: this.eventType,
            isConnected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            maxReconnectAttempts: this.options.maxReconnectAttempts,
        };
    }
}

// Export for use in other modules
window.RealtimeAdapter = RealtimeAdapter;

console.log('[REALTIME] Module loaded');

