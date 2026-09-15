"""Durable, bounded runtime worker primitives for DORMAMMU.

The worker is deliberately externally scheduled: it never creates an implicit
background thread/process. Durable state makes restart/recovery explicit while
keeping execution behind the existing runtime permission/security boundaries.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import sqlite3
from typing import Callable, Any
from uuid import uuid4

@dataclass(frozen=True)
class RuntimeJob:
    job_id: str; scope_id: str; action: str; payload: dict[str, Any]; status: str
    attempts: int; created_at: str; updated_at: str; last_error: str = ""

def _now() -> str: return datetime.now(timezone.utc).isoformat()

class RuntimeJobStore:
    """SQLite-backed job state store with atomic claim transitions."""
    def __init__(self, path: str = ":memory:") -> None:
        self._db = sqlite3.connect(path)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("""CREATE TABLE IF NOT EXISTS runtime_jobs (
            job_id TEXT PRIMARY KEY, scope_id TEXT NOT NULL, action TEXT NOT NULL,
            payload TEXT NOT NULL, status TEXT NOT NULL, attempts INTEGER NOT NULL,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL, last_error TEXT NOT NULL)""")
        self._db.commit()
    def enqueue(self, scope_id: str, action: str, payload: dict[str, Any], *, job_id: str | None = None) -> RuntimeJob:
        if not isinstance(scope_id, str) or not scope_id.strip(): raise ValueError("scope_id is required")
        if not isinstance(action, str) or not action.strip(): raise ValueError("action is required")
        if not isinstance(payload, dict): raise TypeError("payload must be a dict")
        now = _now(); job = RuntimeJob(job_id or uuid4().hex, scope_id, action, dict(payload), "queued", 0, now, now, "")
        self._db.execute("INSERT INTO runtime_jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (job.job_id, job.scope_id, job.action, json.dumps(job.payload, sort_keys=True), job.status, job.attempts, job.created_at, job.updated_at, job.last_error)); self._db.commit(); return job
    def get(self, job_id: str) -> RuntimeJob | None:
        row = self._db.execute("SELECT * FROM runtime_jobs WHERE job_id = ?", (job_id,)).fetchone(); return self._from_row(row) if row else None
    def claim_next(self) -> RuntimeJob | None:
        row = self._db.execute("SELECT * FROM runtime_jobs WHERE status='queued' ORDER BY created_at, job_id LIMIT 1").fetchone()
        if row is None: return None
        updated = self._db.execute("UPDATE runtime_jobs SET status='running', attempts=attempts+1, updated_at=? WHERE job_id=? AND status='queued'", (_now(), row[0])); self._db.commit()
        return self.get(row[0]) if updated.rowcount == 1 else None
    def complete(self, job_id: str) -> RuntimeJob: return self._transition(job_id, "succeeded", "")
    def fail(self, job_id: str, error: str) -> RuntimeJob:
        if not isinstance(error, str) or not error.strip(): raise ValueError("error is required")
        return self._transition(job_id, "failed", error[:2000])
    def requeue_failed(self, job_id: str) -> RuntimeJob:
        job = self.get(job_id)
        if job is None: raise KeyError(job_id)
        if job.status != "failed": raise ValueError("only failed jobs can be requeued")
        return self._transition(job_id, "queued", "")
    def recover_running(self) -> tuple[RuntimeJob, ...]:
        rows = self._db.execute("SELECT * FROM runtime_jobs WHERE status='running' ORDER BY created_at, job_id").fetchall(); self._db.execute("UPDATE runtime_jobs SET status='queued', updated_at=? WHERE status='running'", (_now(),)); self._db.commit(); return tuple(self.get(r[0]) for r in rows if self.get(r[0]) is not None)
    def history(self, scope_id: str | None = None) -> tuple[RuntimeJob, ...]:
        rows = self._db.execute("SELECT * FROM runtime_jobs ORDER BY created_at, job_id").fetchall() if scope_id is None else self._db.execute("SELECT * FROM runtime_jobs WHERE scope_id=? ORDER BY created_at, job_id", (scope_id,)).fetchall(); return tuple(self._from_row(r) for r in rows)
    def close(self) -> None: self._db.close()
    def _transition(self, job_id: str, status: str, error: str) -> RuntimeJob:
        updated = self._db.execute("UPDATE runtime_jobs SET status=?, updated_at=?, last_error=? WHERE job_id=? AND status='running'", (status, _now(), error, job_id)); self._db.commit()
        if updated.rowcount != 1: raise ValueError(f"job {job_id} is not running")
        job = self.get(job_id)
        if job is None: raise KeyError(job_id)
        return job
    @staticmethod
    def _from_row(row: tuple[Any, ...]) -> RuntimeJob: return RuntimeJob(row[0], row[1], row[2], json.loads(row[3]), row[4], row[5], row[6], row[7], row[8])

class RuntimeWorker:
    """Execute at most a caller-defined number of durable jobs per invocation."""
    def __init__(self, store: RuntimeJobStore, dispatch: Callable[[RuntimeJob], Any]) -> None: self.store, self.dispatch = store, dispatch
    def run_once(self, *, max_jobs: int = 1) -> tuple[RuntimeJob, ...]:
        if max_jobs <= 0: raise ValueError("max_jobs must be positive")
        completed = []
        for _ in range(max_jobs):
            job = self.store.claim_next()
            if job is None: break
            try: self.dispatch(job)
            except Exception as exc: completed.append(self.store.fail(job.job_id, type(exc).__name__))
            else: completed.append(self.store.complete(job.job_id))
        return tuple(completed)

def build_worker(store: RuntimeJobStore, dispatch: Callable[[RuntimeJob], Any]) -> RuntimeWorker:
    """Compatibility factory for the public runtime API."""
    if not isinstance(store, RuntimeJobStore): raise TypeError("store must be a RuntimeJobStore")
    if not callable(dispatch): raise TypeError("dispatch must be callable")
    return RuntimeWorker(store, dispatch)
