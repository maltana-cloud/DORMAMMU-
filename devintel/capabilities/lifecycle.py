"""Controlled capability lifecycle with explicit gates and rollback support."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from .contracts import CapabilityDescriptor, CapabilityStatus, Evaluation
from .registry import CapabilityRegistry

_ALLOWED: dict[CapabilityStatus, frozenset[CapabilityStatus]] = {
    CapabilityStatus.DISCOVERED: frozenset({CapabilityStatus.EVALUATED, CapabilityStatus.RETIRED}),
    CapabilityStatus.EVALUATED: frozenset({CapabilityStatus.APPROVED, CapabilityStatus.RETIRED}),
    CapabilityStatus.APPROVED: frozenset({CapabilityStatus.REGISTERED, CapabilityStatus.RETIRED}),
    CapabilityStatus.REGISTERED: frozenset({CapabilityStatus.CANARY, CapabilityStatus.RETIRED}),
    CapabilityStatus.CANARY: frozenset({CapabilityStatus.ACTIVE, CapabilityStatus.DEGRADED, CapabilityStatus.ROLLED_BACK}),
    CapabilityStatus.ACTIVE: frozenset({CapabilityStatus.DEGRADED, CapabilityStatus.RETIRED}),
    CapabilityStatus.DEGRADED: frozenset({CapabilityStatus.CANARY, CapabilityStatus.ROLLED_BACK, CapabilityStatus.RETIRED}),
    CapabilityStatus.ROLLED_BACK: frozenset({CapabilityStatus.CANARY, CapabilityStatus.RETIRED}),
    CapabilityStatus.PLANNED: frozenset({CapabilityStatus.DISCOVERED, CapabilityStatus.RETIRED}),
    CapabilityStatus.RETIRED: frozenset(),
}

@dataclass(frozen=True)
class LifecycleEvent:
    capability_id: str
    from_status: CapabilityStatus
    to_status: CapabilityStatus
    timestamp: str
    reason: str

class CapabilityLifecycle:
    """State machine only. It never installs, executes, or grants permissions."""
    def __init__(self, registry: CapabilityRegistry, recorder=None) -> None:
        self.registry = registry
        self.recorder = recorder

    def transition(self, capability_id: str, target: CapabilityStatus, reason: str) -> CapabilityDescriptor:
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason is required")
        current = self.registry.get(capability_id)
        if current is None:
            raise KeyError(capability_id)
        if target not in _ALLOWED.get(current.status, frozenset()):
            raise ValueError(f"invalid lifecycle transition: {current.status.value} -> {target.value}")
        from dataclasses import replace
        updated = replace(current, status=target)
        self.registry.register(updated)
        if self.recorder:
            self.recorder(LifecycleEvent(capability_id, current.status, target, datetime.now(timezone.utc).isoformat(), reason))
        return updated

    def approve(self, evaluation: Evaluation, permission_granted: bool = False) -> CapabilityDescriptor:
        if not evaluation.eligible:
            raise PermissionError("capability failed evaluation gates")
        if not permission_granted:
            raise PermissionError("explicit approval is required")
        current = self.registry.get(evaluation.candidate.capability_id)
        if current is None:
            from dataclasses import replace
            current = replace(evaluation.candidate, status=CapabilityStatus.DISCOVERED)
            self.registry.register(current)
        if current.status is CapabilityStatus.DISCOVERED:
            current = self.transition(current.capability_id, CapabilityStatus.EVALUATED, "evaluation passed")
        return self.transition(current.capability_id, CapabilityStatus.APPROVED, "owner permission granted")

    def register(self, capability_id: str) -> CapabilityDescriptor:
        return self.transition(capability_id, CapabilityStatus.REGISTERED, "approved capability registered")

    def canary(self, capability_id: str) -> CapabilityDescriptor:
        return self.transition(capability_id, CapabilityStatus.CANARY, "entered controlled canary")

    def activate(self, capability_id: str) -> CapabilityDescriptor:
        return self.transition(capability_id, CapabilityStatus.ACTIVE, "canary verified")

    def degrade(self, capability_id: str, reason: str) -> CapabilityDescriptor:
        return self.transition(capability_id, CapabilityStatus.DEGRADED, reason)

    def rollback(self, capability_id: str, reason: str) -> CapabilityDescriptor:
        return self.transition(capability_id, CapabilityStatus.ROLLED_BACK, reason)
