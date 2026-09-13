"""Optional real external providers for DEVINTEL's bounded provider router.

The adapters use only Python's standard library so the core remains dependency-light.
They are opt-in through environment variables/configuration and never grant side-effect
authority. Research results are evidence candidates, not verified truth.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from .contracts import ProviderHealth
from .live import GenerationRequest, GenerationResponse, ResearchRequest, ResearchResult


class _HttpJson:
    def __init__(self, timeout: float = 15.0, user_agent: str = "DEVINTEL/1.0") -> None:
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.timeout = float(timeout)
        self.user_agent = user_agent

    def request(self, url: str, *, method: str = "GET", payload: dict[str, Any] | None = None,
                headers: dict[str, str] | None = None) -> dict[str, Any]:
        body = None
        request_headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
        if headers:
            request_headers.update(headers)
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        request = Request(url, data=body, headers=request_headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError(f"HTTP provider request failed: {exc}") from exc
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("provider returned invalid JSON") from exc
        if not isinstance(decoded, dict):
            raise RuntimeError("provider returned a non-object JSON response")
        return decoded


@dataclass
class WikipediaResearchProvider:
    """Keyless research provider backed by Wikipedia's public REST search API."""

    provider_id: str = "wikipedia"
    base_url: str = "https://en.wikipedia.org/w/rest.php/v1"
    timeout: float = 15.0

    def health(self) -> ProviderHealth:
        try:
            _HttpJson(self.timeout).request(
                f"{self.base_url.rstrip('/')}/search/page?{urlencode({'q': 'DEVINTEL', 'limit': 1})}"
            )
            return ProviderHealth(self.provider_id, True, "Wikipedia REST API reachable")
        except Exception as exc:
            return ProviderHealth(self.provider_id, False, str(exc))

    def search(self, request: ResearchRequest) -> tuple[ResearchResult, ...]:
        limit = min(max(int(request.max_results), 1), 100)
        url = f"{self.base_url.rstrip('/')}/search/page?{urlencode({'q': request.query.strip(), 'limit': limit})}"
        data = _HttpJson(self.timeout).request(url)
        pages = data.get("pages", [])
        if not isinstance(pages, list):
            raise RuntimeError("Wikipedia returned an invalid pages collection")
        results: list[ResearchResult] = []
        for page in pages[:limit]:
            if not isinstance(page, dict):
                continue
            title = str(page.get("title") or "").strip()
            key = str(page.get("key") or "").strip()
            if not key and not title:
                continue
            encoded_title = quote(key or title, safe="")
            results.append(
                ResearchResult(
                    url=f"https://en.wikipedia.org/wiki/{encoded_title}",
                    title=title,
                    content=str(page.get("excerpt") or page.get("description") or "").strip(),
                    source=self.provider_id,
                    metadata={"type": "encyclopedia_search"},
                )
            )
        return tuple(results)


@dataclass
class GeminiGenerationProvider:
    """Optional Gemini REST adapter. Requires GEMINI_API_KEY; no key is bundled."""

    api_key: str
    provider_id: str = "gemini"
    default_model: str = "gemini-2.5-flash"
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    timeout: float = 30.0

    def __post_init__(self) -> None:
        if not isinstance(self.api_key, str) or not self.api_key.strip():
            raise ValueError("api_key is required")

    def health(self) -> ProviderHealth:
        return ProviderHealth(self.provider_id, True, "Gemini adapter configured")

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        model = request.model.strip() or self.default_model
        if model.startswith("models/"):
            model = model[7:]
        url = f"{self.base_url.rstrip('/')}/models/{quote(model, safe='')}:generateContent?key={quote(self.api_key, safe='')}"
        parts: list[dict[str, str]] = []
        if request.system.strip():
            parts.append({"text": f"System instruction:\n{request.system.strip()}"})
        parts.append({"text": request.prompt})
        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "temperature": float(request.temperature),
                "maxOutputTokens": int(request.max_tokens),
            },
        }
        data = _HttpJson(self.timeout).request(url, method="POST", payload=payload)
        candidates = data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise RuntimeError("Gemini returned no candidates")
        candidate = candidates[0]
        if not isinstance(candidate, dict):
            raise RuntimeError("Gemini returned an invalid candidate")
        content = candidate.get("content", {})
        parts_out = content.get("parts", []) if isinstance(content, dict) else []
        text = "".join(str(part.get("text", "")) for part in parts_out if isinstance(part, dict)).strip()
        if not text:
            raise RuntimeError("Gemini returned empty text")
        usage = data.get("usageMetadata", {})
        usage_map = {
            str(k): int(v) for k, v in usage.items()
            if k in {"promptTokenCount", "candidatesTokenCount", "totalTokenCount"} and isinstance(v, int)
        } if isinstance(usage, dict) else {}
        return GenerationResponse(text=text, provider_id=self.provider_id, model=model, usage=usage_map)


def configured_live_providers() -> tuple[GeminiGenerationProvider | None, WikipediaResearchProvider]:
    """Build the free-first default provider set from environment configuration."""
    timeout = float(os.getenv("DEVINTEL_PROVIDER_TIMEOUT", "15"))
    wikipedia = WikipediaResearchProvider(timeout=timeout)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    gemini = GeminiGenerationProvider(api_key=api_key, timeout=max(timeout, 30.0)) if api_key else None
    return gemini, wikipedia
