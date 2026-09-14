"""Stable contracts for DORMAMMU executive cognition.

These contracts separate objective understanding and task decomposition from
execution authority. They contain no provider-specific or privileged logic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol, Sequence

from ..capabilities import CapabilityRequirement, ResourceRequest
from ..core.contracts import ActionRequest


@dataclass(frozen=True)
class Objective:
    intent: str
    desired_outcome: str
    scope_id: str
    constraints: Mapping[str, str] = field(default_factory=dict)
    priority: int = 0
    objective_id: str = ""

    def __post_init__(self) -> None:
        for value, name in ((self.intent, "intent"), (self.desired_outcome, "desired_outcome"), (self.scope_id, "scope_id")):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        if not isinstance(self.priority, int):
            raise TypeError("priority must be an integer")


@dataclass(frozen=True)
class GoalUnderstanding:
    objective: Objective
    normalized_goal: str
    success_criteria: tuple[str, ...]
    constraints: Mapping[str, str] = field(default_factory=dict)
    evidence_urls: tuple[str, ...] = ()
    evidence_topic: str = ""
    evidence_uncertainty: str = ""


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    name: str
    capability: CapabilityRequirement
    action: ActionRequest
    depends_on: tuple[str, ...] = ()
    resource: ResourceRequest | None = None

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.name.strip():
            raise ValueError("task_id and name are required")
        if not isinstance(self.capability, CapabilityRequirement):
            raise TypeError("capability must be a CapabilityRequirement")
        if not isinstance(self.action, ActionRequest):
            raise TypeError("action must be an ActionRequest")
        if self.resource is not None and not isinstance(self.resource, ResourceRequest):
            raise TypeError("resource must be a ResourceRequest")


@dataclass(frozen=True)
class ExecutivePlan:
    understanding: GoalUnderstanding
    tasks: tuple[TaskSpec, ...]


class GoalInterpreter(Protocol):
    def understand(self, objective: Objective) -> GoalUnderstanding: ...


class TaskDecomposer(Protocol):
    def decompose(self, understanding: GoalUnderstanding) -> Sequence[TaskSpec]: ...
