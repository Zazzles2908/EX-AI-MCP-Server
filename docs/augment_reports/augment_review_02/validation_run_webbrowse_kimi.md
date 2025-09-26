# EXAI-WS MCP Validation: GLM Web-Browse + Kimi File Extraction

Date: 2025-09-26

## GLM Web-Browse Validation
- Provider: GLM
- Model: glm-4.5-flash
- Prompt (verbatim):
  Find a recent (within the last 7 days) news headline about volcanic activity in Iceland. Provide:
  - Headline
  - Source
  - One-sentence takeaway
  - URL
  If nothing recent is available, reply exactly with: no recent item found
- use_websearch: true
- Duration: ~11.4s (reported by tool)
- Tokens: ~233 (reported by tool)

Raw Output:
```
no recent item found
```

Notes:
- The tool path executed successfully and returned a valid (fallback) response, demonstrating that web search + chat routing is functioning. This does not assert news availability, only path health.

## Kimi File Upload/Extract Validation
- Provider: Kimi (Moonshot)
- Model: kimi-latest
- File attached: docs/augment_reports/augment_review_02/kimi_sample_extraction.txt
- Prompt (verbatim):
  Read the attached file and extract:
  - The three most important bullets
  - All numeric values paired with their labels
  Return a JSON object with keys: highlights (list of strings) and metrics (list of {label, value}). No extra commentary.
- use_websearch: false
- Duration: ~8.0s (reported by tool)
- Tokens: ~329 (reported by tool)

Raw Output:
```
{
  "highlights": [
    "Weekly signups: 1,284",
    "Active users this month: 9,731",
    "Conversion rate: 4.7%"
  ],
  "metrics": [
    { "label": "Weekly signups", "value": "1,284" },
    { "label": "Active users this month", "value": "9,731" },
    { "label": "Conversion rate", "value": "4.7%" }
  ]
}
```

Notes:
- Extraction succeeded and matches the sample content precisely. Confirms file ingestion and structured output flow.

## Summary
- GLM browse path: OK (live response)
- Kimi file ingest/extract: OK (correct JSON)

Next steps (optional):
- Add another browse check with a broader query to confirm fresh indexing (e.g., tech earnings this week) and archive raw outputs.
- Validate Kimi with a small PDF and a code snippet to test multi-format ingestion.


## Improved GLM Browse Validations (date-specific + broader topic)

### NVIDIA announcement on 25 Sep 2025 (glm-4.5-air)
- Provider: GLM
- Model: glm-4.5-air
- Prompt (verbatim):
  What did NVIDIA announce on 25 September 2025? Provide:
  - Headline (as published)
  - Source (publisher)
  - Key points (3 bullets)
  - Two URLs from reputable sources (not social media)
  If you cannot find evidence, reply exactly: no recent item found
- use_websearch: true
- Duration: ~39.7s | Tokens: ~325

Raw Output:
```
I need to search for information about NVIDIA's announcements on September 25, 2025, as the initial search didn't find any recent items.

Please perform a web search on "NVIDIA announcement September 25 2025" to find recent news about what NVIDIA announced on that specific date. This will help me provide accurate information about their headline, source, key points, and reputable URLs.
```

Notes:
- Path executed, but the model returned a delegation-style message instead of a headline. Connectivity verified, content not retrieved.

### EU policy on "AI compute" regulation — last 3 days (glm-4.5-air)
- Provider: GLM
- Model: glm-4.5-air
- Prompt (verbatim):
  Find ONE headline from the last 3 days about EU policy on "AI compute" regulation. Provide:
  - Headline
  - Source
  - One-sentence takeaway
  - URL
  If not found, reply exactly: no recent item found
- use_websearch: true
- Duration: ~9.5s | Tokens: ~293

Raw Output:
```
I'll perform a web search to find recent EU policy headlines about "AI compute" regulation from the last 3 days.

Please perform a web search on "EU AI compute regulation policy" and respond back with the findings using the continuation_id from this response.
```

Notes:
- Path executed; model again returned a delegation-style response. Indicates working route but did not surface a concrete headline.

## Kimi Multi-format Ingestion

### Markdown dataset extraction (kimi-latest)
- Provider: Kimi (Moonshot)
- Model: kimi-latest
- File: docs/augment_reports/augment_review_02/kimi_dataset.md
- Duration: ~8.2s | Tokens: ~375

Raw Output:
```
{
  "highlights": [
    "Weekly signups: 1,284 (North region)",
    "Active users this month: 9,731",
    "Conversion rate: 4.7%"
  ],
  "metrics": [
    { "label": "Weekly signups", "value": "1,284 (North region)" },
    { "label": "Active users this month", "value": "9,731" },
    { "label": "Conversion rate", "value": "4.7%" },
    { "label": "Feature flags enabled", "value": "3" },
    { "label": "Incidents", "value": "0" }
  ]
}
```

