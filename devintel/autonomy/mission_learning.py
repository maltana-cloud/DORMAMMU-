"""Bounded bridge from verified mission results to durable learning and next objectives."""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Sequence
from .learning import OutcomeEvidence, OutcomeLearner, LearningProposal
from .learning_store import LearningStore
from .next_objective import NextObjective, ObjectiveCandidate, NextObjectiveSelector

@dataclass(frozen=True)
class LearningTransition:
    evidence: OutcomeEvidence
    proposals: tuple[LearningProposal, ...]
    next_objective: NextObjective | None

class MissionLearningBridge:
    """Persist verified outcomes, reflect bounded learning, then select one next objective."""
    def __init__(self, store: LearningStore, *, learner: OutcomeLearner | None = None, selector: NextObjectiveSelector | None = None, max_history: int = 100) -> None:
        if max_history <= 0: raise ValueError("max_history must be positive")
        self.store, self.learner, self.selector, self.max_history = store, learner or OutcomeLearner(), selector or NextObjectiveSelector(), max_history

    def transition(self, evidence: OutcomeEvidence, candidates: Sequence[ObjectiveCandidate] = ()) -> LearningTransition:
        if not evidence.verified: raise ValueError("mission learning requires verified outcome")
        self.store.record_outcome(evidence)
        outcomes = self.store.outcomes(evidence.scope_id, limit=self.max_history)
        proposals = self.learner.reflect(outcomes)
        for proposal in proposals: self.store.record_proposal(proposal)
        next_objective = self.selector.select(candidates, verified_outcomes=outcomes, learning_proposals=proposals)
        return LearningTransition(evidence, proposals, next_objective)
