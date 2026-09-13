"""Observation-driven capability planning without autonomous authority escalation."""
from __future__ import annotations

from dataclasses import dataclass
from .contracts import CapabilityDescriptor, CapabilityRequirement, DiscoveryResult
from .discovery import CapabilityDiscovery
from .registry import CapabilityRegistry


@dataclass(frozen=True)
class CapabilityDecision:
    """Advisory decision; execution remains behind normal permission gates."""

    requirement: CapabilityRequirement
    action: str
    capability_id: str | None = None
    discovery: DiscoveryResult | None = None
    reason: str = ""


class CapabilityDecisionEngine:
    """Turn an observed requirement into a bounded, auditable next step."""

    def __init__(self, registry: CapabilityRegistry, discovery: CapabilityDiscovery) -> None:
        self.registry = registry
        self.discovery = discovery

    def decide(self, requirement: CapabilityRequirement) -> CapabilityDecision:
        matches: list[CapabilityDescriptor] = []
        required = set(requirement.required_interfaces)
        for capability_id in self.registry.ids():
            candidate = self.registry.get(capability_id)
            if candidate is None:
                continue
            if required.issubset(candidate.interfaces) and candidate.status.value == "active":
                matches.append(candidate)
        if matches:
            chosen = sorted(matches, key=lambda item: (item.cost, item.capability_id))[0]
            return CapabilityDecision(requirement, "use_existing", chosen.capability_id, reason="active compatible capability exists")
        result = self.discovery.discover(requirement)
        if result.evaluations:
            eligible = [item for item in result.evaluations if item.eligible]
            if eligible:
                best = max(eligible, key=lambda item: item.score)
                return CapabilityDecision(requirement, "request_approval", best.candidate.capability_id, result, "eligible candidate requires explicit lifecycle approval")
        return CapabilityDecision(requirement, "record_gap", discovery=result, reason="no eligible capability is currently available")
