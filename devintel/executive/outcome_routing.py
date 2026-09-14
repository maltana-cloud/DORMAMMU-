"""Durable, bounded bridge from verified outcomes to routing preferences."""
from __future__ import annotations
from collections.abc import Sequence
from ..autonomy.learning import LearningProposal, OutcomeEvidence, OutcomeLearner
from ..autonomy.learning_store import LearningStore
from .routing import RouteCandidate, RoutingRequirement, SpecialistRouter

class OutcomeAwareRoutingService:
    """Applies only reversible learned preferences; hard routing gates remain dominant."""
    def __init__(self, router: SpecialistRouter, store: LearningStore, learner: OutcomeLearner | None = None, *, max_preferences: int = 256) -> None:
        if max_preferences <= 0: raise ValueError("max_preferences must be positive")
        self.router, self.store, self.learner = router, store, learner or OutcomeLearner()
        self.max_preferences = max_preferences

    def record_and_reflect(self, evidence: OutcomeEvidence) -> tuple[LearningProposal, ...]:
        self.store.record_outcome(evidence)
        proposals = self.learner.reflect(self.store.outcomes(evidence.scope_id, limit=self.max_preferences))
        for proposal in proposals: self.store.record_proposal(proposal)
        return proposals

    def preferences(self, scope_id: str) -> dict[str, float]:
        result: dict[str, float] = {}
        for proposal in self.store.proposals(scope_id, limit=self.max_preferences):
            if not proposal.subject_id or proposal.subject_id in result: continue
            result[proposal.subject_id] = max(-1.0, min(1.0, proposal.expected_delta)) * 10.0
        return result

    def select(self, scope_id: str, requirement: RoutingRequirement) -> RouteCandidate:
        return self.router.select(requirement, learned_preferences=self.preferences(scope_id))

    def plan_collaboration(self, scope_id: str, steps: Sequence[tuple[str, RoutingRequirement]]):
        return self.router.plan_collaboration(steps, learned_preferences=self.preferences(scope_id))
