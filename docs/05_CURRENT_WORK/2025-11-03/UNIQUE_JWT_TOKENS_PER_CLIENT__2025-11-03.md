# Unique JWT Tokens Per MCP Client
**Date:** 2025-11-03  
**Status:** ✅ COMPLETED  
**Purpose:** Assign unique JWT tokens to each MCP client for better security and tracking

---

## 🎯 Why Unique Tokens?

### Previous Implementation ❌
- **Single JWT token** shared across all clients
- User: `jazeel@example.com`
- **Problem:** No way to distinguish which client is connecting in logs
- **Security Risk:** Token compromise affects all clients

### New Implementation ✅
- **Unique JWT token** per client
- **VSCode Instance 1:** `vscode1@exai-mcp.local`
- **VSCode Instance 2:** `vscode2@exai-mcp.local`
- **Claude Desktop:** `claude@exai-mcp.local`

---

## ✅ Benefits

### 1. Better Security 🔐
- Token compromise affects only one client
- Can revoke individual client access
- Separate authentication per instance

### 2. Better Tracking 📊
- Can identify which client in logs
- Separate user IDs per client
- Clear audit trail

### 3. Better Debugging 🐛
- Know which VSCode instance is having issues
- Separate log entries per client
- Easier troubleshooting

### 4. Better Auditing 📝
- Track usage per client
- Monitor individual client behavior
- Compliance and security reporting

---

## 🔧 Implementation

### Generated Unique Tokens
**Script:** `scripts/generate_all_jwt_tokens.py`

```bash
python scripts/generate_all_jwt_tokens.py
```

**Output:**
```
✅ Generated token for EXAI-WS-VSCode1
✅ Generated token for EXAI-WS-VSCode2
✅ Generated token for Claude Desktop
```

### Token Details

#### VSCode Instance 1
- **User ID:** `vscode1@exai-mcp.local`
- **Config:** `config/daemon/mcp-config.augmentcode.vscode1.json`
- **Token:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ2c2NvZGUxQGV4YWktbWNwLmxvY2FsIiwiaXNzIjoiZXhhaS1tY3Atc2VydmVyIiwiYXVkIjoiZXhhaS1tY3AtY2xpZW50IiwiaWF0IjoxNzYyMTI1MDczLCJleHAiOjE3OTM2NjEwNzN9.ykhiz2bjw3GEXnAif_2CedGQqb2an4Qr0mmuIMsBZ3U`

#### VSCode Instance 2
- **User ID:** `vscode2@exai-mcp.local`
- **Config:** `config/daemon/mcp-config.augmentcode.vscode2.json`
- **Token:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ2c2NvZGUyQGV4YWktbWNwLmxvY2FsIiwiaXNzIjoiZXhhaS1tY3Atc2VydmVyIiwiYXVkIjoiZXhhaS1tY3AtY2xpZW50IiwiaWF0IjoxNzYyMTI1MDczLCJleHAiOjE3OTM2NjEwNzN9.gBhbfK5WHvgXrCVuDmL3hwFvVKQM1i0hsC9m1JDkPJo`

#### Claude Desktop
- **User ID:** `claude@exai-mcp.local`
- **Config:** `config/daemon/mcp-config.claude.json`
- **Token:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjbGF1ZGVAZXhhaS1tY3AubG9jYWwiLCJpc3MiOiJleGFpLW1jcC1zZXJ2ZXIiLCJhdWQiOiJleGFpLW1jcC1jbGllbnQiLCJpYXQiOjE3NjIxMjUwNzMsImV4cCI6MTc5MzY2MTA3M30.hVzyioI0JRDgGnbVIq7NYZOsPiiOYjjuRXwAPBVtFn0`

**All tokens expire:** 2026-11-03 (1 year)

---

## 📋 Configuration Files Updated

### 1. VSCode Instance 1
**File:** `config/daemon/mcp-config.augmentcode.vscode1.json`

```json
{
  "env": {
    ...
    "EXAI_JWT_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ2c2NvZGUxQGV4YWktbWNwLmxvY2FsIi4uLg=="
  }
}
```

### 2. VSCode Instance 2
**File:** `config/daemon/mcp-config.augmentcode.vscode2.json`

```json
{
  "env": {
    ...
    "EXAI_JWT_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ2c2NvZGUyQGV4YWktbWNwLmxvY2FsIi4uLg=="
  }
}
```

### 3. Claude Desktop ✅ NEW
**File:** `config/daemon/mcp-config.claude.json`

```json
{
  "env": {
    ...
    "EXAI_JWT_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjbGF1ZGVAZXhhaS1tY3AubG9jYWwiLi4uPQ=="
  }
}
```

---

## 📊 Expected Log Output

### VSCode Instance 1
```
[JWT_AUTH] JWT token configured (length: 205 chars)
[JWT_AUTH] Valid JWT token (grace period active) - user: vscode1@exai-mcp.local
```

### VSCode Instance 2
```
[JWT_AUTH] JWT token configured (length: 205 chars)
[JWT_AUTH] Valid JWT token (grace period active) - user: vscode2@exai-mcp.local
```

### Claude Desktop
```
[JWT_AUTH] JWT token configured (length: 205 chars)
[JWT_AUTH] Valid JWT token (grace period active) - user: claude@exai-mcp.local
```

**Now you can easily identify which client is connecting!** 🎉

---

## 🔄 Token Regeneration

When tokens expire (2026-11-03), regenerate all at once:

```bash
python scripts/generate_all_jwt_tokens.py
```

Then update:
1. `config/daemon/mcp-config.augmentcode.vscode1.json`
2. `config/daemon/mcp-config.augmentcode.vscode2.json`
3. `config/daemon/mcp-config.claude.json`
4. Restart VSCode / Claude Desktop

---

## 📝 Files Modified

### New Files
1. **scripts/generate_all_jwt_tokens.py** - Generate all three tokens at once

### Updated Files
1. **config/daemon/mcp-config.augmentcode.vscode1.json** - Unique token for vscode1
2. **config/daemon/mcp-config.augmentcode.vscode2.json** - Unique token for vscode2
3. **config/daemon/mcp-config.claude.json** - Added JWT support with unique token
4. **.env** - Added all three tokens for reference (gitignored)
5. **docs/05_CURRENT_WORK/2025-11-03/JWT_AUTHENTICATION_SETUP__2025-11-03.md** - Updated docs

---

## 🎯 Next Steps

1. **Restart VSCode** to apply new JWT tokens
2. **Restart Claude Desktop** (if using)
3. **Check logs** to verify unique user IDs appear
4. **Monitor** for JWT authentication success messages

---

## 🔐 Security Notes

### Token Storage
- Tokens stored in config files (should be gitignored)
- `.env` contains all tokens for reference (gitignored)
- Never commit tokens to git

### Token Revocation
To revoke a specific client's access:
1. Remove token from that client's config file
2. Restart the client
3. Client will fall back to legacy auth (during grace period)
4. After grace period: client will be rejected

### Token Rotation
- Tokens expire in 1 year (2026-11-03)
- Regenerate before expiration
- Can rotate individual client tokens independently

---

**Implementation completed:** 2025-11-03 21:25 AEDT  
**Tokens expire:** 2026-11-03  
**Status:** ✅ Ready for client restart

