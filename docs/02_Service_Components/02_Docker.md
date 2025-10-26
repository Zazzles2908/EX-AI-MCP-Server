# Docker Containerization

## Purpose & Responsibility

This component provides containerization for the EXAI MCP Server using Docker's multi-stage build process and Docker Compose for orchestration.

## Multi-stage Builds

### Build Stages
```dockerfile
# Stage 1: Dependencies
FROM python:3.11-slim as dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim as production
WORKDIR /app
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .

# Security: Non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8079/health || exit 1
```

### Benefits
- Reduced final image size (by ~60% compared to single-stage)
- Faster builds (dependency caching)
- Improved security (no build tools in production)

## Docker Compose Orchestration

### Configuration
```yaml
version: '3.8'
services:
  exai-mcp-server:
    build:
      context: .
      target: production
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - KIMI_API_KEY=${KIMI_API_KEY}
      - GLM_API_KEY=${GLM_API_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config:ro
    ports:
      - "8079:8079"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8079/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Service Dependencies
```yaml
services:
  exai-mcp-server:
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
```

## Volume Mounts

### Data Persistence
```yaml
volumes:
  - ./data:/app/data:rw          # Read-write for data storage
  - ./logs:/app/logs:rw          # Read-write for logs
  - ./config:/app/config:ro      # Read-only for configuration
```

### Volume Types
- **Bind Mounts**: For configuration and local development
- **Named Volumes**: For persistent data storage
- **Tmpfs**: For temporary files in production

## Environment Variables

### Required Variables
```bash
# AI Provider API Keys
KIMI_API_KEY=your_kimi_api_key
GLM_API_KEY=your_glm_api_key

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
AUTH_TOKEN=your_auth_token

# WebSocket Configuration
WS_PORT=8079
WS_HOST=0.0.0.0
```

### Configuration Loading
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    KIMI_API_KEY = os.getenv('KIMI_API_KEY')
    GLM_API_KEY = os.getenv('GLM_API_KEY')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    WS_PORT = int(os.getenv('WS_PORT', 8079))
```

## Production Deployment

### Image Optimization
```dockerfile
# Security Scanning
RUN pip install safety && safety check

# Non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8079/health || exit 1
```

### Resource Limits
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

## Key Files & Their Roles

```
.
├── Dockerfile                    # Multi-stage build definition
├── docker-compose.yml            # Service orchestration
├── .dockerignore                 # Files to exclude from build
├── .env.docker                   # Environment variables
└── scripts/
    ├── docker-build.sh           # Build script
    └── docker-run.sh             # Run script
```

## Usage Examples

### Building the Image

```bash
# Build production image
docker build -t exai-mcp-server:latest .

# Build with specific target
docker build --target production -t exai-mcp-server:prod .
```

### Running with Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f exai-mcp-server

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Running Standalone Container

```bash
# Run with environment file
docker run -d \
  --name exai-mcp-server \
  --env-file .env.docker \
  -p 8079:8079 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  exai-mcp-server:latest
```

## Common Issues & Solutions

### Issue: Image Size Too Large
**Solution**: Use multi-stage builds and .dockerignore to exclude unnecessary files.

```dockerfile
# .dockerignore
__pycache__
*.pyc
*.pyo
.git
.venv
tests/
docs/
```

### Issue: Permission Denied
**Solution**: Ensure volumes have correct permissions for non-root user.

```bash
# Fix permissions
chmod -R 755 ./data ./logs
chown -R 1000:1000 ./data ./logs
```

### Issue: Port Already in Use
**Solution**: Change port mapping in docker-compose.yml or stop conflicting service.

```yaml
ports:
  - "8080:8079"  # Map to different host port
```

## Best Practices

1. **Security**
   - Always run as non-root user
   - Use secrets management for sensitive data
   - Scan images for vulnerabilities regularly

2. **Performance**
   - Use multi-stage builds to reduce image size
   - Leverage build cache effectively
   - Use .dockerignore to exclude unnecessary files

3. **Monitoring**
   - Implement health checks
   - Configure resource limits
   - Use logging drivers for centralized logging

4. **Development**
   - Use volume mounts for hot-reloading
   - Separate development and production configurations
   - Use docker-compose for local development

## Integration Points

- **MCP Server**: Runs inside container on port 8079
- **Supabase**: Connects via environment variables
- **AI Providers**: Accesses via API keys in environment
- **Monitoring**: Exposes health check endpoint

