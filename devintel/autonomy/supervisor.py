"""Bounded supervisor for repeated autonomous cycles.

The supervisor provides operational continuity without creating an unrestricted
background loop. Each run is finite, scope-bound, and governed by explicit
limits. Failures stop the run by default; callers may inspect the persisted
cycle history and decide whether another run is appropriate.
"""
from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Callable

from .contracts import AutonomousCycle
from .engine import AutonomousEngine


@dataclass(frozen=True)
class AutonomyRunPolicy:
    """Explicit limits for a bounded operational run."""

    max_cycles: int = 1
    stop_on_failure: bool = True
    max_duration_seconds: float | None = None

    def __post_init__(self) -> None:
        if self.max_cycles <= 0:
            raise ValueError("max_cycles must be positive")
        if self.max_duration_seconds is not None and self.max_duration_seconds <= 0:
            raise ValueError("max_duration_seconds must be positive when set")


@dataclass(frozen=True)
class AutonomyRun:
    """Result of one finite supervisory run."""

    scope_id: str
    cycles: tuple[AutonomousCycle, ...]
    stopped: bool
    stop_reason: str


class AutonomousSupervisor:
    """Run bounded autonomous cycles with explicit operational guardrails."""

    def __init__(
        self,
        engine: AutonomousEngine,
        *,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self.engine = engine
        self.clock = clock

    def run(
        self,
        scope_id: str,
        *,
        policy: AutonomyRunPolicy | None = None,
        owner_approved: bool = False,
    ) -> AutonomyRun:
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("scope_id is required")
        policy = policy or AutonomyRunPolicy()
        started = self.clock()
        cycles: list[AutonomousCycle] = []

        for _ in range(policy.max_cycles):
            if policy.max_duration_seconds is not None and self.clock() - started >= policy.max_duration_seconds:
                return AutonomyRun(scope_id, tuple(cycles), True, "run duration limit reached")

            cycle = self.engine.run_once(scope_id, owner_approved=owner_approved)
            cycles.append(cycle)
            if policy.stop_on_failure and (cycle.stopped or not cycle.verified):
                return AutonomyRun(scope_id, tuple(cycles), True, cycle.stop_reason or "cycle verification failed")

        return AutonomyRun(scope_id, tuple(cycles), True, "cycle limit reached")
