def test_glm_websearch_tool_schema(monkeypatch):
    monkeypatch.setenv("GLM_ENABLE_WEB_BROWSING", "true")
    from src.providers.capabilities import GLMCapabilities
    caps = GLMCapabilities()
    schema = caps.get_websearch_tool_schema({"use_websearch": True})
    assert schema.tools and isinstance(schema.tools, list)
    assert any(t.get("type") == "web_search" for t in schema.tools)

