"""Unified, read-only capability and resource discovery orchestration.

This module connects local inventory, explicitly trusted external capability
sources, capability evaluation, and resource registration without granting
authority, installing software, acquiring credentials, or spending money.
"""
from __future__ import annotations

from dataclasses import dataclass

from .contracts import CapabilityRequirement, DiscoveryResult, ResourceKind
from .discovery import CapabilityDiscovery, DefaultEvaluator, DiscoveryPolicy
from .inventory import local_capabilities, local_resources
from .registry import CapabilityRegistry, ResourceRegistry
from .resources import ResourceDecision, ResourceManager, ResourceRequest
from .sources import CapabilitySourceConfig, ConfiguredCapabilitySource


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
    ) -> None:
        self.capability_registry = capability_registry or CapabilityRegistry()
        self.resource_registry = resource_registry or ResourceRegistry(max_resources)
        self.discovery_policy = discovery_policy or DiscoveryPolicy()
        self.discovery = CapabilityDiscovery(
            registry=self.capability_registry,
            evaluator=DefaultEvaluator(self.discovery_policy),
        )
        self.resource_manager = ResourceManager(self.resource_registry)
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

    def discover(self, requirement: CapabilityRequirement, gap_id: str | None = None) -> DiscoveryResult:
        """Discover candidates through all configured scouts; no candidate is auto-activated."""
        return self.discovery.discover(requirement, gap_id)

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
