"""Controlled ecosystem evolution built on the locked DORMAMMU boundaries."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from ..autonomy.evolution import EvolutionEngine, EvolutionEvaluation, EvolutionPolicy, ImprovementCandidate, Promotion
from ..autonomy.learning import LearningProposal

_PROTECTED = frozenset({"authority", "security", "secrets", "credentials", "owner_control", "recovery", "code"})


@dataclass(frozen=True)
class EvolutionCyclePolicy:
    """Bound the amount of ecosystem change considered in one cycle."""
    max_proposals: int = 8
    max_candidates: int = 8
    require_capability_health: bool = True

    def __post_init__(self) -> None:
        if self.max_proposals < 1 or self.max_candidates < 1:
            raise ValueError("evolution cycle limits must be positive")


@dataclass(frozen=True)
class EvolutionCycleResult:
    """Auditable result of one bounded evolution cycle."""
    proposals_seen: int
    candidates_considered: tuple[str, ...]
    evaluations: tuple[EvolutionEvaluation, ...]
    promotions: tuple[Promotion, ...]
    rejected: int
    blocked: int


Evaluator = Callable[[ImprovementCandidate], EvolutionEvaluation]


class EcosystemEvolutionEngine:
    """Coordinate controlled evolution without granting new authority."""
    def __init__(self, *, evolution: EvolutionEngine | None = None, policy: EvolutionCyclePolicy | None = None) -> None:
        self.policy = policy or EvolutionCyclePolicy()
        self.evolution = evolution or EvolutionEngine(EvolutionPolicy(max_candidates=self.policy.max_candidates))

    def candidates(self, proposals: Sequence[LearningProposal], *, capability_health: dict[str, bool] | None = None) -> tuple[ImprovementCandidate, ...]:
        bounded = tuple(proposals[: self.policy.max_proposals])
        health = capability_health or {}
        result: list[ImprovementCandidate] = []
        for candidate in self.evolution.candidates_from(bounded):
            if candidate.target.lower() in _PROTECTED:
                continue
            if self.policy.require_capability_health and candidate.scope_id in health and not health[candidate.scope_id]:
                continue
            result.append(candidate)
            if len(result) >= self.policy.max_candidates:
                break
        return tuple(result)

    def run(self, proposals: Sequence[LearningProposal], evaluator: Evaluator, *, capability_health: dict[str, bool] | None = None) -> EvolutionCycleResult:
        """Evaluate and promote only bounded, safe, measurable ecosystem changes."""
        if not callable(evaluator):
            raise TypeError("evaluator must be callable")
        candidates = self.candidates(proposals, capability_health=capability_health)
        evaluations: list[EvolutionEvaluation] = []
        promotions: list[Promotion] = []
        rejected = 0
        bounded_count = min(len(proposals), self.policy.max_proposals)
        blocked = max(0, bounded_count - len(candidates))
        for candidate in candidates:
            evaluation = self.evolution.evaluate(candidate, evaluator)
            evaluations.append(evaluation)
            if not evaluation.safe:
                rejected += 1
                continue
            try:
                promotions.append(self.evolution.promote(candidate, evaluation))
            except ValueError:
                rejected += 1
        return EvolutionCycleResult(bounded_count, tuple(c.candidate_id for c in candidates), tuple(evaluations), tuple(promotions), rejected, blocked)

    def rollback(self, scope_id: str, version: int) -> int:
        """Roll a scope back to an existing non-forward version."""
        return self.evolution.rollback(scope_id, version)
