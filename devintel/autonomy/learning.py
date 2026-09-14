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
    def __post_init__(self) -> None:
        if not self.scope_id.strip() or not self.cycle_id.strip(): raise ValueError("scope_id and cycle_id are required")
        if not self.verified: raise ValueError("only verified outcomes can enter learning")
        if not math.isfinite(float(self.metric)) or not -1.0 <= float(self.metric) <= 1.0: raise ValueError("metric must be finite and between -1 and 1")
        if self.recorded_at.tzinfo is None: raise ValueError("recorded_at must be timezone-aware")

@dataclass(frozen=True)
class LearningProposal:
    scope_id: str
    basis_cycle_ids: tuple[str, ...]
    adjustment: str
    expected_delta: float
    confidence: float
    reversible: bool = True
    def __post_init__(self) -> None:
        if not self.scope_id.strip() or not self.basis_cycle_ids: raise ValueError("scope and evidence cycles are required")
        if not self.adjustment.strip(): raise ValueError("adjustment is required")
        if not 0.0 <= float(self.confidence) <= 1.0: raise ValueError("confidence must be between 0 and 1")
        if not self.reversible: raise ValueError("learning proposals must be reversible")

class OutcomeLearner:
    """Learns only from verified, same-scope outcomes and emits proposals."""
    def __init__(self, *, min_samples: int = 3, max_proposals: int = 3, min_confidence: float = 0.7) -> None:
        if min_samples < 1 or max_proposals < 1 or not 0.0 <= min_confidence <= 1.0: raise ValueError("invalid learning policy")
        self.min_samples, self.max_proposals, self.min_confidence = min_samples, max_proposals, min_confidence
    def reflect(self, evidence: Sequence[OutcomeEvidence]) -> tuple[LearningProposal, ...]:
        items = tuple(evidence)
        if not items: return ()
        scope = items[0].scope_id
        if any(item.scope_id != scope or not item.verified for item in items): raise ValueError("learning evidence must be verified and same-scope")
        if len(items) < self.min_samples: return ()
        mean = sum(item.metric for item in items) / len(items)
        # Confidence starts above the default threshold once the minimum
        # evidence window is satisfied, then increases monotonically to 1.
        confidence = min(1.0, 0.5 + len(items) / (self.min_samples * 2))
        if confidence < self.min_confidence: return ()
        direction = "increase" if mean > 0 else "decrease" if mean < 0 else "retain"
        proposal = LearningProposal(scope, tuple(item.cycle_id for item in items), f"{direction} bounded strategy weight", mean, confidence)
        return (proposal,)[:self.max_proposals]
