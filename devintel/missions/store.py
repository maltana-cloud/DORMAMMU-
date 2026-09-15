"""Durable mission state with explicit bounded lifecycle transitions."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import json
import sqlite3
from typing import Any, Mapping
from uuid import uuid4
from .coordination import MissionLease

def _now() -> str: return datetime.now(timezone.utc).isoformat()

class MissionStatus(StrEnum):
    QUEUED="queued"; RUNNING="running"; PAUSED="paused"; SUCCEEDED="succeeded"; FAILED="failed"; CANCELLED="cancelled"

@dataclass(frozen=True)
class Mission:
    mission_id:str; scope_id:str; objective:str; total_steps:int; current_step:int; status:MissionStatus; attempts:int; max_attempts:int; next_run_at:float; created_at:str; updated_at:str; last_error:str=""

@dataclass(frozen=True)
class MissionStep:
    step_id:str; name:str; payload:Mapping[str,object]|None=None
    def __post_init__(self)->None:
        if not self.step_id.strip() or not self.name.strip(): raise ValueError("step_id and name are required")
        if self.payload is None: object.__setattr__(self,"payload",{})
        if len(self.payload or {})>64: raise ValueError("step payload has too many fields")

@dataclass(frozen=True)
class MissionStepRecord:
    mission_id:str; step_index:int; step:MissionStep; completed:bool; verified:bool; message:str=""; data:Mapping[str,object]|None=None; recorded_at:str=""

class MissionStore:
    """SQLite-backed mission checkpoints, leases, and verified step journal."""
    def __init__(self,path:str=":memory:")->None:
        self._db=sqlite3.connect(path,isolation_level=None); self._db.row_factory=sqlite3.Row
        self._db.execute("PRAGMA foreign_keys=ON"); self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("""CREATE TABLE IF NOT EXISTS missions (mission_id TEXT PRIMARY KEY, scope_id TEXT NOT NULL, objective TEXT NOT NULL, total_steps INTEGER NOT NULL, current_step INTEGER NOT NULL, status TEXT NOT NULL, attempts INTEGER NOT NULL, max_attempts INTEGER NOT NULL, next_run_at REAL NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, last_error TEXT NOT NULL, lease_worker_id TEXT, lease_expires_at REAL)""")
        self._db.execute("""CREATE TABLE IF NOT EXISTS mission_steps (mission_id TEXT NOT NULL, step_index INTEGER NOT NULL, step_id TEXT NOT NULL, name TEXT NOT NULL, payload TEXT NOT NULL, completed INTEGER NOT NULL DEFAULT 0, verified INTEGER NOT NULL DEFAULT 0, message TEXT NOT NULL DEFAULT '', data TEXT NOT NULL DEFAULT '{}', recorded_at TEXT NOT NULL, PRIMARY KEY (mission_id, step_index), UNIQUE (mission_id, step_id), FOREIGN KEY (mission_id) REFERENCES missions(mission_id) ON DELETE CASCADE)""")
        self._db.execute("CREATE INDEX IF NOT EXISTS idx_missions_due ON missions(status,next_run_at,created_at,mission_id)"); self._db.execute("CREATE INDEX IF NOT EXISTS idx_missions_lease ON missions(lease_worker_id,lease_expires_at)")
    def create(self,scope_id:str,objective:str,total_steps:int,*,max_attempts:int=3,mission_id:str|None=None,now:float=0.0)->Mission:
        if not isinstance(scope_id,str) or not scope_id.strip() or not isinstance(objective,str) or not objective.strip(): raise ValueError("scope_id and objective are required")
        if total_steps<=0 or max_attempts<=0 or now<0: raise ValueError("invalid mission bounds")
        created=_now(); m=Mission(mission_id or uuid4().hex,scope_id.strip(),objective.strip(),total_steps,0,MissionStatus.QUEUED,0,max_attempts,now,created,created)
        self._db.execute("INSERT INTO missions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(m.mission_id,m.scope_id,m.objective,m.total_steps,m.current_step,m.status,m.attempts,m.max_attempts,m.next_run_at,m.created_at,m.updated_at,m.last_error,None,None)); return m
    def get(self,mission_id:str)->Mission|None:
        r=self._db.execute("SELECT * FROM missions WHERE mission_id=?",(mission_id,)).fetchone(); return self._from_row(r) if r else None
    def define_steps(self,mission_id:str,steps:tuple[MissionStep,...])->tuple[MissionStepRecord,...]:
        m=self._require(mission_id)
        if len(steps)!=m.total_steps or len({s.step_id for s in steps})!=len(steps): raise ValueError("step count must equal total_steps and step ids must be unique")
        if self._db.execute("SELECT COUNT(*) FROM mission_steps WHERE mission_id=?",(mission_id,)).fetchone()[0]: raise ValueError("mission steps are already defined")
        t=_now(); self._db.executemany("INSERT INTO mission_steps VALUES (?,?,?,?,?,?,?,?,?,?)",[(mission_id,i,s.step_id,s.name,json.dumps(dict(s.payload or {}),sort_keys=True),0,0,"","{}",t) for i,s in enumerate(steps)]); return self.steps(mission_id)
    def steps(self,mission_id:str)->tuple[MissionStepRecord,...]:
        self._require(mission_id); rows=self._db.execute("SELECT * FROM mission_steps WHERE mission_id=? ORDER BY step_index",(mission_id,)).fetchall(); return tuple(MissionStepRecord(r["mission_id"],r["step_index"],MissionStep(r["step_id"],r["name"],json.loads(r["payload"])),bool(r["completed"]),bool(r["verified"]),r["message"],json.loads(r["data"]),r["recorded_at"]) for r in rows)
    def record_step(self,mission_id:str,step_index:int,*,verified:bool,message:str="",data:Mapping[str,object]|None=None)->MissionStepRecord:
        m=self._require_running(mission_id)
        if not 0<=step_index<m.total_steps or len(message)>2000: raise ValueError("invalid step record")
        r=self._db.execute("SELECT * FROM mission_steps WHERE mission_id=? AND step_index=?",(mission_id,step_index)).fetchone()
        if r is None or r["completed"]: raise ValueError("mission step is undefined or already completed")
        self._db.execute("UPDATE mission_steps SET completed=1,verified=?,message=?,data=?,recorded_at=? WHERE mission_id=? AND step_index=?",(int(verified),message,json.dumps(dict(data or {}),sort_keys=True),_now(),mission_id,step_index)); return self.steps(mission_id)[step_index]
    def claim_due(self,*,now:float,scope_id:str|None=None,worker_id:str|None=None,lease_ttl_seconds:float|None=None)->Mission|None:
        if now<0: raise ValueError("now must be non-negative")
        if (worker_id is None)!=(lease_ttl_seconds is None): raise ValueError("worker_id and lease_ttl_seconds must be supplied together")
        if worker_id is not None and (not worker_id.strip() or lease_ttl_seconds is None or lease_ttl_seconds<=0): raise ValueError("invalid worker lease")
        q="SELECT mission_id FROM missions WHERE status IN ('queued','running') AND next_run_at<=? AND (lease_expires_at IS NULL OR lease_expires_at<=?)"; a:list[Any]=[now,now]
        if scope_id is not None:q+=" AND scope_id=?";a.append(scope_id)
        r=self._db.execute(q+" ORDER BY next_run_at,created_at,mission_id LIMIT 1",a).fetchone()
        if r is None:return None
        if worker_id is None:u=self._db.execute("UPDATE missions SET status='running',attempts=attempts+1,lease_worker_id=NULL,lease_expires_at=NULL,updated_at=? WHERE mission_id=? AND status IN ('queued','running') AND next_run_at<=? AND (lease_expires_at IS NULL OR lease_expires_at<=?)",(_now(),r["mission_id"],now,now))
        else:u=self._db.execute("UPDATE missions SET status='running',attempts=attempts+1,lease_worker_id=?,lease_expires_at=?,updated_at=? WHERE mission_id=? AND status IN ('queued','running') AND next_run_at<=? AND (lease_expires_at IS NULL OR lease_expires_at<=?)",(worker_id.strip(),now+float(lease_ttl_seconds),_now(),r["mission_id"],now,now))
        return self.get(r["mission_id"]) if u.rowcount==1 else None
    def renew_lease(self,mission_id:str,*,worker_id:str,now:float,lease_ttl_seconds:float)->MissionLease:
        if not worker_id.strip() or now<0 or lease_ttl_seconds<=0: raise ValueError("invalid lease timing")
        u=self._db.execute("UPDATE missions SET lease_expires_at=?,updated_at=? WHERE mission_id=? AND status='running' AND lease_worker_id=? AND lease_expires_at>?",(now+lease_ttl_seconds,_now(),mission_id,worker_id.strip(),now))
        if u.rowcount!=1: raise ValueError("active lease is not owned by worker")
        return MissionLease(mission_id,worker_id.strip(),now+lease_ttl_seconds)
    def checkpoint(self,mission_id:str,*,current_step:int,now:float,worker_id:str|None=None)->Mission:
        m=self._require_running(mission_id)
        if now<0 or not 0<=current_step<=m.total_steps: raise ValueError("invalid checkpoint")
        defined=self._db.execute("SELECT COUNT(*) FROM mission_steps WHERE mission_id=?",(mission_id,)).fetchone()[0]
        if defined and current_step and self._db.execute("SELECT COUNT(*) FROM mission_steps WHERE mission_id=? AND completed=1 AND verified=1 AND step_index<?",(mission_id,current_step)).fetchone()[0]!=current_step: raise ValueError("checkpoint requires verified prior steps")
        status=MissionStatus.SUCCEEDED if current_step==m.total_steps else MissionStatus.QUEUED
        if worker_id is None:sql="UPDATE missions SET status=?,current_step=?,next_run_at=?,updated_at=?,last_error='',lease_worker_id=NULL,lease_expires_at=NULL WHERE mission_id=? AND status='running'";args=(status,current_step,now,_now(),mission_id)
        else:
            if not worker_id.strip():raise ValueError("worker_id is required")
            sql="UPDATE missions SET status=?,current_step=?,next_run_at=?,updated_at=?,last_error='',lease_worker_id=NULL,lease_expires_at=NULL WHERE mission_id=? AND status='running' AND lease_worker_id=?";args=(status,current_step,now,_now(),mission_id,worker_id.strip())
        if self._db.execute(sql,args).rowcount!=1:raise ValueError("active lease is not owned by worker")
        return self._require(mission_id)
    def fail(self,mission_id:str,error:str,*,now:float,backoff_seconds:float=0.0,worker_id:str|None=None)->Mission:
        m=self._require_running(mission_id)
        if now<0 or not error.strip() or backoff_seconds<0:raise ValueError("invalid failure inputs")
        status=MissionStatus.FAILED if m.attempts>=m.max_attempts else MissionStatus.QUEUED; nxt=now+backoff_seconds if status is MissionStatus.QUEUED else now; owner=" AND lease_worker_id=?" if worker_id is not None else "";args:list[Any]=[status,nxt,_now(),error[:2000],mission_id]
        if worker_id is not None:args.append(worker_id.strip())
        if self._db.execute(f"UPDATE missions SET status=?,next_run_at=?,updated_at=?,last_error=?,lease_worker_id=NULL,lease_expires_at=NULL WHERE mission_id=? AND status='running'{owner}",args).rowcount!=1:raise ValueError("active lease is not owned by worker")
        return self._require(mission_id)
    def pause(self,mission_id:str)->Mission:self._require_running(mission_id);self._db.execute("UPDATE missions SET status='paused',lease_worker_id=NULL,lease_expires_at=NULL,updated_at=? WHERE mission_id=? AND status='running'",(_now(),mission_id));return self._require(mission_id)
    def resume(self,mission_id:str,*,now:float)->Mission:
        m=self._require(mission_id)
        if m.status is not MissionStatus.PAUSED or now<0:raise ValueError("only paused missions can be resumed")
        self._db.execute("UPDATE missions SET status='queued',next_run_at=?,updated_at=?,last_error='',lease_worker_id=NULL,lease_expires_at=NULL WHERE mission_id=?",(now,_now(),mission_id));return self._require(mission_id)
    def cancel(self,mission_id:str)->Mission:
        m=self._require(mission_id)
        if m.status in (MissionStatus.SUCCEEDED,MissionStatus.CANCELLED):raise ValueError("mission is already terminal")
        self._db.execute("UPDATE missions SET status='cancelled',lease_worker_id=NULL,lease_expires_at=NULL,updated_at=? WHERE mission_id=?",(_now(),mission_id));return self._require(mission_id)
    def recover_running(self,*,now:float)->tuple[Mission,...]:
        if now<0:raise ValueError("now must be non-negative")
        rows=self._db.execute("SELECT mission_id FROM missions WHERE status='running' ORDER BY created_at,mission_id").fetchall();self._db.execute("UPDATE missions SET status='queued',next_run_at=?,lease_worker_id=NULL,lease_expires_at=NULL,updated_at=? WHERE status='running'",(now,_now()));return tuple(self._require(r["mission_id"]) for r in rows)
    def close(self)->None:self._db.close()
    def _require(self,mission_id:str)->Mission:
        m=self.get(mission_id)
        if m is None:raise KeyError(mission_id)
        return m
    def _require_running(self,mission_id:str)->Mission:
        m=self._require(mission_id)
        if m.status is not MissionStatus.RUNNING:raise ValueError("mission is not running")
        return m
    @staticmethod
    def _from_row(row:sqlite3.Row)->Mission:return Mission(row["mission_id"],row["scope_id"],row["objective"],row["total_steps"],row["current_step"],MissionStatus(row["status"]),row["attempts"],row["max_attempts"],row["next_run_at"],row["created_at"],row["updated_at"],row["last_error"])
