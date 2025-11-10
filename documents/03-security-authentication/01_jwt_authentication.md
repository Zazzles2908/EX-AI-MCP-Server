# JWT Authentication Guide

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** ✅ **Complete**

---

## 🎯 Executive Summary

JWT (JSON Web Token) authentication is the core security mechanism for the EX-AI MCP Server. This guide explains how to generate, validate, and use JWT tokens for authentication, including how external AI agents can obtain and use tokens to access the system.

### What You'll Learn:
- ✅ How JWT tokens are generated and validated
- ✅ How external AI agents can obtain tokens
- ✅ Token lifecycle and refresh mechanisms
- ✅ Integration patterns for different client types
- ✅ Security best practices and troubleshooting

---

## 🔐 JWT Authentication Overview

### What is JWT?
JWT (JSON Web Token) is a compact, URL-safe token format used for securely transmitting information between parties. For the EX-AI MCP Server, JWT tokens are used to authenticate and authorize requests to the WebSocket daemon and database operations.

### Why JWT?
- **Stateless**: No session storage required
- **Secure**: Cryptographically signed
- **Scalable**: Works across multiple servers
- **Standard**: Industry-standard protocol (RFC 7519)
- **Extensible**: Can carry custom claims

---

## 🏗️ JWT Architecture

### Token Structure
JWT consists of three Base64URL-encoded parts separated by dots:
```
HEADER.PAYLOAD.SIGNATURE
```

**Example Token:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload (Claims)
```json
{
  "sub": "user_id_or_identifier",
  "name": "User Name",
  "iat": 1516239022,
  "exp": 1516242622,
  "iss": "exai-mcp-server",
  "aud": "exai-mcp-client"
}
```

### Signature
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret_key
)
```

---

## 🔑 JWT Secret Management

### Secret Configuration
The JWT secret is configured in the `.env` file:

**Current Secret (Generated 2025-11-10):**
```env
SUPABASE_JWT_SECRET=your_64_character_hex_secret_here
```

⚠️ **Security Note**: The actual secret is stored in the `.env` file and is .gitignored. Do not hardcode secrets in documentation!

**Secret Properties:**
- **Length**: 64 characters (256 bits)
- **Format**: Hexadecimal
- **Algorithm**: HS256 (HMAC-SHA256)
- **Security Level**: Production-ready (256-bit key)

### Secret Generation
To generate a new secret:
```python
import secrets

# Generate 32-byte (256-bit) random key
secret = secrets.token_hex(32)
print(secret)
# Output: b0f9a7e6d88fe868199b0abc59b069d2261cf1f200779bac39484cc1702218b7
```

### Secret Rotation (Recommended Every 90 Days)
1. Generate new secret
2. Update `.env` file
3. Restart all services
4. Invalidate old tokens (if needed)
5. Update documentation

---

## 🚀 How External AI Agents Obtain JWT Tokens

External AI agents have **three methods** to obtain JWT tokens for authentication:

### Method 1: Setup Script (Recommended for New Users)

**Step 1: Run Setup Script**
```bash
# Download and run the JWT setup script
curl -O https://raw.githubusercontent.com/your-org/exai-mcp-server/main/scripts/setup_jwt_token.py
python setup_jwt_token.py
```

**Step 2: Enter Configuration**
```
=== EX-AI MCP Server JWT Token Setup ===
Enter your Supabase JWT Secret: your_64_character_hex_secret_here
Enter your user identifier: agent_001
Enter token expiration (hours, default 24): 24
```

**Step 3: Receive Token**
```
✅ JWT Token Generated Successfully!

Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Expires: 2025-11-11 12:00:00 UTC
User: agent_001
Quota: 100 requests
```

**Step 4: Configure Client**
```python
# In your AI agent
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}
```

---

### Method 2: Programmatic Token Generation (For Developers)

**Python Example:**
```python
import jwt
import time
from datetime import datetime, timedelta

# Configuration
JWT_SECRET = "your_64_character_hex_secret_here"
USER_ID = "agent_001"
EXPIRATION_HOURS = 24

# Generate token
payload = {
    "sub": USER_ID,  # Subject (user identifier)
    "name": "AI Client",  # Display name
    "iat": int(time.time()),  # Issued at
    "exp": int(time.time()) + (EXPIRATION_HOURS * 3600),  # Expiration
    "iss": "exai-mcp-server",  # Issuer
    "aud": "exai-mcp-client",  # Audience
    "quota": 100,  # Request quota
    "role": "user"  # User role
}

token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
print(f"JWT Token: {token}")
```

**JavaScript/Node.js Example:**
```javascript
const jwt = require('jsonwebtoken');

