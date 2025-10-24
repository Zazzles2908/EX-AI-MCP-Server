/**
 * WebSocket Client Module
 * PHASE 2 REFACTORING (2025-10-23)
 * 
 * Handles WebSocket connection management with:
 * - Automatic reconnection with exponential backoff
 * - Connection state tracking
 * - Event-driven architecture for message handling
 * - Health checks and keepalive
 */

class WebSocketClient {
    constructor(url, options = {}) {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = options.maxReconnectAttempts || Infinity;
        this.reconnectDelay = options.reconnectDelay || 5000;
        this.maxReconnectDelay = options.maxReconnectDelay || 30000;
        this.reconnectBackoffMultiplier = options.reconnectBackoffMultiplier || 1.5;
        this.autoReconnect = options.autoReconnect !== false;
        
        // Event handlers
        this.onopen = options.onopen || (() => {});
        this.onmessage = options.onmessage || (() => {});
        this.onerror = options.onerror || (() => {});
        this.onclose = options.onclose || (() => {});
        this.onreconnect = options.onreconnect || (() => {});
        
        // Connection state
        this.isConnected = false;
        this.isConnecting = false;
        this.reconnectTimer = null;
    }
    
    /**
     * Connect to WebSocket server
     */
    connect() {
        if (this.isConnecting || this.isConnected) {
            console.warn('[WebSocketClient] Already connected or connecting');
            return;
        }
        
        this.isConnecting = true;
        console.log(`[WebSocketClient] Connecting to ${this.url}...`);
        
        try {
            this.ws = new WebSocket(this.url);
            this.setupEventHandlers();
        } catch (error) {
            console.error('[WebSocketClient] Connection error:', error);
            this.isConnecting = false;
            this.scheduleReconnect();
        }
    }
    
    /**
     * Setup WebSocket event handlers
     */
    setupEventHandlers() {
        this.ws.onopen = () => {
            console.log('[WebSocketClient] Connected successfully');
            this.isConnected = true;
            this.isConnecting = false;
            this.reconnectAttempts = 0;
            this.onopen();
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.onmessage(data);
            } catch (error) {
                console.error('[WebSocketClient] Failed to parse message:', error);
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('[WebSocketClient] WebSocket error:', error);
            this.onerror(error);
        };
        
        this.ws.onclose = (event) => {
            console.log('[WebSocketClient] Connection closed:', event.code, event.reason);
            this.isConnected = false;
            this.isConnecting = false;
            this.onclose(event);
            
            if (this.autoReconnect) {
                this.scheduleReconnect();
            }
        };
    }
    
    /**
     * Schedule reconnection with exponential backoff
     */
    scheduleReconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('[WebSocketClient] Max reconnection attempts reached');
            return;
        }
        
        const delay = Math.min(
            this.reconnectDelay * Math.pow(this.reconnectBackoffMultiplier, this.reconnectAttempts),
            this.maxReconnectDelay
        );
        
        this.reconnectAttempts++;
        console.log(`[WebSocketClient] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})...`);
        
        this.reconnectTimer = setTimeout(() => {
            this.onreconnect(this.reconnectAttempts);
            this.connect();
        }, delay);
    }
    
    /**
     * Send message to server
     */
    send(data) {
        if (!this.isConnected || !this.ws) {
            console.warn('[WebSocketClient] Cannot send - not connected');
            return false;
        }
        
        try {
            const message = typeof data === 'string' ? data : JSON.stringify(data);
            this.ws.send(message);
            return true;
        } catch (error) {
            console.error('[WebSocketClient] Failed to send message:', error);
            return false;
        }
    }
    
    /**
     * Close connection
     */
    close() {
        this.autoReconnect = false;
        
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        this.isConnected = false;
        this.isConnecting = false;
    }
    
    /**
     * Get connection state
     */
    getState() {
        if (!this.ws) return 'CLOSED';
        
        switch (this.ws.readyState) {
            case WebSocket.CONNECTING: return 'CONNECTING';
            case WebSocket.OPEN: return 'OPEN';
            case WebSocket.CLOSING: return 'CLOSING';
            case WebSocket.CLOSED: return 'CLOSED';
            default: return 'UNKNOWN';
        }
    }
    
    /**
     * Check if connected
     */
    isReady() {
        return this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

// Export for use in dashboard
window.WebSocketClient = WebSocketClient;

