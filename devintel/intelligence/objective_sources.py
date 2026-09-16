"""Evidence-backed objective candidates derived from durable knowledge."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from ..autonomy.next_objective import ObjectiveCandidate
from .knowledge import KnowledgeIntelligence, KnowledgeQuery


@dataclass(frozen=True)
class KnowledgeObjectivePolicy:
    max_candidates: int = 16
    min_confidence: float = 0.7
    max_age_seconds: float | None = None
    include_conflicts: bool = True
    conflict_priority: float = 0.8

    def __post_init__(self) -> None:
        if self.max_candidates <= 0 or not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("invalid knowledge objective policy")
        if self.max_age_seconds is not None and self.max_age_seconds < 0:
            raise ValueError("max_age_seconds must be non-negative")
        if not isinstance(self.include_conflicts, bool):
            raise ValueError("include_conflicts must be a bool")
        if not 0.0 <= self.conflict_priority <= 1.0:
            raise ValueError("conflict_priority must be between 0 and 1")


class KnowledgeObjectiveSource:
    """Translate verified durable knowledge into advisory, bounded objectives.

    Ordinary claims produce verification/implication objectives. Conflicting
    verified claims produce explicit resolution objectives instead of silently
    selecting one side. Stale or low-confidence records never become ordinary
    objectives, and all output remains advisory with no execution authority.
    """

    def __init__(self, knowledge: KnowledgeIntelligence, *, policy: KnowledgeObjectivePolicy | None = None) -> None:
        self.knowledge = knowledge
        self.policy = policy or KnowledgeObjectivePolicy()

    def candidates(self, scope_id: str, *, text: str = "") -> tuple[ObjectiveCandidate, ...]:
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("scope_id is required")
        scope = scope_id.strip()
        items = self.knowledge.query(KnowledgeQuery(
            scope_id=scope,
            text=text,
            limit=self.knowledge.max_results,
            max_age_seconds=self.policy.max_age_seconds,
        ))
        conflict_ids = {
            record_id
            for conflict in self.knowledge.conflicts(scope)
            for record_id in conflict.record_ids
        }
        result: list[ObjectiveCandidate] = []
        for item in items:
            if item.stale or item.confidence < self.policy.min_confidence:
                continue
            if item.record_id in conflict_ids:
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

        if self.policy.include_conflicts:
            for conflict in self.knowledge.conflicts(scope):
                if text.strip() and text.strip().lower() not in f"{conflict.subject} {conflict.predicate} {' '.join(conflict.objects)}".lower():
                    continue
                digest = hashlib.sha256(
                    (scope + "\x1f" + conflict.subject + "\x1f" + conflict.predicate + "\x1f" + "\x1e".join(conflict.objects)).encode("utf-8")
                ).hexdigest()[:32]
                objective_id = f"knowledge-conflict:{digest}"
                objective = f"resolve conflicting verified knowledge about {conflict.subject} {conflict.predicate}"
                result.append(ObjectiveCandidate(
                    objective_id=objective_id,
                    objective=objective,
                    scope_id=scope,
                    source="verified-knowledge-conflict",
                    priority=self.policy.conflict_priority,
                    evidence_cycle_ids=conflict.record_ids,
                ))

        result.sort(key=lambda c: (-c.priority, c.objective_id, c.objective, c.source))
        return tuple(result[: self.policy.max_candidates])
