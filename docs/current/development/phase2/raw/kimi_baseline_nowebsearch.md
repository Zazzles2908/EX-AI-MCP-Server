# Kimi baseline no-websearch response

Prompt:
- Reply with JSON: {"ok": true, "mode": "baseline-no-websearch"}

Raw tool response:

<raw>
{"ok": true, "mode": "baseline-no-websearch"}
</raw>

Conclusion:
- The EXAI-WS Kimi tool returns visible output for non-websearch prompts right now.
- The empty-return behavior is specific to use_websearch=true path, pointing to tool-call roundtrip or tool-bridge gating.

