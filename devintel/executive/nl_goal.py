"""Safety boundary for natural-language goal understanding.

Natural language is untrusted input. This module turns it into a structured
objective only when an interpreter supplies sufficiently complete, scoped,
low-ambiguity fields. It never grants authority or creates executable actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import Objective


@dataclass(frozen=True)
class GoalInterpretation:
    objective: Objective | None
    confidence: float
    ambiguities: tuple[str, ...] = ()
    requires_confirmation: bool = False
    rationale: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.objective is None and not self.requires_confirmation:
            raise ValueError("unresolved interpretation must require confirmation")


class NaturalLanguageGoalInterpreter(Protocol):
    def interpret(self, text: str, *, scope_id: str) -> GoalInterpretation: ...


class BoundedNaturalLanguageGoalBoundary:
    """Validate untrusted NL interpretation before executive planning."""

    def __init__(self, interpreter: NaturalLanguageGoalInterpreter, *, min_confidence: float = 0.85) -> None:
        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError("min_confidence must be between 0 and 1")
        self.interpreter = interpreter
        self.min_confidence = min_confidence

    def understand(self, text: str, *, scope_id: str) -> GoalInterpretation:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("natural-language goal is required")
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("scope_id is required")
        result = self.interpreter.interpret(text.strip(), scope_id=scope_id.strip())
        if not isinstance(result, GoalInterpretation):
            raise TypeError("interpreter must return GoalInterpretation")
        if result.objective is None:
            return result
        if result.objective.scope_id != scope_id.strip():
            raise ValueError("interpreted objective scope does not match requested scope")
        if result.confidence < self.min_confidence or result.ambiguities or result.requires_confirmation:
            return GoalInterpretation(result.objective, result.confidence, result.ambiguities or ("interpretation threshold not satisfied",), True, result.rationale)
        return result


class DeterministicNaturalLanguageInterpreter:
    """Conservative parser for simple goals; ambiguous language fails closed."""

    _HIGH_IMPACT = ("pay", "purchase", "transfer", "withdraw", "deploy", "delete", "publish", "send")

    def interpret(self, text: str, *, scope_id: str) -> GoalInterpretation:
        normalized = " ".join(text.split())
        lowered = normalized.lower()
        if any(word in lowered.split() for word in self._HIGH_IMPACT):
            return GoalInterpretation(None, 0.0, ("high-impact action requires explicit structured intent and authorization",), True, "high-impact natural-language goal rejected")
        if len(normalized) < 8:
            return GoalInterpretation(None, 0.0, ("goal is too short to establish intent and outcome",), True, "insufficient goal detail")
        objective = Objective(intent=normalized, desired_outcome=normalized, scope_id=scope_id)
        return GoalInterpretation(objective, 0.9, rationale="simple bounded normalization")
