/**
 * Supabase Client Initialization
 * 
 * Phase 2.5.1: Supabase Client Infrastructure
 * Date: 2025-11-01
 * 
 * Provides centralized Supabase client initialization and configuration
 * for the monitoring dashboard migration to Supabase Realtime.
 */

// Supabase configuration from environment or defaults
const SUPABASE_CONFIG = {
    url: window.SUPABASE_URL || 'http://localhost:54321',
    anonKey: window.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxvY2FsaG9zdCIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNjI1MDAwMDAwLCJleHAiOjE5MzUwMDAwMDB9.test_key',
};

// Global Supabase client instance
let supabaseClient = null;

/**
 * Initialize Supabase client
 * 
 * @returns {Promise<Object>} Initialized Supabase client
 */
async function initSupabaseClient() {
    if (supabaseClient) {
        console.log('[SUPABASE] Client already initialized');
        return supabaseClient;
    }

    try {
        // Check if supabase-js library is loaded
        if (typeof window.supabase === 'undefined') {
            throw new Error('Supabase library not loaded. Include supabase-js in HTML.');
        }

        const { createClient } = window.supabase;

        supabaseClient = createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey, {
            realtime: {
                params: {
                    eventsPerSecond: 10,
                },
            },
        });

        console.log('[SUPABASE] ✅ Client initialized successfully');
        return supabaseClient;
    } catch (error) {
        console.error('[SUPABASE] ❌ Failed to initialize client:', error);
        throw error;
    }
}

/**
 * Get Supabase client instance
 * 
 * @returns {Object} Supabase client
 */
function getSupabaseClient() {
    if (!supabaseClient) {
        throw new Error('Supabase client not initialized. Call initSupabaseClient() first.');
    }
    return supabaseClient;
}

/**
 * Subscribe to monitoring events
 * 
 * @param {string} eventType - Type of event to subscribe to
 * @param {Function} callback - Callback function for new events
 * @returns {Object} Subscription object with unsubscribe method
 */
function subscribeToMonitoringEvents(eventType, callback) {
    try {
        const client = getSupabaseClient();

        const subscription = client
            .channel(`monitoring:${eventType}`)
            .on(
                'postgres_changes',
                {
                    event: 'INSERT',
                    schema: 'monitoring',
                    table: 'monitoring_events',
                    filter: `event_type=eq.${eventType}`,
                },
                (payload) => {
                    console.log(`[SUPABASE] New ${eventType} event:`, payload);
                    callback(payload.new);
                }
            )
            .subscribe((status) => {
                console.log(`[SUPABASE] Subscription status for ${eventType}:`, status);
            });

        return subscription;
    } catch (error) {
        console.error('[SUPABASE] Failed to subscribe to events:', error);
        throw error;
    }
}

/**
 * Query monitoring events
 * 
 * @param {string} eventType - Type of event to query
 * @param {number} limit - Maximum number of events to return
 * @returns {Promise<Array>} Array of monitoring events
 */
async function queryMonitoringEvents(eventType, limit = 100) {
    try {
        const client = getSupabaseClient();

        const { data, error } = await client
            .from('monitoring_events')
            .select('*')
            .eq('event_type', eventType)
            .order('created_at', { ascending: false })
            .limit(limit);

        if (error) {
            throw error;
        }

        console.log(`[SUPABASE] Retrieved ${data.length} ${eventType} events`);
        return data;
    } catch (error) {
        console.error('[SUPABASE] Failed to query events:', error);
        throw error;
    }
}

/**
 * Insert monitoring event
 * 
 * @param {string} eventType - Type of event
 * @param {Object} data - Event data
 * @param {string} source - Source of the event
 * @returns {Promise<Object>} Inserted event
 */
async function insertMonitoringEvent(eventType, data, source = 'dashboard') {
    try {
        const client = getSupabaseClient();

        const { data: insertedData, error } = await client
            .from('monitoring_events')
            .insert([
                {
                    event_type: eventType,
                    data: data,
                    source: source,
                    timestamp: new Date().toISOString(),
                },
            ])
            .select();

        if (error) {
            throw error;
        }

        console.log('[SUPABASE] Event inserted:', insertedData[0]);
        return insertedData[0];
    } catch (error) {
        console.error('[SUPABASE] Failed to insert event:', error);
        throw error;
    }
}

/**
 * Get connection status
 * 
 * @returns {Promise<Object>} Connection status
 */
async function getConnectionStatus() {
    try {
        const client = getSupabaseClient();

        // Test connection by querying a simple table
        const { data, error } = await client
            .from('monitoring_events')
            .select('count', { count: 'exact', head: true });

        if (error) {
            return {
                connected: false,
                error: error.message,
            };
        }

        return {
            connected: true,
            timestamp: new Date().toISOString(),
        };
    } catch (error) {
        return {
            connected: false,
            error: error.message,
        };
    }
}

// Export functions for use in other modules
window.SupabaseClient = {
    initSupabaseClient,
    getSupabaseClient,
    subscribeToMonitoringEvents,
    queryMonitoringEvents,
    insertMonitoringEvent,
    getConnectionStatus,
};

console.log('[SUPABASE] Module loaded');

