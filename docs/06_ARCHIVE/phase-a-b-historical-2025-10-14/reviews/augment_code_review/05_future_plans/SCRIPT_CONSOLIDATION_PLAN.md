# Script Consolidation Plan (Deferred to Post-Implementation)

**Purpose:** Plan for consolidating scattered scripts into a centralized, organized structure.

**Status:** 🟡 **DEFERRED** - To be executed after Week 3 (all P0/P1/P2 fixes complete)  
**Priority:** P3 (Nice-to-have, organizational improvement)  
**Risk Level:** 🔴 **HIGH** (breaks MCP client configurations)  
**Effort:** Medium (2-3 hours including testing)  
**Created:** 2025-10-05

---

## 🎯 Objective

Consolidate scattered scripts from 3 locations (root, scripts/, scripts/ws/) into a centralized, organized structure with clear categories and better discoverability.

---

## 📊 Current State (Chaotic)

```
Root/
├── run-server.ps1          # Setup & launch (Windows)
├── run-server.sh           # Setup & launch (Unix)
│
scripts/
├── mcp_server_wrapper.py   # Auggie wrapper
├── run_ws_shim.py          # WS shim (stdio ↔ WebSocket bridge)
├── ws_start.ps1            # Start daemon/shim
├── ws_stop.ps1             # Stop daemon
├── force_restart.ps1       # Force restart (kill all Python)
├── [50+ other scripts]     # Various utilities, diagnostics, etc.
│
scripts/ws/
├── run_ws_daemon.py        # Daemon launcher
├── ws_status.py            # Status check
├── ws_chat_once.py         # Test: single message
├── ws_chat_roundtrip.py    # Test: multiple messages
├── ws_chat_analyze_files.py # Test: file analysis
└── ws_chat_review_once.py  # Test: code review
```

**Problems:**
- Scripts scattered across 3 locations
- Hard to find the right script for a task
- No clear categorization
- Maintenance burden (where to add new scripts?)

---

## 🎯 Proposed State (Organized)

```
scripts/
├── setup/                  # Setup & installation
│   ├── run-server.ps1      # Moved from root
│   ├── run-server.sh       # Moved from root
│   └── README.md           # Setup guide
│
├── daemon/                 # Daemon management
│   ├── start.ps1           # Renamed from ws_start.ps1
│   ├── stop.ps1            # Renamed from ws_stop.ps1
│   ├── restart.ps1         # Renamed from force_restart.ps1
│   ├── status.py           # Moved from ws/ws_status.py
│   ├── run_daemon.py       # Moved from ws/run_ws_daemon.py
│   └── README.md           # Daemon management guide
│
├── client/                 # Client wrappers & shims
│   ├── mcp_wrapper.py      # Renamed from mcp_server_wrapper.py
│   ├── ws_shim.py          # Renamed from run_ws_shim.py
│   └── README.md           # Client integration guide
│
├── testing/                # Test scripts
│   ├── ws_chat_once.py     # Moved from ws/
│   ├── ws_chat_roundtrip.py # Moved from ws/
│   ├── ws_chat_analyze_files.py # Moved from ws/
│   ├── ws_chat_review_once.py # Moved from ws/
│   └── README.md           # Testing guide
│
├── diagnostics/            # Existing diagnostics scripts
│   └── [existing files]
│
├── docs_cleanup/           # Existing docs cleanup scripts
│   └── [existing files]
│
├── health/                 # Existing health check scripts
│   └── [existing files]
│
├── maintenance/            # Existing maintenance scripts
│   └── [existing files]
│
└── tools/                  # Existing tool scripts
    └── [existing files]
```

**Benefits:**
- Clear categorization by purpose
- Easy to find the right script
- Better discoverability for new users
- Consistent naming conventions
- README.md in each category for guidance

---

## 🚨 Breaking Changes & Migration Plan

### **Files That Will Break**

#### **1. MCP Client Configurations (3 files)**

**Daemon/mcp-config.auggie.json** (line 7)
```json
// BEFORE
"args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/run_ws_shim.py"]

// AFTER
"args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/client/ws_shim.py"]
```

**Daemon/mcp-config.augmentcode.json** (line 7)
```json
// BEFORE
"args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/run_ws_shim.py"]

// AFTER
"args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/client/ws_shim.py"]
```

**Daemon/mcp-config.claude.json** (line 7)
```json
// BEFORE
"args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/run_ws_shim.py"]

// AFTER
"args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/client/ws_shim.py"]
```

#### **2. Internal Script References**

**scripts/run_ws_shim.py** (line 138) → **scripts/client/ws_shim.py**
```python
# BEFORE
daemon = str(_repo_root / "scripts" / "run_ws_daemon.py")

# AFTER
daemon = str(_repo_root / "scripts" / "daemon" / "run_daemon.py")
```

**scripts/ws_start.ps1** (lines 25, 30) → **scripts/daemon/start.ps1**
```powershell
# BEFORE
& $Py "scripts\run_ws_shim.py"
& $Py "scripts\ws\run_ws_daemon.py"

# AFTER
& $Py "scripts\client\ws_shim.py"
& $Py "scripts\daemon\run_daemon.py"
```

