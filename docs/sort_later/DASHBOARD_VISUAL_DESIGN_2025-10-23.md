# Visual Monitoring Dashboard Design
**Date:** 2025-10-23  
**EXAI Consultation:** b0248f18-4ba5-47e1-8b33-195dc69283f4  
**Purpose:** Comprehensive visual design for EXAI-WS MCP server monitoring

---

## Executive Summary

Based on EXAI consultation, we're implementing a **three-tier dashboard** with:
1. **Real-time data flow visualization** (network graph with micro-animations)
2. **Multi-series time-series charts** (events, response times, throughput)
3. **System health indicators** (color-coded status with alerts)

**Key Design Principles:**
- Information hierarchy (critical metrics above the fold)
- Progressive disclosure (expandable sections)
- Real-time updates (1-second aggregation)
- Performance optimization (canvas rendering, data decimation)

---

## Dashboard Layout

### **Three-Tier Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: SYSTEM HEALTH BAR (Always Visible)                 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│ │ Health: 🟢  │ │ Throughput  │ │ Connections │           │
│ │ 98% Healthy │ │ 45 req/s    │ │ 12 active   │           │
│ └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│ TIER 2: TABBED INTERFACE                                   │
│ ┌─────┬─────────┬───────┬─────────┬─────┬─────┐           │
│ │ All │ WebSock │ Redis │ Supabase│ Kimi│ GLM │           │
│ └─────┴─────────┴───────┴─────────┴─────┴─────┘           │
│                                                             │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ DATA FLOW VISUALIZATION (Network Graph)              │ │
│ │                                                       │ │
│ │  User → WebSocket → Router → Tool →                  │ │
│ │           ↓           ↓        ↓                      │ │
│ │        Supabase    Redis    GLM/Kimi                  │ │
│ └───────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────┐ ┌─────────────────────┐           │
│ │ Events Over Time    │ │ Response Times      │           │
│ │ (Multi-line chart)  │ │ (Line + Histogram)  │           │
│ └─────────────────────┘ └─────────────────────┘           │
│                                                             │
│ ┌─────────────────────┐ ┌─────────────────────┐           │
│ │ Data Transferred    │ │ Error Rates         │           │
│ │ (Stacked area)      │ │ (Line + Threshold)  │           │
│ └─────────────────────┘ └─────────────────────┘           │
├─────────────────────────────────────────────────────────────┤
│ TIER 3: EXPANDABLE DETAIL SECTIONS                         │
│ ▼ Recent Events (Last 100)                                 │
│ ▼ Detailed Metrics Table                                   │
│ ▼ Alert History                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Visual Components

### **1. Data Flow Visualization**

**Type:** Network Graph with Micro-Animations  
**Library:** D3.js force-directed graph  
**Features:**
- Pulsing node borders when processing requests
- Color-coded paths that briefly highlight when traffic flows
- Connection thickness based on current throughput
- Hover states reveal detailed metrics

**Node Structure:**
```javascript
const nodes = [
  {id: "user", group: 1, x: 100, y: 200, label: "User"},
  {id: "websocket", group: 2, x: 250, y: 200, label: "WebSocket"},
  {id: "mcp_router", group: 2, x: 400, y: 200, label: "MCP Router"},
  {id: "tool", group: 3, x: 550, y: 200, label: "Tool Handler"},
  {id: "supabase", group: 4, x: 700, y: 150, label: "Supabase"},
  {id: "redis", group: 4, x: 700, y: 250, label: "Redis"},
  {id: "glm", group: 5, x: 850, y: 150, label: "GLM API"},
  {id: "kimi", group: 5, x: 850, y: 250, label: "Kimi API"}
];
```

**Animation Strategy:**
- Pulsing duration based on actual processing time
- Fade after 1-2 seconds to avoid overwhelming
- Small counters increment/decrement near each node
- NO particle effects (too overwhelming at 100+ events/sec)

---

### **2. Chart Types**

