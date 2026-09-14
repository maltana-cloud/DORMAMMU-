from datetime import datetime, timezone
from io import BytesIO

import pytest

from devintel.modules.growth.contracts import SignalKind
from devintel.modules.growth.live_awareness import AwarenessSourcePolicy, JsonAwarenessSource


def test_live_source_requires_trusted_https_host():
    policy = AwarenessSourcePolicy(trusted_sources=("trusted",), allowed_hosts=("feed.example",))
    with pytest.raises(PermissionError):
        JsonAwarenessSource("https://other.example/feed", source_id="x", trusted_source="trusted", policy=policy)
    with pytest.raises(ValueError):
        JsonAwarenessSource("http://feed.example/feed", source_id="x", trusted_source="trusted", policy=policy)


def test_live_source_rejects_untrusted_provenance():
    policy = AwarenessSourcePolicy(trusted_sources=("trusted",), allowed_hosts=("feed.example",))
    with pytest.raises(PermissionError):
        JsonAwarenessSource("https://feed.example/feed", source_id="x", trusted_source="unknown", policy=policy)


def test_live_source_parses_bounded_items(monkeypatch):
    payload = b'{"items":[{"summary":"Need for better tools","kind":"demand","confidence":0.9,"importance":0.8}]}'

    class Response:
        headers = {"Content-Type": "application/json"}
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, size=-1): return payload[:size]

    monkeypatch.setattr("devintel.modules.growth.live_awareness.urlopen", lambda *args, **kwargs: Response())
    policy = AwarenessSourcePolicy(trusted_sources=("trusted",), allowed_hosts=("feed.example",))
    source = JsonAwarenessSource("https://feed.example/feed", source_id="feed", trusted_source="trusted", policy=policy)
    observations = source.poll(scope_id="growth", now=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert len(observations) == 1
    assert observations[0].kind is SignalKind.DEMAND
    assert observations[0].source_id == "feed"


def test_live_source_rejects_oversized_response(monkeypatch):
    class Response:
        headers = {"Content-Type": "application/json"}
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, size=-1): return b"x" * size

    monkeypatch.setattr("devintel.modules.growth.live_awareness.urlopen", lambda *args, **kwargs: Response())
    policy = AwarenessSourcePolicy(max_bytes=32, trusted_sources=("trusted",), allowed_hosts=("feed.example",))
    source = JsonAwarenessSource("https://feed.example/feed", source_id="feed", trusted_source="trusted", policy=policy)
    with pytest.raises(ValueError, match="exceeds bound"):
        source.poll(scope_id="growth")
