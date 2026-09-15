"""Bridge durable mission steps into the existing bounded executive runtime."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from ..executive import ExecutiveEngine, Objective, TaskSpec
from .engine import MissionRunPolicy
from .progression import PersistentMissionRunner, StepOutcome
from .store import Mission, MissionStep, MissionStore


TaskFactory = Callable[[Mission, MissionStep, Objective], tuple[TaskSpec, ...]]


@dataclass(frozen=True)
class MissionExecutionPolicy:
    """Explicit bounds and approvals for one continuation invocation."""

    max_steps: int = 16
    max_duration_seconds: float | None = None
    retry_backoff_seconds: float = 0.0
    lease_ttl_seconds: float | None = None
    owner_approved: bool = False
    capability_approved: bool | set[str] = False

    def __post_init__(self) -> None:
        if self.max_steps <= 0:
            raise ValueError("max_steps must be positive")
        if self.max_duration_seconds is not None and self.max_duration_seconds <= 0:
            raise ValueError("max_duration_seconds must be positive when set")
        if self.retry_backoff_seconds < 0:
            raise ValueError("retry_backoff_seconds cannot be negative")
        if self.lease_ttl_seconds is not None and self.lease_ttl_seconds <= 0:
            raise ValueError("lease_ttl_seconds must be positive when set")
        if worker_set_requires_approval(self.capability_approved) and not self.owner_approved:
            pass


class MissionExecutiveBridge:
    """Execute persisted mission steps through the already-authorized executive path.

    The bridge owns orchestration only. Task construction remains an explicit
    caller contract, while execution continues through ExecutiveEngine and its
    existing runtime permission, capability, resource, verification and
    telemetry boundaries.
    """

    def __init__(self, store: MissionStore, executive: ExecutiveEngine, task_factory: TaskFactory) -> None:
        if not callable(task_factory):
            raise TypeError("task_factory must be callable")
        self.store = store
        self.executive = executive
        self.task_factory = task_factory
        self.progression = PersistentMissionRunner(store)

    def continue_due(
        self,
        *,
        now: float,
        scope_id: str | None = None,
        worker_id: str | None = None,
        policy: MissionExecutionPolicy | None = None,
    ) -> tuple[Mission, ...]:
        policy = policy or MissionExecutionPolicy()

        def execute(mission: Mission, step: MissionStep) -> StepOutcome:
            objective = self._objective(mission, step)
            tasks = self.task_factory(mission, step, objective)
            if not isinstance(tasks, tuple) or not tasks:
                raise ValueError("task_factory must return a non-empty tuple")
            result = self.executive.execute(
                objective,
                tasks,
                owner_approved=policy.owner_approved,
                capability_approved=policy.capability_approved,
            )
            return StepOutcome(result.success, result.success, result.reason, {"objective_id": result.objective_id})

        run_policy = MissionRunPolicy(
            max_steps=policy.max_steps,
            max_duration_seconds=policy.max_duration_seconds,
            retry_backoff_seconds=policy.retry_backoff_seconds,
            lease_ttl_seconds=policy.lease_ttl_seconds,
        )
        return self.progression.run(
            now=now,
            execute=execute,
            policy=run_policy,
            scope_id=scope_id,
            worker_id=worker_id,
        )

    @staticmethod
    def _objective(mission: Mission, step: MissionStep) -> Objective:
        payload: Mapping[str, object] = step.payload or {}
        intent = payload.get("intent", step.name)
        desired = payload.get("desired_outcome", f"Complete mission step: {step.name}")
        if not isinstance(intent, str) or not intent.strip() or not isinstance(desired, str) or not desired.strip():
            raise ValueError("mission step objective fields are invalid")
        return Objective(intent.strip(), desired.strip(), mission.scope_id, objective_id=f"{mission.mission_id}:{step.step_id}")


def worker_set_requires_approval(value: bool | set[str]) -> bool:
    """Keep policy validation explicit without interpreting capability authority."""
    return isinstance(value, set) and any(not isinstance(item, str) for item in value)
