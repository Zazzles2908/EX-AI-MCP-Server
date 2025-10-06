# Security Hardening Checklist

**Date:** 2025-10-01  
**Phase:** 0 (Architecture & Design)  
**Task:** 0.7  
**Status:** ✅ COMPLETE

---

## Executive Summary

This security hardening checklist provides comprehensive security guidelines for deploying and operating the EX-AI-MCP-Server in production environments. All recommendations align with the design philosophy (Fail Fast, Fail Clear) and are tailored for international users (api.z.ai context).

**Security Posture:**
- **Current:** Good foundation with API key validation, structured logging, error handling
- **Target:** Production-ready with defense-in-depth, monitoring, and incident response

**Priority Levels:**
- 🔴 **CRITICAL:** Must implement before production deployment
- 🟠 **HIGH:** Strongly recommended for production
- 🟡 **MEDIUM:** Recommended for enhanced security
- 🟢 **LOW:** Optional hardening measures

---

## 1. API Key Management

### 1.1 Storage & Access Control 🔴 CRITICAL

**Requirements:**
- ✅ Never commit API keys to version control
- ✅ Use environment variables (not hardcoded)
- ✅ Restrict .env file permissions: `chmod 600 .env`
- ✅ Use separate keys for dev/staging/production
- ✅ Rotate keys every 90 days

**Implementation:**
```bash
# Set restrictive permissions
chmod 600 .env

# Verify .env is in .gitignore
grep -q "^\.env$" .gitignore || echo ".env" >> .gitignore

# Audit for leaked keys
git log -p | grep -i "api_key" | grep -v "your_key_here"
```

**Validation:**
```bash
# Check file permissions
ls -la .env
# Expected: -rw------- (600)

# Verify not in git
git ls-files | grep -q "^\.env$" && echo "ERROR: .env in git!" || echo "OK"
```

### 1.2 Key Rotation 🟠 HIGH

**Process:**
1. Generate new API key from provider dashboard
2. Update .env with new key
3. Restart server
4. Verify functionality with `selfcheck` tool
5. Revoke old key after 24-hour grace period

**Automation:**
```bash
# Create key rotation reminder
echo "0 0 1 */3 * echo 'Rotate API keys' | mail -s 'Security Reminder' admin@example.com" | crontab -
```

### 1.3 Key Validation 🔴 CRITICAL

**Current Implementation:**
- ✅ Server validates API keys on startup
- ✅ Fails fast with clear error if keys invalid
- ✅ Logs authentication failures

**Enhancement:**
```python
# Add to startup validation
def validate_api_keys():
    """Validate API keys before server starts."""
    if not (os.getenv("GLM_API_KEY") or os.getenv("KIMI_API_KEY")):
        raise ValueError("At least one API key required")
    
    # Test connection to providers
    for provider in ["GLM", "KIMI"]:
        if not test_provider_connection(provider):
            logger.warning(f"{provider} API key may be invalid")
```

---

## 2. Environment Variable Security

### 2.1 Secure Storage 🔴 CRITICAL

**Requirements:**
- ✅ Use .env files (not shell exports)
- ✅ Restrict file permissions (600)
- ✅ Never log environment variables
- ✅ Use secrets management in production (e.g., AWS Secrets Manager, HashiCorp Vault)

**Production Deployment:**
```bash
# Option 1: AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id prod/exai/api-keys

# Option 2: HashiCorp Vault
vault kv get secret/exai/api-keys

# Option 3: Kubernetes Secrets
kubectl create secret generic exai-secrets --from-env-file=.env
```

### 2.2 Sensitive Data Masking 🟠 HIGH

**Implementation:**
```python
# Mask API keys in logs
def mask_sensitive(text: str) -> str:
    """Mask API keys and sensitive data in logs."""
    patterns = [
        (r'(api[_-]?key["\s:=]+)([a-zA-Z0-9-_]{20,})', r'\1***MASKED***'),
        (r'(token["\s:=]+)([a-zA-Z0-9-_]{20,})', r'\1***MASKED***'),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
```

---

## 3. Network Security

### 3.1 TLS/SSL Encryption 🔴 CRITICAL

