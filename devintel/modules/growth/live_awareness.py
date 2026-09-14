"""Bounded live ecosystem-awareness source adapters.

Adapters consume explicitly approved HTTPS JSON feeds as untrusted observations.
They never authenticate, publish, contact users, or grant distribution authority.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .awareness import AwarenessObservation
from .contracts import SignalKind

_MAX_BODY_BYTES = 512_000
_MAX_ITEMS = 64
_MAX_SUMMARY_CHARS = 2048

@dataclass(frozen=True)
class AwarenessSourcePolicy:
    timeout_seconds: float = 5.0
    max_bytes: int = _MAX_BODY_BYTES
    trusted_sources: tuple[str, ...] = ()
    allowed_hosts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.1 <= self.timeout_seconds <= 10.0:
            raise ValueError("timeout_seconds must be between 0.1 and 10")
        if not 1 <= self.max_bytes <= _MAX_BODY_BYTES:
            raise ValueError("max_bytes must be between 1 and 512000")
        if not self.trusted_sources or not self.allowed_hosts:
            raise ValueError("trusted_sources and allowed_hosts are required")

class JsonAwarenessSource:
    """Read a bounded JSON feed whose host and provenance are explicitly trusted."""
    def __init__(self, endpoint: str, *, source_id: str, trusted_source: str, policy: AwarenessSourcePolicy) -> None:
        parsed = urlparse(endpoint)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("endpoint must use HTTPS")
        if parsed.hostname not in policy.allowed_hosts:
            raise PermissionError("endpoint host is not allowlisted")
        if trusted_source not in policy.trusted_sources:
            raise PermissionError("source provenance is not trusted")
        self.endpoint = endpoint
        self.source_id = source_id.strip()
        self.trusted_source = trusted_source
        if not self.source_id:
            raise ValueError("source_id is required")
        self.policy = policy

    def poll(self, *, scope_id: str, now: datetime | None = None) -> tuple[AwarenessObservation, ...]:
        if not scope_id.strip():
            raise ValueError("scope_id is required")
        now = now or datetime.now(timezone.utc)
        request = Request(self.endpoint, headers={"Accept": "application/json", "User-Agent": "DORMAMMU-awareness/1"})
        with urlopen(request, timeout=self.policy.timeout_seconds) as response:
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            if content_type != "application/json":
                raise ValueError("awareness source must return JSON")
            body = response.read(self.policy.max_bytes + 1)
        if len(body) > self.policy.max_bytes:
            raise ValueError("awareness source response exceeds bound")
        payload = json.loads(body.decode("utf-8"))
        items = payload.get("items", payload) if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            raise ValueError("awareness source must contain a JSON list or items list")
        observations: list[AwarenessObservation] = []
        for item in items[:_MAX_ITEMS]:
            if not isinstance(item, dict):
                continue
            summary = str(item.get("summary", "")).strip()
            if not summary or len(summary) > _MAX_SUMMARY_CHARS:
                continue
            try:
                kind = SignalKind(str(item.get("kind", SignalKind.AUDIENCE_NEED.value)))
                confidence = float(item.get("confidence", 0.0))
                importance = float(item.get("importance", 0.0))
            except (TypeError, ValueError):
                continue
            if not 0.0 <= confidence <= 1.0 or not 0.0 <= importance <= 1.0:
                continue
            urls = tuple(str(url) for url in item.get("evidence_urls", ()) if isinstance(url, str))
            try:
                observations.append(AwarenessObservation(self.source_id, scope_id, summary, kind, urls, now, confidence, importance))
            except ValueError:
                continue
        return tuple(observations)
