/**
 * Supabase Realtime Adapter
 * Replaces custom WebSocket for dashboard updates
 * 
 * PHASE 4 IMPLEMENTATION (2025-11-01): Supabase Realtime integration
 * EXAI Consultation: 63c00b70-364b-4351-bf6c-5a105e553dce
 * 
 * This adapter provides real-time updates from Supabase PostgreSQL:
 * - Subscribes to database changes via Supabase Realtime
 * - Handles connection management and reconnection
 * - Routes events to appropriate dashboard components
 * - Replaces custom WebSocket server
 * 
 * Architecture:
 * PostgreSQL → Supabase Realtime → SupabaseRealtimeAdapter → Dashboard
 */

class SupabaseRealtimeAdapter {
    /**
     * Initialize Supabase Realtime adapter
     * 
     * @param {string} supabaseUrl - Supabase project URL
     * @param {string} supabaseKey - Supabase anon/public key
     */
    constructor(supabaseUrl, supabaseKey) {
        this.client = supabase.createClient(supabaseUrl, supabaseKey);
        this.subscriptions = {};
        this.eventHandlers = {};
        this.connected = false;
        
        console.log('[SUPABASE_REALTIME] Initialized adapter');
    }
    
    /**
     * Subscribe to a Supabase Realtime channel
     * 
     * @param {string} channelName - Name of the channel to subscribe to
     * @param {Object} options - Subscription options
     * @param {string} options.schema - Database schema (default: 'monitoring')
     * @param {string} options.table - Table name to watch
     * @param {string} options.event - Event type ('INSERT', 'UPDATE', 'DELETE', '*')
     * @param {Function} callback - Callback function for events
     */
    subscribe(channelName, options = {}, callback) {
        const {
            schema = 'monitoring',
            table = 'monitoring_events',
            event = '*'
        } = options;
        
        console.log(`[SUPABASE_REALTIME] Subscribing to channel: ${channelName} (${schema}.${table})`);
        
        const channel = this.client
            .channel(channelName)
            .on(
                'postgres_changes',
                { 
                    event: event,
                    schema: schema,
                    table: table
                },
                (payload) => {
                    console.log(`[SUPABASE_REALTIME] Received event on ${channelName}:`, payload);
                    this.handleEvent(channelName, payload);
                    if (callback) {
                        callback(payload);
                    }
                }
            )
            .subscribe((status) => {
                console.log(`[SUPABASE_REALTIME] Channel ${channelName} status:`, status);
                if (status === 'SUBSCRIBED') {
                    this.connected = true;
                    console.log(`[SUPABASE_REALTIME] Successfully subscribed to ${channelName}`);
                }
            });
        
        this.subscriptions[channelName] = channel;
        return channel;
    }
    
    /**
     * Unsubscribe from a channel
     * 
     * @param {string} channelName - Name of the channel to unsubscribe from
     */
    unsubscribe(channelName) {
        if (this.subscriptions[channelName]) {
            console.log(`[SUPABASE_REALTIME] Unsubscribing from channel: ${channelName}`);
            this.subscriptions[channelName].unsubscribe();
            delete this.subscriptions[channelName];
            delete this.eventHandlers[channelName];
        }
    }
    
    /**
     * Register an event handler for a specific channel
     * 
     * @param {string} channelName - Channel name
     * @param {Function} handler - Event handler function
     */
    on(channelName, handler) {
        this.eventHandlers[channelName] = handler;
    }
    
    /**
     * Handle incoming events from Supabase Realtime
     * 
     * @param {string} channelName - Channel name
     * @param {Object} payload - Event payload
     */
    handleEvent(channelName, payload) {
        const handler = this.eventHandlers[channelName];
        if (handler) {
            try {
                handler(payload.new || payload);
            } catch (error) {
                console.error(`[SUPABASE_REALTIME] Error in event handler for ${channelName}:`, error);
            }
        }
    }
    
