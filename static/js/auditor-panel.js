/**
 * AI Auditor Panel - Real-time observation display
 * 
 * Handles Supabase real-time subscriptions for auditor observations
 * and provides UI for filtering, acknowledging, and viewing insights.
 * 
 * Created: 2025-10-24
 */

class AuditorPanel {
    constructor() {
        this.observations = new Map();
        this.supabaseUrl = null;
        this.supabaseKey = null;
        this.supabase = null;
        this.channel = null;
        
        // Try to get Supabase credentials from environment or config
        this.initializeSupabase();
    }
    
    async initializeSupabase() {
        // For now, we'll need to configure Supabase client
        // This should be set via environment variables or config
        console.log('[AUDITOR_PANEL] Initializing Supabase connection...');
        
        // TODO: Get Supabase URL and key from server endpoint
        // For now, observations will be loaded via polling
        this.startPolling();
    }
    
    startPolling() {
        // FIXED (2025-10-24): Reduced polling frequency from 5s to 30s to reduce API calls
        // Poll for new observations every 30 seconds
        setInterval(() => this.fetchObservations(), 30000);

        // Initial fetch
        this.fetchObservations();
    }
    
    async fetchObservations() {
        try {
            // Fetch recent observations from server
            const response = await fetch('/api/auditor/observations?limit=50');
            if (!response.ok) {
                console.warn('[AUDITOR_PANEL] Failed to fetch observations:', response.status);
                return;
            }
            
            const observations = await response.json();
            this.updateObservations(observations);
            
        } catch (error) {
            console.error('[AUDITOR_PANEL] Error fetching observations:', error);
        }
    }
    
    updateObservations(observations) {
        // Update observations map
        for (const obs of observations) {
            if (!this.observations.has(obs.id)) {
                this.observations.set(obs.id, obs);
                this.renderObservation(obs);
                
                // Show critical alert if needed
                if (obs.severity === 'critical' && !obs.acknowledged) {
                    this.showCriticalAlert(obs);
                }
            }
        }
    }
    
    renderObservation(observation) {
        const container = document.getElementById('auditorObservations');
        
        // Remove "no observations" message if present
        const noObsMsg = container.querySelector('.no-observations');
        if (noObsMsg) {
            noObsMsg.remove();
        }
        
        // Create observation element
        const element = document.createElement('div');
        element.className = `observation observation-${observation.severity}`;
        element.id = `obs-${observation.id}`;
        element.dataset.severity = observation.severity;
        element.dataset.category = observation.category;
        
        element.innerHTML = `
            <div class="observation-header">
                <span class="severity-badge ${observation.severity}">
                    ${observation.severity.toUpperCase()}
                </span>
                <span class="category-badge">${observation.category}</span>
                <span class="confidence">Confidence: ${observation.confidence}%</span>
                <span class="timestamp">${this.formatTimestamp(observation.timestamp)}</span>
            </div>
            <div class="observation-body">
                <p class="observation-text">${this.escapeHtml(observation.observation)}</p>
                ${observation.recommendation ? `
                    <div class="recommendation">
                        <strong>Recommendation:</strong> ${this.escapeHtml(observation.recommendation)}
                    </div>
                ` : ''}
            </div>
            <div class="observation-actions">
                <button onclick="auditorPanel.acknowledgeObservation('${observation.id}')">
                    ✓ Acknowledge
                </button>
                <button onclick="auditorPanel.viewRelatedEvents('${observation.id}')">
                    📊 View Events
                </button>
            </div>
        `;
        
        // Insert at top (most recent first)
        container.insertBefore(element, container.firstChild);
    }
    
    showCriticalAlert(observation) {
        // Create toast notification for critical issues
        const toast = document.createElement('div');
        toast.className = 'critical-alert-toast';
        toast.innerHTML = `
            <div class="alert-icon">⚠️</div>
            <div class="alert-content">
                <strong>Critical Issue Detected</strong>
                <p>${this.escapeHtml(observation.observation)}</p>
                <button onclick="auditorPanel.acknowledgeObservation('${observation.id}'); this.parentElement.parentElement.remove();">
                    Acknowledge
                </button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 10000);
    }
    
    async acknowledgeObservation(observationId) {
        try {
            const response = await fetch(`/api/auditor/observations/${observationId}/acknowledge`, {
                method: 'POST'
            });
            
            if (response.ok) {
                // Update UI
                const element = document.getElementById(`obs-${observationId}`);
                if (element) {
                    element.style.opacity = '0.5';
                    element.querySelector('.observation-actions').innerHTML = '<span style="color: #4CAF50;">✓ Acknowledged</span>';
                }
                
                // Update local state
                const obs = this.observations.get(observationId);
                if (obs) {
                    obs.acknowledged = true;
                }
            }
        } catch (error) {
            console.error('[AUDITOR_PANEL] Error acknowledging observation:', error);
        }
    }
    
    async acknowledgeAllObservations() {
        const unacknowledged = Array.from(this.observations.values())
            .filter(obs => !obs.acknowledged);
        
        for (const obs of unacknowledged) {
            await this.acknowledgeObservation(obs.id);
        }
    }
    
    viewRelatedEvents(observationId) {
        const obs = this.observations.get(observationId);
        if (!obs) return;
        
        // Scroll to event log and highlight related events
        const eventLog = document.getElementById('eventLog');
        if (eventLog) {
            eventLog.scrollIntoView({ behavior: 'smooth' });
            
            // TODO: Highlight events with IDs in obs.event_ids
            console.log('[AUDITOR_PANEL] Related events:', obs.event_ids);
        }
    }
    
    filterObservations() {
        const severityFilter = document.getElementById('severityFilter').value;
        const categoryFilter = document.getElementById('categoryFilter').value;
        
        const observations = document.querySelectorAll('.observation');
        
        observations.forEach(obs => {
            const severity = obs.dataset.severity;
            const category = obs.dataset.category;
            
            let show = true;
            
            // Apply severity filter
            if (severityFilter !== 'all') {
                if (severityFilter === 'critical' && severity !== 'critical') {
                    show = false;
                } else if (severityFilter === 'warning' && severity === 'info') {
                    show = false;
                }
            }
            
            // Apply category filter
            if (categoryFilter !== 'all' && category !== categoryFilter) {
                show = false;
            }
            
            obs.style.display = show ? 'block' : 'none';
        });
    }
    
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        // Show relative time for recent observations
        if (diff < 60000) {
            return 'Just now';
        } else if (diff < 3600000) {
            const minutes = Math.floor(diff / 60000);
            return `${minutes}m ago`;
        } else if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours}h ago`;
        } else {
            return date.toLocaleString();
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize auditor panel
let auditorPanel;
document.addEventListener('DOMContentLoaded', () => {
    auditorPanel = new AuditorPanel();
});

// Global functions for onclick handlers
function filterObservations() {
    if (auditorPanel) {
        auditorPanel.filterObservations();
    }
}

function acknowledgeAllObservations() {
    if (auditorPanel) {
        auditorPanel.acknowledgeAllObservations();
    }
}

