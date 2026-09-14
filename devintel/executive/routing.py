"""Bounded model/agent/specialist selection and collaboration planning.

Routing is advisory: selection never grants permission, credentials, spending,
or authority. Callers must pass the selected capability through the existing
permission and execution boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Sequence


class SpecialistKind(str, Enum):
    MODEL = "model"
    AGENT = "agent"
    SPECIALIST = "specialist"


@dataclass(frozen=True)
class RoutingRequirement:
    """Requirements used to select an already-admitted intelligence capability."""

    purpose: str
    required_skills: tuple[str, ...] = ()
    preferred_provider: str = ""
    preferred_version: str = ""
    max_cost: float | None = None
    required_metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.purpose, str) or not self.purpose.strip():
            raise ValueError("purpose is required")
        if self.max_cost is not None and self.max_cost < 0:
            raise ValueError("max_cost must be non-negative")


@dataclass(frozen=True)
class SpecialistDescriptor:
    """Host-registered specialist metadata; it is not an authority grant."""

    specialist_id: str
    kind: SpecialistKind
    provider: str
    version: str
    skills: tuple[str, ...] = ()
    cost: float = 0.0
    metadata: Mapping[str, str] = field(default_factory=dict)
    healthy: bool = True
    approved: bool = True

    def __post_init__(self) -> None:
        for value, name in ((self.specialist_id, "specialist_id"), (self.provider, "provider"), (self.version, "version")):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        if self.cost < 0:
            raise ValueError("cost must be non-negative")
        if not isinstance(self.healthy, bool) or not isinstance(self.approved, bool):
            raise TypeError("healthy and approved must be bools")


@dataclass(frozen=True)
class RouteCandidate:
    specialist: SpecialistDescriptor
    score: float
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class CollaborationStep:
    step_id: str
    specialist_id: str
    purpose: str
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class CollaborationPlan:
    steps: tuple[CollaborationStep, ...]
    fallback_by_step: Mapping[str, tuple[str, ...]] = field(default_factory=dict)


class SpecialistRouter:
    """Deterministic, bounded router for already-registered specialists."""

    def __init__(self, max_specialists: int = 256) -> None:
        if max_specialists <= 0:
            raise ValueError("max_specialists must be positive")
        self._max = max_specialists
        self._items: dict[str, SpecialistDescriptor] = {}

    def register(self, specialist: SpecialistDescriptor) -> None:
        if not isinstance(specialist, SpecialistDescriptor):
            raise TypeError("specialist must be a SpecialistDescriptor")
        if specialist.specialist_id not in self._items and len(self._items) >= self._max:
            raise RuntimeError("specialist router capacity reached")
        self._items[specialist.specialist_id] = specialist

    def get(self, specialist_id: str) -> SpecialistDescriptor | None:
        return self._items.get(specialist_id)

    def rank(self, requirement: RoutingRequirement) -> tuple[RouteCandidate, ...]:
        candidates: list[RouteCandidate] = []
        required = {skill.strip().lower() for skill in requirement.required_skills if skill.strip()}
        for specialist in self._items.values():
            if not specialist.healthy or not specialist.approved:
                continue
            if requirement.max_cost is not None and specialist.cost > requirement.max_cost:
                continue
            if any(specialist.metadata.get(key) != value for key, value in requirement.required_metadata.items()):
                continue
            skills = {skill.strip().lower() for skill in specialist.skills}
            matched = len(required & skills)
            if required and matched != len(required):
                continue
            score = float(matched * 100)
            reasons = [f"matched {matched} required skill(s)"]
            if requirement.preferred_provider and specialist.provider == requirement.preferred_provider:
                score += 20
                reasons.append("preferred provider")
            if requirement.preferred_version and specialist.version == requirement.preferred_version:
                score += 10
                reasons.append("preferred version")
            score -= specialist.cost
            candidates.append(RouteCandidate(specialist, score, tuple(reasons)))
        return tuple(sorted(candidates, key=lambda item: (-item.score, item.specialist.specialist_id)))

    def select(self, requirement: RoutingRequirement) -> RouteCandidate:
        ranked = self.rank(requirement)
        if not ranked:
            raise LookupError("no eligible specialist satisfies routing requirements")
        return ranked[0]

    def plan_collaboration(self, steps: Sequence[tuple[str, RoutingRequirement]]) -> CollaborationPlan:
        if not steps:
            raise ValueError("collaboration steps are required")
        chosen: list[CollaborationStep] = []
        fallback: dict[str, tuple[str, ...]] = {}
        previous: str | None = None
        for index, (purpose, requirement) in enumerate(steps, 1):
            candidate = self.select(requirement)
            step_id = f"step-{index}"
            deps = (previous,) if previous else ()
            chosen.append(CollaborationStep(step_id, candidate.specialist.specialist_id, purpose, deps))
            fallback[step_id] = tuple(item.specialist.specialist_id for item in self.rank(requirement)[1:])
            previous = step_id
        return CollaborationPlan(tuple(chosen), fallback)
