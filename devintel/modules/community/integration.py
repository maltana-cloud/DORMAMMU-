"""Runtime adapter for Category 10; analysis never becomes external authority."""
from __future__ import annotations
from dataclasses import dataclass
from .contracts import CommunityMember, CommunityContent, CommunityPlan, CommunitySignal, ResponseDraft
from .engine import CommunityIntelligence, CommunityObservation
from .persistence import CommunityStore
from .policy import CommunityPolicy

@dataclass(frozen=True)
class CommunityRun:
    observation: CommunityObservation
    plan: CommunityPlan
    stored_plan_id: str

class CommunityRuntimeAdapter:
    def __init__(self, *, store: CommunityStore | None = None, intelligence: CommunityIntelligence | None = None, policy: CommunityPolicy | None = None) -> None:
        self.store = store or CommunityStore()
        self.intelligence = intelligence or CommunityIntelligence()
        self.policy = policy or CommunityPolicy()

    def analyze(self, community_id: str, members: tuple[CommunityMember, ...], content: tuple[CommunityContent, ...], *, max_drafts: int = 8) -> CommunityRun:
        observation = self.intelligence.observe(community_id, members, content)
        plan = self.intelligence.plan(observation, max_drafts=max_drafts)
        plan_id = self.store.save(plan)
        return CommunityRun(observation, plan, plan_id)

    def publication_decision(self, signal: CommunitySignal, *, owner_approved: bool = False, platform_authorized: bool = False, publish: bool = True, is_reply: bool = True):
        return self.policy.evaluate(signal, owner_approved=owner_approved, platform_authorized=platform_authorized, publish=publish, is_reply=is_reply)

    def close(self) -> None:
        self.store.close()
