"""Bounded mission-worker lease contracts.

Leases prevent two external workers from concurrently executing the same
mission step. They are coordination only: a lease never grants capability,
permission, credentials, or authority.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MissionLease:
    mission_id: str
    worker_id: str
    expires_at: float

    def __post_init__(self) -> None:
        if not self.mission_id.strip():
            raise ValueError("mission_id is required")
        if not self.worker_id.strip():
            raise ValueError("worker_id is required")
        if self.expires_at < 0:
            raise ValueError("expires_at must be non-negative")
