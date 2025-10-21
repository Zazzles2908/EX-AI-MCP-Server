# Phase 1: Implementation Plan (Days 3-5)
**Date**: 2025-10-18  
**Based on**: EXAI Consultation (2d0fb045-b73d-42e8-a4eb-faf6751a5052)  
**Status**: Ready for Implementation  
**Estimated Duration**: 3 days

---

## IMPLEMENTATION SEQUENCE

### Day 3: Circuit Breakers + Async Audit (Parallel)
**Duration**: 8 hours  
**Priority**: CRITICAL

#### Morning (4 hours): Circuit Breaker Implementation

**Step 1: Install Dependencies**
```bash
pip install pybreaker
# Update requirements.txt
```

**Step 2: Create CircuitBreakerManager**
File: `src/resilience/circuit_breaker_manager.py`

```python
import pybreaker
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class CircuitBreakerListener(pybreaker.CircuitBreakerListener):
    """Listener for circuit breaker state changes"""
    def __init__(self, service_name: str):
        self.service_name = service_name
    
    def state_change(self, breaker, old_state, new_state):
        logger.warning(f"Circuit breaker {self.service_name}: {old_state} -> {new_state}")
        # TODO: Add Prometheus metric update here

class CircuitBreakerManager:
    """Manages circuit breakers for all external services"""
    def __init__(self):
        self._breakers: Dict[str, pybreaker.CircuitBreaker] = {}
        self._initialize_breakers()
    
    def _initialize_breakers(self):
        # Redis circuit breaker
        self._breakers['redis'] = pybreaker.CircuitBreaker(
            fail_max=5,
            reset_timeout=60,
            listeners=[CircuitBreakerListener('redis')]
        )
        
        # Supabase circuit breaker
        self._breakers['supabase'] = pybreaker.CircuitBreaker(
            fail_max=3,
            reset_timeout=30,
            listeners=[CircuitBreakerListener('supabase')]
        )
        
        # Kimi API circuit breaker
        self._breakers['kimi'] = pybreaker.CircuitBreaker(
            fail_max=4,
            reset_timeout=120,
            listeners=[CircuitBreakerListener('kimi')]
        )
        
        # GLM API circuit breaker
        self._breakers['glm'] = pybreaker.CircuitBreaker(
            fail_max=4,
            reset_timeout=120,
            listeners=[CircuitBreakerListener('glm')]
        )
    
    def get_breaker(self, service_name: str) -> pybreaker.CircuitBreaker:
        """Get circuit breaker for a service"""
        return self._breakers.get(service_name)

# Singleton instance
circuit_breaker_manager = CircuitBreakerManager()
```

**Step 3: Apply to Redis Operations**
File: `utils/infrastructure/storage_backend.py`

Modify `RedisStorage` class methods:
- Lines 190-217: `get()` method
- Lines 163-188: `set_with_ttl()` method
- Lines 219-224: `delete()` method

```python
from src.resilience.circuit_breaker_manager import circuit_breaker_manager

class RedisStorage:
    def get(self, key: str):
        breaker = circuit_breaker_manager.get_breaker('redis')
        
        @breaker
        def _get_with_breaker():
            return self._client.get(key)
        
        try:
            return _get_with_breaker()
        except pybreaker.CircuitBreakerError:
            logger.error("Redis circuit breaker OPEN - service unavailable")
            return None  # Graceful degradation
```

**Step 4: Apply to Supabase Operations**
File: `src/storage/supabase_client.py`

Modify all database operations:
- Lines 240-278: `save_message()` method
- Lines 200-238: `save_conversation()` method

**Step 5: Apply to Kimi API Calls**
File: `src/providers/kimi_chat.py`

Wrap all API calls with Kimi circuit breaker

**Step 6: Apply to GLM API Calls**
File: `src/providers/glm_chat.py`

Wrap all API calls with GLM circuit breaker

#### Afternoon (4 hours): Async Blocking Audit

