"""Scenario and agent-policy helpers with deterministic bounded decisions."""
from __future__ import annotations

from dataclasses import dataclass

from .contracts import ActionKind, WorldAction, WorldEntity


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_id: str
    objective: str
    max_ticks: int = 32
    seed: int = 0


@dataclass(frozen=True)
class AgentPolicy:
    agent_id: str
    goal: str
    preferred_dx: int = 0
    preferred_dy: int = 0


class ScenarioPlanner:
    def plan(self, scenario: ScenarioSpec, agents: tuple[AgentPolicy, ...]) -> tuple[WorldAction, ...]:
        if not scenario.scenario_id.strip() or not scenario.objective.strip():
            raise ValueError("scenario identity and objective are required")
        if scenario.max_ticks < 1 or scenario.max_ticks > 64:
            raise ValueError("max_ticks is out of bounds")
        if len(agents) > 128:
            raise ValueError("agent count is out of bounds")
        actions: list[WorldAction] = []
        for index, agent in enumerate(sorted(agents, key=lambda a: a.agent_id)):
            if not agent.agent_id.strip():
                raise ValueError("agent_id is required")
            dx, dy = max(-16, min(16, agent.preferred_dx)), max(-16, min(16, agent.preferred_dy))
            actions.append(WorldAction(f"{scenario.scenario_id}:{index}", agent.agent_id, ActionKind.MOVE, agent.agent_id, f"{dx},{dy}"))
        return tuple(actions)


class DeterministicAgentPolicy:
    """Produces proposals only; it has no network, process, payment, or platform authority."""
    def propose(self, entity: WorldEntity, *, goal: str) -> WorldAction:
        if not goal.strip():
            raise ValueError("goal is required")
        dx = 1 if "right" in goal.casefold() else -1 if "left" in goal.casefold() else 0
        dy = 1 if "up" in goal.casefold() else -1 if "down" in goal.casefold() else 0
        return WorldAction(f"policy:{entity.entity_id}:{entity.x}:{entity.y}", entity.entity_id, ActionKind.MOVE, entity.entity_id, f"{dx},{dy}")
