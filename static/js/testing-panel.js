/**
 * Testing Panel - Performance testing and baseline comparison
 * 
 * Provides UI for:
 * - Test execution status tracking
 * - Baseline comparison
 * - Performance regression detection
 * - Testing mode toggle
 * 
 * Created: 2025-10-24 (Phase 0.4)
 */

class TestingPanel {
    constructor() {
        this.testingMode = false;
        this.currentBaseline = null;
        this.testResults = [];
        this.regressions = [];
        
        // Test execution stats
        this.stats = {
            running: 0,
            passed: 0,
            failed: 0,
            total: 0
        };
    }
    
    toggleTestingMode() {
        this.testingMode = !this.testingMode;
        
        const section = document.getElementById('testingSection');
        const toggle = document.getElementById('testingModeToggle');
        
        if (this.testingMode) {
            section.style.display = 'block';
            toggle.textContent = 'Disable Testing Mode';
            toggle.style.background = '#ff4444';
            console.log('[TESTING] Testing mode enabled');
        } else {
            section.style.display = 'none';
            toggle.textContent = 'Enable Testing Mode';
            toggle.style.background = '';
            console.log('[TESTING] Testing mode disabled');
        }
    }
    
    validateMetrics(metrics) {
        /**
         * Validate metrics data structure and values
         * Phase 0.4 Enhancement: Data validation
         */
        if (!metrics) {
            console.error('[TESTING] Metrics object is null or undefined');
            return false;
        }

        if (typeof metrics.latency_p95 !== 'number' || metrics.latency_p95 < 0) {
            console.error('[TESTING] Invalid latency_p95:', metrics.latency_p95);
            return false;
        }

        if (typeof metrics.memory_mb !== 'number' || metrics.memory_mb < 0) {
            console.error('[TESTING] Invalid memory_mb:', metrics.memory_mb);
            return false;
        }

        if (typeof metrics.success_rate !== 'number' || metrics.success_rate < 0 || metrics.success_rate > 100) {
            console.error('[TESTING] Invalid success_rate:', metrics.success_rate);
            return false;
        }

        return true;
    }

    async captureBaseline() {
        console.log('[TESTING] Capturing baseline...');

        try {
            // Fetch current metrics from monitoring system
            const response = await fetch('/api/metrics/current');
            if (!response.ok) {
                console.warn('[TESTING] Failed to fetch current metrics:', response.status);
                alert(`Failed to fetch metrics: HTTP ${response.status}`);
                return;
            }

            const metrics = await response.json();

            // Validate metrics
            if (!this.validateMetrics(metrics)) {
                alert('Invalid metrics data received. Cannot capture baseline.');
                return;
            }

            // Store as baseline
            this.currentBaseline = {
                timestamp: new Date().toISOString(),
                latency_p95: metrics.latency_p95,
                memory_mb: metrics.memory_mb,
                success_rate: metrics.success_rate
            };

            // Save to localStorage
            localStorage.setItem('testing_baseline', JSON.stringify(this.currentBaseline));

            // Update UI
            this.updateBaselineDisplay();

            console.log('[TESTING] Baseline captured:', this.currentBaseline);
            alert('Baseline captured successfully!');

        } catch (error) {
            console.error('[TESTING] Error capturing baseline:', error);
            alert(`Failed to capture baseline: ${error.message}`);
        }
    }
    
