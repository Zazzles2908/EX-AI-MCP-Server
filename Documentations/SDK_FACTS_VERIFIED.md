# SDK Facts - Verified Against Official Documentation

**Date:** 2025-10-20  
**Status:** Fact-Checked and Verified

---

## EXAI's Initial Claims (INCORRECT)

When asked about SDK conversation management capabilities, EXAI initially claimed:

1. ❌ Moonshot API has `conversation_id` parameter for automatic conversation tracking
2. ❌ Z.ai GLM API has `session_id` parameter for automatic conversation tracking
3. ❌ SDKs provide built-in conversation state management

**These claims were WRONG.**

---

## Verified Reality (CORRECT)

### Both SDKs Use Message Array Approach

**Moonshot/Kimi SDK:**
- Uses OpenAI SDK (NOT a custom SDK)
- Base URL: `https://api.moonshot.ai/v1`
- NO `conversation_id` parameter exists
- NO automatic conversation management
- YOU must manually maintain message history array

**GLM/Z.ai SDK:**
- Uses independent ZhipuAI SDK (NOT OpenAI compatible)
- Base URL: `https://api.z.ai/api/paas/v4`
- NO `session_id` parameter for conversation management
- NO automatic conversation management
- YOU must manually maintain message history array

### Official Multi-Turn Conversation Pattern

**Kimi Example (from official docs):**
```python
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://api.moonshot.ai/v1"
)

# YOU maintain the messages array
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is recursion?"}
]

response = client.chat.completions.create(
    model="moonshot-v1-8k",
    messages=messages  # ← Pass full history
)

# Add assistant response to YOUR messages array
messages.append({
    "role": "assistant",
    "content": response.choices[0].message.content
})

# Add next user message to YOUR messages array
messages.append({
    "role": "user",
    "content": "Can you give an example?"
})

# Send full history again
response = client.chat.completions.create(
    model="moonshot-v1-8k",
    messages=messages  # ← Full history every time
)
```

**GLM Example (from official docs):**
```python
import requests

url = "https://api.z.ai/api/paas/v4/chat/completions"

# YOU maintain the messages array
messages = [
    {"role": "system", "content": "You are a professional programming assistant."},
    {"role": "user", "content": "What is recursion?"}
]

payload = {
    "model": "glm-4.6",
    "messages": messages  # ← Pass full history
}

response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {API_KEY}"})

# Add assistant response to YOUR messages array
messages.append({
    "role": "assistant",
    "content": response.json()["choices"][0]["message"]["content"]
})

# Add next user message
messages.append({
    "role": "user",
    "content": "Give me an example"
})

# Send full history again
payload = {
    "model": "glm-4.6",
    "messages": messages  # ← Full history every time
}

response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {API_KEY}"})
```

---

## Why Custom Conversation Management is Necessary

Since SDKs don't provide automatic conversation management:

1. **YOU must store message history** - No SDK-side storage
2. **YOU must pass full history** - Every request needs complete context
3. **YOU must manage conversation state** - Track turns, prune old messages, etc.
4. **YOU must implement persistence** - SDKs don't save anything

This is why we have:
- `utils/conversation/supabase_memory.py` - Stores conversation history
- `continuation_id` parameter - Tracks conversation threads
- Message array building - Converts stored history to SDK format

---

## Model Context Windows (CORRECTED)

**Kimi Models:**
- `kimi-k2-0905-preview`: 256K tokens
- `kimi-k2-0711-preview`: 128K tokens
- `kimi-k2-turbo-preview`: 256K tokens
- `moonshot-v1-128k`: 128K tokens
- `moonshot-v1-32k`: 32K tokens
- `moonshot-v1-8k`: 8K tokens

**GLM Models:**
- `glm-4.6`: 200K tokens
- `glm-4.5`: 128K tokens
- `glm-4.5-flash`: 128K tokens
- `glm-4.5-air`: 128K tokens
- `glm-4.5v`: 65K tokens (vision)

---

## Lessons Learned About Using EXAI

### Attempt 1: Too Vague
**Prompt:** "Research SDK conversation capabilities"  
**Result:** Generic response with no actual research

### Attempt 2: Asked for Specific Searches
**Prompt:** "Search for Moonshot API conversation_id documentation"  
**Result:** EXAI didn't execute searches, just made claims

### Attempt 3: Used continuation_id and Pushed Harder
**Prompt:** "I need exact URLs and code examples"  
**Result:** Got detailed responses BUT claims were incorrect

### Attempt 4: Asked for Verification
**Prompt:** "Provide exact documentation URLs"  
**Result:** URLs returned JavaScript/HTML (not readable)

### Key Insight
**EXAI can hallucinate SDK features that don't exist.** Always verify against:
1. Official documentation
2. Actual code examples from provider
3. Our own codebase implementation

---

## Impact on Architecture

### Current Problem
Our codebase converts conversation history to TEXT STRING:
```python
history_text = "=== CONVERSATION HISTORY ===\n"
history_text += "Turn 1: User said...\n"
history_text += "Turn 1: Assistant said...\n"
# ... etc
```

Then embeds this text into a SINGLE message:
```python
messages = [
    {"role": "user", "content": f"{history_text}\n\n{user_prompt}"}
]
```

### Why This is Wrong
1. **Blocks SDK native features** - Kimi context caching, GLM web search
2. **Inefficient token usage** - Text markers waste tokens
3. **Poor context quality** - SDKs can't distinguish turns
4. **No role separation** - Everything is "user" role

### Correct Approach
Build proper message arrays:
```python
messages = [
    {"role": "system", "content": "System prompt"},
    {"role": "user", "content": "Turn 1 user message"},
    {"role": "assistant", "content": "Turn 1 assistant response"},
    {"role": "user", "content": "Turn 2 user message"},
    {"role": "assistant", "content": "Turn 2 assistant response"},
    {"role": "user", "content": "Current user message"}
]
```

This enables:
- ✅ Kimi context caching (recognizes repeated context)
- ✅ GLM web search (proper role separation)
- ✅ Better token efficiency (no text markers)
- ✅ Proper conversation flow (SDK understands turns)

---

## References

- Moonshot API Docs: https://platform.moonshot.cn/docs
- Z.ai GLM API Docs: https://open.bigmodel.cn/dev/api
- OpenAI SDK (used by Kimi): https://github.com/openai/openai-python
- ZhipuAI SDK: https://github.com/zhipuai/zhipuai-sdk-python

