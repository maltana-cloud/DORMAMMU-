"""Bounded intelligence/knowledge layer over durable persistence."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from devintel.modules.research import Claim, VerifiedClaim
from devintel.persistence import KnowledgeRecord, KnowledgeStore

_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class KnowledgeItem:
    record_id: str
    scope_id: str
    subject: str
    predicate: str
    object: str
    confidence: float
    provenance: tuple[str, ...]
    version: int
    updated_at: str
    stale: bool = False


@dataclass(frozen=True)
class KnowledgeConflict:
    scope_id: str
    subject: str
    predicate: str
    objects: tuple[str, ...]
    record_ids: tuple[str, ...]


@dataclass(frozen=True)
class KnowledgeQuery:
    scope_id: str
    text: str = ""
    limit: int = 20
    max_age_seconds: float | None = None


class KnowledgeIntelligence:
    """Admit verified claims and provide bounded, deterministic retrieval."""

    def __init__(self, store: KnowledgeStore, *, max_results: int = 100) -> None:
        if not isinstance(store, KnowledgeStore):
            raise TypeError("store must be a KnowledgeStore")
        if max_results <= 0:
            raise ValueError("max_results must be positive")
        self.store = store
        self.max_results = max_results

    def admit(self, scope_id: str, claims: Iterable[VerifiedClaim]) -> tuple[KnowledgeItem, ...]:
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("scope_id is required")
        admitted = []
        for verified in claims:
            if not isinstance(verified, VerifiedClaim):
                raise TypeError("only VerifiedClaim values may be admitted")
            claim = verified.claim
            record_id = self._record_id(claim)
            previous = self.store.get_knowledge(record_id, scope_id=scope_id)
            provenance = verified.evidence_urls
            if previous is not None:
                provenance = tuple(dict.fromkeys(previous.provenance + provenance))
            record = self.store.save_knowledge(KnowledgeRecord(
                record_id=record_id,
                scope_id=scope_id,
                kind="claim",
                content=self._encode(claim, verified.confidence),
                provenance=provenance,
            ))
            admitted.append(self._decode(record))
        return tuple(admitted)

    def query(self, query: KnowledgeQuery) -> tuple[KnowledgeItem, ...]:
        if not isinstance(query, KnowledgeQuery):
            raise TypeError("query must be KnowledgeQuery")
        if not query.scope_id.strip():
            raise ValueError("scope_id is required")
        if query.limit <= 0 or query.limit > self.max_results:
            raise ValueError("limit is outside the configured bound")
        if query.max_age_seconds is not None and query.max_age_seconds < 0:
            raise ValueError("max_age_seconds must be non-negative")
        needle = query.text.strip().lower()
        now = datetime.now(timezone.utc)
        found = []
        for record in self.store.list_knowledge(query.scope_id, kind="claim"):
            item = self._decode(record)
            if needle and needle not in f"{item.subject} {item.predicate} {item.object}".lower():
                continue
            if query.max_age_seconds is not None:
                age = (now - datetime.fromisoformat(item.updated_at)).total_seconds()
                if age > query.max_age_seconds:
                    continue
            found.append(item)
        found.sort(key=lambda item: (-item.confidence, item.record_id))
        return tuple(found[:query.limit])

    def conflicts(self, scope_id: str) -> tuple[KnowledgeConflict, ...]:
        groups = {}
        for item in self.query(KnowledgeQuery(scope_id=scope_id, limit=self.max_results)):
            groups.setdefault((item.subject.strip().lower(), item.predicate.strip().lower()), []).append(item)
        result = []
        for (subject, predicate), items in sorted(groups.items()):
            objects = tuple(sorted({item.object for item in items}))
            if len(objects) > 1:
                result.append(KnowledgeConflict(scope_id, subject, predicate, objects,
                                                tuple(sorted(item.record_id for item in items))))
        return tuple(result)

    @staticmethod
    def _record_id(claim: Claim) -> str:
        raw = "\x1f".join((claim.subject.strip().lower(), claim.predicate.strip().lower(), claim.object.strip().lower()))
        return "claim-" + hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def _encode(claim: Claim, confidence: float) -> str:
        return json.dumps({
            "schema_version": _SCHEMA_VERSION,
            "subject": claim.subject.strip(),
            "predicate": claim.predicate.strip(),
            "object": claim.object.strip(),
            "confidence": confidence,
        }, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _decode(record: KnowledgeRecord) -> KnowledgeItem:
        try:
            payload = json.loads(record.content)
            if payload.get("schema_version") != _SCHEMA_VERSION:
                raise ValueError("unsupported knowledge record schema")
            subject = payload["subject"]
            predicate = payload["predicate"]
            object_value = payload["object"]
            confidence = float(payload["confidence"])
            if not all(isinstance(value, str) and value.strip() for value in (subject, predicate, object_value)):
                raise ValueError("stored claim fields are invalid")
            if not 0.0 <= confidence <= 1.0:
                raise ValueError("stored claim confidence is invalid")
        except (TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
            raise ValueError("stored claim record is malformed") from exc
        return KnowledgeItem(record.record_id, record.scope_id, subject, predicate, object_value,
                             confidence, record.provenance, record.version, record.updated_at)
