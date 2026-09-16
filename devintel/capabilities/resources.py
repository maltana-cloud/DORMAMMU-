"""Bounded resource allocation and resource/compute intelligence.

Resource management is deliberately separate from capability authority. It observes
registered resources, checks declared capacity/cost/permission, and creates scoped
SQLite-backed reservations. It never provisions machines, acquires credentials,
spends money, or bypasses platform controls.
"""
from __future__ import annotations
from dataclasses import dataclass
from .contracts import ResourceDescriptor, ResourceKind
from .leases import ResourceLeaseStore
from .registry import ResourceRegistry

@dataclass(frozen=True)
class ResourceRequest:
    kind: ResourceKind
    quantity: float = 1.0
    max_cost: float | None = None
    currency: str = "USD"
    required_permission: str = "approved"
    ttl_seconds: float = 300.0
    def __post_init__(self) -> None:
        if self.quantity <= 0: raise ValueError("quantity must be positive")
        if self.max_cost is not None and self.max_cost < 0: raise ValueError("max_cost must be non-negative")
        if self.ttl_seconds <= 0: raise ValueError("ttl_seconds must be positive")

@dataclass(frozen=True)
class ResourceDecision:
    granted: bool
    resource_id: str | None
    reason: str
    reservation_id: str | None = None

@dataclass(frozen=True)
class ResourceSnapshot:
    resource_id: str
    kind: ResourceKind
    availability: str
    capacity: float | None
    allocated: float
    available: float | None
    cost: float
    currency: str
    permissions: tuple[str, ...]

class ResourceManager:
    """Reserve registered resources through durable, expiring leases."""
    def __init__(self, registry: ResourceRegistry, lease_store: ResourceLeaseStore | None = None) -> None:
        self.registry = registry
        self.lease_store = lease_store or ResourceLeaseStore()
    @staticmethod
    def _capacity(resource: ResourceDescriptor) -> float | None:
        raw = resource.metadata.get("allocatable", resource.metadata.get("bytes", ""))
        if raw:
            try: return float(raw)
            except (TypeError, ValueError): pass
        try: return float(resource.capacity)
        except (TypeError, ValueError): return None
    def _eligible(self, resource: ResourceDescriptor, request: ResourceRequest) -> bool:
        return (resource.kind is request.kind and resource.availability in {"ready", "declared"}
                and (request.max_cost is None or (resource.currency == request.currency and resource.cost <= request.max_cost))
                and (not request.required_permission or request.required_permission in resource.permissions))
    def _available(self, resource: ResourceDescriptor) -> float | None:
        capacity = self._capacity(resource)
        return None if capacity is None else max(0.0, capacity - self.lease_store.active_quantity(resource.resource_id))
    def snapshots(self) -> tuple[ResourceSnapshot, ...]:
        """Return deterministic resource intelligence without creating leases."""
        rows = []
        for resource in self.registry.all():
            capacity = self._capacity(resource)
            allocated = self.lease_store.active_quantity(resource.resource_id)
            available = None if capacity is None else max(0.0, capacity - allocated)
            rows.append(ResourceSnapshot(resource.resource_id, resource.kind, resource.availability, capacity, allocated, available, resource.cost, resource.currency, tuple(resource.permissions)))
        return tuple(sorted(rows, key=lambda item: (item.kind.value, item.cost, item.resource_id)))
    def decide(self, request: ResourceRequest) -> ResourceDecision:
        candidates = []
        for resource in self.registry.all():
            if not self._eligible(resource, request): continue
            available = self._available(resource)
            if available is None or available < request.quantity: continue
            candidates.append(resource)
        if not candidates: return ResourceDecision(False, None, "no registered resource with known sufficient capacity satisfies the request")
        chosen = sorted(candidates, key=lambda item: (item.cost, item.resource_id))[0]
        return ResourceDecision(True, chosen.resource_id, "registered resource satisfies the request")
    def reserve(self, request: ResourceRequest) -> ResourceDecision:
        candidates = [r for r in self.registry.all() if self._eligible(r, request)]
        for resource in sorted(candidates, key=lambda item: (item.cost, item.resource_id)):
            capacity = self._capacity(resource)
            if capacity is None: continue
            lease = self.lease_store.acquire(resource.resource_id, request.quantity, capacity, ttl_seconds=request.ttl_seconds)
            if lease is not None: return ResourceDecision(True, resource.resource_id, "resource reserved with durable lease", lease.lease_id)
        return ResourceDecision(False, None, "no registered resource with known sufficient capacity satisfies the request")
    def release(self, reservation_id: str) -> None: self.lease_store.release(reservation_id)
    def reservation(self, reservation_id: str):
        lease = self.lease_store.get(reservation_id)
        return None if lease is None else (lease.resource_id, lease.quantity)
    def active_reservations(self) -> tuple[tuple[str, str, float], ...]:
        return tuple((lease.lease_id, lease.resource_id, lease.quantity) for lease in self.lease_store.active())
    def close(self) -> None: self.lease_store.close()
