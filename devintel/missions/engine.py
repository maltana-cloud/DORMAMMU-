"""Externally driven, bounded mission execution."""
from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Callable

from .store import Mission, MissionStatus, MissionStore


@dataclass(frozen=True)
class MissionRunPolicy:
    max_steps: int = 1
    max_duration_seconds: float | None = None
    retry_backoff_seconds: float = 0.0
    lease_ttl_seconds: float | None = None

    def __post_init__(self) -> None:
        if self.max_steps <= 0:
            raise ValueError("max_steps must be positive")
        if self.max_duration_seconds is not None and self.max_duration_seconds <= 0:
            raise ValueError("max_duration_seconds must be positive when set")
        if self.retry_backoff_seconds < 0:
            raise ValueError("retry_backoff_seconds cannot be negative")
        if self.lease_ttl_seconds is not None and self.lease_ttl_seconds <= 0:
            raise ValueError("lease_ttl_seconds must be positive when set")


class MissionRunner:
    """Advance durable missions a finite amount per external invocation.

    A worker identity plus lease TTL enables safe multi-worker claiming through
    the store's atomic lease boundary. Leasing is coordination only; callers
    still pass selected capabilities through normal permission/execution paths.
    """

    def __init__(self, store: MissionStore, *, clock: Callable[[], float] = monotonic) -> None:
        self.store = store
        self.clock = clock

    def run_once(
        self,
        *,
        now: float,
        step: Callable[[Mission], object],
        policy: MissionRunPolicy | None = None,
        scope_id: str | None = None,
        worker_id: str | None = None,
    ) -> tuple[Mission, ...]:
        if now < 0:
            raise ValueError("now must be non-negative")
        if not callable(step):
            raise TypeError("step must be callable")
        policy = policy or MissionRunPolicy()
        if (worker_id is None) != (policy.lease_ttl_seconds is None):
            raise ValueError("worker_id and lease_ttl_seconds must be supplied together")
        if worker_id is not None and not worker_id.strip():
            raise ValueError("worker_id is required")
        started = self.clock()
        results: list[Mission] = []

        for _ in range(policy.max_steps):
            if policy.max_duration_seconds is not None and self.clock() - started >= policy.max_duration_seconds:
                break
            mission = self.store.claim_due(now=now, scope_id=scope_id, worker_id=worker_id, lease_ttl_seconds=policy.lease_ttl_seconds)
            if mission is None:
                break
            try:
                step(mission)
            except Exception as exc:
                results.append(self.store.fail(mission.mission_id, type(exc).__name__, now=now, backoff_seconds=policy.retry_backoff_seconds, worker_id=worker_id))
                continue
            results.append(self.store.checkpoint(mission.mission_id, current_step=mission.current_step + 1, now=now, worker_id=worker_id))
        return tuple(results)

    def cancel(self, mission_id: str) -> Mission:
        return self.store.cancel(mission_id)

    def pause(self, mission_id: str) -> Mission:
        return self.store.pause(mission_id)

    def resume(self, mission_id: str, *, now: float) -> Mission:
        return self.store.resume(mission_id, now=now)

    @staticmethod
    def is_terminal(mission: Mission) -> bool:
        return mission.status in (MissionStatus.SUCCEEDED, MissionStatus.FAILED, MissionStatus.CANCELLED)
