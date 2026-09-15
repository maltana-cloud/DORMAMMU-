"""Controlled evolution: evaluate reversible behavioral changes before promotion."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Sequence
from uuid import uuid4

from .learning import LearningProposal

_FORBIDDEN_TARGETS = frozenset({"authority", "security", "secrets", "credentials", "owner_control", "recovery", "code"})

@dataclass(frozen=True)
class ImprovementCandidate:
    candidate_id: str
    scope_id: str
    target: str
    adjustment: str
    basis_cycle_ids: tuple[str, ...]
    expected_delta: float
    confidence: float
    parent_version: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.candidate_id.strip() or not self.scope_id.strip() or not self.target.strip():
            raise ValueError("candidate_id, scope_id and target are required")
        if not self.adjustment.strip() or not self.basis_cycle_ids:
            raise ValueError("adjustment and evidence cycles are required")
        if self.target.strip().lower() in _FORBIDDEN_TARGETS:
            raise ValueError("evolution cannot target authority, security, secrets, credentials, owner control, recovery, or code")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.parent_version < 0:
            raise ValueError("parent_version cannot be negative")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

@dataclass(frozen=True)
class EvolutionEvaluation:
    candidate_id: str
    safe: bool
    baseline_metric: float
    candidate_metric: float
    confidence: float
    evidence_count: int
    reason: str = ""
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def delta(self) -> float:
        return float(self.candidate_metric) - float(self.baseline_metric)

    def __post_init__(self) -> None:
        if not self.candidate_id.strip() or self.evidence_count < 1:
            raise ValueError("candidate_id and evidence_count are required")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.evaluated_at.tzinfo is None:
            raise ValueError("evaluated_at must be timezone-aware")

@dataclass(frozen=True)
class Promotion:
    candidate_id: str
    scope_id: str
    version: int
    parent_version: int
    promoted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass(frozen=True)
class EvolutionPolicy:
    min_evidence: int = 3
    min_gain: float = 0.05
    min_confidence: float = 0.8
    max_candidates: int = 8

    def __post_init__(self) -> None:
        if self.min_evidence < 1 or self.max_candidates < 1:
            raise ValueError("evolution limits must be positive")
        if self.min_gain < 0.0 or self.min_confidence < 0.0 or self.min_confidence > 1.0:
            raise ValueError("invalid evolution policy")

Evaluator = Callable[[ImprovementCandidate], EvolutionEvaluation]

class EvolutionEngine:
    """Turns verified learning proposals into evaluated, reversible behavioral versions."""
    def __init__(self, policy: EvolutionPolicy | None = None) -> None:
        self.policy = policy or EvolutionPolicy()
        self._active: dict[str, int] = {}
        self._promotions: dict[str, Promotion] = {}

    def candidates_from(self, proposals: Sequence[LearningProposal]) -> tuple[ImprovementCandidate, ...]:
        result: list[ImprovementCandidate] = []
        for proposal in proposals:
            if len(proposal.basis_cycle_ids) < self.policy.min_evidence or not proposal.reversible:
                continue
            target = "routing" if proposal.subject_id else "strategy"
            result.append(ImprovementCandidate(uuid4().hex, proposal.scope_id, target, proposal.adjustment, proposal.basis_cycle_ids, proposal.expected_delta, proposal.confidence, self._active.get(proposal.scope_id, 0)))
            if len(result) >= self.policy.max_candidates:
                break
        return tuple(result)

    def evaluate(self, candidate: ImprovementCandidate, evaluator: Evaluator) -> EvolutionEvaluation:
        evaluation = evaluator(candidate)
        if evaluation.candidate_id != candidate.candidate_id:
            raise ValueError("evaluator returned a different candidate")
        if evaluation.evidence_count < self.policy.min_evidence:
            return EvolutionEvaluation(candidate.candidate_id, False, evaluation.baseline_metric, evaluation.candidate_metric, evaluation.confidence, evaluation.evidence_count, "insufficient evaluation evidence")
        return evaluation

    def promote(self, candidate: ImprovementCandidate, evaluation: EvolutionEvaluation) -> Promotion:
        if evaluation.candidate_id != candidate.candidate_id:
            raise ValueError("evaluation does not match candidate")
        if not evaluation.safe or evaluation.delta < self.policy.min_gain or evaluation.confidence < self.policy.min_confidence:
            raise ValueError("candidate did not meet promotion gates")
        current = self._active.get(candidate.scope_id, 0)
        if candidate.parent_version != current:
            raise ValueError("candidate is stale; rebase from the current active version")
        promotion = Promotion(candidate.candidate_id, candidate.scope_id, current + 1, current)
        self._active[candidate.scope_id] = promotion.version
        self._promotions[candidate.candidate_id] = promotion
        return promotion

    def rollback(self, scope_id: str, version: int) -> int:
        if not scope_id.strip() or version < 0:
            raise ValueError("scope_id and non-negative version are required")
        current = self._active.get(scope_id, 0)
        if version > current:
            raise ValueError("cannot roll forward during rollback")
        self._active[scope_id] = version
        return version

    def active_version(self, scope_id: str) -> int:
        return self._active.get(scope_id, 0)

    def promotion(self, candidate_id: str) -> Promotion | None:
        return self._promotions.get(candidate_id)
