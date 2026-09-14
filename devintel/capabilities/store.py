"""Small stdlib-only durable stores for capability state and lifecycle events."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from threading import RLock
from .lifecycle import LifecycleEvent
from .contracts import CapabilityDescriptor, CapabilityStatus
from .evidence import CapabilityEvidence


class CapabilityRegistryStore:
    """SQLite-backed approved-capability state; persistence never grants authority."""
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self._lock = RLock()
        self._db = sqlite3.connect(self.path, check_same_thread=False)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("CREATE TABLE IF NOT EXISTS capabilities (capability_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        self._db.commit()

    @staticmethod
    def _encode(item: CapabilityDescriptor) -> str:
        return json.dumps({
            "capability_id": item.capability_id, "name": item.name, "version": item.version,
            "interfaces": item.interfaces, "provider": item.provider, "license": item.license,
            "status": item.status.value, "cost": item.cost, "currency": item.currency,
            "permissions": item.permissions, "dependencies": item.dependencies,
            "metadata": dict(item.metadata), "evidence": [e.__dict__ for e in item.evidence],
        }, sort_keys=True)

    @staticmethod
    def _decode(payload: str) -> CapabilityDescriptor:
        data = json.loads(payload)
        evidence = tuple(CapabilityEvidence(**item) for item in data.pop("evidence", []))
        data["status"] = CapabilityStatus(data["status"])
        for key in ("interfaces", "permissions", "dependencies"):
            data[key] = tuple(data[key])
        return CapabilityDescriptor(evidence=evidence, **data)

    def save(self, item: CapabilityDescriptor) -> None:
        with self._lock:
            self._db.execute("INSERT INTO capabilities(capability_id,payload) VALUES(?,?) ON CONFLICT(capability_id) DO UPDATE SET payload=excluded.payload", (item.capability_id, self._encode(item)))
            self._db.commit()

    def load_all(self) -> tuple[CapabilityDescriptor, ...]:
        with self._lock:
            rows = self._db.execute("SELECT payload FROM capabilities ORDER BY capability_id").fetchall()
        return tuple(self._decode(payload) for (payload,) in rows)

    def close(self) -> None:
        with self._lock:
            self._db.close()


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
