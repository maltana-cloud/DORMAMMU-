"""Durable, bounded operational measurements for DORMAMMU.

Telemetry is evidence, not authority. It records what happened and derives health
observations; it never grants permissions, activates capabilities, or changes owner
authority by itself.
"""
from __future__ import annotations

from dataclasses import dataclass
import sqlite3
import time
from threading import RLock

from ..capabilities.canary import CanaryHealth


@dataclass(frozen=True)
class OperationObservation:
    operation_id: str
    capability_id: str
    stage: str
    success: bool
    verified: bool
    duration_ms: float
    message: str = ""
    resource_id: str | None = None
    resource_quantity: float | None = None
    recorded_at: float = 0.0


class OperationalTelemetryStore:
    """Append operation observations and derive bounded health measurements."""

    def __init__(self, path: str = ":memory:") -> None:
        self.path = path
        self._lock = RLock()
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS operation_observations (
                operation_id TEXT PRIMARY KEY,
                capability_id TEXT NOT NULL,
                stage TEXT NOT NULL,
                success INTEGER NOT NULL,
                verified INTEGER NOT NULL,
                duration_ms REAL NOT NULL,
                message TEXT NOT NULL,
                resource_id TEXT,
                resource_quantity REAL,
                recorded_at REAL NOT NULL
            )"""
        )
        self._conn.commit()

    def record(self, observation: OperationObservation) -> None:
        if observation.duration_ms < 0:
            raise ValueError("duration_ms must be non-negative")
        recorded_at = observation.recorded_at or time.time()
        with self._lock:
            self._conn.execute(
                "INSERT INTO operation_observations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    observation.operation_id,
                    observation.capability_id,
                    observation.stage,
                    int(observation.success),
                    int(observation.verified),
                    observation.duration_ms,
                    observation.message,
                    observation.resource_id,
                    observation.resource_quantity,
                    recorded_at,
                ),
            )
            self._conn.commit()

    def history(self, capability_id: str | None = None, limit: int = 100) -> tuple[OperationObservation, ...]:
        if limit <= 0:
            raise ValueError("limit must be positive")
        query = "SELECT operation_id, capability_id, stage, success, verified, duration_ms, message, resource_id, resource_quantity, recorded_at FROM operation_observations"
        args: tuple[object, ...] = ()
        if capability_id is not None:
            query += " WHERE capability_id = ?"
            args = (capability_id,)
        query += " ORDER BY recorded_at DESC LIMIT ?"
        args += (limit,)
        with self._lock:
            rows = self._conn.execute(query, args).fetchall()
        return tuple(OperationObservation(row[0], row[1], row[2], bool(row[3]), bool(row[4]), row[5], row[6], row[7], row[8], row[9]) for row in rows)

    def health(self, capability_id: str, *, window: int = 20, min_samples: int = 5) -> CanaryHealth | None:
        observations = self.history(capability_id, limit=window)
        if len(observations) < min_samples:
            return None
        successful = sum(1 for item in observations if item.success and item.verified)
        total = len(observations)
        success_rate = successful / total
        error_rate = 1.0 - success_rate
        latency_ms = max(item.duration_ms for item in observations)
        healthy = all(item.success and item.verified for item in observations)
        reason = f"derived from {total} recorded operation observations"
        return CanaryHealth(healthy, success_rate, error_rate, latency_ms, reason)

    def close(self) -> None:
        with self._lock:
            self._conn.close()
