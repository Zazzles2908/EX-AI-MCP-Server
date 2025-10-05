# Setup Guide - Tool Validation Suite

**Purpose:** Complete setup instructions for the tool validation suite  
**Time Required:** 10-15 minutes  
**Difficulty:** Easy

---

## 📋 PREREQUISITES

### 1. **Python Environment**
- Python 3.12 or higher
- Virtual environment (recommended)
- pip package manager

### 2. **API Keys Required**
You need **3 API keys** for complete testing:

1. **Kimi API Key** (Moonshot)
   - For testing Kimi tools
   - Get from: https://platform.moonshot.ai/
   
2. **GLM API Key** (ZhipuAI)
   - For testing GLM tools
   - Get from: https://open.bigmodel.cn/

3. **GLM Watcher Key** (ZhipuAI - separate account)
   - For independent test observation
   - **Must be different from GLM_API_KEY**
   - Get from: https://open.bigmodel.cn/

### 3. **Disk Space**
- Minimum: 500 MB
- Recommended: 1 GB (for test results and logs)

### 4. **Network**
- Stable internet connection
- Access to Kimi and GLM APIs
- No firewall blocking API endpoints

---

## 🚀 SETUP STEPS

### Step 1: Navigate to Tool Validation Suite

```bash
cd tool_validation_suite
```

### Step 2: Create Environment File

```bash
# Copy the example environment file
cp .env.testing.example .env.testing
```

### Step 3: Configure API Keys

Edit `.env.testing` and add your API keys:

```bash
# Kimi API (Moonshot)
KIMI_API_KEY=sk-ZpS6545OhteEeQuNSexAPhvW92WQqqYjkikNmxWExyeUsOjU
KIMI_BASE_URL=https://api.moonshot.ai/v1

# GLM API (ZhipuAI)
GLM_API_KEY=90c4c8f531334693b2f684687fc7d250.ZhQ1I7U2mAgGZRUD
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4

# GLM Watcher (Independent Observer)
GLM_WATCHER_KEY=1bd71ec183aa49f98d2d02d6cb6393e9.mx4rvtgunLxIipb4
GLM_WATCHER_MODEL=glm-4-flash
GLM_WATCHER_ENABLED=true
```

**IMPORTANT:** The GLM Watcher key should be from a **different account** than the main GLM key for true independence.

### Step 4: Install Dependencies

```bash
# From the project root (not tool_validation_suite/)
cd ..
pip install -r requirements.txt
```

### Step 5: Create Required Directories

```bash
cd tool_validation_suite

# Create all required directories
mkdir -p results/latest/test_logs
mkdir -p results/latest/api_responses/kimi
mkdir -p results/latest/api_responses/glm
mkdir -p results/latest/watcher_observations
mkdir -p results/history
mkdir -p results/reports
mkdir -p cache/kimi
mkdir -p cache/glm
mkdir -p fixtures/sample_files
mkdir -p fixtures/sample_prompts
mkdir -p fixtures/expected_responses
```

### Step 6: Validate Setup

```bash
# Run the setup validation script
python scripts/validate_setup.py
```

**Expected Output:**
```
✅ Python version: 3.12.x
✅ Environment file exists: .env.testing
✅ Kimi API key configured
✅ GLM API key configured
✅ GLM Watcher key configured
✅ All required directories exist
✅ Dependencies installed
✅ API connectivity: Kimi OK, GLM OK
✅ Setup complete! Ready to run tests.
```

---

## 🔧 CONFIGURATION OPTIONS

### Basic Configuration

The `.env.testing` file contains many configuration options. Here are the most important:

#### **Test Timeouts**
```bash
TEST_TIMEOUT_SECS=300        # Max time for any single test
TEST_MAX_RETRIES=3           # Retry failed tests
TEST_DELAY_SECS=1            # Delay between tests
```

#### **Cost Limits**
```bash
TRACK_API_COSTS=true         # Track API costs
MAX_COST_PER_TEST=0.50       # Max cost per test (USD)
MAX_TOTAL_COST=10.00         # Max total cost (USD)
COST_ALERT_THRESHOLD=5.00    # Alert threshold (USD)
```

#### **Conversation Caching**
```bash
CACHE_CONVERSATION_IDS=true  # Cache conversation IDs
CONVERSATION_CACHE_TTL=3600  # Cache TTL (1 hour)
```

