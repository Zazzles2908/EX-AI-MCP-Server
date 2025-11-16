# 🐳 FIX AGENT 3: DOCKER & SYSTEM ARCHITECTURE REMEDIATION

**Agent Type:** DevOps/SRE Specialist & Container Security Engineer  
**Priority:** P0 (Critical)  
**Estimated Time:** 2-3 weeks  
**Scope:** Docker Infrastructure, Container Security, System Architecture  

---

## 🎯 MISSION OBJECTIVE

Fix critical Docker infrastructure issues, security vulnerabilities, container orchestration problems, and system architecture inconsistencies to achieve production-grade containerized deployment with enterprise security standards.

---

## 🚨 CRITICAL ISSUES IDENTIFIED

### 1. HARDCODED SECRETS IN DOCKER FILES (P0-CRITICAL)
**Location:** `docker-compose.yml`, `.env.docker`  
**Impact:** SECURITY BREACH RISK - Exposed credentials in configuration

**Current Vulnerabilities:**
```yaml
# docker-compose.yml - PROBLEMATIC
services:
  exai-mcp-server:
    environment:
      - GLM_API_KEY=95c42879e5c247beb7d9d30f3ba7b28f.uA2184L5axjigykH
      - KIMI_API_KEY=sk-AbCh3IrxmB5Bsx4JV0pnoqb0LajNdkwFvxfwR8KpDXB66qyB
      - REDIS_PASSWORD=ExAi2025RedisSecurePass123
    # EXPOSED: All API keys visible in plain text

# .env.docker - PROBLEMATIC  
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
REDIS_PASSWORD=ExAi2025RedisSecurePass123
```

**Required Security Fixes:**
```yaml
# docker-compose.yml - SECURE
services:
  exai-mcp-server:
    environment:
      - GLM_API_KEY_FILE=/run/secrets/glm_api_key
      - KIMI_API_KEY_FILE=/run/secrets/kimi_api_key  
      - MINIMAX_API_KEY_FILE=/run/secrets/minimax_api_key
      - REDIS_PASSWORD_FILE=/run/secrets/redis_password
    secrets:
      - glm_api_key
      - kimi_api_key
      - minimax_api_key
      - redis_password

secrets:
  glm_api_key:
    external: true
  kimi_api_key:
    external: true
  minimax_api_key:
    external: true
  redis_password:
    external: true
```

### 2. MISSING CONTAINER HEALTH CHECKS (P0-CRITICAL)
**Location:** `Dockerfile`, `docker-compose.yml`  
**Impact:** No visibility into container health, unable to detect failures

**Current Health Check Issues:**
```dockerfile
# Dockerfile - PROBLEMATIC
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD echo "healthy" > /tmp/health || exit 1
# ISSUE: Cosmetic check, doesn't verify actual service
```

**Required Health Check Fixes:**
```dockerfile
# Dockerfile - FIXED
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Or for stdio service:
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:3001/health')" || exit 1
```

### 3. REDIS DEPENDENCY CYCLE (P1-HIGH)
**Location:** `docker-compose.yml` dependency configuration  
**Impact:** Potential startup failures, unpredictable service initialization

**Current Problem:**
```yaml
# Services wait for Redis which waits for services to start
services:
  exai-mcp-server:
    depends_on:
      - redis
      # But Redis healthcheck might not be ready when service starts
  
  redis:
    command: redis-server --requirepass $(REDIS_PASSWORD)
    # Password requires environment variables to be set
```

**Required Fix:**
```yaml
# docker-compose.yml - FIXED
services:
  exai-mcp-server:
    depends_on:
      redis:
        condition: service_healthy
        restart: true
  
  redis:
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 30s
    environment:
      - REDIS_PASSWORD_FILE=/run/secrets/redis_password
```

### 4. CROSS-PLATFORM VOLUME MOUNTING (P1-HIGH)
**Location:** `docker-compose.yml` volume mounts  
**Impact:** Windows paths break on Linux systems, non-portable

**Current Issue:**
```yaml
# docker-compose.yml - PROBLEMATIC
services:
  exai-mcp-server:
    volumes:
      - type: bind
        source: c:\Project\exai-logs:/app/logs
        # ISSUE: Windows-specific path breaks on Linux
        # ISSUE: Hardcoded host path not portable
```

**Required Fix:**
```yaml
# docker-compose.yml - FIXED
services:
  exai-mcp-server:
    volumes:
      - type: volume
        source: exai_logs
        target: /app/logs
      - type: volume  
        source: exai_data
        target: /app/data

volumes:
  exai_logs:
    driver: local
  exai_data:
    driver: local

# For development, use environment variable:
# export EXAI_HOST_PATH=/path/to/local/logs
# docker-compose uses: ${EXAI_HOST_PATH:-./logs}
```

