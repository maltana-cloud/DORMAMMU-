"""Validation contracts for provider-backed semantic goal interpretation."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True)
class SemanticGoalPolicy:
    max_text_length: int = 4096
    min_confidence: float = 0.75
    max_ambiguities: int = 0
    blocked_terms: tuple[str, ...] = ("pay", "purchase", "transfer", "withdraw", "deploy", "delete", "publish", "send")

    def __post_init__(self) -> None:
        if self.max_text_length <= 0: raise ValueError("max_text_length must be positive")
        if not 0 <= self.min_confidence <= 1: raise ValueError("min_confidence must be between 0 and 1")
        if self.max_ambiguities < 0: raise ValueError("max_ambiguities must be non-negative")

class SemanticGoalValidator:
    """Treat semantic-model output as untrusted data and enforce hard gates."""
    def __init__(self, policy: SemanticGoalPolicy | None = None) -> None:
        self.policy = policy or SemanticGoalPolicy()

    def validate_text(self, text: str) -> str:
        if not isinstance(text, str): raise TypeError("goal text must be a string")
        normalized = " ".join(text.split())
        if not normalized: raise ValueError("goal text is required")
        if len(normalized) > self.policy.max_text_length: raise ValueError("goal text exceeds bounded length")
        lowered = normalized.lower()
        if any(term in lowered for term in self.policy.blocked_terms):
            raise PermissionError("high-impact goal requires explicit confirmation")
        return normalized

    def validate_result(self, *, confidence: float, ambiguities: tuple[str, ...], scope_id: str, objective_scope_id: str) -> None:
        if not 0 <= confidence <= 1: raise ValueError("confidence must be between 0 and 1")
        if confidence < self.policy.min_confidence or len(ambiguities) > self.policy.max_ambiguities:
            raise PermissionError("semantic interpretation requires confirmation")
        if not scope_id or objective_scope_id != scope_id:
            raise PermissionError("semantic interpretation changed scope")
