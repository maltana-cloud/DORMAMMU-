"""Bounded OBSERVE→UNDERSTAND→PLAN→PERMISSION→SECURITY→ACT→VERIFY→RECORD→IMPROVE loop."""
from __future__ import annotations
from collections.abc import Callable, Sequence
from uuid import uuid4
from ..core.orchestrator import Orchestrator
from ..core.contracts import ActionRequest, ActionResult
from ..core.permissions import PermissionDenied
from .contracts import AutonomousCycle, AutonomyPhase, Observation

Observer = Callable[[str], Sequence[Observation]]
Planner = Callable[[str, Sequence[Observation]], Sequence[ActionRequest]]
Verifier = Callable[[str, Sequence[ActionResult]], bool]
Improver = Callable[[AutonomousCycle], Sequence[str]]
Recorder = Callable[[AutonomousCycle], None]

class AutonomousEngine:
    """Runs finite, fail-closed cycles; improvement produces proposals, never self-modifies code or authority."""
    def __init__(self, orchestrator: Orchestrator, observer: Observer, planner: Planner, verifier: Verifier, recorder: Recorder | None = None, improver: Improver | None = None, *, max_actions: int = 32) -> None:
        if max_actions <= 0: raise ValueError("max_actions must be positive")
        self.orchestrator = orchestrator; self.observer = observer; self.planner = planner; self.verifier = verifier; self.recorder = recorder; self.improver = improver; self.max_actions = max_actions

    def _finish(self, scope: str, phases: list[AutonomyPhase], planned: int, succeeded: int, failed: int, verified: bool, reason: str = "", improvement_actions_proposed: int = 0) -> AutonomousCycle:
        cycle = AutonomousCycle(uuid4().hex, scope, tuple(phases), planned, succeeded, failed, verified, bool(reason), reason, improvement_actions_proposed)
        if self.recorder:
            try: self.recorder(cycle)
            except Exception: pass
        return cycle

    def run_once(self, scope_id: str, *, owner_approved: bool = False) -> AutonomousCycle:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        if not scope: raise ValueError("scope_id is required")
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
        if not all(isinstance(item, ActionRequest) and item.payload.get("_scope_id") == scope for item in actions):
            return self._finish(scope, phases, len(actions), 0, 0, False, "invalid or cross-scope plan")

        phases.extend((AutonomyPhase.PERMISSION, AutonomyPhase.SECURITY_CHECK))
        scoped_actions: list[ActionRequest] = []
        for action in actions:
            payload = dict(action.payload); payload.pop("_scope_id", None)
            scoped = ActionRequest(action.action, action.risk, action.reason, payload)
            try:
                self.orchestrator.authorize(scoped, owner_approved=owner_approved)
            except PermissionDenied as exc:
                return self._finish(scope, phases, len(actions), 0, len(actions), False, f"permission denied before act: {exc}")
            scoped_actions.append(scoped)

        phases.append(AutonomyPhase.ACT)
        results: list[ActionResult] = []
        for action in scoped_actions:
            result = self.orchestrator.execute(action, owner_approved=owner_approved)
            results.append(result)
            if not result.success:
                break
        succeeded = sum(1 for result in results if result.success)
        failed = len(results) - succeeded
        phases.append(AutonomyPhase.VERIFY)
        try:
            verified = bool(self.verifier(scope, tuple(results)))
            reason = "" if verified else ("action execution failed" if failed else "verification rejected result")
        except Exception as exc:
            verified = False; reason = f"verification failed: {type(exc).__name__}"

        phases.append(AutonomyPhase.RECORD)
        preliminary = AutonomousCycle(uuid4().hex, scope, tuple(phases), len(actions), succeeded, failed, verified, bool(reason), reason, 0)
        phases.append(AutonomyPhase.IMPROVE)
        proposed = 0
        if self.improver is not None:
            try:
                proposals = tuple(self.improver(preliminary))
                if not all(isinstance(item, str) and item.strip() for item in proposals):
                    return self._finish(scope, phases, len(actions), succeeded, failed, verified, "improvement produced invalid proposal", 0)
                proposed = len(proposals)
            except Exception as exc:
                reason = reason or f"improvement failed: {type(exc).__name__}"
        return self._finish(scope, phases, len(actions), succeeded, failed, verified, reason, proposed)