    async compareToBaseline() {
        if (!this.currentBaseline) {
            // Try to load from localStorage
            const stored = localStorage.getItem('testing_baseline');
            if (stored) {
                try {
                    this.currentBaseline = JSON.parse(stored);
                    // Validate loaded baseline
                    if (!this.validateMetrics(this.currentBaseline)) {
                        console.error('[TESTING] Stored baseline is invalid');
                        localStorage.removeItem('testing_baseline');
                        this.currentBaseline = null;
                        alert('Stored baseline is invalid. Please capture a new baseline.');
                        return;
                    }
                } catch (error) {
                    console.error('[TESTING] Failed to parse stored baseline:', error);
                    localStorage.removeItem('testing_baseline');
                    alert('Failed to load baseline. Please capture a new baseline.');
                    return;
                }
            } else {
                alert('No baseline available. Please capture a baseline first.');
                return;
            }
        }

        console.log('[TESTING] Comparing to baseline...');

        try {
            // Fetch current metrics
            const response = await fetch('/api/metrics/current');
            if (!response.ok) {
                console.warn('[TESTING] Failed to fetch current metrics:', response.status);
                alert(`Failed to fetch metrics: HTTP ${response.status}`);
                return;
            }

            const current = await response.json();

            // Validate current metrics
            if (!this.validateMetrics(current)) {
                alert('Invalid metrics data received. Cannot compare to baseline.');
                return;
            }
            
            // Calculate deltas
            const latencyDelta = ((current.latency_p95 - this.currentBaseline.latency_p95) / this.currentBaseline.latency_p95) * 100;
            const memoryDelta = ((current.memory_mb - this.currentBaseline.memory_mb) / this.currentBaseline.memory_mb) * 100;
            const successDelta = current.success_rate - this.currentBaseline.success_rate;
            
            // Update UI
            document.getElementById('currentLatency').textContent = `${current.latency_p95.toFixed(1)}ms`;
            document.getElementById('latencyDelta').textContent = this.formatDelta(latencyDelta, true);
            document.getElementById('latencyDelta').className = `baseline-delta ${this.getDeltaClass(latencyDelta, true)}`;
            document.getElementById('baselineLatency').textContent = `Baseline: ${this.currentBaseline.latency_p95.toFixed(1)}ms`;
            
            document.getElementById('currentMemory').textContent = `${current.memory_mb.toFixed(1)}MB`;
            document.getElementById('memoryDelta').textContent = this.formatDelta(memoryDelta, true);
            document.getElementById('memoryDelta').className = `baseline-delta ${this.getDeltaClass(memoryDelta, true)}`;
            document.getElementById('baselineMemory').textContent = `Baseline: ${this.currentBaseline.memory_mb.toFixed(1)}MB`;
            
            document.getElementById('currentSuccess').textContent = `${current.success_rate.toFixed(1)}%`;
            document.getElementById('successDelta').textContent = this.formatDelta(successDelta, false);
            document.getElementById('successDelta').className = `baseline-delta ${this.getDeltaClass(successDelta, false)}`;
            document.getElementById('baselineSuccess').textContent = `Baseline: ${this.currentBaseline.success_rate.toFixed(1)}%`;
            
            // Detect regressions
            this.detectRegressions(current, latencyDelta, memoryDelta, successDelta);
            
        } catch (error) {
            console.error('[TESTING] Error comparing to baseline:', error);
        }
    }
    
    formatDelta(delta, higherIsBad) {
        const sign = delta >= 0 ? '+' : '';
        return `${sign}${delta.toFixed(1)}%`;
    }
    
    getDeltaClass(delta, higherIsBad) {
        if (Math.abs(delta) < 5) return 'neutral';
        
        if (higherIsBad) {
            return delta > 0 ? 'positive' : 'negative';
        } else {
            return delta > 0 ? 'negative' : 'positive';
        }
    }
    
