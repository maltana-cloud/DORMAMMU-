import pytest

from devintel.intelligence.ecosystem import (
    AgentDescriptor,
    AgentRegistry,
    CoordinationResult,
    EcosystemCoordinator,
)


def test_registry_is_bounded_and_deterministic():
    registry = AgentRegistry(max_agents=2)
    registry.register(AgentDescriptor("z", ("research",)))
    registry.register(AgentDescriptor("a", ("research",)))
    assert [a.agent_id for a in registry.list(capability="research")] == ["a", "z"]
    with pytest.raises(RuntimeError):
        registry.register(AgentDescriptor("b", ("research",)))


def test_task_identity_uses_normalized_stored_content():
    coordinator = EcosystemCoordinator(AgentRegistry())
    a = coordinator.create_task(" scope ", "  Find facts ", " research ", context="  useful  ")
    b = coordinator.create_task("scope", "Find facts", "research", context="useful")
    assert a == b
    assert a.task_id.startswith("task-")


def test_disabled_or_wrong_capability_agents_are_excluded():
    registry = AgentRegistry()
    registry.register(AgentDescriptor("researcher", ("research",)))
    registry.register(AgentDescriptor("writer", ("write",)))
    registry.register(AgentDescriptor("off", ("research",), enabled=False))
    coordinator = EcosystemCoordinator(registry)
    task = coordinator.create_task("s1", "research something", "research")
    assert [a.agent_id for a in coordinator.eligible_agents(task)] == ["researcher"]


def test_dispatch_is_bounded_and_isolates_agent_failure():
    registry = AgentRegistry()
    for agent_id in ("a", "b", "c"):
        registry.register(AgentDescriptor(agent_id, ("research",)))
    coordinator = EcosystemCoordinator(registry, max_tasks=2)
    task = coordinator.create_task("s1", "research", "research")

    def execute(agent, task):
        if agent.agent_id == "a":
            raise RuntimeError("boom")
        return CoordinationResult(task.task_id, agent.agent_id, True, output=agent.agent_id)

    results = coordinator.dispatch(task, execute, max_agents=3)
    assert len(results) == 2
    assert results[0].success is False
    assert results[1].success is True


def test_mismatched_executor_result_fails_closed():
    registry = AgentRegistry()
    registry.register(AgentDescriptor("a", ("research",)))
    coordinator = EcosystemCoordinator(registry)
    task = coordinator.create_task("s1", "research", "research")

    def execute(agent, task):
        return CoordinationResult("wrong", agent.agent_id, True, output="bad")

    result = coordinator.dispatch(task, execute)[0]
    assert result.success is False
    assert result.error == "ValueError"


def test_result_contract_rejects_inconsistent_success_and_failure():
    with pytest.raises(ValueError):
        CoordinationResult("t", "a", True, output="ok", error="bad")
    with pytest.raises(ValueError):
        CoordinationResult("t", "a", False)
