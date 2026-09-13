"""Small stdlib-only durable store for capability lifecycle events."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from threading import RLock
from .lifecycle import LifecycleEvent


class LifecycleStore:
    """Append-only SQLite event store; failures never grant capability authority."""
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self._lock = RLock()
        self._db = sqlite3.connect(self.path, check_same_thread=False)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS lifecycle_events ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, capability_id TEXT NOT NULL, "
            "from_status TEXT NOT NULL, to_status TEXT NOT NULL, timestamp TEXT NOT NULL, "
            "reason TEXT NOT NULL, UNIQUE(capability_id, timestamp, to_status, reason))"
        )
        self._db.commit()

    def record(self, event: LifecycleEvent) -> None:
        with self._lock:
            self._db.execute(
                "INSERT OR IGNORE INTO lifecycle_events "
                "(capability_id, from_status, to_status, timestamp, reason) VALUES (?, ?, ?, ?, ?)",
                (event.capability_id, event.from_status.value, event.to_status.value, event.timestamp, event.reason),
            )
            self._db.commit()

    def history(self, capability_id: str | None = None) -> tuple[LifecycleEvent, ...]:
        with self._lock:
            if capability_id:
                rows = self._db.execute(
                    "SELECT capability_id, from_status, to_status, timestamp, reason "
                    "FROM lifecycle_events WHERE capability_id=? ORDER BY id", (capability_id,)
                ).fetchall()
            else:
                rows = self._db.execute(
                    "SELECT capability_id, from_status, to_status, timestamp, reason "
                    "FROM lifecycle_events ORDER BY id"
                ).fetchall()
        from .contracts import CapabilityStatus
        return tuple(
            LifecycleEvent(capability_id, CapabilityStatus(from_status), CapabilityStatus(to_status), timestamp, reason)
            for capability_id, from_status, to_status, timestamp, reason in rows
        )

    def close(self) -> None:
        with self._lock:
            self._db.close()
