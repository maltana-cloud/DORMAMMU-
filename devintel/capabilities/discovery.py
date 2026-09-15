"""Bounded capability discovery and deterministic candidate evaluation."""
from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from .contracts import CapabilityDescriptor, CapabilityGap, CapabilityRequirement, CapabilityStatus, CandidateEvaluator, CapabilityScout, DiscoveryResult, Evaluation
from .registry import CapabilityRegistry, GapRegistry


@dataclass(frozen=True)
class DiscoveryPolicy:
    allow_paid: bool = False
    require_explicit_permission: bool = True
    minimum_score: float = 0.75
    trusted_evidence_sources: tuple[str, ...] = ()
    require_provenance: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_score <= 1:
            raise ValueError("minimum_score must be between 0 and 1")


class DefaultEvaluator:
    def __init__(self, policy: DiscoveryPolicy | None = None) -> None:
        self.policy = policy or DiscoveryPolicy()

    def evaluate(self, requirement: CapabilityRequirement, candidate: CapabilityDescriptor) -> Evaluation:
        reasons: list[str] = []
        evidence_sources = {item.source for item in candidate.evidence}
        provenance_ok = bool(candidate.evidence) and all(item.trustworthy for item in candidate.evidence)
        source_ok = bool(evidence_sources & set(self.policy.trusted_evidence_sources)) if self.policy.trusted_evidence_sources else False
        trust = candidate.provider.strip().lower() not in {"", "unknown"} and candidate.capability_id.strip().lower() not in {"", "unknown"} and (not self.policy.require_provenance or (provenance_ok and source_ok))
        security = candidate.metadata.get("security_status", "").lower() in {"safe", "verified", "approved"} if self.policy.require_provenance else "unsafe" not in {x.lower() for x in candidate.metadata.values()}
        compatibility = set(requirement.required_interfaces).issubset(candidate.interfaces)
        performance = candidate.metadata.get("performance", "").lower() in {"excellent", "good", "verified", "tested"} if self.policy.require_provenance else candidate.metadata.get("performance", "unknown").lower() not in {"poor", "failed"}
        license_ok = bool(candidate.license.strip()) and (not requirement.required_license or candidate.license == requirement.required_license)
        currency_ok = requirement.max_cost is None or candidate.currency == requirement.currency
        cost_ok = currency_ok and (requirement.max_cost is None or candidate.cost <= requirement.max_cost) and (self.policy.allow_paid or candidate.cost == 0)
        permission_ok = not self.policy.require_explicit_permission or "approved" in {item.lower() for item in candidate.permissions}
        checks = (trust, security, compatibility, performance, license_ok, cost_ok, permission_ok)
        score = sum(checks) / len(checks)
        for name, ok in zip(("trust", "security", "compatibility", "performance", "license", "cost", "permission"), checks):
            if not ok:
                reasons.append(f"{name} check failed")
        if self.policy.minimum_score > score:
            reasons.append("minimum score check failed")
        return Evaluation(candidate, *checks, score, tuple(reasons), self.policy.minimum_score)


class CapabilityDiscovery:
    """Advisory discovery only: no installation, execution, or authority escalation."""
    def __init__(self, registry: CapabilityRegistry | None = None, gaps: GapRegistry | None = None, evaluator: CandidateEvaluator | None = None, *, max_scouts: int = 32, max_candidates: int = 256) -> None:
        if max_scouts <= 0 or max_candidates <= 0:
            raise ValueError("discovery bounds must be positive")
        self.registry = registry or CapabilityRegistry()
        self.gaps = gaps or GapRegistry()
        self.evaluator = evaluator or DefaultEvaluator()
        self._scouts: list[CapabilityScout] = []
        self._max_scouts = max_scouts
        self._max_candidates = max_candidates

    def add_scout(self, scout: CapabilityScout) -> None:
        if len(self._scouts) >= self._max_scouts:
            raise RuntimeError("scout capacity reached")
        self._scouts.append(scout)

    def discover(self, requirement: CapabilityRequirement, gap_id: str | None = None) -> DiscoveryResult:
        gap = CapabilityGap(gap_id or f"gap:{requirement.capability_id}", requirement, datetime.now(timezone.utc).isoformat())
        self.gaps.record(gap)
        candidates: dict[str, CapabilityDescriptor] = {}
        failures: list[str] = []
        for index, scout in enumerate(self._scouts):
            try:
                discovered = scout.discover(requirement)
                for candidate in discovered:
                    if not isinstance(candidate, CapabilityDescriptor):
                        failures.append(f"scout:{index}:invalid_candidate")
                        continue
                    candidates.setdefault(candidate.capability_id, candidate)
                    if len(candidates) >= self._max_candidates:
                        break
            except Exception as exc:
                failures.append(f"scout:{index}:{type(exc).__name__}")
            if len(candidates) >= self._max_candidates:
                break
        ordered_candidates = tuple(sorted(candidates.values(), key=lambda item: (item.capability_id, item.version, item.provider)))
        evaluations = [self.evaluator.evaluate(requirement, candidate) for candidate in ordered_candidates]
        evaluations.sort(key=lambda item: (-item.score, item.candidate.cost, item.candidate.capability_id, item.candidate.version, item.candidate.provider))
        return DiscoveryResult(gap, ordered_candidates, tuple(evaluations), tuple(failures))

    def register_approved(self, evaluation: Evaluation) -> CapabilityDescriptor:
        if not evaluation.eligible:
            raise PermissionError("capability is not eligible for registration")
        if evaluation.candidate.capability_id in self.registry.ids():
            return self.registry.get(evaluation.candidate.capability_id)  # type: ignore[return-value]
        item = replace(evaluation.candidate, status=CapabilityStatus.REGISTERED)
        self.registry.register(item)
        return item
