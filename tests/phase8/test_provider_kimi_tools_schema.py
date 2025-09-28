def test_kimi_websearch_tool_schema_function_mode(monkeypatch):
    monkeypatch.setenv("KIMI_ENABLE_INTERNET_SEARCH", "true")
    monkeypatch.setenv("KIMI_WEBSEARCH_SCHEMA", "function")
    from src.providers.capabilities import KimiCapabilities
    caps = KimiCapabilities()
    schema = caps.get_websearch_tool_schema({"use_websearch": True})
    assert schema.tools and isinstance(schema.tools, list)
    assert any(t.get("type") == "function" for t in schema.tools)


def test_kimi_websearch_tool_schema_builtin_mode(monkeypatch):
    monkeypatch.setenv("KIMI_ENABLE_INTERNET_SEARCH", "true")
    monkeypatch.setenv("KIMI_WEBSEARCH_SCHEMA", "builtin")
    from src.providers.capabilities import KimiCapabilities
    caps = KimiCapabilities()
    schema = caps.get_websearch_tool_schema({"use_websearch": True})
    assert schema.tools and isinstance(schema.tools, list)
    assert any(t.get("type") == "builtin_function" for t in schema.tools)

