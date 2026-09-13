"""Evidence-backed knowledge synthesis.

Synthesis is deliberately conservative: only verified evidence enters the
result, provenance is preserved, contradictions are explicit, and uncertainty
is never hidden behind a single confidence number.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .knowledge import Claim
from .verification import VerificationResult


@dataclass(frozen=True)
class VerifiedClaim:
    claim: Claim
    verification: VerificationResult

    def __post_init__(self) -> None:
        if not self.verification.verified:
            raise ValueError("VerifiedClaim requires a verified VerificationResult")

    @property
    def confidence(self) -> float:
        return min(self.claim.confidence, self.verification.confidence)

    @property
    def evidence_urls(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(self.claim.evidence_urls + self.verification.evidence_urls))


@dataclass(frozen=True)
class Contradiction:
    subject: str
    predicate: str
    claims: tuple[VerifiedClaim, ...]
    reason: str


@dataclass(frozen=True)
class SynthesisSignal:
    statement: str
    confidence: float
    evidence_urls: tuple[str, ...]
    uncertain: bool


@dataclass(frozen=True)
class SynthesisResult:
    topic: str
    signals: tuple[SynthesisSignal, ...]
    contradictions: tuple[Contradiction, ...]
    excluded_claims: int
    uncertainty: str

    @property
    def provenance(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(url for signal in self.signals for url in signal.evidence_urls))

    def executive_requirements(self) -> tuple[str, ...]:
        """Expose only evidence-backed statements; this does not grant authority."""
        return tuple(signal.statement for signal in self.signals if signal.confidence >= 0.5 and not signal.uncertain)


class KnowledgeSynthesisEngine:
    """Combine verified claims without treating corroboration as automatic truth."""

    def synthesize(self, topic: str, claims: Sequence[VerifiedClaim], *, excluded_claims: int = 0) -> SynthesisResult:
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("topic is required")
        grouped: dict[tuple[str, str], dict[str, list[VerifiedClaim]]] = {}
        for item in claims:
            key = (item.claim.subject, item.claim.predicate)
            grouped.setdefault(key, {}).setdefault(item.claim.object, []).append(item)

        signals: list[SynthesisSignal] = []
        contradictions: list[Contradiction] = []
        for (subject, predicate), objects in sorted(grouped.items()):
            if len(objects) > 1:
                contradictory_claims = tuple(item for items in objects.values() for item in items)
                contradiction = Contradiction(subject, predicate, contradictory_claims, "verified claims assert different objects for the same subject/predicate")
                contradictions.append(contradiction)
                for object_value, items in sorted(objects.items()):
                    evidence = tuple(dict.fromkeys(url for item in items for url in item.evidence_urls))
                    confidence = min(item.confidence for item in items)
                    signals.append(SynthesisSignal(f"{subject} {predicate} {object_value}", min(confidence, 0.49), evidence, True))
                continue

            items = next(iter(objects.values()))
            best = max(items, key=lambda item: item.confidence)
            evidence = tuple(dict.fromkeys(url for item in items for url in item.evidence_urls))
            signals.append(SynthesisSignal(f"{subject} {predicate} {best.claim.object}", best.confidence, evidence, False))

        if contradictions:
            uncertainty = "high: contradictory verified claims require resolution before high-confidence executive use"
        elif not signals:
            uncertainty = "high: no verified claims available"
        elif any(signal.confidence < 0.5 for signal in signals):
            uncertainty = "moderate: available evidence has limited confidence"
        else:
            uncertainty = "bounded: synthesis contains only verified claims and preserved provenance"
        return SynthesisResult(topic, tuple(signals), tuple(contradictions), excluded_claims, uncertainty)
