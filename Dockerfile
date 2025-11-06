# EXAI MCP Server - Docker Image
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (optimized for layer caching)
# Upgrade pip first for better dependency resolution
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Add /app to PYTHONPATH so imports work
ENV PYTHONPATH=/app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ ./src/
COPY tools/ ./tools/
COPY utils/ ./utils/
# COPY systemprompts/ ./systemprompts/  # REMOVED - directory doesn't exist (prompts are in src/prompts)
COPY configurations/ ./configurations/
# COPY streaming/ ./streaming/  # REMOVED - directory doesn't exist (2025-11-02)
COPY scripts/ws/ ./scripts/ws/
COPY scripts/runtime/ ./scripts/runtime/
COPY static/ ./static/
COPY server.py ./
# config.py is deprecated - configuration moved to config/ package
COPY config/ ./config/
COPY .env.docker .env

# Create logs directory
RUN mkdir -p logs

# Expose WebSocket port
EXPOSE 8079

# Health check - Comprehensive Supabase + WebSocket validation
# Validates: Supabase connectivity, database access, storage, WebSocket daemon
# Interval: 30s (frequent enough to detect issues quickly)
# Timeout: 5s (fast response requirement)
# Start-period: 60s (allows Supabase connections to initialize)
# Retries: 3 (allows for transient network issues)
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python scripts/runtime/health_check.py || exit 1

# Set environment variables
# CRITICAL FIX (2025-11-01): Removed LOG_LEVEL=INFO hardcode
# - Previously hardcoded LOG_LEVEL=INFO overrode .env.docker settings
# - Now LOG_LEVEL is read from .env.docker (mounted as .env in container)
# - This allows proper configuration via environment files
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    EXAI_WS_HOST=0.0.0.0 \
    EXAI_WS_PORT=8079

# Run daemon
CMD ["python", "-u", "scripts/ws/run_ws_daemon.py"]

