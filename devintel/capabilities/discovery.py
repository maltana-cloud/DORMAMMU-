"""Bounded capability discovery and deterministic candidate evaluation."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from .contracts import CapabilityDescriptor, CapabilityGap, CapabilityRequirement, CandidateEvaluator, CapabilityScout, DiscoveryResult, Evaluation
from .registry import CapabilityRegistry, GapRegistry


@dataclass(frozen=True)
class DiscoveryPolicy:
    allow_paid: bool = False
    require_explicit_permission: bool = True
    minimum_score: float = 0.75
    trusted_evidence_sources: tuple[str, ...] = ()
    require_provenance: bool = True


class DefaultEvaluator:
    def __init__(self, policy: DiscoveryPolicy | None = None) -> None: self.policy = policy or DiscoveryPolicy()

    def evaluate(self, requirement: CapabilityRequirement, candidate: CapabilityDescriptor) -> Evaluation:
        reasons: list[str] = []
        evidence_sources = {item.source for item in candidate.evidence}
        provenance_ok = bool(candidate.evidence) and all(item.trustworthy for item in candidate.evidence)
        source_ok = bool(evidence_sources & set(self.policy.trusted_evidence_sources)) if self.policy.trusted_evidence_sources else False
        trust = candidate.provider.strip().lower() != "unknown" and ((not self.policy.require_provenance and not self.policy.trusted_evidence_sources) or (provenance_ok and source_ok))
        security = candidate.metadata.get("security_status", "").lower() in {"safe", "verified", "approved"}
        compatibility = set(requirement.required_interfaces).issubset(candidate.interfaces)
        performance = candidate.metadata.get("performance", "").lower() in {"excellent", "good", "verified", "tested"}
        license_ok = bool(candidate.license.strip()) and (not requirement.required_license or candidate.license == requirement.required_license)
        currency_ok = requirement.max_cost is None or candidate.currency == requirement.currency
        cost_ok = currency_ok and (requirement.max_cost is None or candidate.cost <= requirement.max_cost) and (self.policy.allow_paid or candidate.cost == 0)
        permission_ok = not self.policy.require_explicit_permission or "approved" in {item.lower() for item in candidate.permissions}
        checks = (trust, security, compatibility, performance, license_ok, cost_ok, permission_ok)
        score = sum(checks) / len(checks)
        for name, ok in zip(("trust", "security", "compatibility", "performance", "license", "cost", "permission"), checks):
            if not ok: reasons.append(f"{name} check failed")
        if self.policy.minimum_score > score: reasons.append("minimum score check failed")
        eligible = all(checks) and score >= self.policy.minimum_score
        return Evaluation(candidate, trust, security, compatibility, performance, license_ok, cost_ok, permission_ok, score, tuple(reasons)) if eligible else Evaluation(candidate, trust, security, compatibility, performance, license_ok, cost_ok, permission_ok, score, tuple(reasons))


class CapabilityDiscovery:
    """Advisory discovery only: no installation, execution, or authority escalation."""
    def __init__(self, registry: CapabilityRegistry | None = None, gaps: GapRegistry | None = None, evaluator: CandidateEvaluator | None = None) -> None:
        self.registry = registry or CapabilityRegistry()
        self.gaps = gaps or GapRegistry()
        self.evaluator = evaluator or DefaultEvaluator()
        self._scouts: list[CapabilityScout] = []

    def add_scout(self, scout: CapabilityScout) -> None:
        self._scouts.append(scout)

    def discover(self, requirement: CapabilityRequirement, gap_id: str | None = None) -> DiscoveryResult:
        gap = CapabilityGap(gap_id or f"gap:{requirement.capability_id}", requirement, datetime.now(timezone.utc).isoformat())
        self.gaps.record(gap)
        candidates: list[CapabilityDescriptor] = []
        for scout in self._scouts:
            for candidate in scout.discover(requirement):
                if candidate.capability_id not in {c.capability_id for c in candidates}:
                    candidates.append(candidate)
        evaluations = tuple(self.evaluator.evaluate(requirement, candidate) for candidate in candidates)
        return DiscoveryResult(gap, tuple(candidates), evaluations)

    def register_approved(self, evaluation: Evaluation) -> CapabilityDescriptor:
        if not evaluation.eligible: raise PermissionError("capability is not eligible for registration")
        if evaluation.candidate.capability_id in self.registry.ids():
            return self.registry.get(evaluation.candidate.capability_id)  # type: ignore[return-value]
        from dataclasses import replace
        item = replace(evaluation.candidate, status=evaluation.candidate.status.REGISTERED)
        self.registry.register(item)
        return item
