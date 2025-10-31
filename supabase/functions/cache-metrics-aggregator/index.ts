/**
 * Cache Metrics Aggregator - Supabase Edge Function
 * Date: 2025-10-31
 * Purpose: Week 2-3 Monitoring Phase - Real-time metrics aggregation and broadcasting
 * EXAI Consultation ID: c78bd85e-470a-4abb-8d0e-aeed72fab0a0
 * 
 * This Edge Function:
 * 1. Receives cache metrics from the monitoring endpoint
 * 2. Stores raw events in cache_metrics table
 * 3. Aggregates metrics into 1-minute windows
 * 4. Broadcasts aggregated metrics via Supabase Realtime
 * 5. Triggers AI Auditor for anomaly detection
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface CacheMetric {
  cache_key: string;
  operation_type: 'hit' | 'miss' | 'set' | 'evict' | 'error';
  implementation_type: 'legacy' | 'new';
  response_time_ms?: number;
  cache_size?: number;
  error_type?: string;
  error_message?: string;
  metadata?: Record<string, any>;
}

interface AggregatedMetrics {
  minute_window: string;
  implementation_type: 'legacy' | 'new';
  total_operations: number;
  hits: number;
  misses: number;
  sets: number;
  evictions: number;
  errors: number;
  avg_response_time_ms: number;
  p95_response_time_ms: number;
  max_response_time_ms: number;
  avg_cache_size: number;
  max_cache_size: number;
  hit_rate: number;
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Create Supabase client
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Parse request body
    const { metrics } = await req.json() as { metrics: CacheMetric[] }

    if (!metrics || !Array.isArray(metrics)) {
      return new Response(
        JSON.stringify({ error: 'Invalid metrics format' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Step 1: Store raw metrics (monitoring schema)
    const { error: insertError } = await supabase
      .schema('monitoring')
      .from('cache_metrics')
      .insert(metrics)

    if (insertError) {
      console.error('Failed to insert metrics:', insertError)
      return new Response(
        JSON.stringify({ error: 'Failed to store metrics', details: insertError }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Step 2: Aggregate metrics for current minute window
    const currentMinute = new Date()
    currentMinute.setSeconds(0, 0)
    const minuteWindow = currentMinute.toISOString()

    // Group metrics by implementation type
    const metricsByImpl = metrics.reduce((acc, metric) => {
      if (!acc[metric.implementation_type]) {
        acc[metric.implementation_type] = []
      }
      acc[metric.implementation_type].push(metric)
      return acc
    }, {} as Record<string, CacheMetric[]>)

    // Aggregate for each implementation type
    const aggregatedMetrics: AggregatedMetrics[] = []

    for (const [implType, implMetrics] of Object.entries(metricsByImpl)) {
      const hits = implMetrics.filter(m => m.operation_type === 'hit').length
      const misses = implMetrics.filter(m => m.operation_type === 'miss').length
      const sets = implMetrics.filter(m => m.operation_type === 'set').length
      const evictions = implMetrics.filter(m => m.operation_type === 'evict').length
      const errors = implMetrics.filter(m => m.operation_type === 'error').length

      const responseTimes = implMetrics
        .filter(m => m.response_time_ms !== undefined)
        .map(m => m.response_time_ms!)
        .sort((a, b) => a - b)

      const cacheSizes = implMetrics
        .filter(m => m.cache_size !== undefined)
        .map(m => m.cache_size!)

      const avgResponseTime = responseTimes.length > 0
        ? responseTimes.reduce((sum, t) => sum + t, 0) / responseTimes.length
        : 0

      const p95Index = Math.floor(responseTimes.length * 0.95)
      const p95ResponseTime = responseTimes.length > 0 ? responseTimes[p95Index] : 0

      const maxResponseTime = responseTimes.length > 0
        ? Math.max(...responseTimes)
        : 0

      const avgCacheSize = cacheSizes.length > 0
        ? cacheSizes.reduce((sum, s) => sum + s, 0) / cacheSizes.length
        : 0

      const maxCacheSize = cacheSizes.length > 0
        ? Math.max(...cacheSizes)
        : 0

      const hitRate = (hits + misses) > 0
        ? (hits / (hits + misses)) * 100
        : 0

      aggregatedMetrics.push({
        minute_window: minuteWindow,
        implementation_type: implType as 'legacy' | 'new',
        total_operations: implMetrics.length,
        hits,
        misses,
        sets,
        evictions,
        errors,
        avg_response_time_ms: Math.round(avgResponseTime * 100) / 100,
        p95_response_time_ms: p95ResponseTime,
        max_response_time_ms: maxResponseTime,
        avg_cache_size: Math.round(avgCacheSize),
        max_cache_size: maxCacheSize,
        hit_rate: Math.round(hitRate * 100) / 100
      })
    }

    // Step 3: Upsert aggregated metrics (monitoring schema)
    for (const aggMetrics of aggregatedMetrics) {
      const { error: upsertError } = await supabase
        .schema('monitoring')
        .from('cache_metrics_1min')
        .upsert(aggMetrics, {
          onConflict: 'minute_window,implementation_type'
        })

      if (upsertError) {
        console.error('Failed to upsert aggregated metrics:', upsertError)
      }
    }

    // Step 4: Broadcast metrics via Supabase Realtime
    const channel = supabase.channel('cache-metrics')
    
    for (const aggMetrics of aggregatedMetrics) {
      await channel.send({
        type: 'broadcast',
        event: 'cache-update',
        payload: aggMetrics
      })
    }

    // Step 5: Check for anomalies and trigger AI Auditor
    await checkAnomalies(supabase, aggregatedMetrics)

    return new Response(
      JSON.stringify({
        success: true,
        metrics_stored: metrics.length,
        aggregations_created: aggregatedMetrics.length
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Error processing metrics:', error)
    return new Response(
      JSON.stringify({ error: 'Internal server error', details: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

/**
 * Check for anomalies and create AI Auditor observations
 */
