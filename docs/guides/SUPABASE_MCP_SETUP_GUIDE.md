# Supabase MCP for Claude Code - Setup Guide

## 🎯 Quick Fix Summary

The Supabase MCP for Claude Code was failing because it was looking for `SUPABASE_ACCESS_TOKEN` which wasn't defined in your `.env` file.

**Fixed:**
- ✅ Added `SUPABASE_ACCESS_TOKEN` to `.env` file
- ✅ Added documentation on where to get it
- ✅ Configuration in `.mcp.json` is correct

---

## 🔑 Getting Your SUPABASE_ACCESS_TOKEN

### Step 1: Go to Supabase Dashboard
Navigate to: https://supabase.com/dashboard/account/tokens

### Step 2: Create a New Access Token
1. Click **"Generate new token"**
2. Give it a name (e.g., "Claude Code MCP")
3. Set expiration as needed
4. Click **"Generate token"**

### Step 3: Copy the Token
⚠️ **Important:** The token will only be shown once! Copy it immediately.

### Step 4: Update .env File
Edit `c:\Project\EX-AI-MCP-Server\.env` and replace:
```bash
SUPABASE_ACCESS_TOKEN=YOUR_SUPABASE_ACCESS_TOKEN_HERE
```

With your actual token:
```bash
SUPABASE_ACCESS_TOKEN=sbp_1234567890abcdef...
```

---

## 📋 What's Configured

### Environment Variables in .env
```bash
# Management API Access Token (Required for Supabase MCP Server)
SUPABASE_ACCESS_TOKEN=sbp_1234567890abcdef...

# Database Connection
SUPABASE_URL=https://mxaazuhlqewmkweewyaz.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### MCP Configuration in .mcp.json
```json
{
  "mcpServers": {
    "supabase-mcp-full": {
      "command": "npx",
      "args": [
        "-y",
        "@supabase/mcp-server-supabase@latest",
        "--features=account,analytics,auth,database,debugging,development,docs,edge-runtime,functions,logs,migrations,monitoring,projects,realtime,security,storage,branching",
        "--access-token=${SUPABASE_ACCESS_TOKEN}"
      ],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "${SUPABASE_ACCESS_TOKEN}"
      }
    }
  }
}
```

---

## ✅ Available Supabase MCP Tools

The Supabase MCP server provides **17 tool categories**:

1. **account** - Account management
2. **analytics** - Analytics and metrics
3. **auth** - Authentication management
4. **database** - Database operations
5. **debugging** - Debug tools
6. **development** - Development utilities
7. **docs** - Documentation
8. **edge-runtime** - Edge function runtime
9. **functions** - Edge functions
10. **logs** - Log management
11. **migrations** - Database migrations
12. **monitoring** - System monitoring
13. **projects** - Project management
14. **realtime** - Realtime subscriptions
15. **security** - Security settings
16. **storage** - File storage
17. **branching** - Database branching

---

## 🧪 Testing the Supabase MCP

### Test 1: Check Environment Variable
```bash
echo $env:SUPABASE_ACCESS_TOKEN
```
Should return your token, not `YOUR_SUPABASE_ACCESS_TOKEN_HERE`

### Test 2: List MCP Tools
Open Claude Code and try:
```
@supabase-mcp-full list_projects
```

### Test 3: Use a Supabase Tool
```
@supabase-mcp-full database list
```

---

## 🚨 Troubleshooting

### Error: "SUPABASE_ACCESS_TOKEN not found"
**Solution:** Make sure you've updated the `.env` file with your actual token

### Error: "Invalid access token"
**Solution:** The token may have expired. Generate a new one from the dashboard

### Error: "Permission denied"
**Solution:** Make sure the token has the necessary permissions in Supabase

### MCP tools not showing
**Solution:** Restart Claude Code after updating the environment variable

---

## 📚 Usage Examples

### List All Projects
```
@supabase-mcp-full list_projects
```

### Check Database Tables
```
@supabase-mcp-full database list
```

### View Edge Functions
```
@supabase-mcp-full functions list
```

### Monitor Project
```
@supabase-mcp-full monitoring status
```

### Check Auth Settings
```
@supabase-mcp-full auth settings
```

---

## 🔐 Security Notes

- **Keep your access token secret** - Never commit it to version control
- **The `.env` file is already in `.gitignore`** - You're safe there
- **Use environment variables** - The token is loaded via `${SUPABASE_ACCESS_TOKEN}`
- **Rotate tokens regularly** - For production use, rotate tokens periodically

---

## ✅ Verification Checklist

- [ ] Access token created at https://supabase.com/dashboard/account/tokens
- [ ] `.env` file updated with actual token (not placeholder)
- [ ] Claude Code restarted
- [ ] `@supabase-mcp-full list_projects` returns results
- [ ] At least one Supabase MCP tool executed successfully

---

## 🎉 Next Steps

Now that Supabase MCP is configured, you can:

1. **Manage your Supabase projects** directly from Claude Code
2. **Query databases** and view tables
3. **Deploy edge functions** and manage them
4. **Monitor project health** and logs
5. **Manage authentication** and security settings

All through Claude Code's MCP integration!

---

**Status:** ✅ **Configuration Complete - Token Required**

**Version:** 1.0.0
**Last Updated:** 2025-11-11