// Configuration
const JWT_SECRET = "your_64_character_hex_secret_here";
const USER_ID = "agent_001";
const EXPIRATION_HOURS = 24;

// Generate token
const payload = {
    sub: USER_ID,  // Subject
    name: "AI Client",  // Display name
    iat: Math.floor(Date.now() / 1000),  // Issued at
    exp: Math.floor(Date.now() / 1000) + (EXPIRATION_HOURS * 3600),  // Expiration
    iss: "exai-mcp-server",  // Issuer
    aud: "exai-mcp-client",  // Audience
    quota: 100,  // Request quota
    role: "user"  // User role
};

const token = jwt.sign(payload, JWT_SECRET, { algorithm: "HS256" });
console.log(`JWT Token: ${token}`);
```

**Bash/curl Example:**
```bash
# Using jwt-cli tool
jwt encode \
  --secret your_64_character_hex_secret_here \
  '{"sub":"agent_001","name":"AI Client","iat":'"$(date +%s)"',"exp":'"$(($(date +%s) + 86400))"',"iss":"exai-mcp-server","aud":"exai-mcp-client","quota":100,"role":"user"}'
```

---

### Method 3: Environment Variable (For Existing Setup)

If you have access to the EX-AI MCP Server environment:

**Step 1: Check Environment**
```bash
echo $SUPABASE_JWT_SECRET
# Output: your_64_character_hex_secret_here
```

**Step 2: Export Token**
```bash
export JWT_TOKEN=$(python3 -c "
import jwt
import time
payload = {
    'sub': 'agent_001',
    'name': 'AI Client',
    'iat': int(time.time()),
    'exp': int(time.time()) + 86400,
    'iss': 'exai-mcp-server',
    'aud': 'exai-mcp-client',
    'quota': 100,
    'role': 'user'
}
print(jwt.encode(payload, 'your_64_character_hex_secret_here', algorithm='HS256'))
")
echo $JWT_TOKEN
```

---

## 🔍 Token Validation

### Server-Side Validation
When a request comes in, the server validates the JWT token:

```python
def validate_jwt_token(token, jwt_secret):
    try:
        # Decode and validate
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience="exai-mcp-client",
            issuer="exai-mcp-server"
        )

        # Check expiration
        if payload["exp"] < time.time():
            raise jwt.ExpiredSignatureError("Token has expired")

        # Check quota
        if payload.get("quota", 0) <= 0:
            raise ValueError("Token quota exceeded")

        return payload

    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")
```

### Client-Side Validation
Before using a token, clients can validate it:

```python
import jwt
import time

def is_token_valid(token, jwt_secret):
    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_signature": True}
        )

        # Check if expired
        if payload["exp"] < time.time():
            print("Token expired")
            return False

        print(f"Token valid for user: {payload['sub']}")
        print(f"Expires at: {datetime.fromtimestamp(payload['exp'])}")
        return True

    except Exception as e:
        print(f"Token validation failed: {str(e)}")
        return False

# Usage
is_token_valid(jwt_token, jwt_secret)
```

---

## 🔄 Token Lifecycle

### 1. Token Issuance
```
Request → Authentication → Token Generation → Token Return
```

**Duration:** Instant (< 100ms)

### 2. Token Usage
```
Client → Attach Token → Send Request → Server Validates → Process
```

**Duration:** Token remains valid until expiration

### 3. Token Expiration
```
Token Exceeds TTL → Server Rejects → Client Requests New Token
```

**Default TTL:** 24 hours
**Recommended:** Refresh tokens 1 hour before expiration

### 4. Token Refresh
```python
def refresh_token(old_token, jwt_secret):
    try:
        # Decode old token (without validation for expired)
        payload = jwt.decode(
            old_token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_exp": False}
        )

        # Generate new token
        new_payload = {
            "sub": payload["sub"],
            "name": payload["name"],
            "iat": int(time.time()),
            "exp": int(time.time()) + 86400,  # 24 hours
            "iss": "exai-mcp-server",
            "aud": "exai-mcp-client",
            "quota": payload.get("quota", 100),
            "role": payload.get("role", "user")
        }

        return jwt.encode(new_payload, jwt_secret, algorithm="HS256")

    except Exception as e:
        raise ValueError(f"Token refresh failed: {str(e)}")
```

---

## 🔌 Integration Examples

### Python Client
```python
import jwt
import requests
import time

