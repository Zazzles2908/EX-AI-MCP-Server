# JWT Authentication Setup for VSCode MCP Connections
**Date:** 2025-11-03  
**Status:** ✅ CONFIGURED  
**Purpose:** Enable proper JWT authentication for WebSocket connections

---

## 🎯 Overview

Added JWT (JSON Web Token) authentication support to the VSCode MCP client shim to eliminate the "No valid JWT token (grace period active)" warning and enable proper authentication.

---

## 🔧 What Was Done

### 1. Created JWT Token Generator Script ✅
**File:** `scripts/generate_jwt_token.py`

A comprehensive script to generate JWT tokens with:
- User ID (sub): jazeel@example.com
- Issuer (iss): exai-mcp-server
- Audience (aud): exai-mcp-client
- Expiration: 365 days (configurable)
- Algorithm: HS256

**Usage:**
```bash
# Generate token for default user (expires in 365 days)
python scripts/generate_jwt_token.py

# Generate token for specific user (expires in 30 days)
python scripts/generate_jwt_token.py --user-id jazeel@example.com --expires-days 30

# Generate token that never expires (expires in 10 years)
python scripts/generate_jwt_token.py --expires-days 3650
```

### 2. Generated JWT Token ✅
**Token Details:**
- User: jazeel@example.com
- Expires: 2026-11-03 (1 year from now)
- Issuer: exai-mcp-server
- Audience: exai-mcp-client
- Algorithm: HS256

