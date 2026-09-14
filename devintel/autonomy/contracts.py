"""Contracts for DORMAMMU's bounded autonomous operating loop."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from datetime import datetime, timezone
from typing import Any

class AutonomyPhase(StrEnum):
    OBSERVE="observe"
    UNDERSTAND="understand"
    PLAN="plan"
    PERMISSION="permission"
    SECURITY_CHECK="security_check"
    ACT="act"
    VERIFY="verify"
    RECORD="record"
    IMPROVE="improve"

@dataclass(frozen=True)
class Observation:
    scope_id: str
    kind: str
    data: Any = None
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    def __post_init__(self):
        if not isinstance(self.scope_id, str) or not self.scope_id.strip() or not isinstance(self.kind, str) or not self.kind.strip(): raise ValueError("scope_id and kind are required")
        if self.observed_at.tzinfo is None: raise ValueError("observed_at must be timezone-aware")

@dataclass(frozen=True)
class AutonomousCycle:
    cycle_id: str
    scope_id: str
    completed_phases: tuple[AutonomyPhase, ...]
    actions_planned: int
    actions_succeeded: int
    actions_failed: int
    verified: bool
    stopped: bool = False
    stop_reason: str = ""
    improvement_actions_proposed: int = 0
    def __post_init__(self):
        if not self.cycle_id.strip() or not self.scope_id.strip(): raise ValueError("cycle_id and scope_id are required")
        if min(self.actions_planned, self.actions_succeeded, self.actions_failed, self.improvement_actions_proposed) < 0: raise ValueError("cycle counts cannot be negative")
        if self.actions_succeeded + self.actions_failed > self.actions_planned: raise ValueError("cycle result counts exceed planned actions")
