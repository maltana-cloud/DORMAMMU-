"""Unified, bounded capability/resource discovery and safe admission orchestration.

This module connects local inventory, explicitly trusted external capability
sources, capability evaluation, resource registration, approval, lifecycle,
and canary controls without granting authority, installing software, acquiring
credentials, or spending money.
"""
from __future__ import annotations

from dataclasses import dataclass

from .acquisition import AcquisitionPlan, CapabilityAcquisition
from .canary import CanaryDecision, CanaryHealth, CanaryPolicy
from .contracts import CapabilityDescriptor, CapabilityRequirement, ResourceKind
from .discovery import CapabilityDiscovery, DefaultEvaluator, DiscoveryPolicy
from .inventory import local_capabilities, local_resources
from .lifecycle import CapabilityLifecycle
from .registry import CapabilityRegistry, ResourceRegistry
from .resources import ResourceDecision, ResourceManager, ResourceRequest
from .sources import CapabilitySourceConfig, ConfiguredCapabilitySource
from .store import LifecycleStore


@dataclass(frozen=True)
class DiscoverySnapshot:
    """Bounded observation of available capabilities and resources."""

    capabilities: tuple[str, ...]
    resources: tuple[str, ...]
    enabled_sources: tuple[str, ...]


class CapabilityResourceDiscoveryEngine:
    """Connect discovery inputs to the existing trust and resource control plane."""

    def __init__(
        self,
        *,
        capability_registry: CapabilityRegistry | None = None,
        resource_registry: ResourceRegistry | None = None,
        discovery_policy: DiscoveryPolicy | None = None,
        max_resources: int = 512,
        lifecycle_store: LifecycleStore | None = None,
        canary_policy: CanaryPolicy | None = None,
    ) -> None:
        self.capability_registry = capability_registry or CapabilityRegistry()
        self.resource_registry = resource_registry or ResourceRegistry(max_resources)
        self.discovery_policy = discovery_policy or DiscoveryPolicy()
        self.discovery = CapabilityDiscovery(
            registry=self.capability_registry,
            evaluator=DefaultEvaluator(self.discovery_policy),
        )
        self.resource_manager = ResourceManager(self.resource_registry)
        self.lifecycle_store = lifecycle_store
        self.lifecycle = CapabilityLifecycle(
            self.capability_registry,
            recorder=self.lifecycle_store.record if self.lifecycle_store else None,
        )
        self.acquisition = CapabilityAcquisition(self.discovery, self.lifecycle)
        self.canary_policy = canary_policy or CanaryPolicy()
        self._source_ids: list[str] = []

    def refresh_local_inventory(self) -> DiscoverySnapshot:
        """Register only read-only local observations; never provisions anything."""
        for capability in local_capabilities():
            self.capability_registry.register(capability)
        for resource in local_resources():
            self.resource_registry.register(resource)
        return self.snapshot()

    def add_source(self, config: CapabilitySourceConfig) -> None:
        source = ConfiguredCapabilitySource(config, discovery_policy=self.discovery_policy)
        self.discovery.add_scout(source)
        if config.source_id not in self._source_ids:
            self._source_ids.append(config.source_id)

    def discover(self, requirement: CapabilityRequirement, gap_id: str | None = None):
        """Discover candidates through all configured scouts; no candidate is auto-activated."""
        return self.discovery.discover(requirement, gap_id)

    def plan_acquisition(self, requirement: CapabilityRequirement, gap_id: str | None = None) -> AcquisitionPlan:
        """Build an auditable admission plan; this has no side effects beyond gap recording."""
        return self.acquisition.plan(requirement, gap_id=gap_id)

    def approve_and_register(self, plan: AcquisitionPlan, *, owner_approved: bool = False) -> CapabilityDescriptor:
        """Admit a selected capability only after explicit owner approval."""
        return self.acquisition.approve_and_register(plan, owner_approved=owner_approved)

    def enter_canary(self, capability_id: str) -> CapabilityDescriptor:
        return self.acquisition.enter_canary(capability_id)

    def evaluate_canary(self, capability_id: str, health: CanaryHealth) -> CanaryDecision:
        from .canary import CanaryMonitor
        return CanaryMonitor(self.lifecycle, self.canary_policy).evaluate(capability_id, health)

    def fallback(self, plan: AcquisitionPlan, failed_capability_id: str):
        """Return the next already-evaluated eligible candidate without activating it."""
        return self.acquisition.fallback_plan(plan, failed_capability_id)

    def snapshot(self) -> DiscoverySnapshot:
        return DiscoverySnapshot(
            capabilities=self.capability_registry.ids(),
            resources=tuple(sorted(item.resource_id for item in self.resource_registry.all())),
            enabled_sources=tuple(sorted(self._source_ids)),
        )

    def decide_resource(self, kind: ResourceKind, quantity: float = 1.0, *, max_cost: float | None = None) -> ResourceDecision:
        return self.resource_manager.decide(ResourceRequest(kind, quantity, max_cost=max_cost))

    def reserve_resource(self, kind: ResourceKind, quantity: float = 1.0, *, max_cost: float | None = None) -> ResourceDecision:
        return self.resource_manager.reserve(ResourceRequest(kind, quantity, max_cost=max_cost))

    def release_resource(self, reservation_id: str) -> None:
        self.resource_manager.release(reservation_id)

    def close(self) -> None:
        self.resource_manager.close()
        if self.lifecycle_store:
            self.lifecycle_store.close()
