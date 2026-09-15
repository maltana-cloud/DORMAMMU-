"""Stable contracts for authorized real-world actions.

Actions are capabilities, not authority. Permission, security, owner control,
and verification remain independent boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping, Protocol

from devintel.core.contracts import ActionRisk


class ActionStatus(StrEnum):
    DRY_RUN = "dry_run"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ActionSpec:
    action_id: str
    capability: str
    risk: ActionRisk
    idempotency_key: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    scope_id: str = "default"
    dry_run: bool = False

    def __post_init__(self) -> None:
        for name in ("action_id", "capability", "idempotency_key", "scope_id"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"{name} is required")
        if not isinstance(self.risk, ActionRisk):
            raise TypeError("risk must be ActionRisk")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")
        if len(self.payload) > 64:
            raise ValueError("payload has too many fields")


@dataclass(frozen=True)
class ActionOutcome:
    action_id: str
    capability: str
    status: ActionStatus
    provider_id: str = ""
    message: str = ""
    data: Mapping[str, Any] = field(default_factory=dict)
    verified: bool = False
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.action_id.strip() or not self.capability.strip():
            raise ValueError("action_id and capability are required")
        if not isinstance(self.status, ActionStatus):
            raise TypeError("status must be ActionStatus")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        if self.status is ActionStatus.SUCCEEDED and not self.provider_id.strip():
            raise ValueError("successful actions require provider_id")
        if self.status is ActionStatus.SUCCEEDED and self.message == "":
            raise ValueError("successful actions require a message")
        if self.status is not ActionStatus.SUCCEEDED and self.verified:
            raise ValueError("only successful outcomes may be verified")


class ActionProvider(Protocol):
    provider_id: str
    capability: str

    def execute(self, spec: ActionSpec) -> ActionOutcome: ...

    def health(self) -> bool: ...
