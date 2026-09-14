"""Bounded SQLite snapshots and deterministic replay records."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict

from .contracts import WorldEntity, WorldSnapshot, EntityKind, snapshot_digest


class SimulationStore:
    """Crash-safe checkpoint store; persisted data never grants execution authority."""

    def __init__(self, path: str = ":memory:") -> None:
        self._db = sqlite3.connect(path)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("CREATE TABLE IF NOT EXISTS simulation_snapshots (world_id TEXT NOT NULL, tick INTEGER NOT NULL, digest TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(world_id, tick))")
        self._db.commit()

    def save(self, snapshot: WorldSnapshot) -> None:
        if len(snapshot.entities) > 256:
            raise ValueError("snapshot is too large")
        if snapshot.digest != snapshot_digest(snapshot.world_id, snapshot.tick, snapshot.entities):
            raise ValueError("snapshot digest mismatch")
        payload = json.dumps([asdict(e) | {"kind": e.kind.value} for e in snapshot.entities], sort_keys=True, separators=(",", ":"))
        self._db.execute("INSERT OR REPLACE INTO simulation_snapshots VALUES (?, ?, ?, ?)", (snapshot.world_id, snapshot.tick, snapshot.digest, payload))
        self._db.commit()

    def load(self, world_id: str, tick: int | None = None) -> WorldSnapshot | None:
        if tick is None:
            row = self._db.execute("SELECT tick, digest, payload FROM simulation_snapshots WHERE world_id=? ORDER BY tick DESC LIMIT 1", (world_id,)).fetchone()
        else:
            row = self._db.execute("SELECT tick, digest, payload FROM simulation_snapshots WHERE world_id=? AND tick=?", (world_id, tick)).fetchone()
        if row is None:
            return None
        entities = tuple(WorldEntity(e["entity_id"], EntityKind(e["kind"]), e["x"], e["y"], e["energy"], tuple(e["attributes"])) for e in json.loads(row[2]))
        snapshot = WorldSnapshot(world_id, row[0], entities, row[1])
        if snapshot.digest != snapshot_digest(world_id, snapshot.tick, snapshot.entities):
            raise ValueError("stored snapshot integrity failure")
        return snapshot

    def history(self, world_id: str, *, limit: int = 100) -> tuple[tuple[int, str], ...]:
        if limit < 1 or limit > 4096:
            raise ValueError("history limit is out of bounds")
        return tuple(self._db.execute("SELECT tick, digest FROM simulation_snapshots WHERE world_id=? ORDER BY tick DESC LIMIT ?", (world_id, limit)).fetchall())

    def close(self) -> None:
        self._db.close()