### 5. NETWORK SECURITY ISSUES (P1-HIGH)
**Location:** `docker-compose.yml` network configuration  
**Impact:** Redis exposed to host network, increased attack surface

**Current Issues:**
```yaml
# docker-compose.yml - PROBLEMATIC
services:
  redis:
    ports:
      - "6379:6379"  # EXPOSED: Direct host access
    networks:
      - default      # Using default bridge
```

**Required Security Fixes:**
```yaml
# docker-compose.yml - SECURE
networks:
  exai_internal:
    driver: bridge
    internal: false  # Allow outbound internet
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  redis:
    networks:
      - exai_internal  # Isolate from default network
    # No port mapping - internal network only
    
  exai-mcp-server:
    networks:
      - exai_internal
    # Access Redis via service name: redis:6379
```

### 6. ARCHITECTURAL INCONSISTENCIES (P1-HIGH)
**Location:** Service configurations, Dockerfile vs compose  
**Impact:** Unpredictable behavior, maintenance complexity

**Current Issues:**
```dockerfile
# Dockerfile
CMD ["python", "-m", "src.daemon.ws_server"]
# But docker-compose overrides with:
command: python -m src.daemon.ws_server --port 8079 --log-level info
```

**Required Consistency:**
```dockerfile
# Dockerfile - CONSISTENT
CMD ["python", "-m", "src.server", "--transport", "ws"]

# docker-compose.yml - CONSISTENT
command: python -m src.server --transport stdio --port 3001
# vs
command: python -m src.server --transport ws --port 8079
```

---

## 🏗️ IMPLEMENTATION PLAN

### Phase 1: Security Hardening (Week 1)

#### Step 1: Secret Management Implementation
```bash
# 1. Create secrets in Docker Swarm/Secrets
echo "$GLM_API_KEY" | docker secret create glm_api_key -
echo "$KIMI_API_KEY" | docker secret create kimi_api_key -
echo "$MINIMAX_API_KEY" | docker secret create minimax_api_key -
echo "$REDIS_PASSWORD" | docker secret create redis_password -

# 2. Update docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

secrets:
  glm_api_key:
    external: true
  kimi_api_key:
    external: true
  minimax_api_key:
    external: true
  redis_password:
    external: true

services:
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass $(cat /run/secrets/redis_password)
    secrets:
      - redis_password
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    networks:
      - exai_internal

  exai-mcp-server:
    build: .
    environment:
      - GLM_API_KEY_FILE=/run/secrets/glm_api_key
      - KIMI_API_KEY_FILE=/run/secrets/kimi_api_key
      - MINIMAX_API_KEY_FILE=/run/secrets/minimax_api_key
    secrets:
      - glm_api_key
      - kimi_api_key
      - minimax_api_key
    volumes:
      - exai_logs:/app/logs
      - exai_data:/app/data
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - exai_internal

volumes:
  redis_data:
  exai_logs:
  exai_data:

networks:
  exai_internal:
    driver: bridge
EOF
```

#### Step 2: Container Security Implementation
```dockerfile
# Dockerfile - SECURE VERSION
FROM python:3.11-slim as builder

# Security: Create non-root user
RUN groupadd -r exai && useradd -r -g exai exai

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set security constraints
RUN echo "exai ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Copy installed packages
COPY --from=builder /root/.local /home/exai/.local

# Create app directory and set ownership
RUN mkdir -p /app/logs /app/data && \
    chown -R exai:exai /app

# Switch to non-root user
USER exai
WORKDIR /app

# Copy application code
COPY --chown=exai:exai . .

# Set PATH for local packages
ENV PATH=/home/exai/.local/bin:$PATH

# Security: Remove unnecessary tools
RUN sudo apt-get remove -y sudo && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["python", "-m", "src.server", "--transport", "ws", "--port", "8080"]
```

#### Step 3: Network Security Configuration
```yaml
# docker-compose.yml - Network Security
networks:
  exai_internal:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1
          ip_range: 172.20.0.0/24
    driver_opts:
      com.docker.network.bridge.name: exai-br0
      com.docker.network.bridge.enable_ip_masquerade: "true"
      com.docker.network.driver.mtu: "1500"

  exai_frontend:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.21.0.0/16
          gateway: 172.21.0.1
    driver_opts:
      com.docker.network.driver.mtu: "1500"
```

### Phase 2: Infrastructure Improvements (Week 2)

