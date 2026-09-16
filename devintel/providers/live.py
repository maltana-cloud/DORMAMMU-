"""Provider routing for live model generation and research retrieval.

Providers are replaceable capabilities. Routing never grants publication,
payment, deployment, or owner authority; callers remain responsible for
truth, permissions, and side effects.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Protocol, Sequence

from .contracts import ProviderCapability, ProviderHealth, ProviderResult


@dataclass(frozen=True)
class GenerationRequest:
    prompt: str
    system: str = ""
    model: str = ""
    temperature: float = 0.2
    max_tokens: int = 1024
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.prompt, str) or not self.prompt.strip():
            raise ValueError("prompt is required")
        if not 0.0 <= float(self.temperature) <= 2.0:
            raise ValueError("temperature must be between 0 and 2")
        if int(self.max_tokens) < 1:
            raise ValueError("max_tokens must be positive")


@dataclass(frozen=True)
class GenerationResponse:
    text: str
    provider_id: str
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("generated text is required")
        if not isinstance(self.provider_id, str) or not self.provider_id.strip():
            raise ValueError("provider_id is required")


@dataclass(frozen=True)
class ResearchRequest:
    query: str
    max_results: int = 10
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.query, str) or not self.query.strip():
            raise ValueError("query is required")
        if int(self.max_results) < 1:
            raise ValueError("max_results must be positive")


@dataclass(frozen=True)
class ResearchResult:
    url: str
    title: str = ""
    content: str = ""
    source: str = ""
    metadata: dict[str, str] = field(default_factory=dict)


class GenerationProvider(Protocol):
    provider_id: str
    def generate(self, request: GenerationRequest) -> GenerationResponse: ...
    def health(self) -> ProviderHealth: ...


class ResearchProvider(Protocol):
    provider_id: str
    def search(self, request: ResearchRequest) -> Sequence[ResearchResult]: ...
    def health(self) -> ProviderHealth: ...


@dataclass
class _ProviderSlot:
    provider: Any
    capability: ProviderCapability
    priority: int
    failures: int = 0
    disabled: bool = False


class ProviderRouter:
    """Bounded, deterministic provider router with safe fallback.

    A provider is eligible only while registered, enabled, and healthy. A
    failed provider is skipped for the remainder of the call and its failure
    counter is recorded. Routing is bounded by ``max_attempts`` and never
    treats provider output as verified truth.
    """

    def __init__(self, max_providers: int = 256, *, max_attempts: int = 3) -> None:
        if max_providers < 1:
            raise ValueError("max_providers must be positive")
        if int(max_attempts) < 1:
            raise ValueError("max_attempts must be positive")
        self._max = max_providers
        self._max_attempts = int(max_attempts)
        self._slots: dict[tuple[ProviderCapability, str], _ProviderSlot] = {}
        self._lock = RLock()

    def register(self, provider_id: str, provider: Any, capability: ProviderCapability, *, priority: int = 100) -> None:
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise ValueError("provider_id is required")
        if provider is None:
            raise ValueError("provider is required")
        if not isinstance(capability, ProviderCapability):
            raise TypeError("capability must be ProviderCapability")
        if int(priority) < 0:
            raise ValueError("priority must be nonnegative")
        if capability is ProviderCapability.GENERATION and not hasattr(provider, "generate"):
            raise TypeError("generation provider must implement generate")
        if capability is ProviderCapability.RESEARCH and not hasattr(provider, "search"):
            raise TypeError("research provider must implement search")
        if not hasattr(provider, "health"):
            raise TypeError("provider must implement health")
        actual_id = getattr(provider, "provider_id", provider_id)
        if actual_id != provider_id:
            raise ValueError("provider_id must match provider.provider_id")
        with self._lock:
            key = (capability, provider_id)
            if key not in self._slots and len(self._slots) >= self._max:
                raise RuntimeError("provider router capacity reached")
            self._slots[key] = _ProviderSlot(provider, capability, int(priority))

    def disable(self, capability: ProviderCapability, provider_id: str) -> bool:
        with self._lock:
            slot = self._slots.get((capability, provider_id))
            if slot is None:
                return False
            slot.disabled = True
            return True

    def enable(self, capability: ProviderCapability, provider_id: str) -> bool:
        with self._lock:
            slot = self._slots.get((capability, provider_id))
            if slot is None:
                return False
            slot.disabled = False
            return True

    def _candidates(self, capability: ProviderCapability) -> list[_ProviderSlot]:
        with self._lock:
            slots = [slot for (cap, _), slot in self._slots.items() if cap is capability and not slot.disabled]
            return sorted(slots, key=lambda slot: (slot.priority, slot.provider.provider_id))

    def _record_failure(self, slot: _ProviderSlot) -> None:
        with self._lock:
            slot.failures += 1

    def generate(self, request: GenerationRequest) -> ProviderResult:
        last_error = "no generation provider available"
        attempted = 0
        for slot in self._candidates(ProviderCapability.GENERATION):
            if attempted >= self._max_attempts:
                break
            attempted += 1
            try:
                health = slot.provider.health()
                if not isinstance(health, ProviderHealth):
                    raise TypeError("provider health returned invalid result")
                if health.provider_id != slot.provider.provider_id:
                    raise ValueError("provider health identity mismatch")
                if not health.healthy:
                    last_error = health.message or "provider unhealthy"
                    continue
                output = slot.provider.generate(request)
                if not isinstance(output, GenerationResponse):
                    raise TypeError("generation provider returned invalid response")
                if output.provider_id != slot.provider.provider_id:
                    raise ValueError("generation provider identity mismatch")
                return ProviderResult(slot.provider.provider_id, True, output)
            except Exception as exc:
                self._record_failure(slot)
                last_error = str(exc) or exc.__class__.__name__
                continue
        return ProviderResult("provider-router", False, error=last_error)

    def research(self, request: ResearchRequest) -> ProviderResult:
        last_error = "no research provider available"
        attempted = 0
        for slot in self._candidates(ProviderCapability.RESEARCH):
            if attempted >= self._max_attempts:
                break
            attempted += 1
            try:
                health = slot.provider.health()
                if not isinstance(health, ProviderHealth):
                    raise TypeError("provider health returned invalid result")
                if health.provider_id != slot.provider.provider_id:
                    raise ValueError("provider health identity mismatch")
                if not health.healthy:
                    last_error = health.message or "provider unhealthy"
                    continue
                output = tuple(slot.provider.search(request))
                if not all(isinstance(item, ResearchResult) for item in output):
                    raise TypeError("research provider returned invalid result")
                return ProviderResult(slot.provider.provider_id, True, output)
            except Exception as exc:
                self._record_failure(slot)
                last_error = str(exc) or exc.__class__.__name__
                continue
        return ProviderResult("provider-router", False, error=last_error)

    def status(self, capability: ProviderCapability) -> tuple[tuple[str, int, bool, int], ...]:
        with self._lock:
            return tuple(sorted(
                (slot.provider.provider_id, slot.priority, not slot.disabled, slot.failures)
                for (cap, _), slot in self._slots.items() if cap is capability
            ))
