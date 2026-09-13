"""First bounded end-to-end operating path.

This module composes existing DORMAMMU boundaries without granting new authority.
It plans a goal, checks capabilities, requires explicit capability approval when a
new candidate is needed, gates activation through canary health, executes through
the core permission path, verifies the result, and records the outcome.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable
from uuid import uuid4

from ..capabilities import CapabilityDecision, CapabilityRequirement, CapabilityStatus, CanaryHealth
from ..core.contracts import ActionRequest, ActionResult, Event

if TYPE_CHECKING:
    from ..runtime.app import DORMAMMURuntime

Verifier = Callable[[Any], bool]


@dataclass(frozen=True)
class BoundedOperation:
    goal: str
    requirement: CapabilityRequirement
    action: ActionRequest
    value: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.goal, str) or not self.goal.strip():
            raise ValueError("goal is required")
        if not isinstance(self.requirement, CapabilityRequirement):
            raise TypeError("requirement must be a CapabilityRequirement")
        if not isinstance(self.action, ActionRequest):
            raise TypeError("action must be an ActionRequest")


@dataclass(frozen=True)
class OperationResult:
    success: bool
    operation_id: str
    stage: str
    message: str
    capability_decision: CapabilityDecision
    action_result: ActionResult | None = None
    verified: bool = False


class BoundedOperationEngine:
    """Compose the first complete bounded operating path without bypassing authority."""

    def __init__(self, runtime: "DORMAMMURuntime") -> None:
        self.runtime = runtime

    def run(
        self,
        operation: BoundedOperation,
        *,
        owner_approved: bool = False,
        capability_approved: bool = False,
        canary_health: CanaryHealth | None = None,
        verifier: Verifier | None = None,
    ) -> OperationResult:
        operation_id = str(uuid4())
        self.runtime.context.events.publish(Event("operation.requested", {"operation_id": operation_id, "goal": operation.goal}))
        decision = self.runtime.decide_capability(operation.requirement)

        if decision.action == "record_gap":
            return self._finish(operation_id, "capability", False, "no eligible capability is available", decision)
        capability_id = decision.capability_id
        if not capability_id:
            return self._finish(operation_id, "capability", False, "capability decision did not identify a capability", decision)
        capability = self.runtime.capability_registry.get(capability_id)
        if capability is None:
            return self._finish(operation_id, "capability", False, "selected capability is not registered", decision)

        if decision.action == "request_approval":
            if not capability_approved:
                return self._finish(operation_id, "approval", False, "explicit capability approval is required", decision)
            if decision.discovery is None:
                return self._finish(operation_id, "approval", False, "approval requires discovery evidence", decision)
            evaluation = next(
                (item for item in decision.discovery.evaluations if item.candidate.capability_id == capability_id and item.eligible),
                None,
            )
            if evaluation is None:
                return self._finish(operation_id, "approval", False, "selected capability no longer has an eligible evaluation", decision)
            try:
                self.runtime.capability_lifecycle.approve(evaluation, permission_granted=True)
                self.runtime.capability_lifecycle.register(capability_id)
                self.runtime.capability_lifecycle.canary(capability_id)
            except (KeyError, PermissionError, ValueError) as exc:
                return self._finish(operation_id, "lifecycle", False, str(exc), decision)
            if canary_health is None:
                return self._finish(operation_id, "canary", False, "canary health is required before activation", decision)
            canary = self.runtime.evaluate_canary(capability_id, canary_health)
            if not canary.activated:
                return self._finish(operation_id, "canary", False, canary.reason, decision)
        elif capability.status is not CapabilityStatus.ACTIVE:
            return self._finish(operation_id, "capability", False, "selected existing capability is not active", decision)

        action_result = self.runtime.execute(operation.action, owner_approved=owner_approved, value=operation.value)
        if not action_result.success:
            return self._finish(operation_id, "act", False, action_result.message, decision, action_result)
        verified = True if verifier is None else bool(verifier(action_result.data.get("output")))
        if not verified:
            self.runtime.context.events.publish(Event("operation.verification_failed", {"operation_id": operation_id, "capability_id": capability_id}))
            return self._finish(operation_id, "verify", False, "operation result failed verification", decision, action_result, False)
        self.runtime.context.events.publish(Event("operation.completed", {"operation_id": operation_id, "capability_id": capability_id}))
        return self._finish(operation_id, "record", True, "bounded operation completed and verified", decision, action_result, True)

    def _finish(self, operation_id: str, stage: str, success: bool, message: str, decision: CapabilityDecision, action_result: ActionResult | None = None, verified: bool = False) -> OperationResult:
        self.runtime.context.events.publish(Event("operation.recorded", {"operation_id": operation_id, "stage": stage, "success": success, "message": message, "capability_id": decision.capability_id or ""}))
        return OperationResult(success, operation_id, stage, message, decision, action_result, verified)
