"""Bounded ecosystem and multi-agent coordination contracts for DORMAMMU.

Agents are replaceable capabilities. Coordination provides scoped task
assignment and result collection, but never grants authority, credentials, or
permission to recursively spawn uncontrolled work.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Callable, Mapping

from ..modules.research.normalization import normalize_text


@dataclass(frozen=True)
class AgentDescriptor:
    agent_id: str
    capabilities: tuple[str, ...] = ()
    version: str = "1"
    enabled: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.agent_id, str) or not self.agent_id.strip():
            raise ValueError("agent_id is required")
        if not isinstance(self.capabilities, tuple) or any(not isinstance(c, str) or not c.strip() for c in self.capabilities):
            raise TypeError("capabilities must be a tuple of non-empty strings")
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("version is required")
        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be boolean")


@dataclass(frozen=True)
class CoordinationTask:
    task_id: str
    scope_id: str
    objective: str
    capability: str
    context: str = ""
    metadata: Mapping[str, str] = ()

    def __post_init__(self) -> None:
        for value, name in ((self.task_id, "task_id"), (self.scope_id, "scope_id"), (self.objective, "objective"), (self.capability, "capability")):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        if not isinstance(self.context, str):
            raise TypeError("context must be a string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")


@dataclass(frozen=True)
class CoordinationResult:
    task_id: str
    agent_id: str
    success: bool
    output: str = ""
    error: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValueError("task_id is required")
        if not isinstance(self.agent_id, str) or not self.agent_id.strip():
            raise ValueError("agent_id is required")
        if not isinstance(self.success, bool):
            raise TypeError("success must be boolean")
        if not isinstance(self.output, str) or not isinstance(self.error, str):
            raise TypeError("output and error must be strings")
        if self.success and self.error:
            raise ValueError("successful result cannot contain an error")
        if not self.success and not self.error.strip():
            raise ValueError("failed result requires an error")


class AgentRegistry:
    """Bounded, deterministic host-controlled agent registry."""

    def __init__(self, *, max_agents: int = 256) -> None:
        if max_agents <= 0:
            raise ValueError("max_agents must be positive")
        self.max_agents = max_agents
        self._agents: dict[str, AgentDescriptor] = {}

    def register(self, agent: AgentDescriptor) -> None:
        if not isinstance(agent, AgentDescriptor):
            raise TypeError("agent must be AgentDescriptor")
        if agent.agent_id not in self._agents and len(self._agents) >= self.max_agents:
            raise RuntimeError("agent registry capacity reached")
        self._agents[agent.agent_id] = agent

    def get(self, agent_id: str) -> AgentDescriptor | None:
        return self._agents.get(agent_id)

    def list(self, *, capability: str | None = None) -> tuple[AgentDescriptor, ...]:
        if capability is not None:
            capability = normalize_text(capability)
        return tuple(agent for agent in sorted(self._agents.values(), key=lambda item: item.agent_id) if agent.enabled and (capability is None or capability in agent.capabilities))


class EcosystemCoordinator:
    """Assign bounded tasks to registered specialists and collect their results."""

    def __init__(self, registry: AgentRegistry, *, max_tasks: int = 100, max_context: int = 20_000) -> None:
        if not isinstance(registry, AgentRegistry):
            raise TypeError("registry must be AgentRegistry")
        if max_tasks <= 0 or max_context <= 0:
            raise ValueError("coordination bounds must be positive")
        self.registry = registry
        self.max_tasks = max_tasks
        self.max_context = max_context

    def create_task(self, scope_id: str, objective: str, capability: str, *, context: str = "", metadata: Mapping[str, str] | None = None) -> CoordinationTask:
        scope = normalize_text(scope_id)
        goal = normalize_text(objective)
        required = normalize_text(capability)
        if not isinstance(context, str):
            raise TypeError("context must be a string")
        context = context.strip()
        if len(context) > self.max_context:
            raise ValueError("context exceeds configured bound")
        normalized_metadata = dict(metadata or {})
        if any(not isinstance(k, str) or not isinstance(v, str) for k, v in normalized_metadata.items()):
            raise TypeError("metadata keys and values must be strings")
        payload = "\x1f".join((scope, goal, required, context, *(f"{k}={normalized_metadata[k]}" for k in sorted(normalized_metadata))))
        task_id = "task-" + sha256(payload.encode("utf-8")).hexdigest()
        return CoordinationTask(task_id, scope, goal, required, context, normalized_metadata)

    def eligible_agents(self, task: CoordinationTask) -> tuple[AgentDescriptor, ...]:
        if not isinstance(task, CoordinationTask):
            raise TypeError("task must be CoordinationTask")
        return self.registry.list(capability=task.capability)

    def dispatch(self, task: CoordinationTask, execute: Callable[[AgentDescriptor, CoordinationTask], CoordinationResult], *, max_agents: int = 1) -> tuple[CoordinationResult, ...]:
        if not isinstance(task, CoordinationTask):
            raise TypeError("task must be CoordinationTask")
        if not callable(execute):
            raise TypeError("execute must be callable")
        if max_agents <= 0:
            raise ValueError("max_agents must be positive")
        agents = self.eligible_agents(task)[: min(max_agents, self.max_tasks)]
        results: list[CoordinationResult] = []
        for agent in agents:
            try:
                result = execute(agent, task)
                if not isinstance(result, CoordinationResult) or result.task_id != task.task_id or result.agent_id != agent.agent_id:
                    raise ValueError("executor returned invalid or mismatched result")
            except Exception as exc:
                result = CoordinationResult(task.task_id, agent.agent_id, False, error=type(exc).__name__)
            results.append(result)
        return tuple(results)
