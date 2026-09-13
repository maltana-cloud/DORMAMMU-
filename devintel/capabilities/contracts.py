"""Contracts for DORMAMMU capability and resource discovery.

Discovery produces candidates and evaluations; it never grants authority or installs
anything. External candidates remain untrusted until they pass explicit gates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Protocol, Sequence


class CapabilityStatus(str, Enum):
    PLANNED = "planned"
    DISCOVERED = "discovered"
    EVALUATED = "evaluated"
    APPROVED = "approved"
    REGISTERED = "registered"
    CANARY = "canary"
    ACTIVE = "active"
    DEGRADED = "degraded"
    ROLLED_BACK = "rolled_back"
    RETIRED = "retired"


class ResourceKind(str, Enum):
    MODEL = "model"
    API = "api"
    TOOL = "tool"
    DATASET = "dataset"
    CPU = "cpu"
    GPU = "gpu"
    STORAGE = "storage"
    BROWSER = "browser"
    PLATFORM = "platform"
    OTHER = "other"


@dataclass(frozen=True)
class CapabilityRequirement:
    capability_id: str
    purpose: str
    required_interfaces: tuple[str, ...] = ()
    preferred_version: str = ""
    max_cost: float | None = None
    currency: str = "USD"
    required_license: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.capability_id.strip():
            raise ValueError("capability_id is required")
        if not self.purpose.strip():
            raise ValueError("purpose is required")
        if self.max_cost is not None and self.max_cost < 0:
            raise ValueError("max_cost must be non-negative")


@dataclass(frozen=True)
class CapabilityGap:
    gap_id: str
    requirement: CapabilityRequirement
    detected_at: str
    blocking: bool = True
    notes: str = ""


@dataclass(frozen=True)
class CapabilityDescriptor:
    capability_id: str
    name: str
    version: str
    interfaces: tuple[str, ...]
    provider: str
    license: str
    status: CapabilityStatus = CapabilityStatus.DISCOVERED
    cost: float = 0.0
    currency: str = "USD"
    permissions: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for value, field_name in ((self.capability_id, "capability_id"), (self.name, "name"), (self.version, "version"), (self.provider, "provider"), (self.license, "license")):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} is required")
        if self.cost < 0:
            raise ValueError("cost must be non-negative")


@dataclass(frozen=True)
class ResourceDescriptor:
    resource_id: str
    kind: ResourceKind
    name: str
    version: str = ""
    capacity: str = ""
    availability: str = "unknown"
    cost: float = 0.0
    currency: str = "USD"
    permissions: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.resource_id.strip() or not self.name.strip():
            raise ValueError("resource_id and name are required")
        if self.cost < 0:
            raise ValueError("cost must be non-negative")


@dataclass(frozen=True)
class Evaluation:
    candidate: CapabilityDescriptor
    trust_ok: bool
    security_ok: bool
    compatibility_ok: bool
    performance_ok: bool
    license_ok: bool
    cost_ok: bool
    permission_ok: bool
    score: float
    reasons: tuple[str, ...] = ()

    @property
    def eligible(self) -> bool:
        return all((self.trust_ok, self.security_ok, self.compatibility_ok, self.performance_ok, self.license_ok, self.cost_ok, self.permission_ok))


@dataclass(frozen=True)
class DiscoveryResult:
    gap: CapabilityGap
    candidates: tuple[CapabilityDescriptor, ...]
    evaluations: tuple[Evaluation, ...]


class CapabilityScout(Protocol):
    def discover(self, requirement: CapabilityRequirement) -> Sequence[CapabilityDescriptor]: ...


class CandidateEvaluator(Protocol):
    def evaluate(self, requirement: CapabilityRequirement, candidate: CapabilityDescriptor) -> Evaluation: ...
