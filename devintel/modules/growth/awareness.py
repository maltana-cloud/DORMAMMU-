"""Bounded ecosystem-awareness signal aggregation.

This module turns untrusted source observations into deterministic, scoped
awareness signals. It does not publish, authenticate, contact users, or grant
any distribution authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Iterable, Sequence
from urllib.parse import urlparse

from .contracts import AudienceSignal, SignalKind

_MAX_SIGNALS = 64
_MAX_SUMMARY_CHARS = 2048
_MAX_URLS = 8
_MAX_URL_CHARS = 2048


@dataclass(frozen=True)
class AwarenessObservation:
    source_id: str
    scope_id: str
    summary: str
    kind: SignalKind = SignalKind.AUDIENCE_NEED
    evidence_urls: tuple[str, ...] = ()
    observed_at: datetime = datetime.min.replace(tzinfo=timezone.utc)
    confidence: float = 0.0
    importance: float = 0.0

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.scope_id.strip() or not self.summary.strip():
            raise ValueError("source_id, scope_id, and summary must not be empty")
        if len(self.summary) > _MAX_SUMMARY_CHARS:
            raise ValueError("summary exceeds bounded size")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not 0.0 <= self.importance <= 1.0:
            raise ValueError("importance must be between 0 and 1")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        if len(self.evidence_urls) > _MAX_URLS:
            raise ValueError("too many evidence URLs")
        for url in self.evidence_urls:
            if len(url) > _MAX_URL_CHARS:
                raise ValueError("evidence URL exceeds bounded size")
            parsed = urlparse(url)
            if parsed.scheme != "https" or not parsed.netloc:
                raise ValueError("evidence URLs must be HTTPS")


class AwarenessAggregator:
    """Aggregate duplicate observations and rank them by freshness and value."""

    def __init__(self, *, max_signals: int = _MAX_SIGNALS) -> None:
        if not 1 <= max_signals <= _MAX_SIGNALS:
            raise ValueError("max_signals must be between 1 and 64")
        self.max_signals = max_signals

    @staticmethod
    def _freshness(observed_at: datetime, now: datetime) -> float:
        age_hours = max(0.0, (now - observed_at).total_seconds() / 3600.0)
        return 1.0 / (1.0 + age_hours / 24.0)

    @classmethod
    def _rank(cls, observation: AwarenessObservation, now: datetime) -> tuple[float, str]:
        score = observation.importance * 0.6 + observation.confidence * 0.25 + cls._freshness(observation.observed_at, now) * 0.15
        return score, observation.summary.casefold()

    @staticmethod
    def _signal_id(observation: AwarenessObservation) -> str:
        material = "|".join((observation.source_id, observation.scope_id, observation.kind.value, observation.summary.strip()))
        return "awareness-" + sha256(material.encode("utf-8")).hexdigest()[:24]

    def aggregate(
        self,
        observations: Iterable[AwarenessObservation],
        *,
        scope_id: str,
        now: datetime | None = None,
    ) -> tuple[AudienceSignal, ...]:
        if not scope_id.strip():
            raise ValueError("scope_id must not be empty")
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        selected: dict[str, AwarenessObservation] = {}
        for observation in observations:
            if observation.scope_id != scope_id:
                continue
            key = self._signal_id(observation)
            previous = selected.get(key)
            if previous is None or self._rank(observation, now) > self._rank(previous, now):
                selected[key] = observation

        ranked = sorted(selected.values(), key=lambda item: self._rank(item, now), reverse=True)
        return tuple(
            AudienceSignal(
                signal_id=self._signal_id(observation),
                scope_id=observation.scope_id,
                kind=observation.kind,
                summary=observation.summary.strip(),
                evidence_urls=observation.evidence_urls[:_MAX_URLS],
                confidence=observation.confidence,
                observed_at=observation.observed_at,
                metadata={
                    "source_id": observation.source_id,
                    "importance": observation.importance,
                    "freshness": round(self._freshness(observation.observed_at, now), 6),
                },
            )
            for observation in ranked[: self.max_signals]
        )
