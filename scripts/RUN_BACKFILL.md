# Quick SHA256 Backfill - Instructions

## What This Does
Calculates SHA256 "fingerprints" for 199 existing files in your database so the new file management system can detect duplicates.

## How To Run

### Step 1: Get into Docker container
```bash
docker exec -it exai-mcp-server bash
```

### Step 2: Run the script
```bash
python scripts/quick_backfill_sha256.py
```

### Step 3: Wait ~2-3 minutes
The script will:
- Connect to Supabase
- Find 199 files without SHA256
- Download each file
- Calculate its fingerprint
- Update the database

### Step 4: Verify it worked
You should see:
```
============================================================
BACKFILL COMPLETE
============================================================
✅ Success: 199
❌ Errors:  0
📊 Total:   199
============================================================
```

## If Something Goes Wrong

**Error: "Supabase not configured"**
- Make sure you're inside the Docker container
- Check that `.env.docker` has SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY

**Error: "File not found in bucket"**
- Some files might have been deleted from storage
- This is okay - the script will skip them and continue

**Error: "Connection timeout"**
- Your internet connection might be slow
- Just run the script again - it will only process files that still need hashes

## After Backfill

Once complete, the new file management system will:
- ✅ Detect duplicate files automatically
- ✅ Save storage space by not storing duplicates
- ✅ Work with both old and new files

## Questions?

If you see errors, just share the output and I can help troubleshoot!