#### **Events Over Time**
- **Type:** Multi-series line chart
- **Library:** Chart.js
- **Data:** Events per second for each connection type
- **Colors:** 
  - WebSocket: Blue (#3B82F6)
  - Redis: Red (#EF4444)
  - Supabase: Green (#10B981)
  - Kimi: Purple (#8B5CF6)
  - GLM: Orange (#F59E0B)
- **Features:** Zoom, pan, hover tooltips

#### **Response Times**
- **Type:** Combination line chart + histogram
- **Library:** Chart.js
- **Data:** 
  - Line: p50, p95, p99 response times over time
  - Histogram: Distribution of response times
- **Threshold bands:** 
  - Green: <200ms
  - Yellow: 200-500ms
  - Red: >500ms

#### **Data Transferred**
- **Type:** Stacked area chart
- **Library:** Chart.js
- **Data:** Cumulative bytes sent/received by service
- **Features:** Toggle between sent/received/total

#### **Error Rates**
- **Type:** Line chart with threshold bands
- **Library:** Chart.js
- **Data:** Error percentage over time
- **Alert markers:** Red dots for critical errors
- **Threshold:** 
  - Green: <1%
  - Yellow: 1-5%
  - Red: >5%

#### **Throughput**
- **Type:** Line chart with moving average
- **Library:** Chart.js
- **Data:** Requests per second
- **Moving average:** 5-minute window
- **Features:** Current vs max capacity indicator

#### **Token Usage** (AI APIs)
- **Type:** Dual-axis chart
- **Library:** Chart.js
- **Data:** 
  - Left axis: Token volume
  - Right axis: Estimated cost
- **Features:** Breakdown by model

---

### **3. System Health Indicator**

**Position:** Top center (most prominent)  
**Type:** Large color-coded status badge  
**States:**
- 🟢 **Healthy** (98-100%): All systems operational
- 🟡 **Degraded** (90-97%): Some issues detected
- 🔴 **Critical** (<90%): Major issues

**Calculation:**
```javascript
health_score = (
  (1 - error_rate) * 0.4 +
  (response_time < 500ms ? 1 : 0) * 0.3 +
  (active_connections > 0 ? 1 : 0) * 0.2 +
  (throughput > 0 ? 1 : 0) * 0.1
) * 100
```

---

### **4. Key Metrics Cards**

**Throughput Card:**
```
┌─────────────────┐
│ Throughput      │
│ 45 req/s        │
│ ▲ +12% vs 1h ago│
└─────────────────┘
```

**Active Connections Card:**
```
┌─────────────────┐
│ Connections     │
│ 12 active       │
│ WS:5 SB:4 RD:3  │
└─────────────────┘
```

**Error Rate Card:**
```
┌─────────────────┐
│ Error Rate      │
│ 0.8%            │
│ 🟢 Normal       │
└─────────────────┘
```

**Response Time Card:**
```
┌─────────────────┐
│ Response (p95)  │
│ 245ms           │
│ 🟢 Good         │
└─────────────────┘
```

---

## Color Scheme

### **Service Colors**
- WebSocket: `#3B82F6` (Blue)
- Redis: `#EF4444` (Red)
- Supabase: `#10B981` (Green)
- Kimi: `#8B5CF6` (Purple)
- GLM: `#F59E0B` (Orange)

### **Status Colors**
- Healthy: `#10B981` (Green)
- Warning: `#F59E0B` (Yellow/Amber)
- Critical: `#EF4444` (Red)
- Info: `#3B82F6` (Blue)
- Neutral: `#6B7280` (Gray)

### **Background**
- Primary: `#1F2937` (Dark gray)
- Secondary: `#111827` (Darker gray)
- Card: `#374151` (Medium gray)
- Border: `#4B5563` (Light gray)

---

## Performance Optimization

### **Update Frequency**
- **Charts:** 1-second updates (aggregate at 100ms for accuracy)
- **Data flow:** Real-time (throttled to 100ms)
- **Metrics cards:** 1-second updates
- **Recent events:** 2-second updates

### **Data Aggregation**
```javascript
// Backend aggregation strategy
function aggregateEvents(events, intervalMs = 1000) {
  const buckets = {};
  events.forEach(event => {
    const bucket = Math.floor(event.timestamp / intervalMs) * intervalMs;
    if (!buckets[bucket]) {
      buckets[bucket] = {
        count: 0,
        total_bytes: 0,
        errors: 0,
        response_times: []
      };
    }
    buckets[bucket].count++;
    buckets[bucket].total_bytes += event.data_size_bytes;
    if (event.error) buckets[bucket].errors++;
    if (event.response_time_ms) {
      buckets[bucket].response_times.push(event.response_time_ms);
    }
  });
  return buckets;
}
```

### **Data Decimation**
```javascript
// Adaptive sampling for historical data
function decimateData(data, maxPoints = 1000) {
  if (data.length <= maxPoints) return data;
  
  // Keep all data for last minute
  const oneMinuteAgo = Date.now() - 60000;
  const recent = data.filter(d => d.timestamp > oneMinuteAgo);
  const older = data.filter(d => d.timestamp <= oneMinuteAgo);
  
  // Decimate older data
  const step = Math.ceil(older.length / (maxPoints - recent.length));
  const decimated = older.filter((_, index) => index % step === 0);
  
  return [...decimated, ...recent];
}
```

### **Rendering Strategy**
- **Canvas:** High-frequency charts (line charts, area charts)
- **SVG:** Static elements (network graph nodes, icons)
- **Virtual scrolling:** Recent events table
- **Lazy loading:** Historical data on demand

---

## Implementation Phases

### **Phase 1: Core Dashboard** (Current Sprint)
1. ✅ Fix dashboard crashes
2. ✅ Fix timezone handling
3. ⚠️ Add Chart.js integration
4. ⚠️ Implement basic time-series charts
5. ⚠️ Add system health indicator

### **Phase 2: Data Flow Visualization** (Next Sprint)
1. Implement D3.js network graph
2. Add micro-animations
3. Implement hover states
4. Add real-time pulsing indicators

### **Phase 3: Advanced Features** (Future)
1. Historical data playback
2. Custom time range selection
3. Export functionality
4. Alert management
5. User preferences

---

## Next Steps

1. **Implement Chart.js integration** in `static/monitoring_dashboard.html`
2. **Add historical data endpoints** in `src/daemon/monitoring_endpoint.py`
3. **Create time-series charts** for events, response times, throughput
4. **Add system health indicator** with color-coded status
5. **Test with Playwright** to verify visual elements work correctly

---

**EXAI Recommendations Applied:**
- ✅ Three-tier layout with expandable sections
- ✅ Network graph for data flow visualization
- ✅ Multi-series charts for metrics
- ✅ Color-coded system health
- ✅ Performance optimization strategies
- ✅ Real-time updates with throttling

