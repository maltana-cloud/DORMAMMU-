"""SQLite-backed, versioned persistence for durable intelligence state."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

_SCHEMA_VERSION = 1
_MAX_TEXT = 200_000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    if len(value) > _MAX_TEXT:
        raise ValueError(f"{name} exceeds bounded size")
    return value


@dataclass(frozen=True)
class KnowledgeRecord:
    record_id: str
    scope_id: str
    kind: str
    content: str
    provenance: tuple[str, ...] = ()
    version: int = 1
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class StateRecord:
    scope_id: str
    key: str
    value: Mapping[str, Any]
    version: int
    updated_at: str


@dataclass(frozen=True)
class PersistenceSnapshot:
    schema_version: int
    knowledge_count: int
    state_count: int


class KnowledgeStore:
    """Durable scoped knowledge/state store with explicit schema versioning."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self.path, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.execute("PRAGMA journal_mode=WAL")
        self._initialize()

    def _initialize(self) -> None:
        self._db.execute("CREATE TABLE IF NOT EXISTS schema_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        row = self._db.execute("SELECT value FROM schema_meta WHERE key='version'").fetchone()
        if row is None:
            self._db.execute("INSERT INTO schema_meta(key,value) VALUES('version',?)", (str(_SCHEMA_VERSION),))
        elif int(row[0]) != _SCHEMA_VERSION:
            raise RuntimeError(f"unsupported persistence schema version: {row[0]}")
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS knowledge (
                record_id TEXT PRIMARY KEY,
                scope_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                content TEXT NOT NULL,
                provenance_json TEXT NOT NULL,
                version INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_knowledge_scope ON knowledge(scope_id, updated_at);
            CREATE TABLE IF NOT EXISTS state (
                scope_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value_json TEXT NOT NULL,
                version INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY(scope_id, key)
            );
            CREATE INDEX IF NOT EXISTS idx_state_scope ON state(scope_id);
            """
        )

    @property
    def schema_version(self) -> int:
        return _SCHEMA_VERSION

    def save_knowledge(self, record: KnowledgeRecord) -> KnowledgeRecord:
        _validate(record.record_id, "record_id"); _validate(record.scope_id, "scope_id"); _validate(record.kind, "kind"); _validate(record.content, "content")
        now = _now()
        previous = self._db.execute("SELECT version, created_at FROM knowledge WHERE record_id=?", (record.record_id,)).fetchone()
        version = (int(previous[0]) + 1) if previous else max(1, record.version)
        created = previous[1] if previous else (record.created_at or now)
        saved = KnowledgeRecord(record.record_id, record.scope_id, record.kind, record.content, tuple(record.provenance), version, created, now)
        self._db.execute(
            """INSERT INTO knowledge(record_id,scope_id,kind,content,provenance_json,version,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(record_id) DO UPDATE SET scope_id=excluded.scope_id,kind=excluded.kind,content=excluded.content,provenance_json=excluded.provenance_json,version=excluded.version,updated_at=excluded.updated_at""",
            (saved.record_id, saved.scope_id, saved.kind, saved.content, json.dumps(saved.provenance), saved.version, saved.created_at, saved.updated_at),
        )
        return saved

    def get_knowledge(self, record_id: str, *, scope_id: str | None = None) -> KnowledgeRecord | None:
        row = self._db.execute("SELECT * FROM knowledge WHERE record_id=?", (record_id,)).fetchone()
        if row is None or (scope_id is not None and row["scope_id"] != scope_id):
            return None
        return KnowledgeRecord(row["record_id"], row["scope_id"], row["kind"], row["content"], tuple(json.loads(row["provenance_json"])), row["version"], row["created_at"], row["updated_at"])

    def list_knowledge(self, scope_id: str, *, kind: str | None = None) -> tuple[KnowledgeRecord, ...]:
        _validate(scope_id, "scope_id")
        if kind is None:
            rows = self._db.execute("SELECT * FROM knowledge WHERE scope_id=? ORDER BY updated_at", (scope_id,)).fetchall()
        else:
            rows = self._db.execute("SELECT * FROM knowledge WHERE scope_id=? AND kind=? ORDER BY updated_at", (scope_id, kind)).fetchall()
        return tuple(KnowledgeRecord(r["record_id"], r["scope_id"], r["kind"], r["content"], tuple(json.loads(r["provenance_json"])), r["version"], r["created_at"], r["updated_at"]) for r in rows)

    def put_state(self, scope_id: str, key: str, value: Mapping[str, Any]) -> StateRecord:
        _validate(scope_id, "scope_id"); _validate(key, "key")
        payload = json.dumps(dict(value), sort_keys=True, separators=(",", ":"))
        previous = self._db.execute("SELECT version FROM state WHERE scope_id=? AND key=?", (scope_id, key)).fetchone()
        version = (int(previous[0]) + 1) if previous else 1
        now = _now()
        self._db.execute("INSERT INTO state(scope_id,key,value_json,version,updated_at) VALUES(?,?,?,?,?) ON CONFLICT(scope_id,key) DO UPDATE SET value_json=excluded.value_json,version=excluded.version,updated_at=excluded.updated_at", (scope_id, key, payload, version, now))
        return StateRecord(scope_id, key, dict(value), version, now)

    def get_state(self, scope_id: str, key: str) -> StateRecord | None:
        row = self._db.execute("SELECT * FROM state WHERE scope_id=? AND key=?", (scope_id, key)).fetchone()
        if row is None:
            return None
        return StateRecord(row["scope_id"], row["key"], json.loads(row["value_json"]), row["version"], row["updated_at"])

    def snapshot(self) -> PersistenceSnapshot:
        knowledge = self._db.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
        state = self._db.execute("SELECT COUNT(*) FROM state").fetchone()[0]
        return PersistenceSnapshot(_SCHEMA_VERSION, int(knowledge), int(state))

    def close(self) -> None:
        self._db.close()