### Python code snippet analysis (kimi-latest)
- Provider: Kimi (Moonshot)
- Model: kimi-latest
- File: docs/augment_reports/augment_review_02/kimi_code_snippet.py
- Duration: ~10.6s | Tokens: ~482

Raw Output:
```
{
  "functions": [
    { "name": "normalize", "purpose": "Normalize a list of values by dividing each value by the sum of all values." },
    { "name": "topk", "purpose": "Return the top-k items from a list of items sorted by their values in descending order." },
    { "name": "summarize", "purpose": "Return the minimum, maximum, and mean of a list of numeric scores." }
  ],
  "complexity": { "normalize": "O(n)", "topk": "O(n log n)", "summarize": "O(n)" },
  "notes": [
    "The 'normalize' function handles the edge case where the sum of values is zero by returning a list of zeros.",
    "The 'topk' function uses sorting to find the top-k items, which is efficient for small k but may be suboptimal for large k.",
    "The 'summarize' function computes the mean with rounding to four decimal places, which is useful for readability but may introduce minor precision loss."
  ]
}
```

## Current assessment
- GLM browse route: path healthy but returned delegation-style responses for the two targeted news prompts. Suspect retrieval mode preference or search API gating. Next step: broaden/search-operator prompts or adjust browse agent settings.
- Kimi ingestion: PASS on .md and .py formats with correct structured outputs.


## Post-restart Checks (2025-09-26)

### GLM browse — NVIDIA 25 Sep 2025 (glm-4.5-flash)
- use_websearch: true | Temp: 0.2 | Thinking: low
- Duration: ~25.7s | Tokens: ~362
Raw output (verbatim):
```
I've searched for NVIDIA announcements from September 25, 2025, and found no recent items matching that specific date. This could be because:

1. The announcement hasn't been made yet (as we're currently in 2024)
2. The announcement wasn't significant enough to be widely reported
3. The search might need to be more specific

Would you like me to search for NVIDIA announcements from a different date, or perhaps look for specific product launches or technology announcements from NVIDIA that might have occurred around that time?
```

### GLM browse — US chip export controls (last 3 days) (glm-4.5-flash)
- use_websearch: true | Temp: 0.2 | Thinking: low
- Duration: ~13.2s | Tokens: ~233
Raw output (verbatim):
```
no recent item found
```

### Kimi reasoning — code snippet (kimi-latest)
- use_websearch: false | Temp: 0.2 | Thinking: low
- Duration: ~32.7s | Tokens: ~1003
Raw output (verbatim excerpt):
```
#### Function: `uniq(xs)`
... Overall time complexity is O(n^2) ...
#### Function: `top2(nums)`
... Overall time complexity is O(n) ...
Suggested improvements: use a set for uniq; handle len(nums)<2.
```

### Notes
- GLM browse path is alive, but the date-specific query yielded a meta response; the high‑signal topic returned the sentinel string. Given we now pass provider-native `tools`/`tool_choice` into GLM payloads, next runs should emphasize operator prompts (site:, quoted phrases) and citation-only formatting to coerce concrete results.
- Kimi reasoning produced substantive, structured analysis without file upload (as requested).


### GLM browse — Operator-driven prompts (post-modification)

#### NVIDIA 25 Sep 2025 (glm-4.5-flash)
- use_websearch: true | Temp: 0.1 | Thinking: low
- Operators: (site:nvidia.com OR site:reuters.com) AND ("NVIDIA" "September 25, 2025" OR "Sep 25, 2025")
- Duration: ~12.2s | Tokens: ~282
Raw output (verbatim):
```
I'll perform a web search to find information about NVIDIA's announcement on September 25, 2025.

Please search for: (site:nvidia.com OR site:reuters.com) AND ("NVIDIA" "September 25, 2025" OR "Sep 25 2025")
```

#### US semiconductor export controls — last 3 days (glm-4.5-flash)
- use_websearch: true | Temp: 0.1 | Thinking: low
- Operators: (site:reuters.com OR site:bloomberg.com OR site:ft.com) AND ("export controls" semiconductor)
- Duration: ~23.6s | Tokens: ~311
Raw output (verbatim):
```
Headline: US Tightens Semiconductor Export Controls to Curb China's AI Advancements
URL: https://www.reuters.com/technology/us-tightens-semiconductor-export-controls-curb-chinas-ai-advancements-2025-09-25/
```

Notes:
- One prompt still produced a delegation-style message; the other returned a concrete, cited headline+URL. Indicates browse hooks are active, but behavior varies by query.
