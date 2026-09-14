"""Durable store for bounded reflection evidence and proposals."""
from __future__ import annotations
import json, sqlite3
from .learning import OutcomeEvidence, LearningProposal

class LearningStore:
    def __init__(self, path: str = ":memory:") -> None:
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("CREATE TABLE IF NOT EXISTS outcome_evidence (cycle_id TEXT PRIMARY KEY, scope_id TEXT NOT NULL, success INTEGER NOT NULL, verified INTEGER NOT NULL, metric REAL NOT NULL, observation TEXT NOT NULL, recorded_at TEXT NOT NULL)")
        self.connection.execute("CREATE TABLE IF NOT EXISTS learning_proposals (id INTEGER PRIMARY KEY AUTOINCREMENT, scope_id TEXT NOT NULL, basis_cycle_ids TEXT NOT NULL, adjustment TEXT NOT NULL, expected_delta REAL NOT NULL, confidence REAL NOT NULL, reversible INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        self.connection.commit()
    def record_outcome(self, evidence: OutcomeEvidence) -> None:
        self.connection.execute("INSERT OR REPLACE INTO outcome_evidence VALUES (?,?,?,?,?,?,?)", (evidence.cycle_id,evidence.scope_id,int(evidence.success),int(evidence.verified),evidence.metric,evidence.observation,evidence.recorded_at.isoformat()))
        self.connection.commit()
    def outcomes(self, scope_id: str, limit: int = 100) -> tuple[OutcomeEvidence,...]:
        if limit <= 0: raise ValueError("limit must be positive")
        rows=self.connection.execute("SELECT cycle_id,scope_id,success,verified,metric,observation,recorded_at FROM outcome_evidence WHERE scope_id=? ORDER BY recorded_at DESC LIMIT ?",(scope_id,limit)).fetchall()
        from datetime import datetime
        return tuple(OutcomeEvidence(r[1],r[0],bool(r[2]),bool(r[3]),r[4],r[5],datetime.fromisoformat(r[6])) for r in rows)
    def record_proposal(self, proposal: LearningProposal) -> None:
        self.connection.execute("INSERT INTO learning_proposals(scope_id,basis_cycle_ids,adjustment,expected_delta,confidence,reversible) VALUES (?,?,?,?,?,?)",(proposal.scope_id,json.dumps(proposal.basis_cycle_ids),proposal.adjustment,proposal.expected_delta,proposal.confidence,int(proposal.reversible)))
        self.connection.commit()
    def proposals(self, scope_id: str, limit: int = 100) -> tuple[LearningProposal,...]:
        if limit <= 0: raise ValueError("limit must be positive")
        rows=self.connection.execute("SELECT scope_id,basis_cycle_ids,adjustment,expected_delta,confidence,reversible FROM learning_proposals WHERE scope_id=? ORDER BY id DESC LIMIT ?",(scope_id,limit)).fetchall()
        return tuple(LearningProposal(r[0],tuple(json.loads(r[1])),r[2],r[3],r[4],bool(r[5])) for r in rows)
    def close(self) -> None: self.connection.close()
