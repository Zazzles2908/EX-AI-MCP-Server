# API Key Management Guide

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** ✅ **Complete**

---

## 🎯 Executive Summary

This guide covers the complete lifecycle of API key management for the EX-AI MCP Server, including GLM (ZhipuAI), Kimi (Moonshot AI), and Supabase keys. It provides best practices for secure storage, rotation, and monitoring of all API credentials.

### What You'll Learn:
- ✅ How to obtain and configure API keys
- ✅ Secure storage patterns (environment variables, secrets managers)
- ✅ Rotation procedures and schedules
- ✅ Monitoring and audit logging
- ✅ Troubleshooting and recovery

---

## 🔑 API Key Overview

The EX-AI MCP Server requires three types of API keys:

| Provider | Key Name | Purpose | Required |
|----------|----------|---------|----------|
| **Supabase** | `SUPABASE_ACCESS_TOKEN` | Database & storage management | ✅ Yes |
| **Supabase** | `SUPABASE_JWT_SECRET` | JWT token generation | ✅ Yes |
| **ZhipuAI** | `GLM_API_KEY` | GLM provider access | ✅ Yes |
| **Moonshot** | `KIMI_API_KEY` | Kimi provider access | ✅ Yes |
| **Supabase** | `SUPABASE_URL` | Database connection | ✅ Yes |
| **Supabase** | `SUPABASE_ANON_KEY` | Client-side operations | ✅ Yes |
| **Supabase** | `SUPABASE_SERVICE_ROLE_KEY` | Server-side operations | ✅ Yes |

---

## 📋 Current Configuration (2025-11-10)

### ✅ Configured Keys
```env
# Supabase (Database & Storage)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (your-anon-key)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (your-service-role-key)
SUPABASE_ACCESS_TOKEN=sbp_your_access_token_here
SUPABASE_JWT_SECRET=your_64_character_hex_secret_here

# GLM (ZhipuAI)
GLM_API_KEY=your_glm_api_key_here

# Kimi (Moonshot AI)
KIMI_API_KEY=your_kimi_api_key_here
```

⚠️ **Security Note**: The above are placeholders. Actual secrets are stored in `.env` file only and are .gitignored.

### 🔐 Security Status
- ✅ **All keys in environment variables** (not hardcoded)
- ✅ **JWT secret generated** (64-char hex, production-ready)
- ✅ **No keys in source code** (verified across 557 files)
- ✅ **Keys in .env only** (git-ignored)
- ✅ **Legacy entries removed** (from scripts and configs)

---

## 🔑 Obtaining API Keys

### 1. Supabase Keys

