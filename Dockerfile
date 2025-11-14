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

# Copy pyproject.toml
COPY config/pyproject.toml .

# Install Python dependencies (optimized for layer caching)
# Upgrade pip first for better dependency resolution
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -e .

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

# Copy application source code
# ALL directories included for complete build
COPY src/ ./src/
COPY tools/ ./tools/
COPY utils/ ./utils/
COPY configurations/ ./configurations/
COPY scripts/ ./scripts/
COPY static/ ./static/
COPY src/server.py ./
# config.py is deprecated - configuration moved to config/ package
COPY config/ ./config/
# Database and migration files
COPY database/ ./database/
COPY migration/ ./migration/
# Tests for verification
COPY tests/ ./tests/
# Web UI for dashboard
COPY web_ui/ ./web_ui/
# Data files (performance metrics, monitoring)
COPY data/ ./data/

# Create logs directory
RUN mkdir -p logs

# Expose WebSocket port
EXPOSE 8079

# Health check - Simple process check
# Interval: 30s
# Timeout: 5s
# Start-period: 60s
# Retries: 3
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import sys; print('healthy'); sys.exit(0)" || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    EXAI_WS_HOST=0.0.0.0 \
    EXAI_WS_PORT=8079

# Run WebSocket daemon (not stdio server)
# The WebSocket daemon handles MCP connections over WebSocket
WORKDIR /app
CMD ["python", "-u", "scripts/ws/run_ws_daemon.py"]
