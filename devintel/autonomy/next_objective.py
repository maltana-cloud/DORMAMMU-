"""Deterministic, evidence-gated selection of the next bounded mission objective."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
from .learning import OutcomeEvidence, OutcomeLearner, LearningProposal

@dataclass(frozen=True)
class ObjectiveCandidate:
    objective_id: str
    objective: str
    scope_id: str
    source: str
    priority: float = 0.0
    evidence_cycle_ids: tuple[str, ...] = ()
    def __post_init__(self) -> None:
        if not self.objective_id.strip() or not self.objective.strip(): raise ValueError("objective_id and objective are required")
        if not self.scope_id.strip() or not self.source.strip(): raise ValueError("scope_id and source are required")
        if not -1.0 <= float(self.priority) <= 1.0: raise ValueError("priority must be between -1 and 1")

@dataclass(frozen=True)
class NextObjective:
    candidate: ObjectiveCandidate
    rationale: str
    learning_proposal_ids: tuple[str, ...] = ()

class NextObjectiveSelector:
    """Selects the next objective without creating authority or execution paths."""
    def __init__(self, *, max_candidates: int = 64, min_confidence: float = 0.7) -> None:
        if max_candidates <= 0 or not 0.0 <= min_confidence <= 1.0: raise ValueError("invalid objective-selection policy")
        self.max_candidates, self.min_confidence = max_candidates, min_confidence
    def select(self, candidates: Sequence[ObjectiveCandidate], *, verified_outcomes: Sequence[OutcomeEvidence] = (), learning_proposals: Sequence[LearningProposal] = ()) -> NextObjective | None:
        items = tuple(candidates)[:self.max_candidates]
        if not items: return None
        scopes = {c.scope_id for c in items}
        if len(scopes) != 1: raise ValueError("objective candidates must use one scope")
        if any(not o.verified for o in verified_outcomes): raise ValueError("only verified outcomes may influence selection")
        proposal_ids = tuple(f"{p.scope_id}:{p.subject_id}:{p.adjustment}:{p.expected_delta:.6f}" for p in learning_proposals if p.reversible and p.confidence >= self.min_confidence and p.scope_id in scopes)
        outcome_by_subject: dict[str,float] = {}
        for outcome in verified_outcomes: outcome_by_subject[outcome.subject_id] = outcome_by_subject.get(outcome.subject_id, 0.0) + float(outcome.metric)
        ranked = sorted(items, key=lambda c: (-(float(c.priority) + max(-1.0,min(1.0,outcome_by_subject.get(c.objective_id,0.0)))), c.objective_id, c.objective, c.source))
        return NextObjective(ranked[0], "selected deterministically from bounded candidates and verified outcomes", proposal_ids)
    def select_from_learning(self, candidates: Sequence[ObjectiveCandidate], evidence: Sequence[OutcomeEvidence], *, learner: OutcomeLearner | None = None) -> NextObjective | None:
        items = tuple(evidence)
        if not items: return self.select(candidates)
        if len({e.scope_id for e in items}) != 1 or any(not e.verified for e in items): raise ValueError("learning evidence must be verified and same-scope")
        proposals = (learner or OutcomeLearner()).reflect(items)
        return self.select(candidates, verified_outcomes=items, learning_proposals=proposals)
