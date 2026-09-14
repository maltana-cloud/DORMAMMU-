"""Bounded core-intelligence contracts for DORMAMMU.

This layer turns verified evidence, learned outcomes, and registered
capabilities into an explicit cognitive state. It does not grant authority or
perform external actions. Decisions remain proposals until the existing
executive/permission boundaries approve them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Mapping, Sequence

from ..modules.research import SynthesisResult

_MAX_FACTS = 128
_MAX_HYPOTHESES = 64
_MAX_HISTORY = 64
_MAX_TEXT = 2048


@dataclass(frozen=True)
class CognitiveFact:
    statement: str
    confidence: float
    provenance: tuple[str, ...] = ()
    scope_id: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.statement, str) or not self.statement.strip() or len(self.statement) > _MAX_TEXT:
            raise ValueError("fact statement is required and bounded")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("fact confidence must be between 0 and 1")


@dataclass(frozen=True)
class CognitiveHypothesis:
    statement: str
    confidence: float
    basis: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.statement, str) or not self.statement.strip() or len(self.statement) > _MAX_TEXT:
            raise ValueError("hypothesis statement is required and bounded")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("hypothesis confidence must be between 0 and 1")


@dataclass(frozen=True)
class CognitiveSelfModel:
    """Explicit model of known capabilities and uncertainty, never authority."""

    capability_ids: tuple[str, ...] = ()
    resource_ids: tuple[str, ...] = ()
    known_limits: tuple[str, ...] = ()
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class CognitiveState:
    scope_id: str
    facts: tuple[CognitiveFact, ...] = ()
    hypotheses: tuple[CognitiveHypothesis, ...] = ()
    unresolved_questions: tuple[str, ...] = ()
    self_model: CognitiveSelfModel = field(default_factory=CognitiveSelfModel)

    @property
    def state_id(self) -> str:
        raw = "|".join((self.scope_id, *(f.statement for f in self.facts), *(h.statement for h in self.hypotheses)))
        return sha256(raw.encode()).hexdigest()


class CoreCognition:
    """Deterministic, bounded synthesis of evidence and operating knowledge."""

    def from_synthesis(
        self,
        scope_id: str,
        synthesis: SynthesisResult,
        *,
        known_capabilities: Sequence[str] = (),
        known_resources: Sequence[str] = (),
        known_limits: Sequence[str] = (),
    ) -> CognitiveState:
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("scope_id is required")
        if not isinstance(synthesis, SynthesisResult):
            raise TypeError("synthesis must be a SynthesisResult")
        requirements = synthesis.executive_requirements()
        facts = tuple(CognitiveFact(item, 1.0, synthesis.provenance, scope_id) for item in requirements[:_MAX_FACTS])
        hypotheses = tuple(
            CognitiveHypothesis(item.summary, item.confidence, tuple(item.evidence_urls))
            for item in getattr(synthesis, "signals", ())[:_MAX_HYPOTHESES]
            if hasattr(item, "summary") and isinstance(getattr(item, "confidence", None), (int, float))
        )
        questions = () if requirements else ("What evidence is sufficient to establish the objective?",)
        self_model = CognitiveSelfModel(tuple(dict.fromkeys(known_capabilities))[:_MAX_HISTORY], tuple(dict.fromkeys(known_resources))[:_MAX_HISTORY], tuple(dict.fromkeys(known_limits))[:_MAX_HISTORY])
        return CognitiveState(scope_id.strip(), facts, hypotheses, questions, self_model)

    def compare(self, left: CognitiveState, right: CognitiveState) -> tuple[str, ...]:
        if left.scope_id != right.scope_id:
            raise ValueError("cognitive states must share a scope")
        left_facts = {fact.statement for fact in left.facts}
        right_facts = {fact.statement for fact in right.facts}
        return tuple(sorted(right_facts - left_facts))