**Requirements:**
- ✅ Use HTTPS for all API calls (enforced by providers)
- ✅ Validate SSL certificates
- ✅ Use TLS 1.2+ only
- ✅ WebSocket over TLS (wss://) in production

**Configuration:**
```env
# Enforce HTTPS
GLM_API_URL=https://api.z.ai/api/paas/v4  # ✅ HTTPS
KIMI_API_URL=https://api.moonshot.ai/v1   # ✅ HTTPS

# WebSocket TLS (production)
EXAI_WS_HOST=0.0.0.0
EXAI_WS_PORT=8079
# Use reverse proxy (nginx) for TLS termination
```

### 3.2 Firewall & Access Control 🟠 HIGH

**Requirements:**
- ✅ Restrict WebSocket port (8079) to trusted IPs
- ✅ Use firewall rules to block unauthorized access
- ✅ Implement rate limiting

**Implementation:**
```bash
# UFW (Ubuntu)
sudo ufw allow from 192.168.1.0/24 to any port 8079
sudo ufw deny 8079

# iptables
sudo iptables -A INPUT -p tcp --dport 8079 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8079 -j DROP
```

### 3.3 Reverse Proxy (Production) 🟠 HIGH

**Recommended Setup:**
```nginx
# nginx configuration
server {
    listen 443 ssl http2;
    server_name exai.example.com;

    ssl_certificate /etc/ssl/certs/exai.crt;
    ssl_certificate_key /etc/ssl/private/exai.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://127.0.0.1:8079;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Rate limiting
        limit_req zone=exai burst=10 nodelay;
    }
}

# Rate limit zone
limit_req_zone $binary_remote_addr zone=exai:10m rate=10r/s;
```

---

## 4. Input Validation & Sanitization

### 4.1 Parameter Validation 🔴 CRITICAL

**Current Implementation:**
- ✅ Pydantic models for tool parameters
- ✅ Type validation on all inputs
- ✅ File size limits (20MB default)

**Enhancement:**
```python
# Add input sanitization
def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    # Remove control characters
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    # Limit length
    max_length = 100000  # 100KB
    if len(text) > max_length:
        raise ValueError(f"Input too long: {len(text)} > {max_length}")
    return text
```

### 4.2 File Upload Security 🟠 HIGH

**Requirements:**
- ✅ Validate file types (whitelist)
- ✅ Scan for malware (optional)
- ✅ Limit file sizes
- ✅ Sanitize filenames

**Implementation:**
```python
# File validation
ALLOWED_EXTENSIONS = {'.txt', '.md', '.py', '.js', '.json', '.csv', '.pdf'}

def validate_file(filepath: str) -> bool:
    """Validate uploaded file."""
    # Check extension
    ext = Path(filepath).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type not allowed: {ext}")
    
    # Check size
    max_size = int(os.getenv("KIMI_FILES_MAX_SIZE_MB", "20")) * 1024 * 1024
    if os.path.getsize(filepath) > max_size:
        raise ValueError(f"File too large: {os.path.getsize(filepath)} > {max_size}")
    
    return True
```

---

## 5. Rate Limiting & Abuse Prevention

### 5.1 Request Rate Limiting 🟠 HIGH

**Implementation:**
```python
# Simple rate limiter
from collections import defaultdict
from time import time

class RateLimiter:
    def __init__(self, max_requests: int = 100, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time()
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window
        ]
        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        self.requests[client_id].append(now)
        return True
```

### 5.2 Cost Monitoring 🟡 MEDIUM

**Implementation:**
```python
# Track API costs
def log_api_cost(provider: str, model: str, tokens: int):
    """Log API usage for cost monitoring."""
    cost_per_1k = {
        "glm-4.5-flash": 0.0001,
        "kimi-k2-0711-preview": 0.0002,
    }
    cost = (tokens / 1000) * cost_per_1k.get(model, 0)
    logger.info(f"API_COST: provider={provider} model={model} tokens={tokens} cost=${cost:.4f}")
```

---

## 6. Logging & Monitoring

### 6.1 Security Event Logging 🔴 CRITICAL

**Requirements:**
- ✅ Log all authentication attempts
- ✅ Log all API errors
- ✅ Log suspicious activity
- ✅ Structured logging (JSONL)

**Current Implementation:**
```python
# Already implemented in server.py
logging.getLogger("metrics").info(json.dumps({
    "timestamp": time.time(),
    "event": "auth_failure",
    "provider": "GLM",
    "error": "Invalid API key"
}))
```

### 6.2 Log Retention & Analysis 🟠 HIGH

**Configuration:**
```env
LOG_MAX_SIZE=50MB
LOG_BACKUP_COUNT=10
LOG_RETENTION_DAYS=90
```

**Analysis:**
```bash
# Detect suspicious patterns
grep "auth_failure" .logs/metrics.jsonl | jq -r '.timestamp' | sort | uniq -c

# Monitor error rates
tail -f .logs/metrics.jsonl | jq 'select(.event == "error")'
```

### 6.3 Alerting 🟡 MEDIUM

**Implementation:**
```python
# Alert on security events
def check_security_alerts():
    """Monitor for security events and send alerts."""
    error_threshold = 10  # errors per minute
    auth_failure_threshold = 5  # failures per minute
    
    # Check error rate
    recent_errors = count_recent_events("error", window=60)
    if recent_errors > error_threshold:
        send_alert(f"High error rate: {recent_errors}/min")
    
    # Check auth failures
    recent_auth_failures = count_recent_events("auth_failure", window=60)
    if recent_auth_failures > auth_failure_threshold:
        send_alert(f"Multiple auth failures: {recent_auth_failures}/min")
```

---

## 7. Dependency Security

### 7.1 Dependency Audit 🔴 CRITICAL

**Process:**
```bash
# Audit dependencies
pip install safety
safety check --json

# Update dependencies
pip list --outdated
pip install --upgrade <package>

# Pin versions
pip freeze > requirements.txt
```

### 7.2 Vulnerability Scanning 🟠 HIGH

**Automation:**
```yaml
# GitHub Actions (.github/workflows/security.yml)
name: Security Scan
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run safety check
        run: |
          pip install safety
          safety check --json
```

---

## 8. Deployment Security Checklist

### Pre-Deployment 🔴 CRITICAL

- [ ] All API keys rotated and validated
- [ ] .env file permissions set to 600
- [ ] .env not in version control
- [ ] TLS/SSL certificates valid
- [ ] Firewall rules configured
- [ ] Rate limiting enabled
- [ ] Logging configured and tested
- [ ] Dependency audit passed
- [ ] Security scan passed

### Post-Deployment 🟠 HIGH

- [ ] Monitor logs for errors
- [ ] Verify API key usage
- [ ] Check rate limiting effectiveness
- [ ] Review security alerts
- [ ] Test incident response procedures

---

## 9. Incident Response Procedures

### 9.1 API Key Compromise 🔴 CRITICAL

**Immediate Actions:**
1. Revoke compromised key from provider dashboard
2. Generate new key
3. Update .env with new key
4. Restart server
5. Review logs for unauthorized usage
6. Notify stakeholders

### 9.2 Unauthorized Access 🔴 CRITICAL

**Immediate Actions:**
1. Block suspicious IP addresses
2. Review access logs
3. Rotate all API keys
4. Audit recent API calls
5. Investigate root cause
6. Document incident

### 9.3 Data Breach 🔴 CRITICAL

**Immediate Actions:**
1. Isolate affected systems
2. Preserve evidence (logs, snapshots)
3. Notify security team
4. Assess scope of breach
5. Implement containment measures
6. Follow legal/regulatory requirements

---

## 10. Compliance & Best Practices

### 10.1 International Users (api.z.ai) 🟠 HIGH

**Requirements:**
- ✅ Use international API endpoint: `https://api.z.ai/api/paas/v4`
- ✅ Comply with GDPR (if EU users)
- ✅ Data residency considerations
- ✅ Privacy policy for user data

### 10.2 Regular Security Reviews 🟡 MEDIUM

**Schedule:**
- **Weekly:** Review security logs
- **Monthly:** Dependency audit
- **Quarterly:** API key rotation
- **Annually:** Full security assessment

---

## Alignment with Design Philosophy

This security hardening approach supports the design principles from Task 0.1:

1. **Fail Fast, Fail Clear:** Validation on startup, clear error messages
2. **Simplicity Over Complexity:** Practical security measures, not over-engineering
3. **Maintainability Focus:** Automated checks, structured logging
4. **User-Centric Design:** Security without sacrificing usability

---

**Task 0.7 Status:** ✅ COMPLETE

