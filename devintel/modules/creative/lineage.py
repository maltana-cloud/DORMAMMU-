"""Bounded immutable lineage for creative planning artifacts."""
from __future__ import annotations
from dataclasses import dataclass
from threading import RLock
from time import time
import sqlite3

@dataclass(frozen=True)
class CreativeLineageRecord:
    artifact_digest: str
    plan_digest: str
    brief_digest: str
    evidence_refs: tuple[str, ...]
    revision: int
    created_at: float

class CreativeLineageStore:
    """Immutable lineage with optional SQLite persistence and a hard record bound."""
    def __init__(self, max_records: int = 1024, path: str = ":memory:") -> None:
        if max_records < 1: raise ValueError("max_records must be positive")
        self._max = max_records; self._records: dict[str, CreativeLineageRecord] = {}; self._lock = RLock()
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.execute("CREATE TABLE IF NOT EXISTS creative_lineage (artifact_digest TEXT PRIMARY KEY, plan_digest TEXT NOT NULL, brief_digest TEXT NOT NULL, evidence_refs TEXT NOT NULL, revision INTEGER NOT NULL, created_at REAL NOT NULL)")
        self._db.commit(); self._load()

    def _load(self) -> None:
        rows = self._db.execute("SELECT artifact_digest, plan_digest, brief_digest, evidence_refs, revision, created_at FROM creative_lineage ORDER BY created_at DESC LIMIT ?", (self._max,)).fetchall()
        self._records = {r[0]: CreativeLineageRecord(r[0], r[1], r[2], tuple(x for x in r[3].split("\n") if x), r[4], r[5]) for r in rows}

    def record(self, record: CreativeLineageRecord) -> None:
        if any(len(x) != 64 or any(c not in "0123456789abcdef" for c in x.lower()) for x in (record.artifact_digest, record.plan_digest, record.brief_digest)): raise ValueError("lineage digests must be SHA-256 hex values")
        if record.revision < 0 or len(record.evidence_refs) > 64: raise ValueError("lineage bounds are invalid")
        with self._lock:
            if record.artifact_digest in self._records: raise ValueError("artifact lineage already recorded")
            count = self._db.execute("SELECT COUNT(*) FROM creative_lineage").fetchone()[0]
            if count >= self._max: raise RuntimeError("creative lineage capacity reached")
            self._db.execute("INSERT INTO creative_lineage VALUES (?, ?, ?, ?, ?, ?)", (record.artifact_digest, record.plan_digest, record.brief_digest, "\n".join(record.evidence_refs), record.revision, record.created_at)); self._db.commit(); self._records[record.artifact_digest] = record

    def get(self, artifact_digest: str) -> CreativeLineageRecord | None:
        with self._lock: return self._records.get(artifact_digest)
    def history(self, *, limit: int = 100) -> tuple[CreativeLineageRecord, ...]:
        if not 1 <= limit <= self._max: raise ValueError("limit out of bounds")
        with self._lock: return tuple(sorted(self._records.values(), key=lambda r: r.created_at, reverse=True)[:limit])
    def close(self) -> None:
        with self._lock: self._db.close()
    @staticmethod
    def now() -> float: return time()
