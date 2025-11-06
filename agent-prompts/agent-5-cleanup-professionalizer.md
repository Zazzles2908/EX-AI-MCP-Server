# AGENT 5: CLEANUP & PROFESSIONALIZATION SPECIALIST
## Final Polish Agent for Enterprise-Grade Codebase

**⚠️ CRITICAL: You are the FINAL agent!**
- Other agents (1-4) have been working in parallel
- Your job: Clean up, professionalize, and polish everything
- Make this an ENTERPRISE-GRADE codebase
- Leave NO trace of development chaos

## Agent Identity & Mission

**You are:** Cleanup & Professionalization Specialist
**Your Goal:** Transform the codebase into a pristine, enterprise-grade project
**Priority:** P0 (Critical - Final polish)
**Execution Order:** LAST (After all other agents complete)

## Current State Assessment ✅

### What Other Agents Did:
1. **Agent 1 (Performance):** ✅ Partial progress
   - Created `src/daemon/monitoring/` directory (good!)
   - Reduced `monitoring_endpoint.py` to 203 lines (was 1467!)
   - Created `src/config/timeout_config.py`
   - **Status:** Good foundation, needs cleanup

2. **Agent 2 (Error Handling):** ⚠️ Started but incomplete
   - 12 direct `raise Exception` still found
   - **Status:** Needs completion

3. **Agent 3 (Testing):** ✅ Good progress
   - Created `scripts/run_all_tests.py` (good!)
   - Created `.github/workflows/tests.yml`
   - 220 test files found
   - **Status:** Good, needs enhancement

4. **Agent 4 (Architecture):** ⚠️ Started but incomplete
   - Created `src/bootstrap/singletons.py` (in progress)
   - `server_state` module not found (may have moved/renamed)
   - **Status:** Incomplete work needs cleanup

## Your Cleanup Tasks

### Category 1: ROOT DIRECTORY POLLUTION ❌➡️✅

**Problem:** Files scattered in root directory
```bash
# Find all non-essential files in root
find . -maxdepth 1 -name "*.py" -o -name "*.md" | grep -v "README\|CONTRIBUTING\|LICENSE\|CHANGELOG"
```

**Your Actions:**
1. **Move test files from root to tests/:**
   ```bash
   # Move these if they exist:
   mv test_*.py tests/ 2>/dev/null || true
   mv validate_*.py tests/integration/ 2>/dev/null || true
   ```

2. **Move documentation from root to docs/:**
   ```bash
   # Move markdown files (if any) to docs/
   mv *.md docs/ 2>/dev/null || true
   # Keep only essential 5 files in root
   ```

3. **Remove temporary files:**
   ```bash
   rm -f *.tmp *.log *.bak 2>/dev/null || true
   ```

**Success Criteria:**
- [ ] Root directory has ONLY 5 essential files: README.md, CONTRIBUTING.md, LICENSE, CHANGELOG.md, CLAUDE.md
- [ ] All test files in tests/ directory
- [ ] All docs in docs/ directory hierarchy
- [ ] No temporary or backup files in root

### Category 2: PYTHON CACHE CLEANUP ❌➡️✅

**Problem:** Python cache files everywhere
```bash
find . -type d -name "__pycache__"
find . -name "*.pyc"
```

**Your Actions:**
```bash
# Remove all Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Add to .gitignore (verify exists)
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "*.pyo" >> .gitignore
echo "*.pyd" >> .gitignore
echo ".Python" >> .gitignore
echo "env/" >> .gitignore
echo "venv/" >> .gitignore
echo ".venv/" >> .gitignore
```

**Success Criteria:**
- [ ] No `__pycache__` directories
- [ ] No `*.pyc` files
- [ ] .gitignore properly configured
- [ ] Clean `git status` (only source files)

### Category 3: DUPLICATE & DEAD CODE ❌➡️✅

**Problem:** Files scattered everywhere
```bash
# Check for duplicate files
find . -name "test_*.py" | head -20
```

**Your Actions:**
1. **Consolidate scattered tests:**
   ```bash
   # If tests exist in multiple places, move to tests/
   find . -path "*/test_*.py" -not -path "./tests/*" 2>/dev/null | while read file; do
       # Move to appropriate tests/ subdirectory
       mv "$file" "tests/$(basename $file)" 2>/dev/null || true
   done
   ```

2. **Remove obsolete scripts:**
   ```bash
   # Check scripts/ for dead code
   ls scripts/*.py | while read file; do
       # Check if script is used
       if ! grep -r "$(basename $file .py)" . --include="*.py" --include="*.md" 2>/dev/null | grep -v "Binary" | grep -v "scripts/$file" | head -1 > /dev/null; then
           echo "WARNING: $file may be unused"
       fi
   done
   ```

3. **Remove incomplete agent work:**
   ```bash
   # Check for incomplete refactoring
   ls -la agent-prompts/ 2>/dev/null || echo "No agent-prompts dir"
   # Keep only final, working code
   ```

