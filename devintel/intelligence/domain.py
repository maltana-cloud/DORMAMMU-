"""Bounded domain intelligence built from verified knowledge.

This layer turns the established synthesis result into a deterministic domain
profile. It never treats unverified material as knowledge or grants authority.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..modules.research.normalization import normalize_text
from ..modules.research.synthesis import SynthesisResult


@dataclass(frozen=True)
class DomainSignal:
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
    domain: str
    signals: tuple[DomainSignal, ...]
    entities: tuple[str, ...]
    topics: tuple[str, ...]
    uncertainty: str


class DomainIntelligenceEngine:
    """Build bounded domain intelligence from established synthesis output."""

    def __init__(self, *, max_signals: int = 100) -> None:
        if max_signals <= 0:
            raise ValueError("max_signals must be positive")
        self.max_signals = max_signals

    def build(self, domain: str, synthesis: SynthesisResult, *, limit: int = 50) -> DomainProfile:
        normalized_domain = normalize_text(domain)
        if not normalized_domain:
            raise ValueError("domain is required")
        if not isinstance(synthesis, SynthesisResult):
            raise TypeError("synthesis must be a SynthesisResult")
        if limit <= 0 or limit > self.max_signals:
            raise ValueError("limit is outside the configured bound")

        signals: list[DomainSignal] = []
        malformed = 0
        for item in synthesis.signals:
            parts = item.statement.split(" ", 2)
            if len(parts) != 3:
                malformed += 1
                continue
            try:
                subject, predicate, object_value = (normalize_text(part) for part in parts)
                signal = DomainSignal(
                    subject,
                    predicate,
                    object_value,
                    min(item.confidence, 0.49) if item.uncertain else item.confidence,
                    item.evidence_urls,
                    item.uncertain,
                )
            except (TypeError, ValueError):
                malformed += 1
                continue
            signals.append(signal)

        signals.sort(key=lambda item: (-item.confidence, item.subject.lower(), item.predicate.lower(), item.object.lower()))
        bounded = tuple(signals[:limit])
        entities = tuple(sorted({signal.subject for signal in bounded}, key=str.lower))
        topics = tuple(sorted({signal.object for signal in bounded}, key=str.lower))

        if not bounded:
            uncertainty = "high: no valid verified domain signals available"
        elif synthesis.uncertainty.startswith("high:") or any(signal.uncertain for signal in bounded):
            uncertainty = "high: domain profile contains unresolved synthesis uncertainty"
        elif malformed or len(signals) > limit:
            uncertainty = "bounded: profile contains verified signals with preserved provenance and exclusions"
        else:
            uncertainty = "bounded: profile contains verified signals with preserved provenance"
        return DomainProfile(normalized_domain, bounded, entities, topics, uncertainty)
