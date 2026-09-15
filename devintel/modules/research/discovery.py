"""Bounded source discovery orchestration.

Discovery produces untrusted candidates only. It never verifies truth, grants
authority, or executes discovered content.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from .contracts import ResearchCandidate, canonicalize_url


class DiscoveryProvider(Protocol):
    def discover(self, query: str, *, limit: int) -> Iterable[ResearchCandidate]: ...


@dataclass(frozen=True)
class DiscoveryResult:
    query: str
    candidates: tuple[ResearchCandidate, ...]
    rejected: int


class ResearchDiscoveryEngine:
    def __init__(self, providers: Iterable[DiscoveryProvider], *, max_candidates: int = 50) -> None:
        providers = tuple(providers)
        if max_candidates <= 0:
            raise ValueError("max_candidates must be positive")
        if len(providers) > max_candidates:
            raise ValueError("too many discovery providers")
        self.providers = providers
        self.max_candidates = max_candidates

    def discover(self, query: str, *, limit: int = 20) -> DiscoveryResult:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query is required")
        if limit <= 0 or limit > self.max_candidates:
            raise ValueError("limit is outside the configured bound")
        seen: set[str] = set()
        found: list[ResearchCandidate] = []
        rejected = 0
        for provider in self.providers:
            remaining = limit - len(found)
            if remaining <= 0:
                break
            try:
                candidates = provider.discover(query.strip(), limit=remaining)
            except Exception:
                rejected += 1
                continue
            for candidate in candidates:
                if len(found) >= limit:
                    break
                try:
                    if not isinstance(candidate, ResearchCandidate):
                        raise ValueError("invalid candidate type")
                    url = canonicalize_url(candidate.url)
                    if url in seen:
                        continue
                    seen.add(url)
                    found.append(candidate)
                except (TypeError, ValueError):
                    rejected += 1
        found.sort(key=lambda item: (item.url, item.title.lower()))
        return DiscoveryResult(query.strip(), tuple(found), rejected)
