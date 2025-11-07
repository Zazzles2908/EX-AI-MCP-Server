/**
 * Main Dashboard Script
 * Refactored from inline script in monitoring_dashboard.html
 * Contains core dashboard initialization and event handling
 */

// Production configuration
const PRODUCTION_MODE = true; // Set to true in production to disable debug logs
const DEBUG = !PRODUCTION_MODE;

// DOM Element Cache
const domCache = {
    healthScore: null,
    healthDetails: null,
    throughputScore: null,
    connectionsScore: null,
    connectionsDetails: null,
    errorRateScore: null,
    errorRateDetails: null,
    responseTimeScore: null,
    eventLog: null,
    connectionStatus: null
};

// Constants
const MAX_EVENTS_DISPLAY = 100; // Limit to last 100 events displayed
const CHART_UPDATE_INTERVAL = 1000; // 1 second
const MAX_CHART_POINTS = 60; // Keep last 60 data points

// Legacy compatibility - expose events array for existing code
let events = [];
let statsData = {};
let wsClient = null;
let dashboard = null;

// Initialize DOM cache
function initDomCache() {
    domCache.healthScore = document.getElementById('healthScore');
    domCache.healthDetails = document.getElementById('healthDetails');
    domCache.throughputScore = document.getElementById('throughputScore');
    domCache.connectionsScore = document.getElementById('connectionsScore');
    domCache.connectionsDetails = document.getElementById('connectionsDetails');
    domCache.errorRateScore = document.getElementById('errorRateScore');
    domCache.errorRateDetails = document.getElementById('errorRateDetails');
    domCache.responseTimeScore = document.getElementById('responseTimeScore');
    domCache.eventLog = document.getElementById('eventLog');
    domCache.connectionStatus = document.getElementById('connectionStatus');
}

// Show error messages to user
function showErrorToUser(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'user-error-notification';
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ef4444;
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        z-index: 10000;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        max-width: 400px;
    `;
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}

// Export functions for use in HTML
window.DashboardMain = {
    initDomCache,
    showErrorToUser,
    getDomCache: () => domCache,
    getEvents: () => events,
    getStatsData: () => statsData,
    isDebugMode: () => DEBUG
};
