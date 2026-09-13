"""Bounded resource allocation for local and registered compute resources.

Resource management is deliberately separate from capability authority. It observes
registered resources, checks declared capacity/cost/permission, and creates scoped
in-memory reservations. It never provisions machines, acquires credentials, spends
money, or bypasses platform controls.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from uuid import uuid4

from .contracts import ResourceDescriptor, ResourceKind
from .registry import ResourceRegistry


@dataclass(frozen=True)
class ResourceRequest:
    kind: ResourceKind
    quantity: float = 1.0
    max_cost: float | None = None
    currency: str = "USD"
    required_permission: str = "approved"

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.max_cost is not None and self.max_cost < 0:
            raise ValueError("max_cost must be non-negative")


@dataclass(frozen=True)
class ResourceDecision:
    granted: bool
    resource_id: str | None
    reason: str
    reservation_id: str | None = None


class ResourceManager:
    """Reserve registered resources without provisioning or authority escalation."""

    def __init__(self, registry: ResourceRegistry) -> None:
        self.registry = registry
        self._reservations: dict[str, tuple[str, float]] = {}
        self._lock = RLock()

    @staticmethod
    def _capacity(resource: ResourceDescriptor) -> float | None:
        raw = resource.metadata.get("allocatable", resource.metadata.get("bytes", ""))
        if raw:
            try:
                return float(raw)
            except ValueError:
                pass
        try:
            return float(resource.capacity)
        except (TypeError, ValueError):
            return None

    def _available(self, resource: ResourceDescriptor) -> float | None:
        capacity = self._capacity(resource)
        if capacity is None:
            return None
        used = sum(quantity for rid, quantity in self._reservations.values() if rid == resource.resource_id)
        return max(0.0, capacity - used)

    def decide(self, request: ResourceRequest) -> ResourceDecision:
        candidates: list[ResourceDescriptor] = []
        for resource in self.registry.all():
            if resource.kind is not request.kind:
                continue
            if resource.availability not in {"ready", "declared"}:
                continue
            if request.max_cost is not None and resource.currency != request.currency:
                continue
            if request.max_cost is not None and resource.cost > request.max_cost:
                continue
            if request.required_permission and request.required_permission not in resource.permissions:
                continue
            available = self._available(resource)
            if available is not None and available < request.quantity:
                continue
            candidates.append(resource)
        if not candidates:
            return ResourceDecision(False, None, "no registered resource satisfies the request")
        chosen = sorted(candidates, key=lambda item: (item.cost, item.resource_id))[0]
        return ResourceDecision(True, chosen.resource_id, "registered resource satisfies the request")

    def reserve(self, request: ResourceRequest) -> ResourceDecision:
        with self._lock:
            decision = self.decide(request)
            if not decision.granted or decision.resource_id is None:
                return decision
            reservation_id = uuid4().hex
            self._reservations[reservation_id] = (decision.resource_id, request.quantity)
            return ResourceDecision(True, decision.resource_id, "resource reserved", reservation_id)

    def release(self, reservation_id: str) -> None:
        with self._lock:
            if reservation_id not in self._reservations:
                raise KeyError(reservation_id)
            del self._reservations[reservation_id]

    def reservation(self, reservation_id: str) -> tuple[str, float] | None:
        with self._lock:
            return self._reservations.get(reservation_id)

    def active_reservations(self) -> tuple[tuple[str, str, float], ...]:
        with self._lock:
            return tuple((rid, resource_id, quantity) for rid, (resource_id, quantity) in sorted(self._reservations.items()))
