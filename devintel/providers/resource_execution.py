"""Resource-aware provider execution with bounded fallback and lease cleanup."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..capabilities.contracts import ResourceKind
from ..capabilities.resources import ResourceManager, ResourceRequest
from .contracts import ProviderCapability, ProviderResult
from .live import GenerationRequest, ResearchRequest, ProviderRouter


@dataclass(frozen=True)
class ResourceExecutionResult:
    capability: ProviderCapability
    result: ProviderResult
    resource_id: str | None
    reservation_id: str | None


class ResourceAwareProviderExecutor:
    """Reserve an admitted resource only for the provider ACT boundary.

    Resource reservation does not grant authority. Provider output remains
    untrusted and must pass the caller's verification boundary.
    """

    def __init__(self, router: ProviderRouter, resources: ResourceManager) -> None:
        if not isinstance(router, ProviderRouter):
            raise TypeError("router must be a ProviderRouter")
        if not isinstance(resources, ResourceManager):
            raise TypeError("resources must be a ResourceManager")
        self.router = router
        self.resources = resources

    def _run(self, capability: ProviderCapability, resource: ResourceRequest, call: Callable[[], ProviderResult]) -> ResourceExecutionResult:
        decision = self.resources.reserve(resource)
        if not decision.granted or not decision.reservation_id:
            return ResourceExecutionResult(capability, ProviderResult("resource-manager", False, error=decision.reason), None, None)
        reservation_id = decision.reservation_id
        try:
            result = call()
            if not isinstance(result, ProviderResult):
                result = ProviderResult("provider-router", False, error="provider executor returned invalid result")
            return ResourceExecutionResult(capability, result, decision.resource_id, reservation_id)
        finally:
            self.resources.release(reservation_id)

    def generate(self, request: GenerationRequest, *, resource_kind: ResourceKind = ResourceKind.API, quantity: float = 1.0, max_cost: float | None = None, currency: str = "USD", required_permission: str = "approved") -> ResourceExecutionResult:
        resource = ResourceRequest(resource_kind, quantity, max_cost, currency, required_permission)
        return self._run(ProviderCapability.GENERATION, resource, lambda: self.router.generate(request))

    def research(self, request: ResearchRequest, *, resource_kind: ResourceKind = ResourceKind.API, quantity: float = 1.0, max_cost: float | None = None, currency: str = "USD", required_permission: str = "approved") -> ResourceExecutionResult:
        resource = ResourceRequest(resource_kind, quantity, max_cost, currency, required_permission)
        return self._run(ProviderCapability.RESEARCH, resource, lambda: self.router.research(request))
