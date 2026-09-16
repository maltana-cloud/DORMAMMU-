"""Evidence-backed objective candidates derived from durable knowledge."""
from __future__ import annotations

from dataclasses import dataclass

from ..autonomy.next_objective import ObjectiveCandidate
from .knowledge import KnowledgeIntelligence, KnowledgeQuery


@dataclass(frozen=True)
class KnowledgeObjectivePolicy:
    max_candidates: int = 16
    min_confidence: float = 0.7
    max_age_seconds: float | None = None

    def __post_init__(self) -> None:
        if self.max_candidates <= 0 or not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("invalid knowledge objective policy")
        if self.max_age_seconds is not None and self.max_age_seconds < 0:
            raise ValueError("max_age_seconds must be non-negative")


class KnowledgeObjectiveSource:
    """Translate verified durable knowledge into advisory, bounded objectives."""

    def __init__(self, knowledge: KnowledgeIntelligence, *, policy: KnowledgeObjectivePolicy | None = None) -> None:
        self.knowledge = knowledge
        self.policy = policy or KnowledgeObjectivePolicy()

    def candidates(self, scope_id: str, *, text: str = "") -> tuple[ObjectiveCandidate, ...]:
        items = self.knowledge.query(KnowledgeQuery(
            scope_id=scope_id,
            text=text,
            limit=self.policy.max_candidates,
            max_age_seconds=self.policy.max_age_seconds,
        ))
        result: list[ObjectiveCandidate] = []
        for item in items:
            if item.stale or item.confidence < self.policy.min_confidence:
                continue
            objective_id = f"knowledge:{item.record_id}"
            objective = f"verify implications of {item.subject} {item.predicate} {item.object}"
            result.append(ObjectiveCandidate(
                objective_id=objective_id,
                objective=objective,
                scope_id=item.scope_id,
                source="verified-knowledge",
                priority=item.confidence,
                evidence_cycle_ids=(item.record_id,),
            ))
        result.sort(key=lambda c: (-c.priority, c.objective_id, c.objective))
        return tuple(result[: self.policy.max_candidates])
