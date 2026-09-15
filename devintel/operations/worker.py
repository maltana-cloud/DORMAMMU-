"""Bounded worker execution over an already-admitted resource lease.

Workers are deliberately provider-neutral. This layer does not install software,
create credentials, bypass owner policy, or grant external authority. A worker
receives a frozen execution request and an already-created resource reservation.
"""
from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Mapping

from ..capabilities.scheduler import CapabilityResourcePlan, CapabilityResourceScheduler


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


class BoundedResourceWorker:
    """Execute one bounded worker call under a scheduler admission lease."""

    def __init__(self, scheduler: CapabilityResourceScheduler) -> None:
        self.scheduler = scheduler

    def execute(self, plan: CapabilityResourcePlan, request: WorkerRequest, worker: Worker) -> WorkerOutcome:
        if not plan.granted or not plan.reservation_id:
            raise PermissionError("worker execution requires an admitted resource reservation")
        if request.capability_id != plan.selected_capability_id:
            raise PermissionError("worker capability does not match admitted plan")
        if request.operation_id.strip() == "":
            raise ValueError("operation_id is required")
        started = perf_counter()
        try:
            outcome = worker(request)
            if not isinstance(outcome, WorkerOutcome):
                raise TypeError("worker returned invalid WorkerOutcome")
            if outcome.operation_id != request.operation_id or outcome.capability_id != request.capability_id:
                raise ValueError("worker returned mismatched execution identity")
            measured = (perf_counter() - started) * 1000.0
            return WorkerOutcome(outcome.operation_id, outcome.capability_id, outcome.success,
                                 outcome.verified, outcome.message, outcome.data, measured)
        finally:
            self.scheduler.release(plan)
