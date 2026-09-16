"""Resource-aware autonomous execution with bounded, fail-closed leases."""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable, Sequence
from typing import Any

from ..capabilities.resources import ResourceDecision, ResourceManager, ResourceRequest
from ..core.contracts import ActionRequest, ActionResult
from ..core.orchestrator import Orchestrator
from .contracts import AutonomousCycle, AutonomyPhase, Observation
from .engine import Observer, Planner, Verifier, Improver, Recorder


@dataclass(frozen=True)
class ResourceExecution:
    action: ActionRequest
    result: ActionResult
    resource_id: str | None
    reservation_id: str | None


class ResourceAwareAutonomousEngine:
    """Runs the autonomous loop while reserving declared resources only at ACT.

    Planning is observational and side-effect free. A resource reservation is
    created immediately before an authorized action and released on every path.
    Resource requirements are carried in the private ``_resource_request``
    payload field and are never passed to action handlers.
    """

    def __init__(
        self,
        orchestrator: Orchestrator,
        resource_manager: ResourceManager,
        observer: Observer,
        planner: Planner,
        verifier: Verifier,
        recorder: Recorder,
        improver: Improver | None = None,
        *,
        max_actions: int = 32,
    ) -> None:
        if max_actions <= 0:
            raise ValueError("max_actions must be positive")
        self.orchestrator = orchestrator
        self.resource_manager = resource_manager
        self.observer = observer
        self.planner = planner
        self.verifier = verifier
        self.recorder = recorder
        self.improver = improver
        self.max_actions = max_actions

    def _finish(self, scope: str, phases: list[AutonomyPhase], planned: int, succeeded: int, failed: int, verified: bool, reason: str = "", proposed: int = 0) -> AutonomousCycle:
        from uuid import uuid4
        cycle = AutonomousCycle(uuid4().hex, scope, tuple(phases), planned, succeeded, failed, verified, bool(reason), reason, proposed)
        try:
            self.recorder(cycle)
        except Exception:
            pass
        return cycle

    @staticmethod
    def _request(action: ActionRequest, scope: str) -> tuple[ActionRequest, ResourceRequest | None]:
        payload = dict(action.payload)
        if payload.get("_scope_id") != scope:
            raise ValueError("invalid or cross-scope plan")
        resource = payload.pop("_resource_request", None)
        if resource is not None and not isinstance(resource, ResourceRequest):
            raise TypeError("_resource_request must be ResourceRequest")
        payload.pop("_scope_id", None)
        return ActionRequest(action.action, action.risk, action.reason, payload), resource

    def run_once(self, scope_id: str, *, owner_approved: bool = False) -> AutonomousCycle:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        if not scope:
            raise ValueError("scope_id is required")
        phases = [AutonomyPhase.OBSERVE]
        try:
            observations = tuple(self.observer(scope))
        except Exception as exc:
            return self._finish(scope, phases, 0, 0, 0, False, f"observation failed: {type(exc).__name__}")
        if not all(isinstance(item, Observation) and item.scope_id == scope for item in observations):
            return self._finish(scope, phases, 0, 0, 0, False, "invalid or cross-scope observation")

        phases.extend((AutonomyPhase.UNDERSTAND, AutonomyPhase.PLAN))
        try:
            actions = tuple(self.planner(scope, observations))
        except Exception as exc:
            return self._finish(scope, phases, 0, 0, 0, False, f"planning failed: {type(exc).__name__}")
        if len(actions) > self.max_actions:
            return self._finish(scope, phases, len(actions), 0, 0, False, "plan exceeds bounded action limit")
        try:
            normalized = tuple(self._request(action, scope) for action in actions)
        except Exception as exc:
            return self._finish(scope, phases, len(actions), 0, 0, False, str(exc))

        phases.extend((AutonomyPhase.PERMISSION, AutonomyPhase.SECURITY_CHECK))
        for action, _ in normalized:
            try:
                self.orchestrator.authorize(action, owner_approved=owner_approved)
            except Exception as exc:
                return self._finish(scope, phases, len(actions), 0, len(actions), False, f"permission denied before act: {type(exc).__name__}")

        phases.append(AutonomyPhase.ACT)
        results: list[ActionResult] = []
        executions: list[ResourceExecution] = []
        for action, request in normalized:
            resource_id = reservation_id = None
            try:
                if request is not None:
                    decision = self.resource_manager.reserve(request)
                    if not decision.granted or not decision.resource_id or not decision.reservation_id:
                        results.append(self.orchestrator.result(action, success=False, message=decision.reason))
                        break
                    resource_id, reservation_id = decision.resource_id, decision.reservation_id
                    lease = self.resource_manager.reservation(reservation_id)
                    if lease is None or lease[0] != resource_id:
                        results.append(self.orchestrator.result(action, success=False, message="resource lease identity mismatch"))
                        break
                result = self.orchestrator.execute(action, owner_approved=owner_approved)
                results.append(result)
                executions.append(ResourceExecution(action, result, resource_id, reservation_id))
                if not result.success:
                    break
            except Exception as exc:
                results.append(self.orchestrator.result(action, success=False, message=f"resource-aware action failed safely: {type(exc).__name__}"))
                break
            finally:
                if reservation_id:
                    self.resource_manager.release(reservation_id)

        succeeded = sum(1 for result in results if result.success)
        failed = len(results) - succeeded
        phases.append(AutonomyPhase.VERIFY)
        try:
            verified = bool(self.verifier(scope, tuple(results)))
            reason = "" if verified else ("action execution failed" if failed else "verification rejected result")
        except Exception as exc:
            verified = False
            reason = f"verification failed: {type(exc).__name__}"

        phases.append(AutonomyPhase.RECORD)
        preliminary = AutonomousCycle(__import__("uuid").uuid4().hex, scope, tuple(phases), len(actions), succeeded, failed, verified, bool(reason), reason, 0)
        phases.append(AutonomyPhase.IMPROVE)
        proposed = 0
        if self.improver is not None:
            try:
                proposals = tuple(self.improver(preliminary))
                if not all(isinstance(item, str) and item.strip() for item in proposals):
                    return self._finish(scope, phases, len(actions), succeeded, failed, verified, "improvement produced invalid proposal")
                proposed = len(proposals)
            except Exception as exc:
                reason = reason or f"improvement failed: {type(exc).__name__}"
        return self._finish(scope, phases, len(actions), succeeded, failed, verified, reason, proposed)