**Step 7: Comprehensive Async Audit**

Search patterns:
- `time.sleep` → Replace with `asyncio.sleep`
- `open(` → Replace with `aiofiles.open`
- Synchronous HTTP calls → Replace with async clients
- Database operations → Verify async implementation

**Files to Audit**:
1. `utils/infrastructure/storage_backend.py`
2. `src/providers/kimi_chat.py`
3. `src/providers/glm_chat.py`
4. `src/storage/supabase_client.py`
5. `src/daemon/ws_server.py`

**Document Findings**: Update `PHASE1_CODE_AUDIT_FINDINGS_2025-10-18.md`

---

### Day 4: Connection Limits + Rate Limiting + Async Fixes
**Duration**: 8 hours  
**Priority**: CRITICAL

#### Morning (4 hours): Connection Limits

**Step 1: Create ConnectionManager**
File: `src/daemon/connection_manager.py`

```python
import asyncio
from collections import defaultdict
from typing import Set
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections with limits"""
    def __init__(self, max_connections: int = 1000, max_per_ip: int = 10):
        self.active_connections: Set = set()
        self.max_connections = max_connections
        self.max_per_ip = max_per_ip
        self.connection_counts_by_ip = defaultdict(int)
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket, client_ip: str) -> bool:
        """Attempt to register a new connection"""
        async with self._lock:
            # Check global limit
            if len(self.active_connections) >= self.max_connections:
                logger.warning(f"Connection rejected: global limit reached ({self.max_connections})")
                await websocket.close(code=1013, reason="Server overloaded")
                return False
            
            # Check per-IP limit
            if self.connection_counts_by_ip[client_ip] >= self.max_per_ip:
                logger.warning(f"Connection rejected: IP {client_ip} limit reached ({self.max_per_ip})")
                await websocket.close(code=1008, reason="Too many connections from your IP")
                return False
            
            # Accept connection
            self.active_connections.add(websocket)
            self.connection_counts_by_ip[client_ip] += 1
            logger.info(f"Connection accepted: {len(self.active_connections)}/{self.max_connections}")
            return True
    
    async def disconnect(self, websocket, client_ip: str):
        """Unregister a connection"""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                self.connection_counts_by_ip[client_ip] -= 1
                logger.info(f"Connection closed: {len(self.active_connections)}/{self.max_connections}")
```

**Step 2: Integrate into ws_server.py**
File: `src/daemon/ws_server.py`

Modify `_serve_connection()` function (Lines 1139-1270):
- Add ConnectionManager initialization
- Add connection acceptance logic
- Add cleanup in finally block

**Step 3: Add Configuration**
File: `.env.docker`

```bash
MAX_CONNECTIONS=1000
MAX_CONNECTIONS_PER_IP=10
DEV_MAX_CONNECTIONS=100
```

#### Afternoon (4 hours): Rate Limiting

**Step 4: Create RateLimiter**
File: `src/resilience/rate_limiter.py`

```python
import time
from collections import defaultdict
import asyncio

class TokenBucket:
    """Token bucket rate limiter"""
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens"""
        async with self._lock:
            now = time.time()
            # Refill tokens
            self.tokens = min(
                self.capacity,
                self.tokens + (now - self.last_refill) * self.refill_rate
            )
            self.last_refill = now
            
            # Check if enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

class RateLimiter:
    """Multi-level rate limiter"""
    def __init__(self):
        self.global_bucket = TokenBucket(1000, 100)  # 1000 capacity, 100/sec refill
        self.ip_buckets = defaultdict(lambda: TokenBucket(100, 10))  # 100 capacity, 10/sec
        self.user_buckets = defaultdict(lambda: TokenBucket(50, 5))  # 50 capacity, 5/sec
    
    async def is_allowed(self, client_ip: str, user_id: str = None) -> bool:
        """Check if request is allowed"""
        # Check global limit
        if not await self.global_bucket.consume():
            return False
        
        # Check per-IP limit
        if not await self.ip_buckets[client_ip].consume():
            return False
        
        # Check per-user limit (if authenticated)
        if user_id and not await self.user_buckets[user_id].consume():
            return False
        
        return True
```