#### Step 1: Cross-Platform Volume Strategy
```yaml
# docker-compose.yml - Cross-Platform Volumes
volumes:
  exai_logs:
    driver: local
    driver_opts:
      type: none
      device: ${EXAI_LOG_PATH:-./logs}
      o: bind

  exai_data:
    driver: local
    driver_opts:
      type: none
      device: ${EXAI_DATA_PATH:-./data}
      o: bind

  redis_data:
    driver: local
```

```bash
# .env.example - Environment template
# Copy to .env and update for your environment
EXAI_LOG_PATH=/path/to/logs
EXAI_DATA_PATH=/path/to/data
EXAI_HOST_PATH=/path/to/host/mounts

# Development settings
COMPOSE_PROJECT_NAME=exai-dev

# Production settings
COMPOSE_PROFILES=production
```

#### Step 2: Health Check Implementation
```python
# src/health/health_checker.py
import aiohttp
import asyncio
import redis
import logging

logger = logging.getLogger(__name__)

class ComprehensiveHealthChecker:
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance"""
        try:
            r = redis.Redis(
                host='redis',
                port=6379,
                password=None,  # Use secrets file
                decode_responses=True
            )
            
            # Test basic operations
            start_time = asyncio.get_event_loop().time()
            r.ping()
            latency = asyncio.get_event_loop().time() - start_time
            
            info = r.info()
            return {
                "status": "healthy",
                "latency_ms": round(latency * 1000, 2),
                "connections": info.get("connected_clients", 0),
                "memory_usage": info.get("used_memory_human", "unknown")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_mcp_server(self) -> Dict[str, Any]:
        """Check MCP server health endpoints"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check main server
                async with session.get('http://localhost:8080/health') as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {"status": "healthy", "server": data}
                    else:
                        return {"status": "unhealthy", "status_code": resp.status}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def check_ai_providers(self) -> Dict[str, Any]:
        """Check AI provider connectivity"""
        providers_status = {}
        
        # Test each provider
        for provider in ["glm", "kimi", "minimax"]:
            try:
                # Implement provider health check
                providers_status[provider] = {"status": "healthy"}
            except Exception as e:
                providers_status[provider] = {
                    "status": "unhealthy", 
                    "error": str(e)
                }
        
        return providers_status
```

```dockerfile
# Dockerfile - Enhanced Health Checks
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=3 \
  CMD python -c "
import sys
import asyncio
import json
from src.health.health_checker import ComprehensiveHealthChecker

async def main():
    checker = ComprehensiveHealthChecker()
    redis_health = await checker.check_redis()
    mcp_health = await checker.check_mcp_server()
    
    if redis_health['status'] != 'healthy':
        print(f'Redis unhealthy: {redis_health}')
        sys.exit(1)
        
    if mcp_health['status'] != 'healthy':
        print(f'MCP server unhealthy: {mcp_health}')
        sys.exit(1)
        
    print('All checks passed')

asyncio.run(main())
  " || exit 1
```

#### Step 3: Restart Policy Optimization
```yaml
# docker-compose.yml - Optimized Restart Policies
services:
  redis:
    restart: unless-stopped  # Critical service
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 30s

  exai-mcp-server:
    restart: on-failure:3  # Retry 3 times on failure
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  exai-mcp-stdio:
    restart: on-failure:3
    depends_on:
      redis:
        condition: service_healthy

  redis-commander:
    restart: unless-stopped  # Management tool
    profiles:
      - management
```

### Phase 3: Monitoring & Observability (Week 3)

#### Step 1: Logging Strategy
```yaml
# docker-compose.yml - Centralized Logging
services:
  exai-mcp-server:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=exai-mcp-server"
    
    labels:
      - "logging=promtail"
      - "monitoring=enabled"

  # Add Promtail for log aggregation
  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log:ro
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml
    networks:
      - exai_internal
    profiles:
      - monitoring
```

#### Step 2: Resource Management
```yaml
# docker-compose.yml - Resource Limits
services:
  redis:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
    
  exai-mcp-server:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M
    
    # Add memory optimization
    environment:
      - PYTHONUNBUFFERED=1
      - MALLOC_TRIM_THRESHOLD_=131072
```

---

## 🧪 VALIDATION & TESTING

### Container Security Tests
```bash
# tests/security/test_container_security.sh
#!/bin/bash

echo "🔒 Running Container Security Tests..."

# Test 1: Non-root user
echo "Testing non-root user execution..."
docker run --rm exai-mcp-server whoami
# Should output: exai

# Test 2: No secrets in image
echo "Testing secrets are not baked into image..."
docker run --rm exai-mcp-server env | grep -i api_key
# Should be empty

# Test 3: Health check functionality
echo "Testing health check..."
timeout 60s docker run --rm --health-cmd="curl -f http://localhost:8080/health" --health-interval=5s --health-timeout=5s --health-retries=3 exai-mcp-server
echo "✅ Container security tests passed"
```

