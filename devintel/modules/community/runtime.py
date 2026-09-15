"""Composition adapter connecting community intelligence to the DORMAMMU runtime."""
from __future__ import annotations
from typing import Any
from .contracts import CommunityContent, CommunityMember
from .integration import CommunityRuntimeAdapter, CommunityRun

class CommunitySubsystemIntegration:
    """Uses the host runtime only for observability; it cannot publish externally."""
    capability_id = "community.intelligence"
    def __init__(self, runtime: Any, adapter: CommunityRuntimeAdapter | None = None) -> None:
        if runtime is None or not hasattr(runtime, "record_operation_observation_from_result"):
            raise TypeError("runtime must expose operation telemetry")
        self.runtime = runtime
        self.adapter = adapter or CommunityRuntimeAdapter()

    def analyze(self, community_id: str, members: tuple[CommunityMember, ...], content: tuple[CommunityContent, ...], *, max_drafts: int = 8) -> CommunityRun:
        result = self.adapter.analyze(community_id, members, content, max_drafts=max_drafts)
        self.runtime.record_operation_observation_from_result(
            "community:" + result.stored_plan_id[:16], self.capability_id, "analyze", True, True, 0.0,
            "community observation analyzed and persisted",
        )
        return result

    def close(self) -> None:
        self.adapter.close()
