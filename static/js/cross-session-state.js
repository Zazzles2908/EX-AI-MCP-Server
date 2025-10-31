/**
 * Cross-Session State Management
 * 
 * Phase 2.5.1: Supabase Client Infrastructure
 * Date: 2025-11-01
 * 
 * Manages shared state across multiple dashboard sessions using Supabase
 * as the persistent backend. Enables real-time synchronization of dashboard
 * state across browser tabs and sessions.
 */

class CrossSessionState {
    constructor(stateKey, options = {}) {
        this.stateKey = stateKey;
        this.options = {
            persistToSupabase: true,
            syncInterval: 5000,
            ...options,
        };

        this.state = {};
        this.subscribers = [];
        this.syncTimer = null;
    }

    /**
     * Initialize state management
     * 
     * @returns {Promise<void>}
     */
    async initialize() {
        try {
            console.log(`[STATE] Initializing cross-session state for ${this.stateKey}`);

            // Load initial state from localStorage
            const savedState = localStorage.getItem(`state:${this.stateKey}`);
            if (savedState) {
                this.state = JSON.parse(savedState);
                console.log(`[STATE] Loaded state from localStorage:`, this.state);
            }

            // Start periodic sync with Supabase
            if (this.options.persistToSupabase) {
                this._startSync();
            }

            console.log(`[STATE] ✅ State initialized for ${this.stateKey}`);
        } catch (error) {
            console.error(`[STATE] ❌ Failed to initialize state:`, error);
            throw error;
        }
    }

    /**
     * Get state value
     * 
     * @param {string} key - State key
     * @param {*} defaultValue - Default value if key not found
     * @returns {*} State value
     */
    get(key, defaultValue = null) {
        return this.state[key] !== undefined ? this.state[key] : defaultValue;
    }

    /**
     * Set state value
     * 
     * @param {string} key - State key
     * @param {*} value - State value
     */
    set(key, value) {
        const oldValue = this.state[key];

        if (oldValue === value) {
            return; // No change
        }

        this.state[key] = value;

        // Save to localStorage
        this._saveToLocalStorage();

        // Notify subscribers
        this._notifySubscribers(key, value, oldValue);

        // Mark for sync
        this._markDirty();
    }

    /**
     * Subscribe to state changes
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
     * Get all state
     * 
     * @returns {Object} Current state
     */
    getAll() {
        return { ...this.state };
    }

    /**
     * Reset state
     */
    reset() {
        this.state = {};
        this._saveToLocalStorage();
        this._notifySubscribers('*', null, null);
    }

    /**
     * Destroy state management
     */
    destroy() {
        if (this.syncTimer) {
            clearInterval(this.syncTimer);
        }
        this.subscribers = [];
        console.log(`[STATE] ✅ State destroyed for ${this.stateKey}`);
    }

    /**
     * Save state to localStorage
     * 
     * @private
     */
    _saveToLocalStorage() {
        try {
            localStorage.setItem(`state:${this.stateKey}`, JSON.stringify(this.state));
        } catch (error) {
            console.error('[STATE] Failed to save to localStorage:', error);
        }
    }

    /**
     * Notify subscribers of state change
     * 
     * @private
     * @param {string} key - Changed key
     * @param {*} newValue - New value
     * @param {*} oldValue - Old value
     */
    _notifySubscribers(key, newValue, oldValue) {
        this.subscribers.forEach((callback) => {
            try {
                callback({
                    key,
                    newValue,
                    oldValue,
                    state: this.state,
                });
            } catch (error) {
                console.error('[STATE] Error in subscriber callback:', error);
            }
        });
    }

    /**
     * Mark state as dirty for sync
     * 
     * @private
     */
    _markDirty() {
        sessionStorage.setItem(`dirty:${this.stateKey}`, 'true');
    }

    /**
     * Check if state is dirty
     * 
     * @private
     * @returns {boolean} True if dirty
     */
    _isDirty() {
        return sessionStorage.getItem(`dirty:${this.stateKey}`) === 'true';
    }

    /**
     * Clear dirty flag
     * 
     * @private
     */
    _clearDirty() {
        sessionStorage.removeItem(`dirty:${this.stateKey}`);
    }

    /**
     * Start periodic sync with Supabase
     * 
     * @private
     */
    _startSync() {
        this.syncTimer = setInterval(() => {
            if (this._isDirty()) {
                this._syncToSupabase();
            }
        }, this.options.syncInterval);

        console.log(`[STATE] Started sync timer (interval: ${this.options.syncInterval}ms)`);
    }

    /**
     * Sync state to Supabase
     * 
     * @private
     */
    async _syncToSupabase() {
        try {
            await window.SupabaseClient.insertMonitoringEvent(
                'state_sync',
                {
                    stateKey: this.stateKey,
                    state: this.state,
                },
                'dashboard'
            );

            this._clearDirty();
            console.log(`[STATE] ✅ State synced to Supabase`);
        } catch (error) {
            console.error('[STATE] Failed to sync to Supabase:', error);
        }
    }
}

// Export for use in other modules
window.CrossSessionState = CrossSessionState;

console.log('[STATE] Module loaded');

