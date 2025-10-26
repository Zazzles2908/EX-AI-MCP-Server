#!/usr/bin/env python3
"""
Check Redis Monitoring Data
Verifies that monitoring events are being persisted to Redis
"""

import redis
import json
import time
import os

def main():
    try:
        # Connect to Redis using environment variables
        # CRITICAL FIX (2025-10-24): Use environment variables instead of hardcoded 'redis'
        redis_host = os.getenv('REDIS_HOST', 'redis')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_password = os.getenv('REDIS_PASSWORD', '')

        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password if redis_password else None,
            decode_responses=True
        )
        
        print("=" * 60)
        print("REDIS MONITORING DATA CHECK")
        print("=" * 60)
        
        # Check each connection type
        connection_types = ['websocket', 'redis', 'supabase', 'kimi', 'glm']
        
        for conn_type in connection_types:
            event_key = f"connection_monitor:{conn_type}:events"
            stats_key = f"connection_monitor:{conn_type}:stats"
            
            # Get event count
            event_count = r.zcard(event_key)
            
            # Get stats
            stats = r.hgetall(stats_key)
            
            print(f"\n{conn_type.upper()}:")
            print(f"  Events in Redis: {event_count}")
            
            if event_count > 0:
                # Get latest event
                latest = r.zrevrange(event_key, 0, 0, withscores=True)
                if latest:
                    event_json, timestamp = latest[0]
                    event_data = json.loads(event_json)
                    print(f"  Latest event: {event_data.get('direction', 'unknown')} at {time.ctime(timestamp)}")
            
            if stats:
                print(f"  Stats: {len(stats)} fields")
                if 'total_events' in stats:
                    print(f"    Total events: {stats['total_events']}")
        
        print("\n" + "=" * 60)
        print("✅ Redis monitoring check complete")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error checking Redis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

