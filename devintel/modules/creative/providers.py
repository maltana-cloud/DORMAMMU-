"""Bounded provider awareness for creative work.

This registry describes available generation capabilities; it never contacts,
authenticates, provisions, pays, or publishes through a provider.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .contracts import AssetKind


@dataclass(frozen=True)
class CreativeProvider:
    provider_id: str
    name: str
    asset_kinds: tuple[AssetKind, ...]
    max_resolution: tuple[int, int] | None = None
    max_duration_seconds: int | None = None
    approved: bool = False
    available: bool = True
    trust_score: float = 0.0
    cost_class: str = "unknown"

    def __post_init__(self) -> None:
        if not self.provider_id.strip() or not self.name.strip():
            raise ValueError("provider identity is required")
        if not 0.0 <= self.trust_score <= 1.0:
            raise ValueError("trust_score must be in [0, 1]")
        if not self.asset_kinds:
            raise ValueError("provider must advertise at least one asset kind")
        if self.max_resolution is not None and any(v <= 0 for v in self.max_resolution):
            raise ValueError("resolution must be positive")
        if self.max_duration_seconds is not None and self.max_duration_seconds <= 0:
            raise ValueError("duration must be positive")


@dataclass(frozen=True)
class ProviderSelection:
    asset_kind: AssetKind
    provider_id: str | None
    reason: str
    candidates_considered: int


class CreativeProviderRegistry:
    """Small, explicit provider catalogue with fail-closed selection."""

    def __init__(self, providers: Iterable[CreativeProvider] = ()) -> None:
        self._providers: dict[str, CreativeProvider] = {}
        for provider in providers:
            self.register(provider)

    def register(self, provider: CreativeProvider) -> None:
        if provider.provider_id in self._providers:
            raise ValueError(f"provider already registered: {provider.provider_id}")
        self._providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> CreativeProvider | None:
        return self._providers.get(provider_id)

    def all(self) -> tuple[CreativeProvider, ...]:
        return tuple(self._providers.values())

    def select(self, asset_kind: AssetKind) -> ProviderSelection:
        candidates = [
            p for p in self._providers.values()
            if p.available and p.approved and asset_kind in p.asset_kinds
        ]
        candidates.sort(key=lambda p: (-p.trust_score, p.cost_class, p.provider_id))
        if not candidates:
            return ProviderSelection(asset_kind, None, "no approved available provider", 0)
        return ProviderSelection(asset_kind, candidates[0].provider_id, "highest-trust approved provider", len(candidates))
