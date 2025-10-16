# Supabase Setup Guide for EXAI MCP Server
**Track 3: Persistent Storage Implementation**  
**Date:** 2025-10-15

---

## 🎯 **OVERVIEW**

This guide walks you through setting up Supabase for persistent storage in EXAI MCP Server.

**What You'll Set Up:**
- Supabase project and database
- Database schema (conversations, messages, files)
- Storage buckets (user-files, generated-files)
- Environment configuration
- Connection testing

**Time Required:** 30-45 minutes

---

## 📋 **PREREQUISITES**

- [ ] Email address for Supabase account
- [ ] Access to `.env` file in project root
- [ ] Python environment with `supabase` package installed

---

## 🚀 **STEP 1: CREATE SUPABASE ACCOUNT & PROJECT**

### 1.1 Sign Up for Supabase

1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub, Google, or email
4. Verify your email address

### 1.2 Create New Project

1. Click "New Project" in dashboard
2. Fill in project details:
   - **Name:** `exai-mcp-server` (or your preferred name)
   - **Database Password:** Generate a strong password (save this!)
   - **Region:** Choose closest to your location
   - **Pricing Plan:** Free tier (sufficient for development)
3. Click "Create new project"
4. Wait 2-3 minutes for project provisioning

### 1.3 Get API Credentials

1. Once project is ready, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (e.g., `https://abcdefgh.supabase.co`)
   - **anon public** key
   - **service_role** key (click "Reveal" to see it)
3. Keep these safe - you'll need them in Step 3

---

## 🗄️ **STEP 2: DEPLOY DATABASE SCHEMA**

### 2.1 Open SQL Editor

1. In Supabase dashboard, navigate to **SQL Editor**
2. Click "New query"

### 2.2 Execute Schema SQL

1. Open the file `supabase/schema.sql` in this project
2. Copy the entire contents
3. Paste into the SQL Editor
4. Click "Run" (or press Ctrl+Enter)
5. Wait for execution to complete (~5 seconds)

### 2.3 Verify Tables Created

1. Navigate to **Table Editor** in dashboard
2. You should see 4 tables:
   - `conversations`
   - `messages`
   - `files`
   - `conversation_files`
3. Click on each table to verify structure

**Expected Tables:**

| Table | Columns | Purpose |
|-------|---------|---------|
| conversations | id, continuation_id, title, metadata, created_at, updated_at | Conversation sessions |
| messages | id, conversation_id, role, content, metadata, created_at | Individual messages |
| files | id, storage_path, original_name, mime_type, size_bytes, file_type, metadata, created_at | File metadata |
| conversation_files | conversation_id, file_id, added_at | Links files to conversations |

---

## 📦 **STEP 3: CREATE STORAGE BUCKETS**

### 3.1 Create User Files Bucket

1. Navigate to **Storage** in dashboard
2. Click "New bucket"
3. Fill in details:
   - **Name:** `user-files`
   - **Public bucket:** Unchecked (private)
   - **File size limit:** 50 MB
   - **Allowed MIME types:** Leave empty (allow all for now)
4. Click "Create bucket"

### 3.2 Create Generated Files Bucket

1. Click "New bucket" again
2. Fill in details:
   - **Name:** `generated-files`
   - **Public bucket:** Unchecked (private)
   - **File size limit:** 10 MB
   - **Allowed MIME types:** Leave empty (allow all for now)
3. Click "Create bucket"

### 3.3 Verify Buckets

You should now see two buckets in the Storage section:
- `user-files` (50 MB limit)
- `generated-files` (10 MB limit)

---

## ⚙️ **STEP 4: CONFIGURE ENVIRONMENT VARIABLES**

### 4.1 Update .env File

1. Open `.env` file in project root
2. Add the following lines (or update if they exist):

```env
# Supabase Configuration (Track 3: Persistent Storage)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

3. Replace the placeholder values with your actual credentials from Step 1.3

**Example:**
```env
SUPABASE_URL=https://abcdefgh.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4.2 Verify .env.example

The `.env.example` file should already have placeholders for Supabase configuration.
If not, they were added in this setup.

---

## 🧪 **STEP 5: TEST CONNECTION**

### 5.1 Install Supabase Python Client

```bash
pip install supabase
```

### 5.2 Test Connection Script

Create a test script `test_supabase_connection.py`:

```python
import os
from dotenv import load_dotenv
from src.storage.supabase_client import get_storage_manager

# Load environment variables
load_dotenv()

# Get storage manager
storage = get_storage_manager()

if not storage.enabled:
    print("❌ Supabase not configured!")
    print("Check your .env file for SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
    exit(1)

print("✅ Supabase storage manager initialized")
print(f"📍 URL: {storage.url}")

# Test conversation creation
try:
    conv_id = storage.save_conversation(
        continuation_id="test-123",
        title="Test Conversation",
        metadata={"test": True}
    )
    
    if conv_id:
        print(f"✅ Created test conversation: {conv_id}")
        
        # Test message creation
        msg_id = storage.save_message(
            conversation_id=conv_id,
            role="user",
            content="Hello, Supabase!",
            metadata={"test": True}
        )
        
        if msg_id:
            print(f"✅ Created test message: {msg_id}")
            
            # Retrieve messages
            messages = storage.get_conversation_messages(conv_id)
            print(f"✅ Retrieved {len(messages)} message(s)")
            
            print("\n🎉 All tests passed! Supabase is working correctly.")
        else:
            print("❌ Failed to create test message")
    else:
        print("❌ Failed to create test conversation")
        
except Exception as e:
    print(f"❌ Error: {e}")
```

### 5.3 Run Test

```bash
python test_supabase_connection.py
```

**Expected Output:**
```
✅ Supabase storage manager initialized
📍 URL: https://abcdefgh.supabase.co
✅ Created test conversation: 12345678-1234-1234-1234-123456789012
✅ Created test message: 87654321-4321-4321-4321-210987654321
✅ Retrieved 1 message(s)

🎉 All tests passed! Supabase is working correctly.
```

---

## ✅ **VERIFICATION CHECKLIST**

After completing all steps, verify:

- [ ] Supabase project created and active
- [ ] 4 database tables exist (conversations, messages, files, conversation_files)
- [ ] 2 storage buckets exist (user-files, generated-files)
- [ ] Environment variables configured in `.env`
- [ ] Python `supabase` package installed
- [ ] Connection test passes successfully

---

## 🔧 **TROUBLESHOOTING**

### Issue: "Supabase not configured"

**Solution:** Check that `.env` file contains:
- `SUPABASE_URL` (not empty)
- `SUPABASE_SERVICE_ROLE_KEY` (not empty)

### Issue: "Failed to create test conversation"

**Possible Causes:**
1. **Wrong API key:** Verify you're using the `service_role` key, not the `anon` key
2. **Network issue:** Check internet connection
3. **Schema not deployed:** Verify tables exist in Table Editor

**Solution:** Double-check credentials and re-run schema.sql

### Issue: "Table does not exist"

**Solution:** Re-run the schema.sql in SQL Editor

### Issue: "Storage bucket not found"

**Solution:** Create buckets manually in Storage section

---

## 🎯 **NEXT STEPS**

Once setup is complete:

1. **Phase 2:** Integrate file storage with existing tools
2. **Phase 3:** Migrate in-memory conversations to Supabase
3. **Phase 4:** Test persistence across container restarts
4. **Phase 5:** Implement Row-Level Security (RLS) for production

---

## 📚 **ADDITIONAL RESOURCES**

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Setup Complete!** 🎉  
You're now ready to use persistent storage in EXAI MCP Server.

