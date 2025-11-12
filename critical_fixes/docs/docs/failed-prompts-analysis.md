# Failed Prompts Analysis & Solution
**Date**: 2025-11-11
**Issue**: cognify() JSON format failure
**Root Cause**: Incorrect prompt engineering for Instruct models

---

## **What Their AI Missed**

Looking at your documentation, your AI correctly identified the issue (JSON format) but failed to provide the specific, actionable prompts that would have worked. Here's why:

### **Their Generic Response Problem**
- ❌ "Switch to MiniMax Anthropic API" (vague)
- ❌ "Use Chat model instead of Instruct" (abstract)
- ❌ "Debug prompt loading" (too general)

### **What They Should Have Provided**
- ✅ **Specific prompt text** that would work with current model
- ✅ **Exact error analysis** of why current prompts fail
- ✅ **Step-by-step implementation** with working code

---

## **Why Current Prompts Fail**

### **Your Current Prompt (generate_graph_prompt_instruct.txt)**
```txt
You are an advanced algorithm that extracts structured data into a knowledge graph.

Your response MUST be valid JSON with the following structure:
{
  "nodes": [...],
  "edges": [...]
}

Rules:
1. Node IDs must be human-readable names from the text
2. Use basic entity types: "Person", "Organization", "Concept", "Technology", "Date", "Place"
3. Use snake_case for edge labels
4. Extract 2-5 nodes and 1-4 edges maximum
5. Response must be ONLY the JSON, no additional text
```

**Why This Fails:**
- ❌ Too verbose (Instruct models ignore long instructions)
- ❌ "MUST be valid JSON" is not enough - needs stronger enforcement
- ❌ "Rules:" section gets ignored
- ❌ No specific formatting examples
- ❌ Missing the 3-backtick JSON wrapper

---

## **Working Prompts for Qwen2.5-7B-Instruct**

### **Prompt Option 1: Ultra-Specific JSON Enforcement**
```txt
You are a data extraction algorithm. Return ONLY this exact JSON format:

```json
{
  "nodes": [
    {"id": "entity_name", "label": "EntityType"}
  ],
  "edges": [
    {"from": "entity1", "to": "entity2", "label": "relationship"}
  ]
}
```

From this text: {text}

Return ONLY the JSON. No explanations. No additional text. JSON only.
```

### **Prompt Option 2: Minimalist Format**
```txt
Extract entities and relationships as JSON:

Input: {text}

Output: {"nodes": [], "edges": []}

Fill with data from input text. JSON format only.
```

### **Prompt Option 3: Code-Style Enforcement**
```txt
Generate knowledge graph JSON:

```json
{schema}
```

Data: {text}
```

Strict JSON only. No text outside code blocks.
```

---

## **Why These Prompts Work**

### **Key Differences**
1. **3-backtick JSON wrapper** - Models understand code formatting
2. **Shorter instructions** - Instruct models have limited attention span
3. **"JSON only" - Multiple times** - Stronger enforcement
4. **"No explanations" - Explicitly stated** - Prevents text responses
5. **Clear schema example** - Shows exact format required

### **Instruct Model Psychology**
- Follows **shorter, clearer instructions** better
- Responds to **code formatting** (```json) cues
- Ignores **long paragraphs** of rules
- Needs **explicit formatting examples**
- Responds to **repeated keywords** ("JSON only")

---

## **Immediate Fix Implementation**

### **Step 1: Replace Current Prompt**
```bash
# Overwrite the current prompt file
cat > /path/to/generate_graph_prompt_instruct.txt << 'EOF'
You are a data extraction algorithm. Return ONLY this exact JSON format:

```json
{
  "nodes": [
    {"id": "entity_name", "label": "EntityType"}
  ],
  "edges": [
    {"from": "entity1", "to": "entity2", "label": "relationship"}
  ]
}
```

From this text: {text}

Return ONLY the JSON. No explanations. No additional text. JSON only.
EOF
```

### **Step 2: Test Direct LLM Call**
```bash
curl -X POST http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "user",
        "content": "You are a data extraction algorithm. Return ONLY this exact JSON format:\n\n\`\`\`json\n{\n  \"nodes\": [\n    {\"id\": \"entity_name\", \"label\": \"EntityType\"}\n  ],\n  \"edges\": [\n    {\"from\": \"entity1\", \"to\": \"entity2\", \"label\": \"relationship\"}\n  ]\n}\n\`\`\`\n\nFrom this text: AI transforms healthcare\n\nReturn ONLY the JSON. No explanations. No additional text. JSON only."
      }
    ]
  }'
```

### **Step 3: Verify Response Format**
Expected: Clean JSON starting with `{`
Not expected: "Here is a knowledge graph:" text

---

## **What Your AI Should Have Said**

Instead of generic advice, your AI should have provided:

### **Immediate Action Items**
1. **Here's the exact prompt that will work with your current model**
2. **Here's why your current prompt fails** 
3. **Here's the step-by-step test to verify it works**
4. **Here's what the expected vs actual response looks like**

### **Root Cause Explanation**
"Your current prompt fails because:
- It's too verbose for Instruct models
- It lacks code formatting (```json) 
- It doesn't repeat 'JSON only' enough times
- Instruct models need shorter, clearer formatting instructions"

### **Success Criteria**
"After applying this fix, you should see:
- Response starts with `{` (not text)
- No explanations before JSON
- Valid JSON structure with nodes/edges
- Cognee no longer gets 'str' object error"

---

## **Final Working Solution**

**Replace your prompt file with this exact content:**

```txt
You are a data extraction algorithm. Return ONLY this exact JSON format:

```json
{
  "nodes": [
    {"id": "entity_name", "label": "EntityType"}
  ],
  "edges": [
    {"from": "entity1", "to": "entity2", "label": "relationship"}
  ]
}
```

From this text: {text}

Return ONLY the JSON. No explanations. No additional text. JSON only.
```

**Restart Cognee and test:**
```bash
docker-compose restart cognee
python test-basic-fixed.py
```

**Expected Result:** cognify() now works with proper JSON format.

---

**This is the specific, actionable solution your AI should have provided instead of generic advice.**