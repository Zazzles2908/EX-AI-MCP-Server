# EX-AI MCP Server - Development Setup Guide

This guide will help you set up the EX-AI MCP Server for local development.

## Prerequisites

- **Docker Desktop** installed and running
- **Git** installed
- **API Keys** for:
  - Kimi (Moonshot AI) - Get from: https://platform.moonshot.cn/
  - GLM (ZhipuAI) - Get from: https://open.bigmodel.cn/
  - Supabase - Get from: https://supabase.com/dashboard

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd EX-AI-MCP-Server
```

### 2. Set Up Environment Variables

The project uses environment files to configure API keys and settings. **These files contain sensitive information and are NOT tracked in git.**

#### Step 2.1: Create `.env.docker`

```bash
# Copy the template
cp .env.docker.template .env.docker
```

#### Step 2.2: Add Your API Keys

Open `.env.docker` in your text editor and replace the placeholders with your actual API keys:

```bash
# Find these lines and replace with your actual keys:
KIMI_API_KEY=your_kimi_api_key_here          # Replace with your Kimi API key
GLM_API_KEY=your_glm_api_key_here            # Replace with your GLM API key
ZHIPUAI_API_KEY=your_glm_api_key_here        # Same as GLM_API_KEY (legacy)

# Supabase credentials
SUPABASE_URL=https://your-project.supabase.co                    # Your Supabase project URL
SUPABASE_ANON_KEY=your_supabase_anon_key_here                   # Your Supabase anon key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here   # Your Supabase service role key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret_here               # Your Supabase JWT secret
SUPABASE_PROJECT_ID=your_project_id                             # Your Supabase project ID
SUPABASE_KEY=your_supabase_anon_key_here                        # Same as SUPABASE_ANON_KEY (legacy)
```

#### Step 2.3: Configure Supabase (Optional)

If you're working with Supabase Edge Functions, also configure `supabase/.env.supabase`:

```bash
# This file should already exist, but if not:
cd supabase
cp .env.supabase.template .env.supabase  # If template exists
# Or create it manually with the same Supabase credentials
```

### 3. Build and Run

```bash
# Build the Docker container
docker-compose build

# Start the server
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 4. Verify Setup

The server should be running on:
- **WebSocket**: `ws://localhost:8079`
- **Redis Commander**: `http://localhost:8081`

Test the connection:
```bash
# Check if the server is responding
curl http://localhost:8079/health
```

## Important Security Notes

⚠️ **NEVER commit files with actual API keys to git!**

The following files are automatically ignored by git (see `.gitignore`):
- `.env.docker` - Your actual environment configuration
- `supabase/.env.supabase` - Supabase-specific configuration
- `.env.*.local` - Any local environment overrides

**What IS tracked in git:**
- `.env.docker.template` - Template with placeholders
- `.env.example` - Example configuration structure
- This `SETUP.md` file

## Getting API Keys

### Kimi (Moonshot AI)

1. Visit: https://platform.moonshot.cn/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

### GLM (ZhipuAI)

1. Visit: https://open.bigmodel.cn/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (format: `xxxxxxxx.xxxxxxxx`)

### Supabase

1. Visit: https://supabase.com/dashboard
2. Select your project (or create a new one)
3. Go to: **Project Settings** → **API**
4. Copy the following:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_ANON_KEY` and `SUPABASE_KEY`
   - **service_role** key → `SUPABASE_SERVICE_ROLE_KEY`
5. Go to: **Project Settings** → **API** → **JWT Settings**
   - Copy **JWT Secret** → `SUPABASE_JWT_SECRET`
6. Your project ID is in the URL: `https://supabase.com/dashboard/project/<project-id>`

## Configuration Options

The `.env.docker` file contains many configuration options. Key settings:

### Model Configuration
```bash
DEFAULT_MODEL=glm-4.5-flash              # Default model for all tools
ROUTER_ENABLED=true                      # Enable intelligent model routing
GLM_ENABLE_WEB_BROWSING=true            # Enable GLM web search
```

### Connection Limits (Phase 1 - Production Readiness)
```bash
MAX_CONNECTIONS=1000                     # Global connection limit
MAX_CONNECTIONS_PER_IP=10               # Per-IP connection limit
```

### Rate Limiting (Phase 1 - Production Readiness)
```bash
RATE_LIMIT_GLOBAL_CAPACITY=1000         # Global token bucket capacity
RATE_LIMIT_GLOBAL_REFILL_RATE=100       # Global tokens per second
RATE_LIMIT_IP_CAPACITY=100              # Per-IP token bucket capacity
RATE_LIMIT_IP_REFILL_RATE=10            # Per-IP tokens per second
RATE_LIMIT_USER_CAPACITY=50             # Per-user token bucket capacity
RATE_LIMIT_USER_REFILL_RATE=5           # Per-user tokens per second
```

### Redis Configuration
```bash
REDIS_URL=redis://redis:6379            # Redis connection URL
REDIS_TTL=3600                          # Default TTL for cached data
```

## Troubleshooting

### "Connection refused" errors

**Problem**: Docker container can't connect to services

**Solution**:
```bash
# Check if Docker is running
docker ps

# Restart Docker Desktop
# Then rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### "Invalid API key" errors

**Problem**: API keys are incorrect or not set

**Solution**:
1. Verify your `.env.docker` file has actual keys (not placeholders)
2. Check for extra spaces or quotes around keys
3. Verify keys are valid by testing them directly with the provider

### "Supabase connection failed"

**Problem**: Supabase credentials are incorrect

**Solution**:
1. Verify all Supabase credentials in `.env.docker`
2. Check that your Supabase project is active
3. Verify the project URL matches your actual project

### Container won't start

**Problem**: Docker build or startup fails

**Solution**:
```bash
# Check logs for errors
docker-compose logs

# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Development Workflow

### Making Changes

1. Make code changes in your local repository
2. Rebuild the container: `docker-compose build`
3. Restart: `docker-compose up -d`
4. Check logs: `docker-compose logs -f`

### Testing

```bash
# Run tests inside the container
docker-compose exec exai-mcp pytest

# Or run specific tests
docker-compose exec exai-mcp pytest tests/test_specific.py
```

### Viewing Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f exai-mcp

# Last 100 lines
docker-compose logs --tail=100 exai-mcp
```

## Additional Resources

- **Project Documentation**: See `docs/` directory
- **Phase 1 Implementation**: See `docs/07_LOGS/PRODUCTION_READINESS_ROADMAP_2025-10-18.md`
- **Architecture**: See `docs/current/` directory
- **GitHub Repository**: [Add your repo URL here]

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs: `docker-compose logs -f`
3. Check existing documentation in `docs/`
4. Open an issue on GitHub (if applicable)

## Security Reminders

✅ **DO**:
- Keep your `.env.docker` file secure and private
- Use different API keys for development and production
- Rotate API keys regularly
- Review `.gitignore` to ensure sensitive files aren't tracked

❌ **DON'T**:
- Commit `.env.docker` to git
- Share your API keys in chat, email, or screenshots
- Use production API keys for development
- Hardcode API keys in source code

---

**Last Updated**: 2025-10-18 (Phase 1 - Production Readiness)

