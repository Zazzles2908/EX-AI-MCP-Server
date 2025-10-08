# Configuration Audit Report

**Total Findings:** 72

## INTERVAL (5 findings)

### tool_validation_suite\utils\performance_monitor.py

**Line 165:** `return self.process.cpu_percent(interval=0.1)`
- Value: `0`

**Line 180:** `time.sleep(2)`
- Value: `2`

### tools\diagnostics\batch_markdown_reviews.py

**Line 56:** `async with websockets.connect(uri, ping_interval=60, ping_timeout=30, close_timeout=10) as ws:`
- Value: `60`

### tools\diagnostics\ping_activity.py

**Line 13:** `async with websockets.connect(uri, ping_interval=60, ping_timeout=30, close_timeout=10) as ws:`
- Value: `60`

### tools\workflow\expert_analysis.py

**Line 223:** `wait_interval = 0.5`
- Value: `0`

## RETRY (1 findings)

### src\providers\mixins\retry_mixin.py

**Line 26:** `DEFAULT_MAX_RETRIES = 4`
- Value: `4`

## SIZE_LIMIT (31 findings)

### src\daemon\ws_server.py

**Line 386:** `args_preview = json.dumps(arguments, indent=2)[:500]`
- Value: `500`

### src\providers\glm_chat.py

**Line 231:** `logger.warning(f"GLM returned tool call as TEXT: {text[:200]}")`
- Value: `200`

**Line 335:** `logger.warning(f"GLM returned tool call as TEXT (HTTP path): {text[:200]}")`
- Value: `200`

### src\providers\kimi_chat.py

**Line 27:** `content = str(m.get("content", ""))[:2048]`
- Value: `2048`

### src\providers\openai_compatible.py

**Line 297:** `content_item["text"] = text[:100] + "... [truncated]"`
- Value: `100`

### tool_validation_suite\scripts\audit_hardcoded_configs.py

**Line 29:** `r"\[:(\d{3,})\]",  # String slicing like [:1000]`
- Value: `1000`

### tool_validation_suite\scripts\create_remaining_tests.py

**Line 58:** `"response": response[:200],`
- Value: `200`

### tool_validation_suite\scripts\generate_test_templates.py

**Line 73:** `"response": response[:200],`
- Value: `200`

**Line 100:** `"response": response[:200],`
- Value: `200`

**Line 127:** `"response": response[:200],`
- Value: `200`

**Line 154:** `"response": response[:200],`
- Value: `200`

### tool_validation_suite\scripts\regenerate_all_tests.py

**Line 204:** `"content": content[:200] if content else "",`
- Value: `200`

**Line 227:** `"content": content[:200] if content else "",`
- Value: `200`

### tool_validation_suite\scripts\run_all_tests_simple.py

**Line 219:** `print(f"Error: {result['errors'][:200]}")`
- Value: `200`

**Line 226:** `print(f"Error: {result['errors'][:200]}")`
- Value: `200`

### tool_validation_suite\utils\glm_watcher.py

**Line 170:** `input_str = json.dumps(test_input, indent=2)[:1000]`
- Value: `1000`

**Line 171:** `output_str = json.dumps(actual_output, indent=2)[:2000]`
- Value: `2000`

**Line 362:** `logger.debug(f"Content was: {content[:500]}")`
- Value: `500`

**Line 369:** `"observations": content[:500]  # Increased from 200 to 500`
- Value: `500`

### tool_validation_suite\utils\mcp_client.py

**Line 135:** `logger.debug(f"Raw response: {response_str[:500]}")`
- Value: `500`

**Line 142:** `logger.error(f"Response was: {response_str[:500]}")`
- Value: `500`

**Line 143:** `raise Exception(f"Invalid JSON response: {response_str[:200]}")`
- Value: `200`

### tools\diagnostics\diagnose_ws_stack.py

**Line 157:** `text = outs[0].get("text")[:120] if outs else "<none>"`
- Value: `120`

### tools\diagnostics\ping_activity.py

**Line 29:** `print("activity ok, preview:\n", text[:400])`
- Value: `400`

### tools\diagnostics\ws_daemon_smoke.py

**Line 20:** `preview = outs[0].get("text")[:180] if outs and isinstance(outs[0], dict) else str(outs)[:180]`
- Value: `180`

**Line 20:** `preview = outs[0].get("text")[:180] if outs and isinstance(outs[0], dict) else str(outs)[:180]`
- Value: `180`

### tools\providers\kimi\kimi_tools_chat.py

**Line 237:** `parts.append(str(m.get("role","")) + "\n" + str(m.get("content",""))[:2048])`
- Value: `2048`

**Line 285:** `parts.append(str(m.get("role","")) + "\n" + str(m.get("content",""))[:2048])`
- Value: `2048`