**Step 5: Integrate into ws_server.py**
Add rate limiting check in message loop (Lines 1250-1262)

**Step 6: Fix Async Blocking Issues**
Apply fixes identified in morning audit

---

### Day 5: API Key Security + Testing + Documentation
**Duration**: 8 hours  
**Priority**: CRITICAL

#### Morning (4 hours): API Key Security

**Step 1: Remove Keys from .env.docker**
```bash
# Remove all API keys from .env.docker
# Add to .gitignore if not already there
echo ".env.docker" >> .gitignore
```

**Step 2: Update Configuration Loading**
File: `src/config.py`

Ensure all keys loaded from environment variables only

**Step 3: Create .env.docker.template**
Create template file with empty placeholders

**Step 4: Document Secret Management**
Update README with instructions for setting environment variables

#### Afternoon (4 hours): Testing + QA

**Step 7: Present to EXAI for QA Review**
- Compile all changes made
- Document implementation details
- Request EXAI validation

**Step 8: Rebuild Docker Container**
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

**Step 9: Execute EXAI-Recommended Tests**
- Circuit breaker failure simulation
- Connection limit testing
- Rate limiting verification
- API key security validation

**Step 10: Report Results to EXAI**
- Share test results
- Get final validation
- Address any issues identified

**Step 11: Update Documentation**
- Update PRODUCTION_READINESS_ROADMAP_2025-10-18.md
- Mark Phase 1 as complete
- Document all scripts and changes

---

## TESTING CHECKLIST

### Circuit Breaker Tests
- [ ] Redis failure triggers circuit breaker
- [ ] Supabase failure triggers circuit breaker
- [ ] Kimi API failure triggers circuit breaker
- [ ] GLM API failure triggers circuit breaker
- [ ] Circuit breaker resets after timeout
- [ ] Graceful degradation when circuit open

### Connection Limit Tests
- [ ] Global connection limit enforced
- [ ] Per-IP connection limit enforced
- [ ] Graceful rejection with 503 status
- [ ] Connection cleanup on disconnect

### Rate Limiting Tests
- [ ] Global rate limit enforced
- [ ] Per-IP rate limit enforced
- [ ] Per-user rate limit enforced
- [ ] Rate limit headers in responses

### API Key Security Tests
- [ ] Keys not in .env.docker
- [ ] Keys loaded from environment
- [ ] No keys in git history (verify)

---

## FILES TO CREATE/MODIFY

### New Files
- `src/resilience/circuit_breaker_manager.py`
- `src/resilience/rate_limiter.py`
- `src/daemon/connection_manager.py`
- `.env.docker.template`

### Modified Files
- `utils/infrastructure/storage_backend.py` (Circuit breakers)
- `src/storage/supabase_client.py` (Circuit breakers)
- `src/providers/kimi_chat.py` (Circuit breakers)
- `src/providers/glm_chat.py` (Circuit breakers)
- `src/daemon/ws_server.py` (Connection limits + Rate limiting)
- `.env.docker` (Remove API keys)
- `requirements.txt` (Add pybreaker)

---

## SUCCESS CRITERIA

✅ All circuit breakers implemented and tested  
✅ Connection limits enforced and tested  
✅ Rate limiting active and tested  
✅ API keys secured (removed from .env.docker)  
✅ Async blocking issues identified and fixed  
✅ EXAI QA validation passed  
✅ Docker container rebuilt and tested  
✅ Documentation updated

---

**Status**: Ready for Day 3 Implementation  
**Next Action**: Install pybreaker and begin circuit breaker implementation  
**EXAI Consultation**: Continue with 2d0fb045-b73d-42e8-a4eb-faf6751a5052

