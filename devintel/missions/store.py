"""Durable mission state with explicit bounded lifecycle transitions."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import sqlite3
from typing import Any
from uuid import uuid4

from .coordination import MissionLease


class MissionStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Mission:
    mission_id: str
    scope_id: str
    objective: str
    total_steps: int
    current_step: int
    status: MissionStatus
    attempts: int
    max_attempts: int
    next_run_at: float
    created_at: str
    updated_at: str
    last_error: str = ""


class MissionStore:
    """SQLite-backed mission checkpoints with atomic optional worker leases."""

    def __init__(self, path: str = ":memory:") -> None:
        self._db = sqlite3.connect(path, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS missions (
                mission_id TEXT PRIMARY KEY, scope_id TEXT NOT NULL,
                objective TEXT NOT NULL, total_steps INTEGER NOT NULL,
                current_step INTEGER NOT NULL, status TEXT NOT NULL,
                attempts INTEGER NOT NULL, max_attempts INTEGER NOT NULL,
                next_run_at REAL NOT NULL, created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL, last_error TEXT NOT NULL,
                lease_worker_id TEXT, lease_expires_at REAL
            )"""
        )
        self._ensure_lease_columns()
        self._db.execute("CREATE INDEX IF NOT EXISTS idx_missions_due ON missions(status, next_run_at, created_at, mission_id)")
        self._db.execute("CREATE INDEX IF NOT EXISTS idx_missions_lease ON missions(lease_worker_id, lease_expires_at)")

    def _ensure_lease_columns(self) -> None:
        columns = {row[1] for row in self._db.execute("PRAGMA table_info(missions)").fetchall()}
        if "lease_worker_id" not in columns:
            self._db.execute("ALTER TABLE missions ADD COLUMN lease_worker_id TEXT")
        if "lease_expires_at" not in columns:
            self._db.execute("ALTER TABLE missions ADD COLUMN lease_expires_at REAL")

    def create(self, scope_id: str, objective: str, total_steps: int, *, max_attempts: int = 3, mission_id: str | None = None, now: float = 0.0) -> Mission:
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("scope_id is required")
        if not isinstance(objective, str) or not objective.strip():
            raise ValueError("objective is required")
        if total_steps <= 0 or max_attempts <= 0:
            raise ValueError("total_steps and max_attempts must be positive")
        if now < 0:
            raise ValueError("now must be non-negative")
        created = _now()
        mission = Mission(mission_id or uuid4().hex, scope_id.strip(), objective.strip(), total_steps, 0, MissionStatus.QUEUED, 0, max_attempts, now, created, created, "")
        self._db.execute("INSERT INTO missions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (mission.mission_id, mission.scope_id, mission.objective, mission.total_steps, mission.current_step, mission.status, mission.attempts, mission.max_attempts, mission.next_run_at, mission.created_at, mission.updated_at, mission.last_error, None, None))
        return mission

    def get(self, mission_id: str) -> Mission | None:
        row = self._db.execute("SELECT * FROM missions WHERE mission_id=?", (mission_id,)).fetchone()
        return self._from_row(row) if row else None

    def claim_due(self, *, now: float, scope_id: str | None = None, worker_id: str | None = None, lease_ttl_seconds: float | None = None) -> Mission | None:
        if now < 0:
            raise ValueError("now must be non-negative")
        if worker_id is not None and (not isinstance(worker_id, str) or not worker_id.strip() or lease_ttl_seconds is None or lease_ttl_seconds <= 0):
            raise ValueError("worker_id requires a positive lease_ttl_seconds")
        if worker_id is None and lease_ttl_seconds is not None:
            raise ValueError("lease_ttl_seconds requires worker_id")
        query = "SELECT mission_id FROM missions WHERE status IN ('queued','running') AND next_run_at<=? AND (lease_expires_at IS NULL OR lease_expires_at<=?)"
        args: list[Any] = [now, now]
        if scope_id is not None:
            query += " AND scope_id=?"; args.append(scope_id)
        query += " ORDER BY next_run_at, created_at, mission_id LIMIT 1"
        row = self._db.execute(query, args).fetchone()
        if row is None:
            return None
        if worker_id is None:
            updated = self._db.execute("UPDATE missions SET status='running', attempts=attempts+1, lease_worker_id=NULL, lease_expires_at=NULL, updated_at=? WHERE mission_id=? AND status IN ('queued','running') AND next_run_at<=? AND (lease_expires_at IS NULL OR lease_expires_at<=?)", (_now(), row["mission_id"], now, now))
        else:
            updated = self._db.execute("UPDATE missions SET status='running', attempts=attempts+1, lease_worker_id=?, lease_expires_at=?, updated_at=? WHERE mission_id=? AND status IN ('queued','running') AND next_run_at<=? AND (lease_expires_at IS NULL OR lease_expires_at<=?)", (worker_id.strip(), now + float(lease_ttl_seconds), _now(), row["mission_id"], now, now))
        return self.get(row["mission_id"]) if updated.rowcount == 1 else None

    def renew_lease(self, mission_id: str, *, worker_id: str, now: float, lease_ttl_seconds: float) -> MissionLease:
        self._validate_lease_inputs(worker_id, now, lease_ttl_seconds)
        expires = now + lease_ttl_seconds
        updated = self._db.execute("UPDATE missions SET lease_expires_at=?, updated_at=? WHERE mission_id=? AND status='running' AND lease_worker_id=? AND lease_expires_at>?", (expires, _now(), mission_id, worker_id.strip(), now))
        if updated.rowcount != 1:
            raise ValueError("active lease is not owned by worker")
        return MissionLease(mission_id, worker_id.strip(), expires)

    def release_lease(self, mission_id: str, *, worker_id: str, now: float) -> Mission:
        if not isinstance(worker_id, str) or not worker_id.strip() or now < 0:
            raise ValueError("invalid lease release inputs")
        updated = self._db.execute("UPDATE missions SET lease_worker_id=NULL, lease_expires_at=NULL, updated_at=? WHERE mission_id=? AND lease_worker_id=? AND status='running'", (_now(), mission_id, worker_id.strip()))
        if updated.rowcount != 1:
            raise ValueError("active lease is not owned by worker")
        return self._require(mission_id)

    def checkpoint(self, mission_id: str, *, current_step: int, now: float, worker_id: str | None = None) -> Mission:
        mission = self._require_running(mission_id)
        if now < 0:
            raise ValueError("now must be non-negative")
        if not 0 <= current_step <= mission.total_steps:
            raise ValueError("current_step is outside mission bounds")
        status = MissionStatus.SUCCEEDED if current_step == mission.total_steps else MissionStatus.QUEUED
        if worker_id is None:
            updated = self._db.execute("UPDATE missions SET status=?, current_step=?, next_run_at=?, updated_at=?, last_error=?, lease_worker_id=NULL, lease_expires_at=NULL WHERE mission_id=? AND status='running'", (status, current_step, now, _now(), "", mission_id))
        else:
            if not worker_id.strip():
                raise ValueError("worker_id is required")
            updated = self._db.execute("UPDATE missions SET status=?, current_step=?, next_run_at=?, updated_at=?, last_error=?, lease_worker_id=NULL, lease_expires_at=NULL WHERE mission_id=? AND status='running' AND lease_worker_id=?", (status, current_step, now, _now(), "", mission_id, worker_id.strip()))
        if updated.rowcount != 1:
            raise ValueError("active lease is not owned by worker")
        return self._require(mission_id)

    def fail(self, mission_id: str, error: str, *, now: float, backoff_seconds: float = 0.0, worker_id: str | None = None) -> Mission:
        mission = self._require_running(mission_id)
        if now < 0:
            raise ValueError("now must be non-negative")
        if not isinstance(error, str) or not error.strip():
            raise ValueError("error is required")
        if backoff_seconds < 0:
            raise ValueError("backoff_seconds cannot be negative")
        status = MissionStatus.FAILED if mission.attempts >= mission.max_attempts else MissionStatus.QUEUED
        next_run = now + backoff_seconds if status is MissionStatus.QUEUED else now
        if worker_id is None:
            updated = self._db.execute("UPDATE missions SET status=?, next_run_at=?, updated_at=?, last_error=?, lease_worker_id=NULL, lease_expires_at=NULL WHERE mission_id=? AND status='running'", (status, next_run, _now(), error[:2000], mission_id))
        else:
            if not worker_id.strip():
                raise ValueError("worker_id is required")
            updated = self._db.execute("UPDATE missions SET status=?, next_run_at=?, updated_at=?, last_error=?, lease_worker_id=NULL, lease_expires_at=NULL WHERE mission_id=? AND status='running' AND lease_worker_id=?", (status, next_run, _now(), error[:2000], mission_id, worker_id.strip()))
        if updated.rowcount != 1:
            raise ValueError("active lease is not owned by worker")
        return self._require(mission_id)

    def pause(self, mission_id: str) -> Mission:
        self._require_running(mission_id)
        self._db.execute("UPDATE missions SET status='paused', lease_worker_id=NULL, lease_expires_at=NULL, updated_at=? WHERE mission_id=? AND status='running'", (_now(), mission_id))
        return self._require(mission_id)

    def resume(self, mission_id: str, *, now: float) -> Mission:
        mission = self._require(mission_id)
        if mission.status is not MissionStatus.PAUSED:
            raise ValueError("only paused missions can be resumed")
        if now < 0:
            raise ValueError("now must be non-negative")
        self._db.execute("UPDATE missions SET status='queued', next_run_at=?, updated_at=?, last_error='', lease_worker_id=NULL, lease_expires_at=NULL WHERE mission_id=?", (now, _now(), mission_id))
        return self._require(mission_id)

    def cancel(self, mission_id: str) -> Mission:
        mission = self._require(mission_id)
        if mission.status in (MissionStatus.SUCCEEDED, MissionStatus.CANCELLED):
            raise ValueError("mission is already terminal")
        self._db.execute("UPDATE missions SET status='cancelled', lease_worker_id=NULL, lease_expires_at=NULL, updated_at=? WHERE mission_id=?", (_now(), mission_id))
        return self._require(mission_id)

    def recover_running(self, *, now: float) -> tuple[Mission, ...]:
        if now < 0:
            raise ValueError("now must be non-negative")
        rows = self._db.execute("SELECT mission_id FROM missions WHERE status='running' ORDER BY created_at, mission_id").fetchall()
        self._db.execute("UPDATE missions SET status='queued', next_run_at=?, lease_worker_id=NULL, lease_expires_at=NULL, updated_at=? WHERE status='running'", (now, _now()))
        return tuple(self._require(row["mission_id"]) for row in rows)

    def close(self) -> None:
        self._db.close()

    @staticmethod
    def _validate_lease_inputs(worker_id: str, now: float, lease_ttl_seconds: float) -> None:
        if not isinstance(worker_id, str) or not worker_id.strip():
            raise ValueError("worker_id is required")
        if now < 0 or lease_ttl_seconds <= 0:
            raise ValueError("invalid lease timing")

    def _require(self, mission_id: str) -> Mission:
        mission = self.get(mission_id)
        if mission is None:
            raise KeyError(mission_id)
        return mission

    def _require_running(self, mission_id: str) -> Mission:
        mission = self._require(mission_id)
        if mission.status is not MissionStatus.RUNNING:
            raise ValueError("mission is not running")
        return mission

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Mission:
        return Mission(row["mission_id"], row["scope_id"], row["objective"], row["total_steps"], row["current_step"], MissionStatus(row["status"]), row["attempts"], row["max_attempts"], row["next_run_at"], row["created_at"], row["updated_at"], row["last_error"])
