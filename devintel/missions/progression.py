"""Persistent, resumable mission progression over the durable mission journal."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from .engine import MissionRunPolicy
from .store import Mission, MissionStatus, MissionStep, MissionStepRecord, MissionStore


@dataclass(frozen=True)
class StepOutcome:
    """Executor result; successful progression requires explicit verification."""
    success: bool
    verified: bool
    message: str = ""
    data: Mapping[str, object] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.data is None:
            object.__setattr__(self, "data", {})
        if len(self.data) > 64:
            raise ValueError("outcome data has too many fields")


StepExecutor = Callable[[Mission, MissionStep], StepOutcome]


class PersistentMissionRunner:
    """Advance durable mission steps until a bounded budget is exhausted.

    The mission store is the source of truth. A step is advanced only after its
    executor explicitly reports both success and verification. Failed or
    unverified work never advances the durable checkpoint. Reopening the store
    therefore resumes from the first incomplete step without a manual continue
    prompt, while authority and external actions remain the executor's normal
    responsibility.
    """

    def __init__(self, store: MissionStore) -> None:
        self.store = store

    def define(self, mission_id: str, steps: tuple[MissionStep, ...]) -> tuple[MissionStepRecord, ...]:
        return self.store.define_steps(mission_id, steps)

    def run(
        self,
        *,
        now: float,
        execute: StepExecutor,
        policy: MissionRunPolicy | None = None,
        scope_id: str | None = None,
        worker_id: str | None = None,
    ) -> tuple[Mission, ...]:
        policy = policy or MissionRunPolicy()
        if not callable(execute):
            raise TypeError("execute must be callable")
        if now < 0:
            raise ValueError("now must be non-negative")
        results: list[Mission] = []
        steps_run = 0
        while steps_run < policy.max_steps:
            mission = self.store.claim_due(now=now, scope_id=scope_id, worker_id=worker_id, lease_ttl_seconds=policy.lease_ttl_seconds)
            if mission is None:
                break
            records = self.store.steps(mission.mission_id)
            if len(records) != mission.total_steps:
                self.store.fail(mission.mission_id, "mission steps are undefined or incomplete", now=now, backoff_seconds=policy.retry_backoff_seconds, worker_id=worker_id)
                results.append(self.store.get(mission.mission_id))  # type: ignore[arg-type]
                steps_run += 1
                continue
            current = records[mission.current_step]
            try:
                outcome = execute(mission, current.step)
                if not isinstance(outcome, StepOutcome):
                    raise TypeError("executor returned invalid StepOutcome")
                if not outcome.success or not outcome.verified:
                    reason = outcome.message or ("step succeeded but was not verified" if outcome.success else "step execution failed")
                    results.append(self.store.fail(mission.mission_id, reason, now=now, backoff_seconds=policy.retry_backoff_seconds, worker_id=worker_id))
                else:
                    self.store.record_step(mission.mission_id, mission.current_step, verified=True, message=outcome.message, data=outcome.data)
                    results.append(self.store.checkpoint(mission.mission_id, current_step=mission.current_step + 1, now=now, worker_id=worker_id))
            except Exception as exc:
                results.append(self.store.fail(mission.mission_id, type(exc).__name__, now=now, backoff_seconds=policy.retry_backoff_seconds, worker_id=worker_id))
            steps_run += 1
        return tuple(results)

    @staticmethod
    def is_terminal(mission: Mission) -> bool:
        return mission.status in (MissionStatus.SUCCEEDED, MissionStatus.FAILED, MissionStatus.CANCELLED)