#### **GLM Watcher**
```bash
GLM_WATCHER_ENABLED=true     # Enable watcher
WATCHER_DETAIL_LEVEL=high    # Detail level (low/medium/high)
WATCHER_TIMEOUT_SECS=30      # Watcher timeout
```

#### **Logging**
```bash
TEST_LOG_LEVEL=INFO          # Log level
SAVE_DETAILED_LOGS=true      # Save detailed logs
VERBOSE_OUTPUT=true          # Verbose console output
```

---

## 🔍 VERIFY API KEYS

### Test Kimi API

```bash
curl -X POST https://api.moonshot.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-ZpS6545OhteEeQuNSexAPhvW92WQqqYjkikNmxWExyeUsOjU" \
  -d '{
    "model": "moonshot-v1-8k",
    "messages": [{"role": "user", "content": "test"}],
    "max_tokens": 10
  }'
```

**Expected:** JSON response with completion

### Test GLM API

```bash
curl -X POST https://open.bigmodel.cn/api/paas/v4/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 90c4c8f531334693b2f684687fc7d250.ZhQ1I7U2mAgGZRUD" \
  -d '{
    "model": "glm-4-flash",
    "messages": [{"role": "user", "content": "test"}],
    "max_tokens": 10
  }'
```

**Expected:** JSON response with completion

### Test GLM Watcher API

```bash
curl -X POST https://open.bigmodel.cn/api/paas/v4/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 1bd71ec183aa49f98d2d02d6cb6393e9.mx4rvtgunLxIipb4" \
  -d '{
    "model": "glm-4-flash",
    "messages": [{"role": "user", "content": "test"}],
    "max_tokens": 10
  }'
```

**Expected:** JSON response with completion

---

## 📁 DIRECTORY STRUCTURE VERIFICATION

After setup, your directory structure should look like:

```
tool_validation_suite/
├── .env.testing              ✅ Created
├── .env.testing.example      ✅ Exists
├── README.md                 ✅ Exists
├── SETUP_GUIDE.md           ✅ You are here
├── results/
│   ├── latest/              ✅ Created
│   ├── history/             ✅ Created
│   └── reports/             ✅ Created
├── cache/
│   ├── kimi/                ✅ Created
│   └── glm/                 ✅ Created
├── fixtures/
│   ├── sample_files/        ✅ Created
│   ├── sample_prompts/      ✅ Created
│   └── expected_responses/  ✅ Created
└── ...
```

---

## ⚠️ TROUBLESHOOTING

### Problem: "API key not configured"

**Solution:**
1. Check `.env.testing` exists
2. Verify API keys are correct (no extra spaces)
3. Ensure file is in `tool_validation_suite/` directory

### Problem: "API connection failed"

**Solution:**
1. Check internet connection
2. Verify API endpoints are accessible
3. Test API keys with curl commands above
4. Check firewall settings

### Problem: "Permission denied" creating directories

**Solution:**
```bash
# Run with appropriate permissions
sudo mkdir -p results/latest/test_logs
# Or change ownership
sudo chown -R $USER:$USER tool_validation_suite/
```

### Problem: "Module not found"

**Solution:**
```bash
# Install dependencies from project root
cd ..
pip install -r requirements.txt
```

### Problem: "GLM Watcher key same as GLM key"

**Solution:**
- GLM Watcher must use a **different API key**
- Create a second ZhipuAI account
- Or use a different API key from the same account

---

## 🎯 NEXT STEPS

After successful setup:

1. ✅ Read **TESTING_GUIDE.md** to learn how to run tests
2. ✅ Read **ARCHITECTURE.md** to understand the system
3. ✅ Run a quick test: `python scripts/run_core_tests.py --limit 1`
4. ✅ Review results: `cat results/latest/summary.json`

---

## 📞 SUPPORT

If you encounter issues:

1. Check this troubleshooting section
2. Review `results/latest/test_logs/` for error details
3. Verify API keys are valid
4. Check network connectivity
5. Review ARCHITECTURE.md for system details

---

## ✅ SETUP CHECKLIST

Before running tests, verify:

- [ ] Python 3.12+ installed
- [ ] `.env.testing` file created
- [ ] All 3 API keys configured
- [ ] Required directories created
- [ ] Dependencies installed
- [ ] `validate_setup.py` passes all checks
- [ ] API connectivity verified
- [ ] Read TESTING_GUIDE.md

**Ready to test!** 🚀

