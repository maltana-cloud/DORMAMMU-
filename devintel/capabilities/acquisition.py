"""Bounded orchestration for discovering and safely admitting capabilities.

This layer coordinates existing discovery, evaluation, lifecycle, and canary
contracts. It never installs software, acquires credentials, spends money, or
bypasses owner/platform controls. External candidates remain untrusted until
all evaluation gates and explicit approval have passed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .canary import CanaryDecision, CanaryHealth
from .contracts import CapabilityDescriptor, CapabilityRequirement, CapabilityStatus, Evaluation
from .discovery import CapabilityDiscovery, DiscoveryResult
from .lifecycle import CapabilityLifecycle


@dataclass(frozen=True)
class AcquisitionPlan:
    """Auditable recommendation; producing a plan has no side effects."""

    requirement: CapabilityRequirement
    discovery: DiscoveryResult
    selected: Evaluation | None
    alternatives: tuple[Evaluation, ...] = ()
    reason: str = ""

    @property
    def ready_for_approval(self) -> bool:
        return self.selected is not None


class CapabilityAcquisition:
    """Coordinate the complete safe admission lifecycle for one capability gap."""

    def __init__(self, discovery: CapabilityDiscovery, lifecycle: CapabilityLifecycle) -> None:
        self.discovery = discovery
        self.lifecycle = lifecycle

    @staticmethod
    def _rank(evaluations: Sequence[Evaluation]) -> tuple[Evaluation, ...]:
        return tuple(sorted(
            (item for item in evaluations if item.eligible),
            key=lambda item: (-item.score, item.candidate.cost, item.candidate.capability_id),
        ))

    def plan(self, requirement: CapabilityRequirement, *, gap_id: str | None = None) -> AcquisitionPlan:
        result = self.discovery.discover(requirement, gap_id=gap_id)
        ranked = self._rank(result.evaluations)
        if not ranked:
            return AcquisitionPlan(requirement, result, None, (), "no candidate passed every trust, security, compatibility, performance, license, cost, and permission gate")
        return AcquisitionPlan(requirement, result, ranked[0], ranked[1:], "best eligible candidate selected; explicit approval is still required")

    def approve_and_register(self, plan: AcquisitionPlan, *, owner_approved: bool = False) -> CapabilityDescriptor:
        if not owner_approved:
            raise PermissionError("explicit owner approval is required")
        if plan.selected is None:
            raise PermissionError("no eligible capability is available")
        approved = self.lifecycle.approve(plan.selected, permission_granted=True)
        return self.lifecycle.register(approved.capability_id)

    def enter_canary(self, capability_id: str) -> CapabilityDescriptor:
        return self.lifecycle.canary(capability_id)

    def evaluate_canary(self, capability_id: str, health: CanaryHealth) -> CanaryDecision:
        from .canary import CanaryMonitor
        return CanaryMonitor(self.lifecycle).evaluate(capability_id, health)

    def fallback_plan(self, plan: AcquisitionPlan, failed_capability_id: str) -> Evaluation | None:
        """Return the next already-evaluated eligible candidate without activating it."""
        if not failed_capability_id.strip():
            raise ValueError("failed_capability_id is required")
        for candidate in plan.alternatives:
            if candidate.candidate.capability_id != failed_capability_id and candidate.eligible:
                return candidate
        return None