    detectRegressions(current, latencyDelta, memoryDelta, successDelta) {
        this.regressions = [];
        
        // Latency regression: > 20% increase
        if (latencyDelta > 20) {
            this.regressions.push({
                type: 'latency',
                severity: latencyDelta > 50 ? 'critical' : 'warning',
                message: `Latency increased by ${latencyDelta.toFixed(1)}% (threshold: 20%)`,
                current: current.latency_p95,
                baseline: this.currentBaseline.latency_p95
            });
        }
        
        // Memory regression: > 30% increase
        if (memoryDelta > 30) {
            this.regressions.push({
                type: 'memory',
                severity: memoryDelta > 60 ? 'critical' : 'warning',
                message: `Memory usage increased by ${memoryDelta.toFixed(1)}% (threshold: 30%)`,
                current: current.memory_mb,
                baseline: this.currentBaseline.memory_mb
            });
        }
        
        // Success rate regression: > 5% decrease
        if (successDelta < -5) {
            this.regressions.push({
                type: 'success_rate',
                severity: successDelta < -10 ? 'critical' : 'warning',
                message: `Success rate decreased by ${Math.abs(successDelta).toFixed(1)}% (threshold: 5%)`,
                current: current.success_rate,
                baseline: this.currentBaseline.success_rate
            });
        }
        
        // Update regression display
        this.updateRegressionDisplay();
    }
    
    updateRegressionDisplay() {
        const container = document.getElementById('regressionDetection');
        
        if (this.regressions.length === 0) {
            container.innerHTML = '<div class="no-regressions">No regressions detected ✓</div>';
            return;
        }
        
        container.innerHTML = '';
        
        for (const regression of this.regressions) {
            const element = document.createElement('div');
            element.className = 'regression-item';
            element.innerHTML = `
                <div class="regression-header">
                    <span class="regression-tool">${this.escapeHtml(regression.type.toUpperCase())}</span>
                    <span class="regression-severity">${this.escapeHtml(regression.severity.toUpperCase())}</span>
                </div>
                <div class="regression-details">
                    ${this.escapeHtml(regression.message)}
                    <br>
                    Current: ${this.escapeHtml(regression.current.toFixed(1))} | Baseline: ${this.escapeHtml(regression.baseline.toFixed(1))}
                </div>
            `;
            container.appendChild(element);
        }
    }
    
    updateBaselineDisplay() {
        if (!this.currentBaseline) return;
        
        document.getElementById('baselineLatency').textContent = `Baseline: ${this.currentBaseline.latency_p95.toFixed(1)}ms`;
        document.getElementById('baselineMemory').textContent = `Baseline: ${this.currentBaseline.memory_mb.toFixed(1)}MB`;
        document.getElementById('baselineSuccess').textContent = `Baseline: ${this.currentBaseline.success_rate.toFixed(1)}%`;
    }
    
    updateTestStats(stats) {
        this.stats = { ...this.stats, ...stats };
        
        document.getElementById('testsRunning').textContent = this.stats.running;
        document.getElementById('testsPassed').textContent = this.stats.passed;
        document.getElementById('testsFailed').textContent = this.stats.failed;
        
        if (this.stats.total > 0) {
            const successRate = (this.stats.passed / this.stats.total) * 100;
            document.getElementById('testSuccessRate').textContent = `${successRate.toFixed(1)}%`;
        } else {
            document.getElementById('testSuccessRate').textContent = '--';
        }
    }
    
    recordTestResult(testName, success, latency, memory) {
        this.testResults.push({
            testName,
            success,
            latency,
            memory,
            timestamp: new Date().toISOString()
        });

        // Update stats
        if (success) {
            this.stats.passed++;
        } else {
            this.stats.failed++;
        }
        this.stats.total++;

        this.updateTestStats(this.stats);
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize testing panel
let testingPanel;
document.addEventListener('DOMContentLoaded', () => {
    testingPanel = new TestingPanel();
    
    // Try to load baseline from localStorage
    const stored = localStorage.getItem('testing_baseline');
    if (stored) {
        testingPanel.currentBaseline = JSON.parse(stored);
        testingPanel.updateBaselineDisplay();
    }
});

// Global functions for onclick handlers
function toggleTestingMode() {
    if (testingPanel) {
        testingPanel.toggleTestingMode();
    }
}

function captureBaseline() {
    if (testingPanel) {
        testingPanel.captureBaseline();
    }
}

function compareToBaseline() {
    if (testingPanel) {
        testingPanel.compareToBaseline();
    }
}

