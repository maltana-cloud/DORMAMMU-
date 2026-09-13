"""Small stdlib-only durable store for capability lifecycle events."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import RLock
from .lifecycle import LifecycleEvent
from .contracts import CapabilityStatus

class LifecycleStore:
    """Append-only SQLite event store; persistence never grants authority."""
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self._lock = RLock()
        self._db = sqlite3.connect(self.path, check_same_thread=False)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("CREATE TABLE IF NOT EXISTS lifecycle_events (id INTEGER PRIMARY KEY AUTOINCREMENT, capability_id TEXT NOT NULL, from_status TEXT NOT NULL, to_status TEXT NOT NULL, timestamp TEXT NOT NULL, reason TEXT NOT NULL)")
        self._db.commit()

    def record(self, event: LifecycleEvent) -> None:
        with self._lock:
            self._db.execute("INSERT INTO lifecycle_events(capability_id,from_status,to_status,timestamp,reason) VALUES (?,?,?,?,?)", (event.capability_id,event.from_status.value,event.to_status.value,event.timestamp,event.reason))
            self._db.commit()

    def history(self, capability_id: str | None = None) -> tuple[LifecycleEvent, ...]:
        with self._lock:
            query = "SELECT capability_id,from_status,to_status,timestamp,reason FROM lifecycle_events"
            args: tuple[str, ...] = ()
            if capability_id:
                query += " WHERE capability_id=?"
                args = (capability_id,)
            rows = self._db.execute(query + " ORDER BY id", args).fetchall()
        return tuple(LifecycleEvent(cid, CapabilityStatus(src), CapabilityStatus(dst), timestamp, reason) for cid,src,dst,timestamp,reason in rows)

    def close(self) -> None:
        with self._lock:
            self._db.close()