**scripts/force_restart.ps1** (lines 17, 67) → **scripts/daemon/restart.ps1**
```powershell
# BEFORE
powershell -ExecutionPolicy Bypass -File "$Root\scripts\ws_stop.ps1" -Force
powershell -ExecutionPolicy Bypass -File "$Root\scripts\ws_start.ps1"

# AFTER
powershell -ExecutionPolicy Bypass -File "$Root\scripts\daemon\stop.ps1" -Force
powershell -ExecutionPolicy Bypass -File "$Root\scripts\daemon\start.ps1"
```

---

## 📋 Migration Steps (Detailed)

### **Phase 1: Preparation (30 minutes)**

1. **Create new directory structure**
   ```powershell
   New-Item -ItemType Directory -Path "scripts/setup" -Force
   New-Item -ItemType Directory -Path "scripts/daemon" -Force
   New-Item -ItemType Directory -Path "scripts/client" -Force
   New-Item -ItemType Directory -Path "scripts/testing" -Force
   ```

2. **Create README.md files for each category**
   - `scripts/setup/README.md` - Setup and installation guide
   - `scripts/daemon/README.md` - Daemon management guide
   - `scripts/client/README.md` - Client integration guide
   - `scripts/testing/README.md` - Testing guide

3. **Create backward compatibility symlinks (optional)**
   ```powershell
   # Keep old paths working temporarily
   New-Item -ItemType SymbolicLink -Path "scripts/run_ws_shim.py" -Target "client/ws_shim.py"
   New-Item -ItemType SymbolicLink -Path "scripts/ws_start.ps1" -Target "daemon/start.ps1"
   New-Item -ItemType SymbolicLink -Path "scripts/ws_stop.ps1" -Target "daemon/stop.ps1"
   New-Item -ItemType SymbolicLink -Path "scripts/force_restart.ps1" -Target "daemon/restart.ps1"
   ```

### **Phase 2: Move Files (15 minutes)**

1. **Move setup scripts**
   ```powershell
   Move-Item "run-server.ps1" "scripts/setup/"
   Move-Item "run-server.sh" "scripts/setup/"
   ```

2. **Move daemon scripts**
   ```powershell
   Move-Item "scripts/ws_start.ps1" "scripts/daemon/start.ps1"
   Move-Item "scripts/ws_stop.ps1" "scripts/daemon/stop.ps1"
   Move-Item "scripts/force_restart.ps1" "scripts/daemon/restart.ps1"
   Move-Item "scripts/ws/run_ws_daemon.py" "scripts/daemon/run_daemon.py"
   Move-Item "scripts/ws/ws_status.py" "scripts/daemon/status.py"
   ```

3. **Move client scripts**
   ```powershell
   Move-Item "scripts/mcp_server_wrapper.py" "scripts/client/mcp_wrapper.py"
   Move-Item "scripts/run_ws_shim.py" "scripts/client/ws_shim.py"
   ```

4. **Move testing scripts**
   ```powershell
   Move-Item "scripts/ws/ws_chat_once.py" "scripts/testing/"
   Move-Item "scripts/ws/ws_chat_roundtrip.py" "scripts/testing/"
   Move-Item "scripts/ws/ws_chat_analyze_files.py" "scripts/testing/"
   Move-Item "scripts/ws/ws_chat_review_once.py" "scripts/testing/"
   ```

5. **Remove empty ws/ directory**
   ```powershell
   Remove-Item "scripts/ws" -Recurse -Force
   ```

### **Phase 3: Update References (30 minutes)**

1. **Update MCP client configurations (3 files)**
   - `Daemon/mcp-config.auggie.json`
   - `Daemon/mcp-config.augmentcode.json`
   - `Daemon/mcp-config.claude.json`
   - Change: `scripts/run_ws_shim.py` → `scripts/client/ws_shim.py`

2. **Update internal script references**
   - `scripts/client/ws_shim.py` (line 138)
     - Change: `scripts/run_ws_daemon.py` → `scripts/daemon/run_daemon.py`
   - `scripts/daemon/start.ps1` (lines 25, 30)
     - Change: `scripts\run_ws_shim.py` → `scripts\client\ws_shim.py`
     - Change: `scripts\ws\run_ws_daemon.py` → `scripts\daemon\run_daemon.py`
   - `scripts/daemon/restart.ps1` (lines 17, 67)
     - Change: `scripts\ws_stop.ps1` → `scripts\daemon\stop.ps1`
     - Change: `scripts\ws_start.ps1` → `scripts\daemon\start.ps1`

3. **Update documentation**
   - `docs/reviews/augment_code_review/SERVER_ARCHITECTURE_MAP.md`
   - `docs/reviews/augment_code_review/SCRIPT_INTERCONNECTIONS.md`
   - Update all script paths to new locations

### **Phase 4: Testing (45 minutes)**

1. **Test daemon management**
   ```powershell
   # Start daemon
   .\scripts\daemon\start.ps1
   
   # Check status
   python scripts\daemon\status.py
   
   # Stop daemon
   .\scripts\daemon\stop.ps1
   
   # Restart daemon
   .\scripts\daemon\restart.ps1
   ```