### Infrastructure Tests
```python
# tests/infrastructure/test_docker_deployment.py
import pytest
import docker
import subprocess
import time

class TestDockerInfrastructure:
    
    @pytest.fixture(scope="class")
    def docker_client(self):
        return docker.from_env()
    
    def test_container_startup(self, docker_client):
        """Test all containers start successfully"""
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        time.sleep(30)  # Wait for startup
        
        # Check Redis
        redis_container = docker_client.containers.get("exai-redis-1")
        assert redis_container.status == "running"
        
        # Check MCP server
        mcp_container = docker_client.containers.get("exai-exai-mcp-server-1")
        assert mcp_container.status == "running"
        
        # Check health
        result = subprocess.run([
            "docker", "exec", "exai-exai-mcp-server-1", 
            "curl", "-f", "http://localhost:8080/health"
        ], capture_output=True, text=True)
        assert result.returncode == 0
    
    def test_secrets_are_external(self):
        """Test secrets are loaded from Docker secrets"""
        result = subprocess.run([
            "docker", "inspect", "exai-exai-mcp-server-1",
            "--format", "{{.HostConfig.Secrets}}"
        ], capture_output=True, text=True)
        
        assert "glm_api_key" in result.stdout
        assert "kimi_api_key" in result.stdout
        assert "minimax_api_key" in result.stdout
    
    def test_network_isolation(self):
        """Test network isolation"""
        result = subprocess.run([
            "docker", "network", "inspect", "exai-docker_exai_internal"
        ], capture_output=True, text=True)
        
        import json
        network_info = json.loads(result.stdout)
        assert len(network_info[0]["Containers"]) > 0
        
        # Redis should not be accessible from host
        result = subprocess.run([
            "docker", "exec", "exai-exai-mcp-server-1", 
            "ping", "-c", "1", "redis"
        ], capture_output=True)
        assert result.returncode == 0  # Should work internally
```

### Load Testing
```python
# tests/performance/test_container_performance.py
import asyncio
import aiohttp
import time

class TestContainerPerformance:
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test container handles concurrent requests"""
        async def make_request(session):
            async with session.get('http://localhost:8080/health') as resp:
                return resp.status
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            tasks = [make_request(session) for _ in range(100)]
            results = await asyncio.gather(*tasks)
            end_time = time.time()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        
        # Should complete within reasonable time
        total_time = end_time - start_time
        assert total_time < 10, f"100 requests took {total_time:.2f}s, should be <10s"
```

---

## 🎯 SUCCESS CRITERIA

### Security Compliance
- [ ] All secrets externalized to Docker secrets
- [ ] Non-root user execution enforced
- [ ] No hardcoded credentials in any files
- [ ] Network isolation implemented
- [ ] Container security profiles applied

### Infrastructure Quality
- [ ] All containers have proper health checks
- [ ] Cross-platform volume mounting works
- [ ] Redis dependency cycle resolved
- [ ] Consistent service architectures
- [ ] Proper restart policies implemented

### Monitoring & Observability
- [ ] Centralized logging configured
- [ ] Health check monitoring active
- [ ] Resource limits properly set
- [ ] Performance benchmarks validated
- [ ] Container orchestration stable

### Production Readiness
- [ ] Zero security vulnerabilities
- [ ] Sub-10s startup times
- [ ] 99.9% availability target
- [ ] Horizontal scaling support
- [ ] Disaster recovery plan

---

## 🚀 DEPLOYMENT STRATEGY

### Phase 1: Security Hardening
1. Implement Docker secrets
2. Update Dockerfile for non-root
3. Configure network isolation
4. Test security measures

### Phase 2: Infrastructure Updates
1. Fix health checks
2. Implement cross-platform volumes
3. Resolve dependency cycles
4. Update restart policies

### Phase 3: Monitoring Setup
1. Configure centralized logging
2. Set up health monitoring
3. Implement performance tracking
4. Create alerting rules

### Phase 4: Production Deployment
1. Deploy to staging environment
2. Run comprehensive tests
3. Performance optimization
4. Production rollout

---

**FIX AGENT 3 DELIVERABLES:**
- Enterprise-grade container security
- Cross-platform Docker deployment
- Comprehensive monitoring setup
- Production-ready infrastructure
- Complete security compliance
- Automated testing suite

**Ready for implementation when all P0/P1 issues are resolved!**