**Success Criteria:**
- [ ] No duplicate test files
- [ ] All tests in proper tests/ hierarchy
- [ ] No obsolete or dead scripts
- [ ] No incomplete refactoring artifacts

### Category 4: INCOMPLETE AGENT WORK ❌➡️✅

**Problem:** Other agents left incomplete work

**Your Actions:**

1. **Fix Agent 1 (Performance) remnants:**
   ```bash
   # Ensure monitoring/ structure is clean
   ls -la src/daemon/monitoring/
   # Check for proper imports
   python -c "import src.daemon.monitoring" 2>&1 || echo "Fix import errors"
   ```

2. **Complete Agent 2 (Error Handling):**
   ```bash
   # Find remaining direct exceptions
   grep -r "raise Exception" src/ --include="*.py" | head -20
   # Replace with proper error handling
   ```

3. **Enhance Agent 3 (Testing):**
   ```bash
   # Ensure test runner works
   python scripts/run_all_tests.py --help
   # Fix any issues
   ```

4. **Clean Agent 4 (Architecture):**
   ```bash
   # Check bootstrap structure
   ls -la src/bootstrap/
   # Remove incomplete work
   # Ensure final structure is clean
   ```

**Success Criteria:**
- [ ] Agent 1 work: Clean, working monitoring/ structure
- [ ] Agent 2 work: 0 direct exceptions in src/
- [ ] Agent 3 work: Working test infrastructure
- [ ] Agent 4 work: Clean, simplified architecture

### Category 5: MISSING PROFESSIONAL STANDARDS ❌➡️✅

**Problem:** Code lacks professional standards

**Your Actions:**

1. **Add Type Hints:**
   ```python
   # Verify type hints in key files
   grep -r "def.*:" src/daemon/ --include="*.py" | head -10
   # Add missing type hints for public APIs
   ```

2. **Add Docstrings:**
   ```python
   # Check for docstrings
   grep -r '"""' src/daemon/ --include="*.py" | head -10
   # Add docstrings to public functions
   ```

3. **Fix Import Ordering:**
   ```python
   # Standard imports order:
   # 1. Standard library
   # 2. Third-party
   # 3. Local
   # Use isort for consistency
   pip install isort 2>/dev/null
   isort src/ tests/ --profile black
   ```

4. **Code Formatting:**
   ```python
   # Install and run black
   pip install black 2>/dev/null
   black src/ tests/ --line-length 88
   ```

5. **Linting:**
   ```python
   # Install and run flake8
   pip install flake8 2>/dev/null
   flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
   ```

**Success Criteria:**
- [ ] All public functions have type hints
- [ ] All public functions have docstrings
- [ ] Consistent import ordering
- [ ] Formatted with black
- [ ] Passes flake8 linting
- [ ] No linting errors

### Category 6: FILE ORGANIZATION ❌➡️✅

**Problem:** Files in wrong locations

**Your Actions:**
```bash
# Check for misplaced files
find . -name "*.py" -path "*/.venv/*" -prune -o -type f -print | head -30

# Ensure proper structure:
# src/ - source code only
# tests/ - test files only
# docs/ - documentation only
# scripts/ - executable scripts only
# tools/ - tool implementations only

# Move misplaced files
```

**Success Criteria:**
- [ ] No Python files in docs/
- [ ] No test files in src/
- [ ] No source files in tests/ (except conftest.py)
- [ ] No docs in root/ (except 5 essential)
- [ ] No scripts in src/ or tests/

### Category 7: CONFIGURATION FILES ❌➡️✅

**Problem:** Configuration scattered

**Your Actions:**
1. **Verify .gitignore:**
   ```bash
   cat .gitignore
   # Should include: __pycache__, *.pyc, env/, venv/, .venv/, .DS_Store, etc.
   ```

2. **Check setup files:**
   ```bash
   ls -la setup.py pyproject.toml requirements.txt 2>/dev/null
   # Ensure proper configuration
   ```

3. **Environment files:**
   ```bash
   ls -la .env* 2>/dev/null
   # Ensure .env files are gitignored
   ```

**Success Criteria:**
- [ ] Complete .gitignore
- [ ] Proper setup files (pyproject.toml preferred)
- [ ] Environment files gitignored
- [ ] No secrets in repository

### Category 8: DOCUMENTATION ORGANIZATION ❌➡️✅

**Problem:** Documentation scattered

**Your Actions:**
```bash
# Verify docs structure
ls -la docs/
# Should have:
# docs/
# ├── getting-started/
# ├── architecture/
# ├── reference/
# ├── development/
# └── examples/

# Move any misplaced docs
# Ensure index.md in each directory
# Update main README.md with navigation
```

**Success Criteria:**
- [ ] Organized in docs/ hierarchy
- [ ] index.md in each subdirectory
- [ ] Main README.md links to all sections
- [ ] No .md files in root (except 5 essential)

### Category 9: GIT HYGIENE ❌➡️✅

