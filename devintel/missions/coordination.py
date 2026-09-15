"""Bounded worker coordination for durable mission execution.

Coordination prevents concurrent workers from claiming the same mission. It
never grants capability, permission, credentials, spending, or authority.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MissionLease:
    mission_id: str
    worker_id: str
    expires_at: float

    def __post_init__(self) -> None:
        if not isinstance(self.mission_id, str) or not self.mission_id.strip():
            raise ValueError("mission_id is required")
        if not isinstance(self.worker_id, str) or not self.worker_id.strip():
            raise ValueError("worker_id is required")
        if self.expires_at < 0:
            raise ValueError("expires_at must be non-negative")
