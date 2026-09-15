"""Bounded domain intelligence built from verified knowledge.

This layer turns verified claims into a deterministic, scope-isolated domain
profile. It does not infer authority, execute actions, or treat unverified
material as knowledge.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..modules.research.synthesis import VerifiedClaim
from ..modules.research.normalization import normalize_text


@dataclass(frozen=True)
class DomainSignal:
    """A normalized, evidence-backed signal about a domain."""

    subject: str
    predicate: str
    object: str
    confidence: float
    evidence_urls: tuple[str, ...]
    uncertain: bool

    def __post_init__(self) -> None:
        for name, value in (("subject", self.subject), ("predicate", self.predicate), ("object", self.object)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.uncertain and self.confidence > 0.49:
            raise ValueError("uncertain signals cannot have high confidence")


@dataclass(frozen=True)
class DomainProfile:
    """Deterministic domain view assembled from verified claims."""

    domain: str
    signals: tuple[DomainSignal, ...]
    entities: tuple[str, ...]
    topics: tuple[str, ...]
    uncertainty: str


class DomainIntelligenceEngine:
    """Build bounded domain intelligence from verified synthesis inputs."""

    def __init__(self, *, max_signals: int = 100) -> None:
        if max_signals <= 0:
            raise ValueError("max_signals must be positive")
        self.max_signals = max_signals

    def build(
        self,
        domain: str,
        claims: Iterable[VerifiedClaim],
        *,
        limit: int = 50,
    ) -> DomainProfile:
        normalized_domain = normalize_text(domain)
        if not normalized_domain:
            raise ValueError("domain is required")
        if limit <= 0 or limit > self.max_signals:
            raise ValueError("limit is outside the configured bound")

        items = tuple(claims)
        if any(not isinstance(item, VerifiedClaim) for item in items):
            raise TypeError("claims must contain only VerifiedClaim values")

        signals: list[DomainSignal] = []
        for item in items:
            subject = normalize_text(item.claim.subject)
            predicate = normalize_text(item.claim.predicate)
            object_value = normalize_text(item.claim.object)
            if not subject or not predicate or not object_value:
                continue
            confidence = min(item.confidence, 0.49) if item.uncertain else item.confidence
            signals.append(
                DomainSignal(
                    subject,
                    predicate,
                    object_value,
                    confidence,
                    item.evidence_urls,
                    item.uncertain,
                )
            )

        signals.sort(key=lambda item: (-item.confidence, item.subject.lower(), item.predicate.lower(), item.object.lower()))
        bounded = tuple(signals[:limit])
        entity_values = {signal.subject for signal in bounded}
        topic_values = {signal.object for signal in bounded}
        entities = tuple(sorted(entity_values, key=str.lower))
        topics = tuple(sorted(topic_values, key=str.lower))

        if not bounded:
            uncertainty = "high: no verified domain signals available"
        elif any(signal.uncertain for signal in bounded):
            uncertainty = "moderate: domain profile contains unresolved uncertainty"
        else:
            uncertainty = "bounded: profile contains only verified signals with preserved provenance"
        return DomainProfile(normalized_domain, bounded, entities, topics, uncertainty)
