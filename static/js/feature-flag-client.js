/**
 * Feature Flag Client
 * 
 * Phase 2.5.1: Supabase Client Infrastructure
 * Date: 2025-11-01
 * 
 * Client-side feature flag management for controlling dashboard behavior
 * during the migration from WebSocket to Supabase Realtime.
 */

class FeatureFlagClient {
    constructor(options = {}) {
        this.options = {
            cacheInterval: 60000, // 1 minute
            ...options,
        };

        this.flags = {};
        this.cacheTime = 0;
        this.subscribers = [];
    }

    /**
     * Initialize feature flags
     * 
     * @returns {Promise<void>}
     */
    async initialize() {
        try {
            console.log('[FLAGS] Initializing feature flags');

            // Load flags from server
            await this._loadFlags();

            console.log('[FLAGS] ✅ Feature flags initialized');
        } catch (error) {
            console.error('[FLAGS] ❌ Failed to initialize flags:', error);
            // Use defaults on error
            this._setDefaults();
        }
    }

    /**
     * Check if feature is enabled
     * 
     * @param {string} flagName - Feature flag name
     * @returns {boolean} True if enabled
     */
    isEnabled(flagName) {
        return this.flags[flagName] === true;
    }

    /**
     * Get flag value
     * 
     * @param {string} flagName - Feature flag name
     * @param {*} defaultValue - Default value
     * @returns {*} Flag value
     */
    get(flagName, defaultValue = false) {
        return this.flags[flagName] !== undefined ? this.flags[flagName] : defaultValue;
    }

    /**
     * Set flag value (client-side only)
     * 
     * @param {string} flagName - Feature flag name
     * @param {*} value - Flag value
     */
    set(flagName, value) {
        const oldValue = this.flags[flagName];

        if (oldValue === value) {
            return; // No change
        }

        this.flags[flagName] = value;

        // Notify subscribers
        this._notifySubscribers(flagName, value, oldValue);

        console.log(`[FLAGS] Flag changed: ${flagName} = ${value}`);
    }

    /**
     * Subscribe to flag changes
     * 
     * @param {Function} callback - Callback function
     * @returns {Function} Unsubscribe function
     */
    subscribe(callback) {
        this.subscribers.push(callback);

        // Return unsubscribe function
        return () => {
            this.subscribers = this.subscribers.filter((cb) => cb !== callback);
        };
    }

    /**
     * Get all flags
     * 
     * @returns {Object} All flags
     */
    getAll() {
        return { ...this.flags };
    }

    /**
     * Load flags from server
     * 
     * @private
     */
    async _loadFlags() {
        try {
            // Check cache
            const now = Date.now();
            if (now - this.cacheTime < this.options.cacheInterval) {
                console.log('[FLAGS] Using cached flags');
                return;
            }

            // Fetch from server
            const response = await fetch('/flags/status');

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (data.flags) {
                this.flags = data.flags;
                this.cacheTime = now;
                console.log('[FLAGS] ✅ Flags loaded from server:', this.flags);
            }
        } catch (error) {
            console.error('[FLAGS] Failed to load flags from server:', error);
            this._setDefaults();
        }
    }

    /**
     * Set default flags
     * 
     * @private
     */
    _setDefaults() {
        this.flags = {
            // Phase 2.5: Dashboard migration flags
            MONITORING_DASHBOARD_WEBSOCKET_ENABLED: true,
            MONITORING_DASHBOARD_REALTIME_ENABLED: false,
            MONITORING_DASHBOARD_DUAL_MODE: false,

            // Adapter selection
            MONITORING_ADAPTER_WEBSOCKET: true,
            MONITORING_ADAPTER_REALTIME: false,

            // Feature flags
            MONITORING_METRICS_PERSISTENCE: false,
            MONITORING_METRICS_FLUSH_INTERVAL: 300,

            // Realtime configuration
            MONITORING_REALTIME_ENABLED: false,
            MONITORING_REALTIME_BROADCAST_ENABLED: false,
        };

        console.log('[FLAGS] Using default flags:', this.flags);
    }

    /**
     * Notify subscribers of flag change
     * 
     * @private
     * @param {string} flagName - Changed flag
     * @param {*} newValue - New value
     * @param {*} oldValue - Old value
     */
    _notifySubscribers(flagName, newValue, oldValue) {
        this.subscribers.forEach((callback) => {
            try {
                callback({
                    flagName,
                    newValue,
                    oldValue,
                    flags: this.flags,
                });
            } catch (error) {
                console.error('[FLAGS] Error in subscriber callback:', error);
            }
        });
    }
}

// Global instance
let flagClient = null;

/**
 * Get or create feature flag client
 * 
 * @returns {FeatureFlagClient} Feature flag client instance
 */
function getFeatureFlagClient() {
    if (!flagClient) {
        flagClient = new FeatureFlagClient();
    }
    return flagClient;
}

// Export for use in other modules
window.FeatureFlagClient = FeatureFlagClient;
window.getFeatureFlagClient = getFeatureFlagClient;

console.log('[FLAGS] Module loaded');

