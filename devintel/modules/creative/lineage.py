"""Immutable in-process lineage for creative planning artifacts."""
from __future__ import annotations
from dataclasses import dataclass
from threading import RLock
from time import time

@dataclass(frozen=True)
class CreativeLineageRecord:
    artifact_digest: str
    plan_digest: str
    brief_digest: str
    evidence_refs: tuple[str, ...]
    revision: int
    created_at: float

class CreativeLineageStore:
    def __init__(self, max_records: int = 1024) -> None:
        if max_records < 1: raise ValueError("max_records must be positive")
        self._max = max_records; self._records: dict[str, CreativeLineageRecord] = {}; self._lock = RLock()
    def record(self, record: CreativeLineageRecord) -> None:
        if len(record.artifact_digest) != 64 or len(record.plan_digest) != 64 or len(record.brief_digest) != 64: raise ValueError("lineage digests must be SHA-256 hex values")
        with self._lock:
            if record.artifact_digest in self._records: raise ValueError("artifact lineage already recorded")
            if len(self._records) >= self._max: raise RuntimeError("creative lineage capacity reached")
            self._records[record.artifact_digest] = record
    def get(self, artifact_digest: str) -> CreativeLineageRecord | None: return self._records.get(artifact_digest)
    def history(self, *, limit: int = 100) -> tuple[CreativeLineageRecord, ...]:
        if not 1 <= limit <= self._max: raise ValueError("limit out of bounds")
        with self._lock: return tuple(sorted(self._records.values(), key=lambda r: r.created_at, reverse=True)[:limit])
    @staticmethod
    def now() -> float: return time()