2. **Test MCP client connections**
   - Test Auggie CLI connection
   - Test Augment Code (VSCode) connection
   - Test Claude Desktop connection
   - Verify all clients can connect and call tools

3. **Test WebSocket shim**
   ```powershell
   # Start shim
   .\scripts\daemon\start.ps1 -Shim
   
   # Test connection
   python scripts\testing\ws_chat_once.py
   ```

4. **Test backward compatibility (if symlinks created)**
   - Verify old paths still work via symlinks
   - Test that old scripts can still be called

### **Phase 5: Cleanup (15 minutes)**

1. **Remove backward compatibility symlinks (if created)**
   ```powershell
   Remove-Item "scripts/run_ws_shim.py"
   Remove-Item "scripts/ws_start.ps1"
   Remove-Item "scripts/ws_stop.ps1"
   Remove-Item "scripts/force_restart.ps1"
   ```

2. **Update .gitignore if needed**
   - Add any new directories to .gitignore if necessary

3. **Commit changes**
   ```bash
   git add .
   git commit -m "refactor: consolidate scripts into organized structure

   - Move setup scripts to scripts/setup/
   - Move daemon scripts to scripts/daemon/
   - Move client scripts to scripts/client/
   - Move testing scripts to scripts/testing/
   - Update all references to new paths
   - Add README.md to each category
   - Remove empty scripts/ws/ directory
   
   BREAKING CHANGE: Script paths have changed. Update MCP client configs."
   ```

---

## ⚠️ Risks & Mitigation

### **Risk 1: Breaking MCP Client Connections**
- **Probability:** High (100% if configs not updated)
- **Impact:** Critical (users can't connect)
- **Mitigation:**
  - Update all 3 MCP configs simultaneously
  - Test each client connection before committing
  - Create symlinks for backward compatibility during transition
  - Document migration in release notes

### **Risk 2: Missing a Reference**
- **Probability:** Medium (easy to miss a reference)
- **Impact:** High (script fails at runtime)
- **Mitigation:**
  - Use grep to find all references: `grep -r "run_ws_shim.py" .`
  - Test all affected scripts thoroughly
  - Keep symlinks for 1-2 releases as safety net

### **Risk 3: Breaking User Scripts**
- **Probability:** Low (most users use MCP clients, not scripts directly)
- **Impact:** Medium (user scripts fail)
- **Mitigation:**
  - Document migration in CHANGELOG.md
  - Provide migration guide for users
  - Keep symlinks for backward compatibility

---

## 📊 Effort Estimate

| Phase | Time | Difficulty |
|-------|------|------------|
| Preparation | 30 min | Easy |
| Move Files | 15 min | Easy |
| Update References | 30 min | Medium |
| Testing | 45 min | Medium |
| Cleanup | 15 min | Easy |
| **TOTAL** | **2h 15min** | **Medium** |

---

## ✅ Success Criteria

- [ ] All scripts moved to new locations
- [ ] All references updated (MCP configs, internal scripts, docs)
- [ ] All 3 MCP clients can connect successfully
- [ ] Daemon management scripts work (start, stop, restart, status)
- [ ] WebSocket shim works
- [ ] Testing scripts work
- [ ] Documentation updated
- [ ] No broken references (grep confirms)
- [ ] Backward compatibility symlinks work (if created)
- [ ] Changes committed to git

---

## 📅 Recommended Timeline

**When to Execute:** After Week 3 (all P0/P1/P2 fixes complete)

**Suggested Approach:**
1. Complete Master Fix Implementation (Weeks 1-3)
2. Test thoroughly and ensure system is stable
3. Create a separate branch for script consolidation
4. Execute migration plan in one sitting (2-3 hours)
5. Test thoroughly on the branch
6. Merge to main after validation

**Alternative Approach (Lower Risk):**
1. Create symlinks first (no breaking changes)
2. Update documentation to reference new paths
3. Gradually migrate users to new paths
4. Remove symlinks after 1-2 releases

---

## 📝 Notes

- This is a **P3 (nice-to-have)** improvement, not critical
- Focus on **P0/P1/P2 fixes first** (timeout hierarchy, progress heartbeat, logging, expert validation, etc.)
- Script consolidation is **organizational cleanup**, not a functional fix
- **High risk of breaking MCP client connections** if not done carefully
- **Defer to post-implementation** to minimize risk during critical bug fixes

---

## 🔗 Related Documents

- `SERVER_ARCHITECTURE_MAP.md` - Current architecture overview
- `SCRIPT_INTERCONNECTIONS.md` - Current script relationships
- `MASTER_CHECKLIST.md` - Master fix implementation checklist
- `IMPLEMENTATION_PLAN.md` - Day-by-day implementation plan

---

**Status:** 🟡 **DEFERRED** - To be executed after Week 3  
**Priority:** P3 (Nice-to-have)  
**Risk:** 🔴 **HIGH** (breaks MCP client configurations)  
**Effort:** Medium (2-3 hours)

**End of Script Consolidation Plan**

