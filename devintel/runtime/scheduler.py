"""Externally driven scheduling primitives.

A scheduler computes due work but never starts an unbounded background loop.
An OS scheduler, container platform, queue consumer, or another trusted host
can call ``tick`` at the desired cadence.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from .worker import RuntimeJob, RuntimeJobStore, RuntimeWorker


@dataclass(frozen=True)
class ScheduledJob:
    schedule_id: str
    scope_id: str
    action: str
    payload: dict
    interval_seconds: float
    next_run_at: float
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.schedule_id.strip() or not self.scope_id.strip() or not self.action.strip():
            raise ValueError("schedule_id, scope_id, and action are required")
        if self.interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")


class RuntimeScheduler:
    """Schedule bounded work and enqueue due jobs for an external worker."""

    def __init__(self, store: RuntimeJobStore) -> None:
        self.store = store
        self._schedules: dict[str, ScheduledJob] = {}

    @staticmethod
    def now() -> float:
        return datetime.now(timezone.utc).timestamp()

    def register(self, schedule: ScheduledJob) -> None:
        if schedule.schedule_id in self._schedules:
            raise ValueError("schedule already exists")
        self._schedules[schedule.schedule_id] = schedule

    def disable(self, schedule_id: str) -> None:
        schedule = self._schedules.get(schedule_id)
        if schedule is None:
            raise KeyError(schedule_id)
        self._schedules[schedule_id] = ScheduledJob(
            schedule.schedule_id, schedule.scope_id, schedule.action, schedule.payload,
            schedule.interval_seconds, schedule.next_run_at, False
        )

    def tick(self, *, now: float | None = None, max_jobs: int = 1) -> tuple[RuntimeJob, ...]:
        if max_jobs <= 0:
            raise ValueError("max_jobs must be positive")
        current = self.now() if now is None else now
        if current < 0:
            raise ValueError("now must be non-negative")
        queued: list[RuntimeJob] = []
        for schedule_id in sorted(self._schedules):
            schedule = self._schedules[schedule_id]
            if not schedule.enabled or schedule.next_run_at > current or len(queued) >= max_jobs:
                continue
            queued.append(self.store.enqueue(schedule.scope_id, schedule.action, schedule.payload))
            # Advance from the scheduled instant, not wall-clock now, so delayed ticks
            # do not drift the schedule indefinitely.
            next_run = schedule.next_run_at + schedule.interval_seconds
            while next_run <= current:
                next_run += schedule.interval_seconds
            self._schedules[schedule_id] = ScheduledJob(
                schedule.schedule_id, schedule.scope_id, schedule.action, schedule.payload,
                schedule.interval_seconds, next_run, schedule.enabled
            )
        return tuple(queued)

    def schedules(self) -> tuple[ScheduledJob, ...]:
        return tuple(self._schedules[key] for key in sorted(self._schedules))


def build_worker(store: RuntimeJobStore, dispatch: Callable[[RuntimeJob], object]) -> RuntimeWorker:
    return RuntimeWorker(store, dispatch)
