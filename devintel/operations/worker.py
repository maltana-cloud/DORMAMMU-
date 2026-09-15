"""Bounded worker execution over an already-admitted resource lease.

Workers remain provider-neutral. Runtime integration adds existing owner authority,
operational telemetry, and explicit result verification without granting new authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Mapping, TYPE_CHECKING

from ..capabilities.scheduler import CapabilityResourcePlan, CapabilityResourceScheduler
from ..control.authority import AuthorityMode
from ..core.contracts import Event

if TYPE_CHECKING:
    from ..runtime.app import DORMAMMURuntime

@dataclass(frozen=True)
class WorkerRequest:
    operation_id: str
    capability_id: str
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        if not self.operation_id.strip() or not self.capability_id.strip():
            raise ValueError("operation_id and capability_id are required")
        if len(self.payload) > 64:
            raise ValueError("payload has too many fields")

@dataclass(frozen=True)
class WorkerOutcome:
    operation_id: str
    capability_id: str
    success: bool
    verified: bool
    message: str
    data: Mapping[str, object]
    duration_ms: float

Worker = Callable[[WorkerRequest], WorkerOutcome]
Verifier = Callable[[WorkerOutcome], bool]

class BoundedResourceWorker:
    """Execute one bounded worker call under admission and runtime controls."""

    def __init__(self, scheduler: CapabilityResourceScheduler, runtime: DORMAMMURuntime | None = None) -> None:
        self.scheduler = scheduler
        self.runtime = runtime

    def execute(self, plan: CapabilityResourcePlan, request: WorkerRequest, worker: Worker, *, scope_id: str = "runtime", owner_approved: bool = False, verifier: Verifier | None = None) -> WorkerOutcome:
        if not plan.granted or not plan.reservation_id:
            raise PermissionError("worker execution requires an admitted resource reservation")
        if request.capability_id != plan.selected_capability_id:
            raise PermissionError("worker capability does not match admitted plan")
        if not scope_id.strip():
            raise ValueError("scope_id is required")
        if self.runtime is not None:
            authority = self.runtime.authority(scope_id, request.capability_id)
            if authority is AuthorityMode.DENIED:
                raise PermissionError("worker capability is denied by runtime authority")
            if authority is AuthorityMode.APPROVAL_REQUIRED and not owner_approved:
                raise PermissionError("worker capability requires explicit owner approval")
            self.runtime.context.events.publish(Event("worker.requested", {"operation_id": request.operation_id, "capability_id": request.capability_id, "scope_id": scope_id}))
        started = perf_counter()
        try:
            outcome = worker(request)
            if not isinstance(outcome, WorkerOutcome):
                raise TypeError("worker returned invalid WorkerOutcome")
            if outcome.operation_id != request.operation_id or outcome.capability_id != request.capability_id:
                raise ValueError("worker returned mismatched execution identity")
            verified = bool(outcome.success and outcome.verified)
            if verifier is not None:
                verified = bool(verifier(outcome))
            measured = (perf_counter() - started) * 1000.0
            final = WorkerOutcome(outcome.operation_id, outcome.capability_id, outcome.success, verified, outcome.message, outcome.data, measured)
            if self.runtime is not None:
                self.runtime.record_operation_observation_from_result(request.operation_id, request.capability_id, "worker", final.success, final.verified, final.duration_ms, final.message if final.verified else "worker result failed verification", plan.selected_resource_id, None)
                self.runtime.context.events.publish(Event("worker.completed", {"operation_id": request.operation_id, "capability_id": request.capability_id, "success": final.success, "verified": final.verified}))
            return final
        except Exception as exc:
            if self.runtime is not None:
                measured = (perf_counter() - started) * 1000.0
                self.runtime.record_operation_observation_from_result(request.operation_id, request.capability_id, "worker_exception", False, False, measured, f"worker failed safely: {type(exc).__name__}", plan.selected_resource_id, None)
                self.runtime.context.events.publish(Event("worker.failed", {"operation_id": request.operation_id, "capability_id": request.capability_id, "error": type(exc).__name__}))
            raise
        finally:
            self.scheduler.release(plan)
