# Environment Files - Quick Reference

**Purpose:** Quick guide to environment files
**Status:** Should be read alongside ENVIRONMENT_SETUP.md

---

## 📋 The 5 Environment Files

```
.env                     ← MODIFY: Your local settings (API keys, etc.)
.env.docker             ← MODIFY: Docker container settings
.env.example            ← REFERENCE: Copy from this to create .env
.env.docker.template    ← DEPRECATED: Don't use (replaced by .env.example)
.env.patched            ← TEMPORARY: Delete after use
```

---

## 🚀 Quick Start

### **1. Copy Template**
```bash
cp .env.example .env
cp .env.example .env.docker
```

### **2. Add Your API Keys**
Edit both `.env` and `.env.docker`:
```bash
GLM_API_KEY=your_actual_key_here
KIMI_API_KEY=your_actual_key_here
MINIMAX_M2_KEY=your_actual_key_here
```

### **3. Verify**
```bash
python -c "from dotenv import load_dotenv; load_dotenv('.env'); print('OK')"
```

---

## 🔒 What's Hidden from Git

**These files are in .gitignore (not committed):**
- `.env` ❌ (contains real API keys)
- `.env.docker` ❌ (contains real API keys)
- `.env.patched` ❌ (temporary only)

**These files are committed (safe to share):**
- `.env.example` ✅ (template with placeholder values)
- `.env.docker.template` ✅ (deprecated but committed)

---

## 📚 For More Details

See **[ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)** for:
- Detailed setup instructions
- All configuration options
- Docker-specific settings
- Troubleshooting guide

---

**Remember: NEVER commit files with real API keys!**
