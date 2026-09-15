"""Integrated, bounded control-plane primitives for DORMAMMU's Ω frontier.

The module deliberately stores *references* to credentials, never secret values.
It provides a durable local queue, finite worker leases, resource budgets, and
reflection records. These are coordination and evidence mechanisms: they do not
create permissions, authenticate an owner, install capabilities, or authorize
external actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
import sqlite3
import time
from typing import Any, Mapping, Protocol


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass(frozen=True)
class CredentialReference:
    """Opaque external credential handle; the secret itself never enters DORMAMMU."""
    provider_id: str
    reference_id: str
    scope: str

    def __post_init__(self) -> None:
        for name in ("provider_id", "reference_id", "scope"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        if any(ch in self.reference_id for ch in ("\n", "\r")):
            raise ValueError("reference_id must not contain newlines")


class CredentialResolver(Protocol):
    """Host-owned boundary for resolving an opaque reference at execution time."""
    def resolve(self, reference: CredentialReference) -> object: ...


@dataclass(frozen=True)
class FrontierJob:
    job_id: str
    scope_id: str
    kind: str
    payload: Mapping[str, Any]
    priority: int
    attempts: int
    max_attempts: int
    next_run_at: float
    state: JobState
    worker_id: str | None = None
    lease_expires_at: float | None = None
    last_error: str = ""

    def __post_init__(self) -> None:
        for name in ("job_id", "scope_id", "kind"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")
        if len(self.payload) > 128:
            raise ValueError("payload has too many fields")
        if self.max_attempts <= 0 or self.attempts < 0 or self.attempts > self.max_attempts:
            raise ValueError("invalid attempt bounds")
        if self.next_run_at < 0:
            raise ValueError("next_run_at must be non-negative")
        if not isinstance(self.state, JobState):
            raise TypeError("state must be JobState")


@dataclass(frozen=True)
class FrontierResourceBudget:
    resource_id: str
    scope_id: str
    capacity: float
    used: float = 0.0

    def __post_init__(self) -> None:
        for name in ("resource_id", "scope_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        if self.capacity <= 0 or self.used < 0 or self.used > self.capacity:
            raise ValueError("invalid resource budget")


@dataclass(frozen=True)
class FrontierReflection:
    job_id: str
    outcome: str
    evidence: tuple[str, ...]
    lesson: str
    uncertainty: str = ""

    def __post_init__(self) -> None:
        if not self.job_id.strip() or not self.outcome.strip() or not self.lesson.strip():
            raise ValueError("job_id, outcome, and lesson are required")
        if len(self.evidence) > 32:
            raise ValueError("too many evidence references")
        if any(not isinstance(item, str) or not item.strip() for item in self.evidence):
            raise ValueError("evidence references must be non-empty strings")


class FrontierJobStore:
    """Durable bounded queue with atomic leases and explicit dead-lettering."""

    def __init__(self, path: str = ":memory:") -> None:
        self._db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.execute("PRAGMA busy_timeout=5000")
        self._db.executescript(
            """CREATE TABLE IF NOT EXISTS frontier_jobs (
                job_id TEXT PRIMARY KEY, scope_id TEXT NOT NULL, kind TEXT NOT NULL,
                payload TEXT NOT NULL, priority INTEGER NOT NULL, attempts INTEGER NOT NULL,
                max_attempts INTEGER NOT NULL, next_run_at REAL NOT NULL, state TEXT NOT NULL,
                worker_id TEXT, lease_expires_at REAL, last_error TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_frontier_due
                ON frontier_jobs(state, next_run_at, priority, job_id);
            CREATE TABLE IF NOT EXISTS frontier_budgets (
                resource_id TEXT PRIMARY KEY, scope_id TEXT NOT NULL,
                capacity REAL NOT NULL, used REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS frontier_reflections (
                reflection_id TEXT PRIMARY KEY, job_id TEXT NOT NULL,
                outcome TEXT NOT NULL, evidence TEXT NOT NULL,
                lesson TEXT NOT NULL, uncertainty TEXT NOT NULL, recorded_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_frontier_reflections_job
                ON frontier_reflections(job_id, recorded_at DESC);
            """
        )

    def enqueue(self, *, scope_id: str, kind: str, payload: Mapping[str, Any],
                priority: int = 0, max_attempts: int = 3,
                next_run_at: float = 0.0, job_id: str | None = None) -> FrontierJob:
        if not isinstance(scope_id, str) or not scope_id.strip() or not isinstance(kind, str) or not kind.strip():
            raise ValueError("scope_id and kind are required")
        if not isinstance(payload, Mapping) or len(payload) > 128:
            raise ValueError("payload is invalid or too large")
        if max_attempts <= 0 or next_run_at < 0:
            raise ValueError("invalid job bounds")
        try:
            encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            raise TypeError("payload must contain JSON-serializable values") from exc
        if len(encoded.encode("utf-8")) > 65536:
            raise ValueError("payload is too large")
        jid = job_id or hashlib.sha256(f"{scope_id}:{kind}:{time.time_ns()}".encode()).hexdigest()[:32]
        if not isinstance(jid, str) or not jid.strip():
            raise ValueError("job_id is required")
        self._db.execute(
            "INSERT INTO frontier_jobs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (jid, scope_id.strip(), kind.strip(), encoded, int(priority), 0,
             int(max_attempts), float(next_run_at), JobState.QUEUED, None, None, ""),
        )
        return self.get(jid)  # type: ignore[return-value]

    def get(self, job_id: str) -> FrontierJob | None:
        row = self._db.execute("SELECT * FROM frontier_jobs WHERE job_id=?", (job_id,)).fetchone()
        return self._from_row(row) if row else None

    def claim(self, *, worker_id: str, now: float, lease_ttl: float,
              scope_id: str | None = None) -> FrontierJob | None:
        if not isinstance(worker_id, str) or not worker_id.strip() or now < 0 or lease_ttl <= 0:
            raise ValueError("invalid worker lease")
        query = ("SELECT job_id FROM frontier_jobs WHERE state IN ('queued','running') "
                 "AND attempts < max_attempts AND next_run_at<=? AND (lease_expires_at IS NULL OR lease_expires_at<=?)")
        args: list[object] = [now, now]
        if scope_id is not None:
            if not isinstance(scope_id, str) or not scope_id.strip():
                raise ValueError("scope_id is required when supplied")
            query += " AND scope_id=?"; args.append(scope_id.strip())
        query += " ORDER BY priority DESC, next_run_at, job_id LIMIT 1"
        row = self._db.execute(query, args).fetchone()
        if row is None:
            return None
        result = self._db.execute(
            "UPDATE frontier_jobs SET state='running', attempts=attempts+1, worker_id=?, "
            "lease_expires_at=?, last_error='' WHERE job_id=? AND state IN ('queued','running') "
            "AND attempts < max_attempts AND next_run_at<=? AND (lease_expires_at IS NULL OR lease_expires_at<=?)",
            (worker_id.strip(), now + lease_ttl, row["job_id"], now, now),
        )
        return self.get(row["job_id"]) if result.rowcount == 1 else None

    def renew(self, job_id: str, *, worker_id: str, now: float, lease_ttl: float) -> FrontierJob:
        if not isinstance(worker_id, str) or not worker_id.strip() or now < 0 or lease_ttl <= 0:
            raise ValueError("invalid worker lease")
        result = self._db.execute(
            "UPDATE frontier_jobs SET lease_expires_at=? WHERE job_id=? AND state='running' "
            "AND worker_id=? AND lease_expires_at>?",
            (now + lease_ttl, job_id, worker_id.strip(), now),
        )
        if result.rowcount != 1:
            raise ValueError("active lease is not owned by worker")
        return self.get(job_id)  # type: ignore[return-value]

    def complete(self, job_id: str, *, worker_id: str, now: float, success: bool,
                 error: str = "", retry_delay: float = 0.0) -> FrontierJob:
        if not isinstance(worker_id, str) or not worker_id.strip() or now < 0 or retry_delay < 0:
            raise ValueError("invalid completion inputs")
        if not isinstance(error, str):
            raise TypeError("error must be a string")
        current = self.get(job_id)
        if current is None:
            raise KeyError(job_id)
        if (current.state is not JobState.RUNNING or current.worker_id != worker_id
                or current.lease_expires_at is None or current.lease_expires_at <= now):
            raise ValueError("active lease is not owned by worker")
        if success:
            state, next_run, last_error = JobState.SUCCEEDED, now, ""
        elif current.attempts >= current.max_attempts:
            state, next_run, last_error = JobState.DEAD_LETTER, now, error[:2000]
        else:
            state, next_run, last_error = JobState.QUEUED, now + retry_delay, error[:2000]
        result = self._db.execute(
            "UPDATE frontier_jobs SET state=?, next_run_at=?, worker_id=NULL, lease_expires_at=NULL, last_error=? "
            "WHERE job_id=? AND state='running' AND worker_id=? AND lease_expires_at>?",
            (state, next_run, last_error, job_id, worker_id.strip(), now),
        )
        if result.rowcount != 1:
            raise ValueError("active lease is not owned by worker")
        return self.get(job_id)  # type: ignore[return-value]

    def recover_expired(self, *, now: float) -> int:
        if now < 0:
            raise ValueError("now must be non-negative")
        result = self._db.execute(
            "UPDATE frontier_jobs SET state=CASE WHEN attempts>=max_attempts THEN 'dead_letter' ELSE 'queued' END, "
            "worker_id=NULL, lease_expires_at=NULL "
            "WHERE state='running' AND lease_expires_at IS NOT NULL AND lease_expires_at<=?",
            (now,),
        )
        return int(result.rowcount)

    def register_budget(self, budget: FrontierResourceBudget) -> None:
        self._db.execute(
            "INSERT INTO frontier_budgets(resource_id,scope_id,capacity,used) VALUES(?,?,?,?) "
            "ON CONFLICT(resource_id) DO UPDATE SET scope_id=excluded.scope_id, "
            "capacity=excluded.capacity, used=MIN(frontier_budgets.used, excluded.capacity)",
            (budget.resource_id, budget.scope_id, budget.capacity, budget.used),
        )

    def reserve(self, *, resource_id: str, quantity: float, scope_id: str) -> bool:
        if not isinstance(resource_id, str) or not resource_id.strip() or quantity <= 0 or not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("invalid reservation")
        result = self._db.execute(
            "UPDATE frontier_budgets SET used=used+? WHERE resource_id=? AND scope_id=? AND used+?<=capacity",
            (float(quantity), resource_id.strip(), scope_id.strip(), float(quantity)),
        )
        return result.rowcount == 1

    def release(self, *, resource_id: str, quantity: float, scope_id: str) -> bool:
        if not isinstance(resource_id, str) or not resource_id.strip() or quantity <= 0 or not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("invalid release")
        result = self._db.execute(
            "UPDATE frontier_budgets SET used=MAX(0, used-?) WHERE resource_id=? AND scope_id=?",
            (float(quantity), resource_id.strip(), scope_id.strip()),
        )
        return result.rowcount == 1

    def record_reflection(self, reflection: FrontierReflection, *, recorded_at: float = 0.0) -> str:
        timestamp = recorded_at or time.time()
        rid = hashlib.sha256(
            json.dumps((reflection.job_id, reflection.outcome, reflection.evidence,
                        reflection.lesson, reflection.uncertainty), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        self._db.execute(
            "INSERT OR IGNORE INTO frontier_reflections VALUES (?,?,?,?,?,?,?)",
            (rid, reflection.job_id, reflection.outcome,
             json.dumps(reflection.evidence, separators=(",", ":")), reflection.lesson,
             reflection.uncertainty, timestamp),
        )
        return rid

    def reflections(self, job_id: str, limit: int = 20) -> tuple[FrontierReflection, ...]:
        if not isinstance(job_id, str) or not job_id.strip() or limit <= 0:
            raise ValueError("job_id and positive limit are required")
        rows = self._db.execute(
            "SELECT job_id,outcome,evidence,lesson,uncertainty FROM frontier_reflections "
            "WHERE job_id=? ORDER BY recorded_at DESC, reflection_id DESC LIMIT ?", (job_id, limit)
        ).fetchall()
        return tuple(FrontierReflection(r[0], r[1], tuple(json.loads(r[2])), r[3], r[4]) for r in rows)

    def close(self) -> None:
        self._db.close()

    @staticmethod
    def _from_row(row: sqlite3.Row) -> FrontierJob:
        return FrontierJob(
            row["job_id"], row["scope_id"], row["kind"], json.loads(row["payload"]),
            row["priority"], row["attempts"], row["max_attempts"], row["next_run_at"],
            JobState(row["state"]), row["worker_id"], row["lease_expires_at"], row["last_error"],
        )


class FrontierControlPlane:
    """One bounded facade for queueing, resources, credential references and reflection."""

    def __init__(self, store: FrontierJobStore | None = None) -> None:
        self.store = store or FrontierJobStore()

    @staticmethod
    def credential_reference(*, provider_id: str, reference_id: str, scope: str) -> CredentialReference:
        return CredentialReference(provider_id, reference_id, scope)

    def submit(self, **kwargs: Any) -> FrontierJob:
        return self.store.enqueue(**kwargs)

    def reflect(self, reflection: FrontierReflection) -> str:
        return self.store.record_reflection(reflection)

    def close(self) -> None:
        self.store.close()
