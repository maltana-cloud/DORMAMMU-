from devintel.providers.live import GenerationRequest, ResearchRequest
from devintel.providers.live_adapters import GeminiGenerationProvider, WikipediaResearchProvider


def test_wikipedia_adapter_parses_search_payload(monkeypatch):
    provider = WikipediaResearchProvider()

    def fake_request(self, url, **kwargs):
        return {"pages": [{"title": "DEVINTEL", "key": "DEVINTEL", "excerpt": "developer intelligence"}]}

    monkeypatch.setattr("devintel.providers.live_adapters._HttpJson.request", fake_request)
    result = provider.search(ResearchRequest("DEVINTEL", max_results=1))
    assert result[0].title == "DEVINTEL"
    assert result[0].url.endswith("/DEVINTEL")
    assert result[0].source == "wikipedia"


def test_gemini_adapter_parses_generation_payload(monkeypatch):
    provider = GeminiGenerationProvider("test-key")

    def fake_request(self, url, **kwargs):
        return {
            "candidates": [{"content": {"parts": [{"text": "hello from Gemini"}]}}],
            "usageMetadata": {"totalTokenCount": 7},
        }

    monkeypatch.setattr("devintel.providers.live_adapters._HttpJson.request", fake_request)
    result = provider.generate(GenerationRequest("say hello"))
    assert result.text == "hello from Gemini"
    assert result.provider_id == "gemini"
    assert result.usage["totalTokenCount"] == 7


def test_gemini_adapter_requires_key():
    try:
        GeminiGenerationProvider("")
    except ValueError as exc:
        assert "api_key is required" in str(exc)
    else:
        raise AssertionError("missing API key must fail closed")
