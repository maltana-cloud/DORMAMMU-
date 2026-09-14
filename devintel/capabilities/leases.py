"""Durable, scoped resource leases backed by SQLite."""
from __future__ import annotations

from dataclasses import dataclass
import sqlite3
import time
from threading import RLock
from uuid import uuid4


@dataclass(frozen=True)
class ResourceLease:
    lease_id: str
    resource_id: str
    quantity: float
    acquired_at: float
    expires_at: float


class ResourceLeaseStore:
    """Crash-safe lease storage with expiry and atomic acquisition."""

    def __init__(self, path: str = ":memory:") -> None:
        self.path = path
        self._lock = RLock()
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS resource_leases (
                lease_id TEXT PRIMARY KEY,
                resource_id TEXT NOT NULL,
                quantity REAL NOT NULL CHECK(quantity > 0),
                acquired_at REAL NOT NULL,
                expires_at REAL NOT NULL
            )"""
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_resource_leases_resource ON resource_leases(resource_id, expires_at)"
        )
        self._conn.commit()

    def _purge_expired_locked(self, now: float) -> None:
        self._conn.execute("DELETE FROM resource_leases WHERE expires_at <= ?", (now,))

    def active_quantity(self, resource_id: str, *, now: float | None = None) -> float:
        now = time.time() if now is None else now
        with self._lock:
            self._purge_expired_locked(now)
            row = self._conn.execute(
                "SELECT COALESCE(SUM(quantity), 0) FROM resource_leases WHERE resource_id = ?",
                (resource_id,),
            ).fetchone()
            self._conn.commit()
            return float(row[0])

    def acquire(
        self,
        resource_id: str,
        quantity: float,
        capacity: float,
        *,
        ttl_seconds: float = 300.0,
        now: float | None = None,
    ) -> ResourceLease | None:
        if not resource_id or quantity <= 0 or capacity < 0 or ttl_seconds <= 0:
            raise ValueError("resource_id, quantity, capacity, and ttl_seconds must be valid")
        now = time.time() if now is None else now
        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                self._purge_expired_locked(now)
                row = self._conn.execute(
                    "SELECT COALESCE(SUM(quantity), 0) FROM resource_leases WHERE resource_id = ?",
                    (resource_id,),
                ).fetchone()
                used = float(row[0])
                if used + quantity > capacity:
                    self._conn.rollback()
                    return None
                lease = ResourceLease(uuid4().hex, resource_id, quantity, now, now + ttl_seconds)
                self._conn.execute(
                    "INSERT INTO resource_leases VALUES (?, ?, ?, ?, ?)",
                    (lease.lease_id, lease.resource_id, lease.quantity, lease.acquired_at, lease.expires_at),
                )
                self._conn.commit()
                return lease
            except Exception:
                self._conn.rollback()
                raise

    def get(self, lease_id: str, *, now: float | None = None) -> ResourceLease | None:
        now = time.time() if now is None else now
        with self._lock:
            self._purge_expired_locked(now)
            row = self._conn.execute(
                "SELECT lease_id, resource_id, quantity, acquired_at, expires_at FROM resource_leases WHERE lease_id = ?",
                (lease_id,),
            ).fetchone()
            self._conn.commit()
        return ResourceLease(*row) if row else None

    def release(self, lease_id: str) -> None:
        with self._lock:
            cursor = self._conn.execute("DELETE FROM resource_leases WHERE lease_id = ?", (lease_id,))
            self._conn.commit()
            if cursor.rowcount == 0:
                raise KeyError(lease_id)

    def active(self, *, now: float | None = None) -> tuple[ResourceLease, ...]:
        now = time.time() if now is None else now
        with self._lock:
            self._purge_expired_locked(now)
            rows = self._conn.execute(
                "SELECT lease_id, resource_id, quantity, acquired_at, expires_at FROM resource_leases ORDER BY acquired_at, lease_id"
            ).fetchall()
            self._conn.commit()
        return tuple(ResourceLease(*row) for row in rows)

    def close(self) -> None:
        with self._lock:
            self._conn.close()
