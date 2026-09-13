import pytest

from devintel.capabilities import CapabilityRequirement, ResourceKind, ResourceRequest
from devintel.core.contracts import ActionRequest, ActionRisk
from devintel.executive import ExecutiveEngine, Objective, TaskSpec
from devintel.runtime import DORMAMMURuntime


def task(task_id, name, value, depends_on=()):
    return TaskSpec(
        task_id,
        name,
        CapabilityRequirement("runtime-local", "run locally", ("runtime",)),
        ActionRequest("test.echo", ActionRisk.LOW, name, {"value": value, "_scope_id": "scope"}),
        depends_on=depends_on,
        resource=ResourceRequest(ResourceKind.CPU, 1),
    )


def test_plan_understands_objective_and_validates_dependencies():
    runtime = DORMAMMURuntime()
    try:
        engine = ExecutiveEngine(runtime)
        objective = Objective("prepare a test result", "the result is produced", "scope")
        plan = engine.plan(objective, (task("a", "first", 1), task("b", "second", 2, ("a",))))
        assert plan.understanding.normalized_goal == "prepare a test result"
        assert plan.understanding.success_criteria == ("the result is produced",)
        assert [item.task_id for item in plan.tasks] == ["a", "b"]
    finally:
        runtime.close()


def test_plan_rejects_cycles_unknown_dependencies_and_scope_crossing():
    runtime = DORMAMMURuntime()
    try:
        engine = ExecutiveEngine(runtime)
        objective = Objective("test", "done", "scope")
        with pytest.raises(ValueError, match="unknown dependency"):
            engine.plan(objective, (task("a", "first", 1, ("missing",)),))
        with pytest.raises(ValueError, match="cycle"):
            engine.plan(objective, (task("a", "first", 1, ("b",)), task("b", "second", 2, ("a",))))
        cross_scope = TaskSpec(
            "cross", "cross scope", CapabilityRequirement("runtime-local", "run", ("runtime",)),
            ActionRequest("test.echo", ActionRisk.LOW, "cross scope", {"_scope_id": "other"}),
        )
        with pytest.raises(ValueError, match="scope"):
            engine.plan(objective, (cross_scope,))
    finally:
        runtime.close()


def test_execute_runs_decomposed_tasks_through_bounded_path():
    runtime = DORMAMMURuntime()
    try:
        runtime.register_action("test.echo", lambda payload: {"value": payload["value"]})
        engine = ExecutiveEngine(runtime)
        objective = Objective("produce two values", "both values are produced", "scope", objective_id="obj-1")
        result = engine.execute(objective, (task("a", "first", 1), task("b", "second", 2, ("a",))))
        assert result.success
        assert result.objective_id == "obj-1"
        assert [item[1].verified for item in result.task_results] == [True, True]
        assert runtime.resource_reservations() == ()
    finally:
        runtime.close()


def test_execute_stops_when_bounded_task_hits_permission_boundary():
    runtime = DORMAMMURuntime()
    try:
        runtime.register_action("test.echo", lambda payload: {"value": payload["value"]})
        protected = TaskSpec(
            "protected",
            "protected work",
            CapabilityRequirement("runtime-local", "run locally", ("runtime",)),
            ActionRequest("test.echo", ActionRisk.HIGH, "protected", {"_scope_id": "scope"}),
        )
        result = ExecutiveEngine(runtime).execute(Objective("protected", "done", "scope"), (protected,))
        assert not result.success
        assert result.task_results[0][1].stage == "act"
    finally:
        runtime.close()
