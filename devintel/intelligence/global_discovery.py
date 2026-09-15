"""Bounded continuous multi-source intelligence discovery.

The engine is an externally driven polling boundary. Source observations remain
untrusted until the existing verification and knowledge pipeline admits them.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Iterable, Protocol

from devintel.modules.growth.awareness import AwarenessObservation


class GlobalDiscoverySource(Protocol):
    source_id: str

    def discover(self, *, scope_id: str, query: str, limit: int) -> Iterable[AwarenessObservation]: ...

    def health(self) -> bool: ...


@dataclass(frozen=True)
class DiscoveryRound:
    scope_id: str
    query: str
    observations: tuple[AwarenessObservation, ...]
    rejected: int
    started_at: datetime
    next_run_at: datetime


@dataclass(frozen=True)
class GlobalDiscoveryPolicy:
    interval_seconds: int = 300
    max_sources: int = 32
    max_observations: int = 64
    max_age_seconds: int = 86_400

    def __post_init__(self) -> None:
        if not 1 <= self.interval_seconds <= 86_400:
            raise ValueError("interval_seconds must be between 1 and 86400")
        if not 1 <= self.max_sources <= 256:
            raise ValueError("max_sources must be between 1 and 256")
        if not 1 <= self.max_observations <= 512:
            raise ValueError("max_observations must be between 1 and 512")
        if not 1 <= self.max_age_seconds <= 604_800:
            raise ValueError("max_age_seconds must be between 1 and 604800")


class GlobalDiscoveryEngine:
    """Run bounded, deterministic discovery rounds across replaceable sources."""

    def __init__(self, sources: Iterable[GlobalDiscoverySource], *, policy: GlobalDiscoveryPolicy | None = None) -> None:
        values = tuple(sources)
        self.policy = policy or GlobalDiscoveryPolicy()
        if len(values) > self.policy.max_sources:
            raise ValueError("too many discovery sources")
        seen_ids: set[str] = set()
        for source in values:
            source_id = getattr(source, "source_id", "")
            if not isinstance(source_id, str) or not source_id.strip() or source_id in seen_ids:
                raise ValueError("source IDs must be non-empty and unique")
            if not callable(getattr(source, "discover", None)) or not callable(getattr(source, "health", None)):
                raise TypeError("source must implement discover and health")
            seen_ids.add(source_id)
        self.sources = tuple(sorted(values, key=lambda source: source.source_id))

    @staticmethod
    def _identity(observation: AwarenessObservation) -> str:
        material = "|".join((observation.scope_id, observation.kind.value, observation.summary.strip().casefold()))
        return sha256(material.encode("utf-8")).hexdigest()

    def due(self, now: datetime, next_run_at: datetime | None) -> bool:
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        return next_run_at is None or now >= next_run_at

    def run_round(self, *, scope_id: str, query: str, now: datetime | None = None) -> DiscoveryRound:
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("scope_id is required")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query is required")
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        cutoff = now - timedelta(seconds=self.policy.max_age_seconds)
        selected: dict[str, AwarenessObservation] = {}
        rejected = 0
        per_source_limit = self.policy.max_observations
        for source in self.sources:
            try:
                if not bool(source.health()):
                    rejected += 1
                    continue
                values = source.discover(scope_id=scope_id.strip(), query=query.strip(), limit=per_source_limit)
                for observation in values:
                    if not isinstance(observation, AwarenessObservation):
                        rejected += 1
                        continue
                    if observation.scope_id != scope_id.strip() or observation.observed_at < cutoff or observation.observed_at > now:
                        rejected += 1
                        continue
                    identity = self._identity(observation)
                    previous = selected.get(identity)
                    if previous is None or (observation.confidence, observation.importance, observation.observed_at.isoformat(), observation.source_id) > (previous.confidence, previous.importance, previous.observed_at.isoformat(), previous.source_id):
                        selected[identity] = observation
            except Exception:
                rejected += 1

        observations = sorted(
            selected.values(),
            key=lambda item: (-item.importance, -item.confidence, item.observed_at, item.source_id, item.summary.casefold()),
        )[: self.policy.max_observations]
        return DiscoveryRound(scope_id.strip(), query.strip(), tuple(observations), rejected, now,
                              now + timedelta(seconds=self.policy.interval_seconds))
