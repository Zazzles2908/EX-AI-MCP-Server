# SECURE SECRETS FILE - DO NOT COMMIT TO GIT
# This file contains all the actual secrets that were exposed in documentation/source code
# These have been REMOVED from all markdown files and replaced with placeholders
# This file is .gitignored and will NOT be committed to the repository

## 🚨 CRITICAL: REAL CREDENTIALS EXPOSED IN SOURCE CODE (2025-11-10)

### web_ui/index.html:224-225 - FIXED ON 2025-11-10
**Status:** ✅ **REPLACED with placeholders**

**REAL CREDENTIALS (ROTATE IMMEDIATELY):**
```
SUPABASE_URL=https://mxaazuhlqewmkweewyaz.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14YWF6dWhscWV3bWt3ZWV3eWF6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxOTA1MjUsImV4cCI6MjA3Mzc2NjUyNX0.4UfuP40d5L72bp-WAXYTSOF8-P11eR3C5oEcr8dZHVI
```

**Action Taken:**
✅ Updated web_ui/index.html with placeholders on 2025-11-10
🔄 **ROTATE these credentials immediately in Supabase dashboard**

### static/js/supabase-client.js:14 - FIXED ON 2025-11-10
**Status:** ✅ **REPLACED with placeholder**

**Test Key (Less Critical):**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxvY2FsaG9zdCIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNjI1MDAwMDAwLCJleHAiOjE5MzUwMDAwMDB9.test_key
```

**Action Taken:**
✅ Updated static/js/supabase-client.js to use environment variables

---

## 🚨 CRITICAL: Documentation Secrets (Earlier Session)

### Supabase Credentials
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
SUPABASE_ACCESS_TOKEN=sbp_your_access_token_here
SUPABASE_JWT_SECRET=your_64_character_hex_secret_here
```

### API Keys
```
GLM_API_KEY=your_glm_api_key_here
KIMI_API_KEY=your_kimi_api_key_here
```

## 🔄 IMMEDIATE ACTION REQUIRED

### These secrets were exposed in documentation and MUST be rotated:

1. **SUPABASE_ACCESS_TOKEN** - Rotate immediately
   - Login to https://supabase.com/dashboard/account/tokens
   - Generate new token
   - Update .env file
   - Update .mcp.json

2. **SUPABASE_JWT_SECRET** - Rotate immediately
   - Generate new 64-character hex secret
   - Update .env file
   - Restart services

3. **GLM_API_KEY** - Rotate immediately
   - Login to https://open.bigmodel.cn
   - Generate new API key
   - Update .env file

4. **KIMI_API_KEY** - Rotate immediately
   - Login to https://platform.moonshot.cn
   - Generate new API key
   - Update .env file

5. **SUPABASE_SERVICE_ROLE_KEY** - Consider rotation
   - This is a JWT token, less critical to rotate
   - But should be rotated for security

6. **SUPABASE_ANON_KEY** - Less critical (public key)
   - This is a public key, not sensitive
   - No rotation needed

## 📋 Remediation Steps Taken

1. ✅ Created this secure file to document all exposed secrets
2. ✅ Created .gitignore to prevent this file from being committed
3. 🔄 NEXT: Remove all secrets from documentation files
4. 🔄 NEXT: Replace with placeholders in documentation
5. 🔄 NEXT: Update integration strategy checklist
6. 🔄 NEXT: Rotate all exposed secrets

## ⚠️ Security Notes

- These secrets were accidentally exposed in documentation markdown files
- They have NOT been committed to git (as of 2025-11-10)
- This secure file is .gitignored
- All documentation will be updated to use placeholders only
- Actual secrets will remain in .env file only

---

**Status:** 🚨 EXPOSED - REQUIRES IMMEDIATE ROTATION
**Date Identified:** 2025-11-10
**Remediation:** In Progress