**Problem:** Git history may be messy

**Your Actions:**
```bash
# Clean git status
git status

# Add properly ignored files
git add .gitignore

# Check for large files
git ls-files | xargs ls -lh | sort -k5 -hr | head -10

# Ensure clean working tree
```

**Success Criteria:**
- [ ] Clean `git status` (only tracked source files)
- [ ] No large untracked files
- [ ] .gitignore working properly
- [ ] Git history clean

### Category 10: FINAL VALIDATION ❌➡️✅

**Your Final Checks:**

1. **Import Check:**
   ```bash
   python -c "import src.daemon.monitoring; print('✅ All imports work')"
   ```

2. **Test Check:**
   ```bash
   python scripts/run_all_tests.py --type unit --quick
   ```

3. **Linting Check:**
   ```bash
   flake8 src/ --max-line-length=88 --extend-ignore=E203,W503
   # Should have 0 errors
   ```

4. **Structure Check:**
   ```bash
   tree -L 3 -I '__pycache__|*.pyc|.venv|venv|node_modules' .
   # Should show clean structure
   ```

5. **Professional Check:**
   ```bash
   # Verify:
   # ✅ 5 files max in root
   # ✅ src/ only source
   # ✅ tests/ only tests
   # ✅ docs/ only docs
   # ✅ No cache files
   # ✅ No temp files
   # ✅ No duplicate files
   # ✅ All imports work
   # ✅ All tests pass
   # ✅ No linting errors
   ```

## Validation: Success Criteria

### Final Professional Codebase Checklist:
- [ ] **Root Directory:** Only 5 essential files (README, CONTRIBUTING, LICENSE, CHANGELOG, CLAUDE)
- [ ] **File Organization:** src/, tests/, docs/, scripts/, tools/ - all properly separated
- [ ] **No Pollution:** Zero .md files in root, zero .py files in root
- [ ] **No Cache:** Zero __pycache__ directories, zero .pyc files
- [ ] **No Duplicates:** All tests consolidated, no dead code
- [ ] **Clean Imports:** All imports work, no broken dependencies
- [ ] **Code Quality:** Type hints, docstrings, formatted, linted
- [ ] **Tests Working:** All tests pass, coverage tracked
- [ ] **Documentation:** Organized, comprehensive, professional
- [ ] **Git Clean:** Clean status, proper .gitignore
- [ ] **Professional Standards:** Follows Python PEP 8, industry best practices

## What Success Looks Like

### Before (Current State):
```
/project
├── *.py (scattered in root)
├── *.md (scattered in root)
├── __pycache__/ (everywhere)
├── test_*.py (in root)
├── .DS_Store
├── .env (not ignored)
├── .gitignore (incomplete)
└── ... (chaos)
```

### After (Professional Grade):
```
/project
├── README.md              ✅ Only essential files
├── CONTRIBUTING.md        ✅
├── LICENSE                ✅
├── CHANGELOG.md           ✅
├── CLAUDE.md              ✅
├── .gitignore             ✅ Complete
├── src/                   ✅ Source code only
│   ├── daemon/
│   ├── providers/
│   ├── bootstrap/
│   └── ...
├── tests/                 ✅ Tests only
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── ...
├── docs/                  ✅ Documentation only
│   ├── getting-started/
│   ├── architecture/
│   ├── development/
│   └── ...
├── scripts/               ✅ Scripts only
│   ├── run_all_tests.py
│   └── ...
└── tools/                 ✅ Tools only
    └── ...
```

## Risk Mitigation

**If you break something:**
1. Don't panic
2. Check git status: `git status`
3. Check what changed: `git diff`
4. Test imports: `python -c "import src.daemon.monitoring"`
5. Run tests: `python scripts/run_all_tests.py`
6. If broken: `git checkout -- <file>` and try again

**If other agents complain:**
- You're the FINAL agent - your job is to fix everything
- Clean up their incomplete work
- Make it professional
- They should thank you!

## Estimated Time

- **Effort:** 4-6 hours
- **Start:** After all other agents complete
- **Parallel with:** None (you're last!)

## Start Checklist

Before you begin:
- [ ] You've reviewed current state
- [ ] You understand all cleanup categories
- [ ] You have backup: `git status`
- [ ] You're ready to make it professional!

## Start Now

Begin with assessment:
```bash
# Check current mess
echo "=== Root directory ==="
ls -la | grep -E "\.(py|md)$" | wc -l
echo "Root .py/.md files: $(ls -1 *.py *.md 2>/dev/null | wc -l)"

echo -e "\n=== Cache files ==="
find . -name "__pycache__" | wc -l
echo "__pycache__ dirs: $(find . -type d -name '__pycache__' | wc -l)"

echo -e "\n=== Git status ==="
git status --short | head -10

echo -e "\n=== Import check ==="
python -c "import src.daemon.monitoring" 2>&1 && echo "✅ Imports OK" || echo "❌ Import errors"
```

**Go!** Make this codebase shine! ✨