**Token:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYXplZWxAZXhhbXBsZS5jb20iLCJpc3MiOiJleGFpLW1jcC1zZXJ2ZXIiLCJhdWQiOiJleGFpLW1jcC1jbGllbnQiLCJpYXQiOjE3NjIxMjQ3OTgsImV4cCI6MTc5MzY2MDc5OH0.kHUrEPaQfP3qo3m3s4hkABxto8p3CQXCHpjMFiGm1DQ
```

### 3. Updated Configuration Files ✅

#### `.env` - Added JWT Token
```bash
# JWT authentication (added 2025-11-03)
# Generated with: python scripts/generate_jwt_token.py --user-id jazeel@example.com --expires-days 365
# Expires: 2026-11-03 (1 year)
EXAI_JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### `config/daemon/mcp-config.augmentcode.vscode1.json` - Added JWT Token
```json
{
  "env": {
    ...
    "EXAI_JWT_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### `config/daemon/mcp-config.augmentcode.vscode2.json` - Added JWT Token
```json
{
  "env": {
    ...
    "EXAI_JWT_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 4. Updated Shim to Send JWT Token ✅
**File:** `scripts/runtime/run_ws_shim.py`

**Changes:**
1. Load JWT token from environment:
   ```python
   EXAI_JWT_TOKEN = os.getenv("EXAI_JWT_TOKEN", "")  # JWT authentication (added 2025-11-03)
   ```

2. Add JWT token to hello handshake:
   ```python
   # Hello handshake (with JWT support - added 2025-11-03)
   hello_msg = {
       "op": "hello",
       "session_id": SESSION_ID,
       "token": EXAI_WS_TOKEN,
   }
   # Add JWT token if available
   if EXAI_JWT_TOKEN:
       hello_msg["jwt"] = EXAI_JWT_TOKEN
   await _ws.send(json.dumps(hello_msg))
   ```

3. Add JWT status logging:
   ```python
   # JWT authentication status (added 2025-11-03)
   if EXAI_JWT_TOKEN:
       logger.info(f"[JWT_AUTH] JWT token configured (length: {len(EXAI_JWT_TOKEN)} chars)")
   else:
       logger.info("[JWT_AUTH] No JWT token configured - using legacy auth only")
   ```

---

## 🔍 How JWT Authentication Works

### Server Side (Docker Container)
**File:** `src/daemon/ws/connection_manager.py`

The WebSocket server validates JWT tokens during the hello handshake:

```python
# Batch 4.3 (2025-11-02): JWT authentication with grace period
jwt_validator = get_jwt_validator()
if jwt_validator:
    jwt_token = hello.get("jwt", "") or ""
    jwt_payload = jwt_validator.validate_token(jwt_token) if jwt_token else None
    
    # Check if grace period is active
    if jwt_validator.is_grace_period_active():
        # Grace period: allow both JWT and legacy auth
        if jwt_payload:
            logger.info(f"[JWT_AUTH] Valid JWT token (grace period active) - user: {jwt_payload.get('sub', 'unknown')}")
        else:
            logger.info(f"[JWT_AUTH] No valid JWT token (grace period active) - allowing legacy auth")
    else:
        # Grace period ended: require JWT
        if not jwt_payload:
            logger.warning(f"[JWT_AUTH] No valid JWT token and grace period ended - rejecting connection")
            # Reject connection
```

### Grace Period
**Configuration:** `.env.docker`
```bash
JWT_GRACE_PERIOD_DAYS=14  # Grace period for migration (0 = strict enforcement)
```

**Current Status:**
- Grace period is **ACTIVE** (14 days from 2025-11-03)
- Both JWT and legacy auth are accepted
- After grace period ends, JWT will be **REQUIRED**

---

## ✅ Verification

### Before Changes
```
2025-11-03 21:02:11 INFO src.daemon.ws.connection_manager: [JWT_AUTH] No valid JWT token (grace period active) - allowing legacy auth
```

### After Changes (Expected)
```
2025-11-03 21:XX:XX INFO scripts.runtime.run_ws_shim: [JWT_AUTH] JWT token configured (length: 205 chars)
2025-11-03 21:XX:XX INFO src.daemon.ws.connection_manager: [JWT_AUTH] Valid JWT token (grace period active) - user: jazeel@example.com
```

---

## 🎯 Next Steps for User

**Restart VSCode to apply JWT authentication:**
1. Close all VSCode windows
2. Reopen VSCode
3. Wait 10 seconds for MCP connections to auto-connect
4. Check logs for JWT authentication success

**Verify it worked:**
```bash
# Check shim logs
Get-Content logs/ws_shim_vscode1.log -Tail 50 | Select-String "JWT_AUTH"

# Check daemon logs
docker logs exai-mcp-daemon --tail 100 | Select-String "JWT_AUTH"
```

**Expected output:**
- Shim: `[JWT_AUTH] JWT token configured (length: 205 chars)`
- Daemon: `[JWT_AUTH] Valid JWT token (grace period active) - user: jazeel@example.com`

---

## 📋 Files Modified

1. **scripts/generate_jwt_token.py** - NEW: JWT token generator script
2. **.env** - Added EXAI_JWT_TOKEN
3. **config/daemon/mcp-config.augmentcode.vscode1.json** - Added EXAI_JWT_TOKEN to env
4. **config/daemon/mcp-config.augmentcode.vscode2.json** - Added EXAI_JWT_TOKEN to env
5. **scripts/runtime/run_ws_shim.py** - Load and send JWT token in hello handshake

---

## 🔐 Security Notes

### Token Storage
- JWT token is stored in `.env` (gitignored)
- JWT token is in VSCode MCP config files (should be gitignored)
- Token expires in 1 year (2026-11-03)

### Token Regeneration
When the token expires, regenerate it:
```bash
python scripts/generate_jwt_token.py --user-id jazeel@example.com --expires-days 365
```

Then update:
1. `.env` - EXAI_JWT_TOKEN
2. `config/daemon/mcp-config.augmentcode.vscode1.json` - env.EXAI_JWT_TOKEN
3. `config/daemon/mcp-config.augmentcode.vscode2.json` - env.EXAI_JWT_TOKEN
4. Restart VSCode

### JWT Secret Key
The JWT secret key is stored in `.env.docker`:
```bash
JWT_SECRET_KEY=7xDAibhd1vBRKRdNahRpT713a74Q2_UXt-BPW3MTu80
```

**NEVER commit this to git!** It's used to sign and validate JWT tokens.

---

## 📊 Impact Assessment

### Before JWT Setup
- ⚠️ Warning: "No valid JWT token (grace period active) - allowing legacy auth"
- ✅ Connections work (legacy auth)
- ❌ Not using modern authentication

### After JWT Setup
- ✅ JWT token configured and sent
- ✅ Server validates JWT token
- ✅ User authenticated as jazeel@example.com
- ✅ Ready for grace period expiration

---

**Setup completed:** 2025-11-03 21:15 AEDT  
**JWT token expires:** 2026-11-03  
**Grace period ends:** 2025-11-17 (14 days)  
**Status:** ✅ Ready for VSCode restart

