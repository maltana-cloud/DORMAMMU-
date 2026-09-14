"""Bounded research-driven domain expansion contracts.

Domain discovery is evidence gathering, not authority. A proposed domain must
carry provenance, explicit boundaries, and verification state before it can be
considered for admission. This module does not install code, grant permissions,
or execute external providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Iterable


@dataclass(frozen=True)
class DomainEvidence:
    source: str
    claim: str
    confidence: float
    verified: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source is required")
        if not isinstance(self.claim, str) or not self.claim.strip():
            raise ValueError("claim is required")
        value = float(self.confidence)
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        object.__setattr__(self, "confidence", value)


@dataclass(frozen=True)
class DomainProposal:
    name: str
    purpose: str
    boundaries: tuple[str, ...]
    evidence: tuple[DomainEvidence, ...] = ()
    risks: tuple[str, ...] = ()
    required_capabilities: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)
    proposal_id: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("domain name is required")
        if not isinstance(self.purpose, str) or not self.purpose.strip():
            raise ValueError("domain purpose is required")
        boundaries = tuple(item.strip() for item in self.boundaries if isinstance(item, str) and item.strip())
        if not boundaries:
            raise ValueError("at least one domain boundary is required")
        evidence = tuple(self.evidence)
        if any(not isinstance(item, DomainEvidence) for item in evidence):
            raise TypeError("evidence must contain DomainEvidence values")
        object.__setattr__(self, "boundaries", boundaries)
        object.__setattr__(self, "evidence", evidence)
        payload = "|".join((self.name.strip().lower(), self.purpose.strip(), *boundaries))
        object.__setattr__(self, "proposal_id", sha256(payload.encode("utf-8")).hexdigest())


@dataclass(frozen=True)
class DomainAssessment:
    proposal_id: str
    evidence_score: float
    risk_score: float
    capability_coverage: float
    eligible: bool
    reasons: tuple[str, ...]


class DomainExpander:
    """Evaluate domain proposals without granting execution or authority."""

    def __init__(self, *, minimum_evidence: float = 0.65, maximum_risk: float = 0.40) -> None:
        if not 0.0 <= minimum_evidence <= 1.0:
            raise ValueError("minimum_evidence must be between 0 and 1")
        if not 0.0 <= maximum_risk <= 1.0:
            raise ValueError("maximum_risk must be between 0 and 1")
        self.minimum_evidence = minimum_evidence
        self.maximum_risk = maximum_risk

    def assess(self, proposal: DomainProposal, available_capabilities: Iterable[str] = ()) -> DomainAssessment:
        capabilities = {item.strip() for item in available_capabilities if isinstance(item, str) and item.strip()}
        verified = [item for item in proposal.evidence if item.verified]
        evidence_score = round(sum(item.confidence for item in verified) / len(verified), 4) if verified else 0.0
        risk_score = round(min(1.0, len(proposal.risks) / 5.0), 4)
        required = set(proposal.required_capabilities)
        coverage = 1.0 if not required else round(len(required & capabilities) / len(required), 4)
        reasons: list[str] = []
        if not verified:
            reasons.append("no verified evidence")
        if evidence_score < self.minimum_evidence:
            reasons.append("verified evidence is below threshold")
        if risk_score > self.maximum_risk:
            reasons.append("declared risk exceeds threshold")
        if coverage < 1.0:
            reasons.append("required capabilities are not fully available")
        return DomainAssessment(
            proposal.proposal_id,
            evidence_score,
            risk_score,
            coverage,
            not reasons,
            tuple(reasons),
        )

    @staticmethod
    def admission_allowed(assessment: DomainAssessment) -> bool:
        """Return whether the proposal passes the bounded admission gate.

        Passing this gate is not permission to install, execute, authenticate,
        spend, publish, or access protected resources.
        """
        return assessment.eligible
