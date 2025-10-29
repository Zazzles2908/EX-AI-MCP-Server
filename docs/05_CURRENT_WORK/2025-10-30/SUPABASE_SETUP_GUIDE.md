# Supabase Universal File Hub - Setup Guide

**Date:** 2025-10-30  
**Status:** Setup Instructions  
**EXAI Consultation ID:** bbfac185-ce22-4140-9b30-b3fda4c362d9

---

## 📋 OVERVIEW

This guide provides step-by-step instructions for setting up the Supabase Universal File Hub architecture for EXAI-MCP-Server.

**Architecture:**
```
Application (anywhere) 
  → Upload to Supabase Storage
  → Trigger EXAI-MCP-Server processing
  → EXAI downloads from Supabase
  → EXAI processes with AI
  → EXAI uploads result to Supabase
  → Application downloads result
```

---

## 🚀 STEP 1: CREATE SUPABASE PROJECT

### 1.1 Sign Up and Create Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up or log in to your account
3. Click **"New Project"**
4. Configure your project:
   - **Name:** `exai-file-hub` (or your preferred name)
   - **Database Password:** Generate a strong password (save this!)
   - **Region:** Choose closest to your location (e.g., `us-west-1`)
   - **Pricing Plan:** Free tier (sufficient for 5 users initially)

5. Click **"Create new project"** and wait for provisioning (~2 minutes)

### 1.2 Get API Credentials

Once the project is ready:

1. Navigate to **Settings** → **API**
2. Copy the following values:
   - **Project URL:** `https://your-project-id.supabase.co`
   - **anon/public key:** `eyJhbGc...` (long JWT token)
   - **service_role key:** `eyJhbGc...` (different JWT token)

3. Navigate to **Settings** → **Database**
4. Copy the **Connection string** (URI format)

**⚠️ IMPORTANT:** Keep the `service_role` key secret! Never expose it in client-side code.

---

## 🗄️ STEP 2: CREATE STORAGE BUCKETS

### 2.1 Create Buckets via UI

1. Navigate to **Storage** in the left sidebar
2. Click **"New bucket"** and create:

**Bucket 1: user-files**
- Name: `user-files`
- Public: ❌ (unchecked)
- File size limit: 50MB
- Allowed MIME types: Leave empty (all types)

**Bucket 2: results**
- Name: `results`
- Public: ❌ (unchecked)
- File size limit: 100MB
- Allowed MIME types: Leave empty (all types)

**Bucket 3: generated-files**
- Name: `generated-files`
- Public: ❌ (unchecked)
- File size limit: 50MB
- Allowed MIME types: Leave empty (all types)

### 2.2 Verify Buckets

You should see all three buckets listed in the Storage section.

---

## 📊 STEP 3: CREATE DATABASE TABLES

### 3.1 Run SQL Schema

1. Navigate to **SQL Editor** in the left sidebar
2. Click **"New query"**
3. Copy and paste the SQL from `scripts/supabase/schema.sql` (see below)
4. Click **"Run"** to execute

The schema creates:
- `file_operations` table - Track file lifecycle
- `file_metadata` table - File information and access patterns
- Indexes for performance
- Triggers for automatic timestamp updates

### 3.2 Verify Tables

1. Navigate to **Table Editor**
2. You should see:
   - `file_operations`
   - `file_metadata`

---

## 🔒 STEP 4: CONFIGURE ROW LEVEL SECURITY (RLS)

### 4.1 Run RLS Policies

1. Navigate to **SQL Editor**
2. Click **"New query"**
3. Copy and paste the SQL from `scripts/supabase/rls_policies.sql` (see below)
4. Click **"Run"** to execute

This creates:
- RLS policies for database tables
- Storage bucket policies
- User isolation (users can only access their own files)

### 4.2 Verify RLS

1. Navigate to **Authentication** → **Policies**
2. You should see policies for:
   - `file_operations` (4 policies: SELECT, INSERT, UPDATE, DELETE)
   - `file_metadata` (4 policies: SELECT, INSERT, UPDATE, DELETE)
   - `storage.objects` (policies for each bucket)

---

## ⚙️ STEP 5: CONFIGURE ENVIRONMENT VARIABLES

### 5.1 Update .env File

Add the following to your `.env` file in the project root:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Database Configuration (optional - for direct DB access)
SUPABASE_DB_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project-id.supabase.co:5432/postgres

# File Hub Configuration
FILE_HUB_CACHE_DIR=/tmp/exai-file-cache
FILE_HUB_CACHE_SIZE_MB=1024
FILE_HUB_CACHE_TTL_HOURS=24
```

**Replace:**
- `your-project-id` with your actual Supabase project ID
- `your-anon-key-here` with the anon/public key from Step 1.2
- `your-service-role-key-here` with the service_role key from Step 1.2
- `[YOUR-PASSWORD]` with your database password from Step 1.1

### 5.2 Verify Environment Variables

Run the verification script:

```bash
python scripts/supabase/verify_config.py
```

This checks:
- ✅ All required environment variables are set
- ✅ Supabase connection is working
- ✅ Buckets are accessible
- ✅ Database tables exist

---

## 🧪 STEP 6: TEST THE SETUP

### 6.1 Run Basic Tests

```bash
# Test Supabase connection
python scripts/supabase/test_connection.py

# Test file upload/download
python scripts/supabase/test_file_operations.py

# Test RLS policies
python scripts/supabase/test_rls_policies.py
```

### 6.2 Expected Results

All tests should pass:
- ✅ Connection to Supabase successful
- ✅ File upload to user-files bucket successful
- ✅ File download from user-files bucket successful
- ✅ Metadata tracking working
- ✅ RLS policies enforcing user isolation

---

## 📝 STEP 7: INSTALL PYTHON DEPENDENCIES

### 7.1 Install Supabase Client

```bash
pip install supabase
```

### 7.2 Verify Installation

```python
python -c "from supabase import create_client; print('Supabase client installed successfully')"
```

---

## ✅ SETUP COMPLETE CHECKLIST

- [ ] Supabase project created
- [ ] API credentials copied and saved
- [ ] Three storage buckets created (user-files, results, generated-files)
- [ ] Database tables created (file_operations, file_metadata)
- [ ] RLS policies configured
- [ ] Environment variables set in .env
- [ ] Python dependencies installed
- [ ] All tests passing

---

## 🔧 TROUBLESHOOTING

### Issue: "Invalid API key"
**Solution:** Double-check that you copied the correct anon key from Settings → API

### Issue: "Bucket not found"
**Solution:** Verify bucket names are exactly: `user-files`, `results`, `generated-files`

### Issue: "Permission denied"
**Solution:** Check that RLS policies are correctly configured

### Issue: "Connection timeout"
**Solution:** Check your internet connection and Supabase project status

---

## 📚 NEXT STEPS

Once setup is complete:

1. **Implement Upload Utilities** - See `tools/supabase_upload.py`
2. **Implement Download Utilities** - See `tools/supabase_download.py`
3. **Integrate with Existing Tools** - Update `smart_file_query.py`
4. **Test End-to-End** - Upload → Process → Download workflow

---

## 🔗 USEFUL LINKS

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Storage Guide](https://supabase.com/docs/guides/storage)
- [Supabase RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Python Client Documentation](https://supabase.com/docs/reference/python/introduction)

---

**For Questions:** Consult EXAI using continuation_id: bbfac185-ce22-4140-9b30-b3fda4c362d9

