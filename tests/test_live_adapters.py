from devintel.providers.live import GenerationRequest, ResearchRequest
from devintel.providers.live_adapters import GeminiGenerationProvider, WikipediaResearchProvider, configured_live_providers


def test_wikipedia_adapter_parses_search_payload(monkeypatch):
    provider = WikipediaResearchProvider()

    def fake_request(self, url, **kwargs):
        return {"pages": [{"title": "DORMAMMU", "key": "DORMAMMU", "excerpt": "autonomous intelligence"}]}

    monkeypatch.setattr("devintel.providers.live_adapters._HttpJson.request", fake_request)
    result = provider.search(ResearchRequest("DORMAMMU", max_results=1))
    assert result[0].title == "DORMAMMU"
    assert result[0].url.endswith("/DORMAMMU")
    assert result[0].source == "wikipedia"


def test_wikipedia_adapter_rejects_empty_query():
    provider = WikipediaResearchProvider()
    try:
        provider.search(ResearchRequest("   "))
    except ValueError as exc:
        assert "research query is required" in str(exc)
    else:
        raise AssertionError("empty research query must fail closed")


def test_gemini_adapter_parses_generation_payload_and_system_instruction(monkeypatch):
    provider = GeminiGenerationProvider("test-key")
    captured = {}

    def fake_request(self, url, **kwargs):
        captured.update(kwargs)
        return {
            "candidates": [{"content": {"parts": [{"text": "hello from Gemini"}]}}],
            "usageMetadata": {"totalTokenCount": 7},
        }

    monkeypatch.setattr("devintel.providers.live_adapters._HttpJson.request", fake_request)
    result = provider.generate(GenerationRequest("say hello", system="be concise"))
    assert result.text == "hello from Gemini"
    assert result.provider_id == "gemini"
    assert result.usage["totalTokenCount"] == 7
    assert captured["headers"]["x-goog-api-key"] == "test-key"
    assert captured["payload"]["systemInstruction"]["parts"][0]["text"] == "be concise"
    assert captured["payload"]["contents"][0]["parts"][0]["text"] == "say hello"


def test_gemini_adapter_requires_key():
    try:
        GeminiGenerationProvider("")
    except ValueError as exc:
        assert "api_key is required" in str(exc)
    else:
        raise AssertionError("missing API key must fail closed")


def test_configured_providers_prefer_canonical_dormammu_environment(monkeypatch):
    monkeypatch.setenv("DORMAMMU_PROVIDER_TIMEOUT", "7")
    monkeypatch.setenv("DORMAMMU_GEMINI_API_KEY", "canonical-key")
    monkeypatch.setenv("DEVINTEL_PROVIDER_TIMEOUT", "99")
    monkeypatch.setenv("GEMINI_API_KEY", "legacy-key")
    gemini, wikipedia = configured_live_providers()
    assert gemini is not None
    assert gemini.api_key == "canonical-key"
    assert wikipedia.timeout == 7.0