    /**
     * Disconnect all subscriptions
     */
    disconnect() {
        console.log('[SUPABASE_REALTIME] Disconnecting all subscriptions');
        Object.keys(this.subscriptions).forEach(channelName => {
            this.unsubscribe(channelName);
        });
        this.connected = false;
    }
    
    /**
     * Check if adapter is connected
     * 
     * @returns {boolean} Connection status
     */
    isConnected() {
        return this.connected;
    }
}


/**
 * Supabase Query Interface
 * Provides methods for querying aggregated metrics from PostgreSQL
 * 
 * PHASE 4 IMPLEMENTATION (2025-11-01): Direct PostgreSQL queries
 * Replaces Edge Functions with native RPC calls
 */
class SupabaseQueryInterface {
    /**
     * Initialize query interface
     * 
     * @param {string} supabaseUrl - Supabase project URL
     * @param {string} supabaseKey - Supabase anon/public key
     */
    constructor(supabaseUrl, supabaseKey) {
        this.client = supabase.createClient(supabaseUrl, supabaseKey);
        console.log('[SUPABASE_QUERY] Initialized query interface');
    }
    
    /**
     * Get cache metrics summary
     * 
     * @param {string} timeRange - Time range ('1hour', '24hours', '7days')
     * @returns {Promise<Object>} Cache metrics summary
     */
    async getCacheMetrics(timeRange = '1hour') {
        try {
            const { data, error } = await this.client
                .rpc('get_cache_metrics_summary', { 
                    time_range: timeRange 
                });
            
            if (error) {
                console.error('[SUPABASE_QUERY] Error fetching cache metrics:', error);
                return null;
            }
            
            return data;
        } catch (error) {
            console.error('[SUPABASE_QUERY] Exception fetching cache metrics:', error);
            return null;
        }
    }
    
    /**
     * Get WebSocket health metrics
     * 
     * @param {string} timeRange - Time range ('1hour', '24hours', '7days')
     * @returns {Promise<Object>} WebSocket health metrics
     */
    async getWebSocketMetrics(timeRange = '1hour') {
        try {
            const { data, error } = await this.client
                .rpc('get_websocket_metrics_summary', { 
                    time_range: timeRange 
                });
            
            if (error) {
                console.error('[SUPABASE_QUERY] Error fetching WebSocket metrics:', error);
                return null;
            }
            
            return data;
        } catch (error) {
            console.error('[SUPABASE_QUERY] Exception fetching WebSocket metrics:', error);
            return null;
        }
    }
    
    /**
     * Get connection health metrics
     * 
     * @param {string} timeRange - Time range ('1hour', '24hours', '7days')
     * @returns {Promise<Object>} Connection health metrics
     */
    async getConnectionMetrics(timeRange = '1hour') {
        try {
            const { data, error } = await this.client
                .rpc('get_connection_metrics_summary', { 
                    time_range: timeRange 
                });
            
            if (error) {
                console.error('[SUPABASE_QUERY] Error fetching connection metrics:', error);
                return null;
            }
            
            return data;
        } catch (error) {
            console.error('[SUPABASE_QUERY] Exception fetching connection metrics:', error);
            return null;
        }
    }
    
    /**
     * Get performance metrics
     * 
     * @param {string} timeRange - Time range ('1hour', '24hours', '7days')
     * @returns {Promise<Object>} Performance metrics
     */
    async getPerformanceMetrics(timeRange = '1hour') {
        try {
            const { data, error} = await this.client
                .rpc('get_performance_metrics_summary', { 
                    time_range: timeRange 
                });
            
            if (error) {
                console.error('[SUPABASE_QUERY] Error fetching performance metrics:', error);
                return null;
            }
            
            return data;
        } catch (error) {
            console.error('[SUPABASE_QUERY] Exception fetching performance metrics:', error);
            return null;
        }
    }
}


// Export for use in dashboard
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SupabaseRealtimeAdapter, SupabaseQueryInterface };
}

