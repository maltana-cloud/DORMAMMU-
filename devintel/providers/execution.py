"""Bounded execution facade for real provider capabilities."""
from __future__ import annotations

from dataclasses import dataclass

from .contracts import ProviderCapability, ProviderHealth, ProviderResult
from .live import GenerationRequest, ProviderRouter, ResearchRequest


@dataclass(frozen=True)
class CapabilityExecution:
    capability: ProviderCapability
    result: ProviderResult
    attempted: tuple[str, ...]


class CapabilityExecutor:
    """Execute replaceable provider capabilities without granting authority."""

    def __init__(self, router: ProviderRouter, *, max_attempts: int = 3) -> None:
        if not isinstance(router, ProviderRouter):
            raise TypeError("router must be a ProviderRouter")
        if int(max_attempts) < 1:
            raise ValueError("max_attempts must be positive")
        self.router = router
        self.max_attempts = int(max_attempts)

    def generate(self, request: GenerationRequest) -> CapabilityExecution:
        result = self.router.generate(request)
        return CapabilityExecution(ProviderCapability.GENERATION, result, (result.provider_id,))

    def research(self, request: ResearchRequest) -> CapabilityExecution:
        result = self.router.research(request)
        return CapabilityExecution(ProviderCapability.RESEARCH, result, (result.provider_id,))

    def health(self, capability: ProviderCapability) -> tuple[ProviderHealth, ...]:
        statuses = self.router.status(capability)
        return tuple(
            ProviderHealth(
                provider_id,
                enabled,
                "registered provider",
                {"priority": str(priority), "failures": str(failures)},
            )
            for provider_id, priority, enabled, failures in statuses
        )