**Line 525:** `"content_preview": (content_text or "")[:256],`
- Value: `256`

### tools\workflow\expert_analysis.py

**Line 484:** `response_preview = model_response.content[:500] if len(model_response.content) > 500 else model_response.content`
- Value: `500`

**Line 495:** `f"Response preview (first 1000 chars): {model_response.content[:1000]}\n"`
- Value: `1000`

## TIMEOUT (35 findings)

### src\daemon\ws_server.py

**Line 136:** `with socket.create_connection((host, port), timeout=0.25):`
- Value: `0`

**Line 486:** `await asyncio.wait_for(_global_sem.acquire(), timeout=0.001)`
- Value: `0`

**Line 486:** `await asyncio.wait_for(_global_sem.acquire(), timeout=0.001)`
- Value: `0`

**Line 507:** `await asyncio.wait_for(_provider_sems[prov_key].acquire(), timeout=0.001)`
- Value: `0`

**Line 507:** `await asyncio.wait_for(_provider_sems[prov_key].acquire(), timeout=0.001)`
- Value: `0`

**Line 522:** `await asyncio.wait_for((await _sessions.get(session_id)).sem.acquire(), timeout=0.001)  # type: ignore`
- Value: `0`

**Line 522:** `await asyncio.wait_for((await _sessions.get(session_id)).sem.acquire(), timeout=0.001)  # type: ignore`
- Value: `0`

**Line 959:** `await asyncio.wait_for(stop_event.wait(), timeout=10.0)`
- Value: `10`

**Line 959:** `await asyncio.wait_for(stop_event.wait(), timeout=10.0)`
- Value: `10`

**Line 1008:** `close_timeout=1.0,`
- Value: `1`

### src\providers\tool_executor.py

**Line 42:** `with urllib.request.urlopen(req, timeout=25) as resp:`
- Value: `25`

**Line 57:** `with urllib.request.urlopen(req, timeout=25) as resp:`
- Value: `25`

**Line 76:** `with urllib.request.urlopen(req, timeout=15) as resp:`
- Value: `15`

### tool_validation_suite\scripts\run_all_tests_simple.py

**Line 144:** `branch = sp.run(["git", "branch", "--show-current"], capture_output=True, text=True, timeout=5).stdout.strip()`
- Value: `5`

**Line 145:** `commit = sp.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5).stdout.strip()`
- Value: `5`

### tool_validation_suite\scripts\validate_setup.py

**Line 199:** `timeout=10`
- Value: `10`

**Line 231:** `timeout=10`
- Value: `10`

**Line 262:** `timeout=10`
- Value: `10`

### tool_validation_suite\utils\file_uploader.py

**Line 93:** `timeout=60`
- Value: `60`

**Line 155:** `timeout=60`
- Value: `60`

### tools\capabilities\version.py

**Line 97:** `with urlopen(github_url, timeout=10) as response:`
- Value: `10`

### tools\diagnostics\batch_markdown_reviews.py

**Line 56:** `async with websockets.connect(uri, ping_interval=60, ping_timeout=30, close_timeout=10) as ws:`
- Value: `30`

**Line 56:** `async with websockets.connect(uri, ping_interval=60, ping_timeout=30, close_timeout=10) as ws:`
- Value: `10`

### tools\diagnostics\diagnose_ws_stack.py

**Line 179:** `await asyncio.wait_for(session.initialize(), timeout=20)`
- Value: `20`

**Line 179:** `await asyncio.wait_for(session.initialize(), timeout=20)`
- Value: `20`

**Line 180:** `tools = await asyncio.wait_for(session.list_tools(), timeout=20)`
- Value: `20`

**Line 180:** `tools = await asyncio.wait_for(session.list_tools(), timeout=20)`
- Value: `20`

### tools\diagnostics\ping_activity.py

**Line 13:** `async with websockets.connect(uri, ping_interval=60, ping_timeout=30, close_timeout=10) as ws:`
- Value: `30`

**Line 13:** `async with websockets.connect(uri, ping_interval=60, ping_timeout=30, close_timeout=10) as ws:`
- Value: `10`

### tools\providers\kimi\kimi_tools_chat.py

**Line 314:** `timeout_secs = 240.0`
- Value: `240`

**Line 437:** `with urllib.request.urlopen(req, timeout=25) as resp:`
- Value: `25`

**Line 452:** `with urllib.request.urlopen(req, timeout=25) as resp:`
- Value: `25`

**Line 462:** `with urllib.request.urlopen(url, timeout=20) as resp:`
- Value: `20`

**Line 496:** `timeout_secs = 180.0`
- Value: `180`

### tools\version.py

**Line 97:** `with urlopen(github_url, timeout=10) as response:`
- Value: `10`
