"""Bounded durable storage for advisory business plans."""
from __future__ import annotations
import sqlite3
from .contracts import BusinessPlan,digest_plan
class EconomicPlanStore:
    def __init__(self,path=":memory:"):
        self.db=sqlite3.connect(path); self.db.execute("PRAGMA journal_mode=WAL"); self.db.execute("CREATE TABLE IF NOT EXISTS plans (id TEXT PRIMARY KEY, digest TEXT NOT NULL, payload TEXT NOT NULL)"); self.db.commit()
    def save(self,plan:BusinessPlan)->str:
        d=digest_plan(plan); payload=repr(plan)
        self.db.execute("INSERT OR REPLACE INTO plans VALUES (?,?,?)",(plan.plan_id,d,payload)); self.db.commit(); return d
    def get_digest(self,plan_id:str)->str|None:
        row=self.db.execute("SELECT digest FROM plans WHERE id=?",(plan_id,)).fetchone(); return row[0] if row else None
    def count(self)->int:return int(self.db.execute("SELECT COUNT(*) FROM plans").fetchone()[0])
    def close(self):self.db.close()