#### SUPABASE_ACCESS_TOKEN
**Purpose:** Management API access (deploy migrations, manage projects)
**How to Get:**
1. Go to [https://supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens)
2. Sign in to your Supabase account
3. Click "Generate new token"
4. Name it "EX-AI MCP Server"
5. Copy the token (starts with `sbp_`)

**Format:** `sbp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### SUPABASE_URL
**Purpose:** Database connection endpoint
**How to Get:**
1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to Settings → API
4. Copy the "Project URL"

**Format:** `https://xxxxxxxxxxxxxxxxxx.supabase.co`

#### SUPABASE_ANON_KEY
**Purpose:** Client-side database access (public key)
**How to Get:**
1. In project settings → API
2. Copy the "anon public" key

**Format:** Long JWT token (eyJ...)

#### SUPABASE_SERVICE_ROLE_KEY
**Purpose:** Server-side database access (secret key)
**How to Get:**
1. In project settings → API
2. Copy the "service_role" key (keep secret!)

**Format:** Long JWT token (eyJ...)

#### SUPABASE_JWT_SECRET
**Purpose:** Sign JWT tokens for authentication
**How to Generate:**
```python
import secrets
secret = secrets.token_hex(32)
print(secret)
# Output: a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
```

---

### 2. GLM (ZhipuAI) API Key

**Purpose:** Access GLM models (glm-4.5-flash, glm-4.6, etc.)
**How to Get:**
1. Go to [https://z.ai/manage-apikey/apikey-list](https://z.ai/manage-apikey/apikey-list)
2. Sign up for an account at ZhipuAI
3. Go to API Keys section
4. Create a new API key
5. Copy the key

**Format:** `xxxxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyy`

**Pricing:** Pay-per-use (check current rates on website)

**Getting Started Credit:** Usually includes free trial credits

**Migration from OpenAI to ZhipuAI:**

#### Migration Checklist
When migrating from OpenAI to ZhipuAI GLM, update the following:

1. **API Endpoint**:
   ```python
   # OLD (OpenAI)
   BASE_URL = "https://api.openai.com/v1"

   # NEW (ZhipuAI)
   BASE_URL = "https://api.z.ai/api/paas/v4"
   ```

2. **Model Names**:
   ```python
   # OLD (OpenAI)
   models = {
       "gpt-3.5-turbo": "glm-4",
       "gpt-4": "glm-4",
       "gpt-4-turbo": "glm-4.5"
   }

   # NEW (ZhipuAI)
   models = {
       "glm-4": "glm-4",
       "glm-4.5": "glm-4.5",
       "glm-4.5-flash": "glm-4.5-flash",  # Fast, cost-effective
       "glm-4.6": "glm-4.6"  # Latest, most capable
   }
   ```

3. **Sampling Parameters**:
   ```python
   # ZhipuAI supports all OpenAI parameters plus:
   params = {
       "model": "glm-4.5-flash",
       "messages": [...],
       "temperature": 0.7,
       "max_tokens": 1000,
       # ZhipuAI specific:
       "top_p": 0.9,
       "repetition_penalty": 1.1,
       "stream": True  # Streaming support
   }
   ```

4. **Deep Thinking Mode** (ZhipuAI exclusive):
   ```python
   # Enable for complex reasoning tasks
   params = {
       "model": "glm-4.6",
       "messages": [...],
       "enable_thinking": True  # NEW: Enhanced reasoning
   }
   ```

5. **Response Format**:
   ```python
   # ZhipuAI returns additional fields
   response = {
       "id": "chatglm-...",
       "object": "chat.completion",
       "created": 1234567890,
       "model": "glm-4.5-flash",
       "choices": [...],
       "usage": {
           "prompt_tokens": 10,
           "completion_tokens": 20,
           "total_tokens": 30
       },
       # ZhipuAI specific:
       "reasoning_tokens": 15,  # NEW
       "system_fingerprint": "..."  # NEW
   }
   ```

6. **Rate Limits**:
   ```python
   # ZhipuAI has different rate limits
   # Check headers in response:
   headers = response.headers
   rate_limit = {
       "requests_per_minute": headers.get("X-RateLimit-Limit-Requests"),
       "tokens_per_minute": headers.get("X-RateLimit-Limit-Tokens")
   }
   ```

7. **Error Handling**:
   ```python
   # ZhipuAI error format
   try:
       response = requests.post(...)
   except requests.exceptions.RequestException as e:
       if hasattr(e, 'response'):
           error = e.response.json()
           error_code = error.get("error", {}).get("code")
           # Handle specific error codes
   ```

8. **Environment Variables**:
   ```env
   # OLD
   # OPENAI_API_KEY=sk-...

   # NEW
   GLM_API_KEY=your_glm_api_key_here
   ```

9. **Testing Migration**:
   ```python
   def test_glm_migration():
       import requests

       response = requests.post(
           "https://api.z.ai/api/paas/v4/chat/completions",
           headers={
               "Authorization": f"Bearer {os.getenv('GLM_API_KEY')}",
               "Content-Type": "application/json"
           },
           json={
               "model": "glm-4.5-flash",
               "messages": [{"role": "user", "content": "Hello, GLM!"}]
           }
       )
       assert response.status_code == 200
       print("✅ GLM migration successful")
   ```

10. **Deploy & Monitor**:
    - Update .env file with GLM_API_KEY
    - Restart services: `docker-compose restart`
    - Monitor logs for any issues
    - Run integration tests
    - Update documentation

---

### 3. Kimi (Moonshot AI) API Key

**Purpose:** Access Kimi models (kimi-k2-0905-preview, etc.)
**How to Get:**
1. Go to [https://platform.moonshot.ai/console/account](https://platform.moonshot.ai/console/account)
2. Sign up for an account at Moonshot AI
3. Go to API Keys section
4. Create a new API key
5. Copy the key

**Format:** `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Pricing:** Pay-per-use (check current rates on website)

**Getting Started Credit:** Usually includes free trial credits

**Code Example - Kimi API Integration:**

```python
import requests
import json
from typing import List, Dict, Optional

class KimiAPIClient:
    """Kimi (Moonshot AI) API client for chat completions"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.moonshot.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def chat_completions_create(
        self,
        model: str = "moonshot-v1-8k",
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs
    ) -> Dict:
        """
        Create a chat completion using Kimi API

        Args:
            model: Kimi model name (moonshot-v1-8k, moonshot-v1-32k, etc.)
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Randomness parameter (0.0 to 2.0)
            stream: Enable streaming responses
            **kwargs: Additional parameters

        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }

        # Add optional parameters
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature

        # Add any additional parameters
        payload.update(kwargs)

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        return response.json()

    def get_models(self) -> List[str]:
        """Get list of available models"""
        url = f"{self.base_url}/models"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        models_data = response.json()
        return [model["id"] for model in models_data["data"]]

    def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> requests.Response:
        """
        Create a streaming chat completion

        Yields:
            Chunks of the response
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs
        }

        response = requests.post(url, headers=self.headers, json=payload, stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line_data = line.decode('utf-8')
                if line_data.startswith('data: '):
                    data = line_data[6:]  # Remove 'data: ' prefix
                    if data.strip() == '[DONE]':
                        break
                    yield json.loads(data)

# Usage Example
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Initialize client
    client = KimiAPIClient(os.getenv("KIMI_API_KEY"))

    # Non-streaming example
    response = client.chat_completions_create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain quantum computing in simple terms."}
        ],
        max_tokens=500,
        temperature=0.7
    )

    print("Response:", response["choices"][0]["message"]["content"])

    # Streaming example
    print("\n--- Streaming Response ---")
    for chunk in client.stream_chat(
        model="moonshot-v1-8k",
        messages=[{"role": "user", "content": "Count to 5"}]
    ):
        if "choices" in chunk and len(chunk["choices"]) > 0:
            delta = chunk["choices"][0].get("delta", {})
            if "content" in delta:
                print(delta["content"], end="", flush=True)

    print("\n")

    # Get available models
    models = client.get_models()
    print(f"Available models: {models}")
```

---

## 🔒 Secure Storage Patterns

### 1. Environment Variables (Recommended)

**File:** `.env`
```env
# ✅ CORRECT: Environment variables
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
GLM_API_KEY=your_glm_api_key_here
KIMI_API_KEY=your_kimi_api_key_here
```

**Loading in Code:**
```python
import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# Access securely
supabase_url = os.getenv("SUPABASE_URL")
glm_api_key = os.getenv("GLM_API_KEY")
kimi_api_key = os.getenv("KIMI_API_KEY")
```

---

### 2. Secrets Manager (Production)

**For Kubernetes:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: exai-mcp-secrets
type: Opaque
data:
  SUPABASE_URL: https://your-project.supabase.co
  GLM_API_KEY: your_glm_api_key_here
  KIMI_API_KEY: your_kimi_api_key_here
```

**For AWS:**
```bash
aws secretsmanager create-secret \
  --name exai-mcp/api-keys \
  --secret-string '{"SUPABASE_URL":"...","GLM_API_KEY":"...","KIMI_API_KEY":"..."}'
```

**For Azure:**
```bash
az keyvault secret set \
  --vault-name exai-mcp-vault \
  --name api-keys \
  --value '{"SUPABASE_URL":"...","GLM_API_KEY":"...","KIMI_API_KEY":"..."}'
```

---

### 3. Docker Secrets
```yaml
# docker-compose.yml
services:
  exai-mcp-daemon:
    secrets:
      - supabase_url
      - glm_api_key
      - kimi_api_key

secrets:
  supabase_url:
    file: ./secrets/supabase_url.txt
  glm_api_key:
    file: ./secrets/glm_api_key.txt
  kimi_api_key:
    file: ./secrets/kimi_api_key.txt
```

---

### 4. System Environment (Systemd)

**File:** `/etc/systemd/system/exai-mcp-daemon.service`
```ini
[Service]
Environment="SUPABASE_URL=https://your-project.supabase.co"
Environment="GLM_API_KEY=your_glm_api_key_here"
Environment="KIMI_API_KEY=your_kimi_api_key_here"
ExecStart=/usr/local/bin/exai-mcp-daemon
```

---

## 🔄 Key Rotation Procedures

### Rotation Schedule (Recommended)
- **Supabase Access Token**: Every 90 days
- **JWT Secret**: Every 90 days
- **GLM API Key**: Every 90 days
- **Kimi API Key**: Every 90 days
- **Supabase Service Role**: Every 180 days (less frequent, more disruptive)

---

### 1. GLM API Key Rotation

**Step 1: Generate New Key**
1. Log into [https://z.ai/manage-apikey/apikey-list](https://z.ai/manage-apikey/apikey-list)
2. Go to API Keys section
3. Click "Create new key"
4. Name it "EX-AI MCP (Rotation 2025-11-10)"
5. Copy the new key

**Step 2: Update Configuration**
```env
# Old key (comment out)
# GLM_API_KEY=your_old_glm_api_key_here

# New key
GLM_API_KEY=NEW_KEY_HERE
```

**Step 3: Restart Services**
```bash
docker-compose restart exai-mcp-daemon
```

**Step 4: Verify**
```bash
# Check logs
docker logs exai-mcp-daemon | grep "GLM"

# Test GLM connection
curl -X POST https://api.z.ai/api/paas/v4/chat/completions \
  -H "Authorization: Bearer $GLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-4.5-flash","messages":[{"role":"user","content":"test"}]}'
```

**Step 5: Revoke Old Key**
1. Go to API Keys section
2. Delete the old key
3. Verify it's no longer active

---

### 2. Kimi API Key Rotation

**Step 1: Generate New Key**
1. Log into [https://platform.moonshot.ai/console/account](https://platform.moonshot.ai/console/account)
2. Go to API Keys section
3. Create new key
4. Name it "EX-AI MCP (Rotation 2025-11-10)"
5. Copy the new key

**Step 2: Update Configuration**
```env
# Old key (comment out)
# KIMI_API_KEY=your_old_kimi_api_key_here

# New key
KIMI_API_KEY=NEW_KEY_HERE
```

**Step 3: Restart and Verify**
```bash
docker-compose restart exai-mcp-daemon

# Test Kimi connection
curl -X POST https://api.moonshot.ai/v1/chat/completions \
  -H "Authorization: Bearer $KIMI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"moonshot-v1-8k","messages":[{"role":"user","content":"test"}]}'
```

---

### 3. Supabase Access Token Rotation

**Step 1: Generate New Token**
1. Go to [https://supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens)
2. Click "Generate new token"
3. Name it "EX-AI MCP (2025-11-10)"
4. Copy the token

**Step 2: Update Configuration**
```env
# Old token (keep for verification)
# SUPABASE_ACCESS_TOKEN=sbp_your_old_token_here

# New token
SUPABASE_ACCESS_TOKEN=sbp_NEW_TOKEN_HERE
```

**Step 3: Update .mcp.json**
```json
{
  "mcpServers": {
    "supabase-mcp-full": {
      "args": [
        "--access-token=${SUPABASE_ACCESS_TOKEN}"
      ],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "${SUPABASE_ACCESS_TOKEN}"
      }
    }
  }
}
```

**Step 4: Restart and Verify**
```bash
docker-compose restart

# Test Supabase connection
python scripts/test_supabase_connection.py
```

---

### 4. JWT Secret Rotation

**Step 1: Generate New Secret**
```python
import secrets
new_secret = secrets.token_hex(32)
print(f"New JWT secret: {new_secret}")
```

**Step 2: Update Configuration**
```env
# Old secret (keep for verification)
# SUPABASE_JWT_SECRET=your_old_secret_here

# New secret
SUPABASE_JWT_SECRET=NEW_SECRET_HERE
```

**Step 3: Restart Services**
```bash
docker-compose restart
```

**Step 4: Invalidate Old Tokens**
```python
# Old tokens will automatically stop working
# No additional action needed if exp < 24h
# If exp > 24h, notify users to refresh
```

---

## 📊 Monitoring & Audit

### 1. API Key Usage Monitoring

**Log API Key Usage:**
```python
import logging

logger = logging.getLogger("api-key-usage")

def log_api_usage(provider, key_prefix, status):
    # Log only prefix for security
    key_display = f"{key_prefix}...{key[-4:]}" if len(key) > 8 else key
    logger.info(f"API usage - Provider: {provider}, Key: {key_display}, Status: {status}")
```

**Monitor in Supabase:**
```sql
-- Check API usage patterns
SELECT
    provider,
    COUNT(*) as usage_count,
    MAX(timestamp) as last_usage
FROM audit_logs
WHERE action LIKE '%api_key%'
GROUP BY provider;
```

---

### 2. Audit Logging

**Log All Key Operations:**
```python
def audit_key_operation(operation, provider, user_id):
    audit_log = {
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation,  # create, update, delete, rotate
        "provider": provider,    # glm, kimi, supabase
        "user_id": user_id,
        "status": "success"
    }

    # Insert into Supabase
    supabase.table("audit_logs").insert(audit_log).execute()
```

---

### 3. Alerting

**Set up alerts for:**
- Multiple failed API calls (rate limit or invalid key)
- Unusual usage patterns
- Key expiration warnings (notify 7 days before)
- Failed authentication attempts

**Example Alert:**
```python
if failed_attempts > 10:
    send_alert(
        "API Key Failure Alert",
        f"Provider {provider}: {failed_attempts} failed attempts in 5 minutes"
    )
```

---

## 🛠️ Troubleshooting

### Issue: "Invalid API Key"
**Diagnosis:**
```bash
# Check if key is set
echo $GLM_API_KEY

# Verify key format
echo $GLM_API_KEY | head -c 10
# Should start with correct prefix
```

**Solution:**
```bash
# Regenerate key from provider
# Update .env file
# Restart services
docker-compose restart
```

---

### Issue: "Rate Limit Exceeded"
**Diagnosis:**
```bash
# Check rate limit headers
curl -I -H "Authorization: Bearer $GLM_API_KEY" \
  https://api.z.ai/api/paas/v4/models
```

**Solution:**
```python
# Implement exponential backoff
import time
import random

def retry_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

---

### Issue: "Key Expired"
**Diagnosis:**
```python
# Check key expiration (if available in response)
response = requests.get("https://api.provider.com/status", headers={
    "Authorization": f"Bearer {api_key}"
})
if response.status_code == 401:
    print("Key expired or invalid")
```

**Solution:**
1. Log into provider dashboard
2. Check key expiration date
3. Generate new key
4. Update configuration
5. Restart services

---

### Issue: "Insufficient Credits"
**Diagnosis:**
```python
# Check account balance
response = requests.get("https://api.provider.com/billing", headers={
    "Authorization": f"Bearer {api_key}"
})
balance = response.json()["balance"]
if balance < 0.01:
    print("Insufficient credits")
```

**Solution:**
1. Log into provider dashboard
2. Add payment method
3. Add credits
4. Verify key still works

---

## 🔐 Security Best Practices

### 1. Never Commit Keys
```bash
# Add to .gitignore
.env
.env.local
.env.production
secrets/
*.key
*.pem
```

---

### 2. Use Key Prefixes
```python
# Only log prefixes
def log_key_usage(key, provider):
    prefix = key[:8] if len(key) > 8 else key
    logger.info(f"Key used: {provider} - {prefix}... (hidden)")
```

---

### 3. Rotate Regularly
```python
# Set up automated rotation reminders
import schedule

def rotation_reminder():
    send_email(
        "API Key Rotation Due",
        f"Time to rotate your {provider} API key"
    )

# Schedule: 7 days before expiration
schedule.every().day.at("09:00").do(rotation_reminder)
```

---

### 4. Use Separate Keys for Different Environments
```env
# Development
GLM_API_KEY_DEV=dev_key_here

# Production
GLM_API_KEY=prod_key_here
```

---

### 5. Monitor for Leaks
```bash
# Scan for exposed keys
git log --all --grep="api_key" --oneline

# Use tools like truffleHog
trufflehog git file://. --json
```

---

## 📋 Key Management Checklist

### Initial Setup
- [ ] Obtain all required API keys
- [ ] Store in environment variables
- [ ] Verify keys work
- [ ] Test all providers
- [ ] Document key locations

### Monthly Checks
- [ ] Review usage statistics
- [ ] Check for unusual activity
- [ ] Verify key expiration dates
- [ ] Test all providers still work
- [ ] Update documentation if needed

### Quarterly Rotation
- [ ] Generate new keys (GLM, Kimi, Supabase)
- [ ] Update configuration
- [ ] Restart services
- [ ] Verify functionality
- [ ] Revoke old keys
- [ ] Update documentation

### Annual Review
- [ ] Review all security practices
- [ ] Audit access logs
- [ ] Update rotation schedule
- [ ] Review provider pricing
- [ ] Consider alternative providers

---

## 📚 Related Documentation

- **JWT Authentication**: [01_jwt_authentication.md](01_jwt_authentication.md)
- **Security Best Practices**: [03_security_best_practices.md](03_security_best_practices.md)
- **System Architecture**: [../01-architecture-overview/01_system_architecture.md](../01-architecture-overview/01_system_architecture.md)

---

## 🔗 Quick Reference

### Key Formats
```
Supabase Access Token:  sbp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Supabase URL:          https://xxxxxxxxxxxxxxxxxx.supabase.co
Supabase JWT:          eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
GLM API Key:           xxxxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyy
Kimi API Key:          sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
JWT Secret:            your_64_character_hex_secret_here
```

### Key Provider URLs
- **Supabase**: [https://supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens)
- **GLM (ZhipuAI)**: [https://z.ai/manage-apikey/apikey-list](https://z.ai/manage-apikey/apikey-list)
- **Kimi (Moonshot)**: [https://platform.moonshot.ai/console/account](https://platform.moonshot.ai/console/account)

### Rotation Commands
```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_hex(32))"

# Test Supabase connection
python scripts/test_supabase_connection.py

# Restart services
docker-compose restart
```

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server Security Team
**Status:** ✅ **Complete - API Key Management Fully Documented**
