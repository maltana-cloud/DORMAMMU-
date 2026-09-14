"""Bounded, evidence-gated reflection and outcome learning."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Sequence
import math

@dataclass(frozen=True)
class OutcomeEvidence:
    scope_id: str
    cycle_id: str
    success: bool
    verified: bool
    metric: float
    observation: str = ""
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    subject_id: str = ""
    def __post_init__(self) -> None:
        if not self.scope_id.strip() or not self.cycle_id.strip(): raise ValueError("scope_id and cycle_id are required")
        if not self.verified: raise ValueError("only verified outcomes can enter learning")
        if not math.isfinite(float(self.metric)) or not -1.0 <= float(self.metric) <= 1.0: raise ValueError("metric must be finite and between -1 and 1")
        if self.recorded_at.tzinfo is None: raise ValueError("recorded_at must be timezone-aware")
        if not isinstance(self.subject_id, str): raise TypeError("subject_id must be a string")

@dataclass(frozen=True)
class LearningProposal:
    scope_id: str
    basis_cycle_ids: tuple[str, ...]
    adjustment: str
    expected_delta: float
    confidence: float
    reversible: bool = True
    subject_id: str = ""
    def __post_init__(self) -> None:
        if not self.scope_id.strip() or not self.basis_cycle_ids: raise ValueError("scope and evidence cycles are required")
        if not self.adjustment.strip(): raise ValueError("adjustment is required")
        if not 0.0 <= float(self.confidence) <= 1.0: raise ValueError("confidence must be between 0 and 1")
        if not self.reversible: raise ValueError("learning proposals must be reversible")
        if not isinstance(self.subject_id, str): raise TypeError("subject_id must be a string")

class OutcomeLearner:
    """Learns only from verified, same-scope outcomes and emits proposals."""
    def __init__(self, *, min_samples: int = 3, max_proposals: int = 3, min_confidence: float = 0.7) -> None:
        if min_samples < 1 or max_proposals < 1 or not 0.0 <= min_confidence <= 1.0: raise ValueError("invalid learning policy")
        self.min_samples, self.max_proposals, self.min_confidence = min_samples, max_proposals, min_confidence
    def reflect(self, evidence: Sequence[OutcomeEvidence]) -> tuple[LearningProposal, ...]:
        items = tuple(evidence)
        if not items: return ()
        scopes = {item.scope_id for item in items}
        if len(scopes) != 1 or any(not item.verified for item in items): raise ValueError("learning evidence must be verified and same-scope")
        grouped: dict[str, list[OutcomeEvidence]] = {}
        for item in items: grouped.setdefault(item.subject_id, []).append(item)
        proposals: list[LearningProposal] = []
        for subject_id, group in sorted(grouped.items()):
            if subject_id and len(group) < self.min_samples: continue
            if not subject_id and len(group) < self.min_samples: continue
            mean = sum(item.metric for item in group) / len(group)
            confidence = min(1.0, 0.5 + len(group) / (self.min_samples * 2))
            if confidence < self.min_confidence: continue
            direction = "increase" if mean > 0 else "decrease" if mean < 0 else "retain"
            adjustment = f"{direction} bounded routing preference" if subject_id else f"{direction} bounded strategy weight"
            proposals.append(LearningProposal(group[0].scope_id, tuple(item.cycle_id for item in group), adjustment, mean, confidence, True, subject_id))
            if len(proposals) >= self.max_proposals: break
        return tuple(proposals)