class EXAIClient:
    def __init__(self, jwt_token, base_url="ws://127.0.0.1:3000"):
        self.jwt_token = jwt_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

    def validate_token(self):
        """Check if token is still valid"""
        try:
            payload = jwt.decode(
                self.jwt_token,
                "your_64_character_hex_secret_here",
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            return True
        except jwt.ExpiredSignatureError:
            print("Token expired!")
            return False

    def call_tool(self, tool_name, arguments):
        """Call an MCP tool with authentication"""
        if not self.validate_token():
            raise ValueError("Authentication required - token expired")

        # Prepare request
        request_data = {
            "tool": tool_name,
            "arguments": arguments
        }

        # Make request (WebSocket or HTTP)
        try:
            response = requests.post(
                f"{self.base_url}/call",
                json=request_data,
                headers=self.headers,
                timeout=30
            )
            return response.json()
        except Exception as e:
            print(f"Request failed: {str(e)}")
            raise

# Usage
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
client = EXAIClient(jwt_token)
result = client.call_tool("chat", {"message": "Hello, EX-AI!"})
```

### JavaScript Client
```javascript
const jwt = require('jsonwebtoken');
const WebSocket = require('ws');

class EXAIClient {
    constructor(jwtToken, wsUrl = 'ws://127.0.0.1:3000') {
        this.jwtToken = jwtToken;
        this.wsUrl = wsUrl;
        this.ws = null;
    }

    connect() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.wsUrl, {
                headers: {
                    'Authorization': `Bearer ${this.jwtToken}`
                }
            });

            this.ws.on('open', () => {
                console.log('Connected to EX-AI MCP Server');
                resolve();
            });

            this.ws.on('error', (error) => {
                console.error('Connection error:', error);
                reject(error);
            });
        });
    }

    callTool(toolName, arguments) {
        return new Promise((resolve, reject) => {
            const request = {
                tool: toolName,
                arguments: arguments
            };

            this.ws.send(JSON.stringify(request));

            this.ws.on('message', (data) => {
                try {
                    const response = JSON.parse(data);
                    resolve(response);
                } catch (error) {
                    reject(error);
                }
            });
        });
    }
}

// Usage
const jwtToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';
const client = new EXAIClient(jwtToken);

client.connect()
    .then(() => client.callTool('chat', { message: 'Hello, EX-AI!' }))
    .then(result => console.log('Result:', result))
    .catch(error => console.error('Error:', error));
```

### cURL Example
```bash
# Validate token
curl -X POST http://127.0.0.1:3000/validate \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"

# Call tool
curl -X POST http://127.0.0.1:3000/call \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "chat",
    "arguments": {
      "message": "Hello, EX-AI!"
    }
  }'
```

---

## 🔒 Security Best Practices

### 1. Token Storage
```python
# ✅ DO: Store tokens securely
import keyring

# Save token
keyring.set_password("exai-mcp", "jwt_token", jwt_token)

# Retrieve token
jwt_token = keyring.get_password("exai-mcp", "jwt_token")

# ❌ DON'T: Store tokens in plain text
# with open("token.txt", "w") as f:
#     f.write(jwt_token)  # INSECURE!
```

### 2. Token Transmission
```python
# ✅ DO: Use HTTPS/WSS in production
JWT_ENDPOINT = "wss://your-domain.com:3000"  # Secure WebSocket

# ❌ DON'T: Use HTTP in production
# JWT_ENDPOINT = "ws://127.0.0.1:3000"  # INSECURE for production!
```

### 3. Token Expiration
```python
# ✅ DO: Use reasonable expiration times
EXPIRATION_SECONDS = 24 * 60 * 60  # 24 hours

# ❌ DON'T: Use very long expirations
# EXPIRATION_SECONDS = 365 * 24 * 60 * 60  # 1 year (INSECURE!)
```

### 4. Token Refresh
```python
# ✅ DO: Refresh tokens proactively
def is_token_expiring_soon(token, warning_minutes=60):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        time_until_expiry = payload["exp"] - time.time()
        return time_until_expiry < (warning_minutes * 60)
    except:
        return True

if is_token_expiring_soon(jwt_token):
    jwt_token = refresh_token(jwt_token, jwt_secret)
```

### 5. Secret Management
```python
# ✅ DO: Use environment variables
import os
jwt_secret = os.getenv("SUPABASE_JWT_SECRET")

# ❌ DON'T: Hardcode secrets
# jwt_secret = "b0f9a7e6d88fe868199b0abc59b069d2261cf1f200779bac39484cc1702218b7"
```

---

## 🐛 Troubleshooting

### Issue: "Token has expired"
**Solution:**
```python
# Generate a new token
jwt_token = refresh_token(old_token, jwt_secret)
```

### Issue: "Invalid signature"
**Solution:**
```python
# Verify you're using the correct secret
print(f"Using secret: {jwt_secret[:10]}...")

