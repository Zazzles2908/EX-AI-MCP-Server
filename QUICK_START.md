# EXAI Supabase Web UI - Quick Start
**Version:** 2.0  
**Date:** 2025-10-14

---

## 🚀 **3-Step Deployment**

### **Step 1: Deploy Edge Function**
```bash
cd c:\Project\EX-AI-MCP-Server
supabase functions deploy exai-chat
```

### **Step 2: Configure Environment**

Go to: https://supabase.com/dashboard/project/mxaazuhlqewmkweewyaz/settings/functions

Click "exai-chat" → Add these variables:
```
EXAI_DAEMON_URL = ws://YOUR_IP:8079
EXAI_AUTH_TOKEN = test-token-12345
EXAI_TIMEOUT_MS = 60000
```

**Find your IP:**
```powershell
ipconfig | Select-String "IPv4"
# Use your local network IP (e.g., 192.168.1.100)
```

### **Step 3: Test**

Open: `web_ui\index_v2.html`

---

## ✅ **What's New in v2**

- ✅ **Security:** XSS protection, input validation
- ✅ **Features:** Markdown, code highlighting, session management
- ✅ **UX:** Copy to clipboard, auto-resize, mobile responsive
- ✅ **Error Handling:** Retry logic, timeouts, status indicators

---

## 📚 **Full Documentation**

- **Deployment Guide:** `docs/05_CURRENT_WORK/DEPLOYMENT_GUIDE.md`
- **Diagnostic Report:** `docs/05_CURRENT_WORK/DIAGNOSTIC_REPORT.md`
- **Final Summary:** `docs/05_CURRENT_WORK/FINAL_SUMMARY.md`

---

## 🐛 **Troubleshooting**

**Connection timeout?**
- Check Docker: `docker-compose ps`
- Check port: `Test-NetConnection localhost -Port 8079`
- Update `EXAI_DAEMON_URL` with your IP (not localhost)

**Authentication failed?**
- Check token matches in `.env` and Edge Function
- Restart Docker: `docker-compose restart`

---

**Ready to deploy! 🎉**

