"""Bounded SQLite persistence for community intelligence plans."""
from __future__ import annotations
import hashlib
import json
import sqlite3
from .contracts import CommunityPlan

class CommunityStore:
    def __init__(self, path: str = ":memory:") -> None:
        self._db = sqlite3.connect(path)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("CREATE TABLE IF NOT EXISTS community_plans (community_id TEXT NOT NULL, plan_id TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY (community_id, plan_id))")
        self._db.commit()

    def save(self, plan: CommunityPlan) -> str:
        payload = {"signals":[{"content_id":s.content_id,"kind":s.kind.value,"summary":s.summary,"relevance":s.relevance,"confidence":s.confidence,"evidence":list(s.evidence)} for s in plan.signals], "drafts":[{"draft_id":d.draft_id,"content_id":d.content_id,"text":d.text,"purpose":d.purpose,"evidence":list(d.evidence)} for d in plan.drafts], "next_steps":list(plan.next_steps)}
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        plan_id = hashlib.sha256((plan.community_id + "|" + encoded).encode()).hexdigest()[:32]
        self._db.execute("INSERT OR REPLACE INTO community_plans(community_id, plan_id, payload) VALUES(?,?,?)", (plan.community_id, plan_id, encoded))
        self._db.commit()
        return plan_id

    def history(self, community_id: str | None = None, limit: int = 100) -> tuple[tuple[str, str], ...]:
        if limit < 1 or limit > 1000: raise ValueError("limit is out of bounds")
        query = "SELECT plan_id, payload FROM community_plans WHERE community_id=? ORDER BY rowid DESC LIMIT ?" if community_id else "SELECT plan_id, payload FROM community_plans ORDER BY rowid DESC LIMIT ?"
        rows = self._db.execute(query, (community_id, limit) if community_id else (limit,)).fetchall()
        return tuple((str(plan_id), str(payload)) for plan_id, payload in rows)

    def close(self) -> None:
        self._db.close()
