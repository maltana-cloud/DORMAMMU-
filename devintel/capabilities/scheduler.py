"""Bounded capability/resource scheduling with deterministic fallback.

Scheduling selects already-discovered eligible capabilities and registered
resources. Planning is side-effect free; resource reservations happen only
through explicit admission. It does not install software, acquire credentials,
spend money, or invoke external providers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .contracts import CapabilityDescriptor, CapabilityRequirement, Evaluation, ResourceKind
from .engine import CapabilityResourceDiscoveryEngine

_MAX_ATTEMPTS = 16


@dataclass(frozen=True)
class CapabilityResourceCandidate:
    capability: CapabilityDescriptor
    evaluation: Evaluation
    resource_kind: ResourceKind


@dataclass(frozen=True)
class CapabilityResourcePlan:
    requirement: CapabilityRequirement
    selected_capability_id: str | None
    selected_resource_id: str | None
    reservation_id: str | None
    attempts: tuple[str, ...]
    reason: str
    @property
    def granted(self) -> bool:
        return self.selected_capability_id is not None and self.selected_resource_id is not None


class CapabilityResourceScheduler:
    """Coordinate capability eligibility and resource capacity without authority."""

    def __init__(
        self,
        engine: CapabilityResourceDiscoveryEngine,
        capability_resource_kinds: Mapping[str, ResourceKind] | None = None,
    ) -> None:
        self.engine = engine
        self._kinds = dict(capability_resource_kinds or {})

    def _ordered(self, evaluations: Sequence[Evaluation]) -> tuple[Evaluation, ...]:
        eligible = [item for item in evaluations if item.eligible]
        return tuple(sorted(eligible, key=lambda item: (-item.score, item.candidate.cost, item.candidate.capability_id)))

    def plan(
        self,
        requirement: CapabilityRequirement,
        *,
        resource_kind: ResourceKind,
        gap_id: str | None = None,
    ) -> CapabilityResourcePlan:
        result = self.engine.discover(requirement, gap_id)
        attempts: list[str] = []
        for evaluation in self._ordered(result.evaluations)[:_MAX_ATTEMPTS]:
            capability_id = evaluation.candidate.capability_id
            attempts.append(capability_id)
            decision = self.engine.decide_resource(resource_kind, 1.0, max_cost=requirement.max_cost)
            if not decision.granted:
                continue
            return CapabilityResourcePlan(
                requirement,
                capability_id,
                decision.resource_id,
                None,
                tuple(attempts),
                "eligible capability selected and resource capacity confirmed",
            )
        reason = "no eligible capability could be paired with sufficient registered resource capacity"
        if not result.evaluations:
            reason = "no capability candidates were discovered"
        elif not attempts:
            reason = "no discovered capability passed the hard eligibility gates"
        return CapabilityResourcePlan(requirement, None, None, None, tuple(attempts), reason)

    def admit(self, plan: CapabilityResourcePlan) -> CapabilityResourcePlan:
        """Create the actual bounded resource reservation after explicit admission."""
        if not plan.granted:
            raise PermissionError("resource admission requires a granted plan")
        decision = self.engine.reserve_resource(
            self._kinds.get(plan.selected_capability_id, ResourceKind.OTHER),
            1.0,
            max_cost=plan.requirement.max_cost,
        )
        if not decision.granted:
            raise RuntimeError("planned resource capacity is no longer available")
        if decision.resource_id != plan.selected_resource_id:
            self.engine.release_resource(decision.reservation_id or "")
            raise RuntimeError("resource changed between planning and admission")
        return CapabilityResourcePlan(
            plan.requirement,
            plan.selected_capability_id,
            plan.selected_resource_id,
            decision.reservation_id,
            plan.attempts,
            "resource reservation admitted",
        )

    def release(self, plan: CapabilityResourcePlan) -> None:
        if plan.reservation_id:
            self.engine.release_resource(plan.reservation_id)