async function checkAnomalies(supabase: any, metrics: AggregatedMetrics[]) {
  for (const metric of metrics) {
    // Get baseline metrics (monitoring schema)
    const { data: baseline } = await supabase
      .schema('monitoring')
      .from('cache_baseline_metrics')
      .select('*')
      .eq('implementation_type', metric.implementation_type)
      .eq('is_active', true)
      .single()

    if (!baseline) {
      // No baseline yet, skip anomaly detection
      continue
    }

    const observations = []

    // Check hit rate deviation
    const hitRateDeviation = ((metric.hit_rate - baseline.baseline_hit_rate) / baseline.baseline_hit_rate) * 100
    if (Math.abs(hitRateDeviation) > 10) {
      observations.push({
        severity: Math.abs(hitRateDeviation) > 20 ? 'critical' : 'warning',
        category: 'performance',
        title: `Cache hit rate ${hitRateDeviation > 0 ? 'increased' : 'decreased'} significantly`,
        description: `Hit rate is ${metric.hit_rate.toFixed(2)}% (baseline: ${baseline.baseline_hit_rate.toFixed(2)}%), deviation: ${hitRateDeviation.toFixed(2)}%`,
        recommendation: hitRateDeviation < 0 
          ? 'Investigate cache eviction patterns and consider increasing cache size'
          : 'Monitor for sustained improvement',
        implementation_type: metric.implementation_type,
        metric_name: 'hit_rate',
        metric_value: metric.hit_rate,
        baseline_value: baseline.baseline_hit_rate,
        deviation_percentage: hitRateDeviation
      })
    }

    // Check response time deviation
    const responseTimeDeviation = ((metric.avg_response_time_ms - baseline.baseline_avg_response_time_ms) / baseline.baseline_avg_response_time_ms) * 100
    if (responseTimeDeviation > 25) {
      observations.push({
        severity: responseTimeDeviation > 50 ? 'critical' : 'warning',
        category: 'performance',
        title: 'Cache response time increased significantly',
        description: `Average response time is ${metric.avg_response_time_ms.toFixed(2)}ms (baseline: ${baseline.baseline_avg_response_time_ms.toFixed(2)}ms), deviation: ${responseTimeDeviation.toFixed(2)}%`,
        recommendation: 'Investigate cache contention, network latency, or Redis performance',
        implementation_type: metric.implementation_type,
        metric_name: 'avg_response_time_ms',
        metric_value: metric.avg_response_time_ms,
        baseline_value: baseline.baseline_avg_response_time_ms,
        deviation_percentage: responseTimeDeviation
      })
    }

    // Check error rate
    const errorRate = (metric.errors / metric.total_operations) * 100
    if (errorRate > 1) {
      observations.push({
        severity: errorRate > 5 ? 'critical' : 'warning',
        category: 'reliability',
        title: 'Elevated cache error rate detected',
        description: `Error rate is ${errorRate.toFixed(2)}% (${metric.errors} errors in ${metric.total_operations} operations)`,
        recommendation: 'Check cache logs for error details and investigate root cause',
        implementation_type: metric.implementation_type,
        metric_name: 'error_rate',
        metric_value: errorRate,
        baseline_value: baseline.baseline_error_rate,
        deviation_percentage: ((errorRate - baseline.baseline_error_rate) / baseline.baseline_error_rate) * 100
      })
    }

    // Insert observations (monitoring schema)
    if (observations.length > 0) {
      await supabase
        .schema('monitoring')
        .from('cache_auditor_observations')
        .insert(observations)
    }
  }
}

