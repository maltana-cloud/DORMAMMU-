from devintel.modules.simulation import (
    ActionKind, AgentPolicy, DeterministicAgentPolicy, EntityKind, ScenarioPlanner,
    ScenarioSpec, SimulationRuntimeAdapter, SimulationStore, SimulationWorld, WorldAction, WorldEntity,
)
from devintel.runtime.app import DORMAMMURuntime


def actor(entity_id="a", energy=100):
    return WorldEntity(entity_id, EntityKind.ACTOR, energy=energy)


def test_world_is_deterministic_and_replayable():
    actions = (WorldAction("m1", "a", ActionKind.MOVE, "a", "2,3"), WorldAction("s1", "a", ActionKind.SET, "a", "mood=focused"))
    left = SimulationWorld("w", entities=(actor(),)).step(actions)
    right = SimulationWorld("w", entities=(actor(),)).step(actions)
    assert left.snapshot.digest == right.snapshot.digest
    assert tuple((e.kind, e.reason) for e in left.events) == tuple((e.kind, e.reason) for e in right.events)


def test_invalid_actions_fail_closed_without_mutating_entity_state():
    world = SimulationWorld("w", entities=(actor(),))
    result = world.step((WorldAction("bad", "missing", ActionKind.MOVE, "missing", "1,1"),))
    assert result.rejected_actions == 1
    assert world.entity("a") == actor()


def test_action_and_tick_bounds_are_enforced():
    world = SimulationWorld("w", entities=(actor(),))
    for actions, ticks in [ ((), 65), (tuple(WorldAction(str(i), "a", ActionKind.MOVE, "a", "0,0") for i in range(129)), 1) ]:
        try:
            world.step(actions, ticks=ticks)
            assert False
        except ValueError:
            pass


def test_entity_limit_is_enforced():
    try:
        SimulationWorld("w", entities=tuple(actor(str(i)) for i in range(257)))
        assert False
    except ValueError:
        pass


def test_snapshot_integrity_and_persistence():
    store = SimulationStore()
    world = SimulationWorld("w", entities=(actor(),))
    snapshot = world.step((WorldAction("m", "a", ActionKind.MOVE, "a", "1,0"),)).snapshot
    store.save(snapshot)
    assert store.load("w", snapshot.tick) == snapshot
    assert store.history("w")[0] == (snapshot.tick, snapshot.digest)
    store.close()


def test_snapshot_tampering_is_rejected():
    world = SimulationWorld("w", entities=(actor(),))
    snapshot = world.snapshot()
    tampered = type(snapshot)(snapshot.world_id, snapshot.tick, snapshot.entities, "bad")
    store = SimulationStore()
    try:
        store.save(tampered)
        assert False
    except ValueError:
        pass
    finally:
        store.close()


def test_agent_policy_is_proposal_only_and_bounded():
    action = DeterministicAgentPolicy().propose(actor(), goal="move right and up")
    assert action.kind is ActionKind.MOVE and action.value == "1,1"
    planned = ScenarioPlanner().plan(ScenarioSpec("s", "practice"), (AgentPolicy("a", "move", 100, -100),))
    assert planned[0].value == "16,-16"


def test_runtime_adapter_persists_recovers_and_records_telemetry():
    runtime = DORMAMMURuntime()
    adapter = SimulationRuntimeAdapter(runtime)
    adapter.create_world("w", entities=(actor(),))
    run = adapter.step("w", (WorldAction("m", "a", ActionKind.MOVE, "a", "1,0"),))
    assert run.result.snapshot.tick == 1
    assert adapter.recover_latest("w").snapshot() == run.result.snapshot
    assert runtime.operation_history("simulation.world", limit=10)
    adapter.close(); runtime.close()


def test_no_external_execution_surface_exists():
    world = SimulationWorld("w", entities=(actor(),))
    assert not hasattr(world, "execute") and not hasattr(world, "publish") and not hasattr(world, "network")