# Check if secret matches server configuration
# Verify in .env: SUPABASE_JWT_SECRET=...
```

### Issue: "Audience mismatch"
**Solution:**
```python
# Ensure audience is correct
payload = jwt.decode(
    token,
    jwt_secret,
    algorithms=["HS256"],
    audience="exai-mcp-client",  # Must match server config
    issuer="exai-mcp-server"
)
```

### Issue: "Issuer mismatch"
**Solution:**
```python
# Ensure issuer is correct
payload = jwt.decode(
    token,
    jwt_secret,
    algorithms=["HS256"],
    audience="exai-mcp-client",
    issuer="exai-mcp-server"  # Must match server config
)
```

### Issue: "Token quota exceeded"
**Solution:**
```python
# Token has used all its quota
# Generate a new token with higher quota
payload = {
    "sub": "agent_001",
    "quota": 1000,  # Higher quota
    # ... other claims
}
new_token = jwt.encode(payload, jwt_secret, algorithm="HS256")
```

---

## 📊 Token Monitoring

### Logging Token Usage
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("jwt-auth")

def log_token_usage(token, user_id):
    logger.info(f"Token used by user: {user_id}")
    logger.info(f"Token: {token[:20]}...")

# Log successful authentication
logger.info(f"Authenticated user: {payload['sub']}")
```

### Token Statistics
```sql
-- Check token usage in audit logs
SELECT
    user_id,
    COUNT(*) as request_count,
    MAX(timestamp) as last_usage
FROM audit_logs
WHERE action = 'jwt_authentication'
GROUP BY user_id
ORDER BY request_count DESC;
```

---

## 🔄 Automated Token Management

### Token Manager Class
```python
import jwt
import time
import threading
from datetime import datetime

class TokenManager:
    def __init__(self, jwt_secret, user_id, refresh_callback=None):
        self.jwt_secret = jwt_secret
        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self.token = None
        self._lock = threading.Lock()

    def get_valid_token(self):
        """Get a valid token, refresh if needed"""
        with self._lock:
            if not self.token or self._is_expired():
                self.token = self._generate_token()
                if self.refresh_callback:
                    self.refresh_callback(self.token)
            return self.token

    def _is_expired(self):
        """Check if token is expired or will expire soon"""
        if not self.token:
            return True

        try:
            payload = jwt.decode(
                self.token,
                self.jwt_secret,
                algorithms=["HS256"],
                options={"verify_signature": False}
            )
            # Refresh if expires in next hour
            return payload["exp"] < (time.time() + 3600)
        except:
            return True

    def _generate_token(self):
        """Generate a new token"""
        payload = {
            "sub": self.user_id,
            "name": f"Agent {self.user_id}",
            "iat": int(time.time()),
            "exp": int(time.time()) + 86400,  # 24 hours
            "iss": "exai-mcp-server",
            "aud": "exai-mcp-client",
            "quota": 1000,
            "role": "user"
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

# Usage
token_manager = TokenManager(
    jwt_secret="your_64_character_hex_secret_here",
    user_id="agent_001"
)

# Get valid token (auto-refreshes if needed)
token = token_manager.get_valid_token()
```

---

## 📚 Related Documentation

- **API Key Management**: [02_api_key_management.md](02_api_key_management.md)
- **Security Best Practices**: [03_security_best_practices.md](03_security_best_practices.md)
- **System Architecture**: [../01-architecture-overview/01_system_architecture.md](../01-architecture-overview/01_system_architecture.md)
- **Database Integration**: [../02-database-integration/](../02-database-integration/)

---

## 🔗 Quick Reference

### JWT Claims
| Claim | Description | Required |
|-------|-------------|----------|
| `sub` | User identifier | ✅ Yes |
| `iat` | Issued at timestamp | ✅ Yes |
| `exp` | Expiration timestamp | ✅ Yes |
| `iss` | Issuer | ✅ Yes |
| `aud` | Audience | ✅ Yes |
| `name` | Display name | ❌ No |
| `quota` | Request quota | ❌ No |
| `role` | User role | ❌ No |

### Token Generation Commands
```python
# Python
token = jwt.encode(payload, jwt_secret, algorithm="HS256")

# JavaScript
token = jwt.sign(payload, jwt_secret, { algorithm: "HS256" })

# Bash
jwt encode --secret <secret> <payload>
```

### Token Validation
```python
payload = jwt.decode(
    token,
    jwt_secret,
    algorithms=["HS256"],
    audience="exai-mcp-client",
    issuer="exai-mcp-server"
)
```

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server Security Team
**Status:** ✅ **Complete - JWT Authentication Fully Documented**
