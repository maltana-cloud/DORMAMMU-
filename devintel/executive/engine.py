"""Bounded objective understanding, decomposition, and execution orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from .contracts import ExecutivePlan, GoalInterpreter, GoalUnderstanding, Objective, TaskDecomposer, TaskSpec
from ..operations import BoundedOperation, OperationResult


class DefaultGoalInterpreter:
    """Understand explicit objective fields without pretending to perform hidden reasoning."""

    def understand(self, objective: Objective) -> GoalUnderstanding:
        goal = " ".join(objective.intent.split())
        outcome = " ".join(objective.desired_outcome.split())
        criteria = (outcome,)
        return GoalUnderstanding(objective, goal, criteria, dict(objective.constraints))


class ExplicitTaskDecomposer:
    """Validate caller-supplied task decomposition while preserving dependency order."""

    def decompose(self, understanding: GoalUnderstanding, tasks: tuple[TaskSpec, ...] = ()) -> tuple[TaskSpec, ...]:
        if not tasks:
            raise ValueError("explicit task decomposition is required")
        by_id = {task.task_id: task for task in tasks}
        if len(by_id) != len(tasks):
            raise ValueError("task ids must be unique")
        for task in tasks:
            if any(dep not in by_id for dep in task.depends_on):
                raise ValueError(f"task {task.task_id} has an unknown dependency")
            if task.action.payload.get("_scope_id") not in {None, understanding.objective.scope_id}:
                raise ValueError("task action crosses objective scope")
        self._assert_acyclic(tasks)
        return tasks

    @staticmethod
    def _assert_acyclic(tasks: tuple[TaskSpec, ...]) -> None:
        graph = {task.task_id: set(task.depends_on) for task in tasks}
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> None:
            if task_id in visiting:
                raise ValueError("task dependency cycle detected")
            if task_id in visited:
                return
            visiting.add(task_id)
            for dependency in graph[task_id]:
                visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in graph:
            visit(task_id)


@dataclass(frozen=True)
class ExecutiveResult:
    objective_id: str
    plan: ExecutivePlan
    task_results: tuple[tuple[str, OperationResult], ...]
    success: bool
    reason: str = ""


class ExecutiveEngine:
    """Connect objective understanding and decomposition to bounded operation execution."""

    def __init__(self, runtime, interpreter: GoalInterpreter | None = None) -> None:
        self.runtime = runtime
        self.interpreter = interpreter or DefaultGoalInterpreter()

    def plan(self, objective: Objective, tasks: tuple[TaskSpec, ...]) -> ExecutivePlan:
        understanding = self.interpreter.understand(objective)
        decomposer = ExplicitTaskDecomposer()
        normalized = tuple(decomposer.decompose(understanding, tasks))
        return ExecutivePlan(understanding, normalized)

    def execute(
        self,
        objective: Objective,
        tasks: tuple[TaskSpec, ...],
        *,
        owner_approved: bool = False,
        capability_approved: bool = False,
        canary_health_by_capability: dict[str, object] | None = None,
    ) -> ExecutiveResult:
        plan = self.plan(objective, tasks)
        task_results: list[tuple[str, OperationResult]] = []
        completed: set[str] = set()
        health = canary_health_by_capability or {}
        for task in plan.tasks:
            if any(dep not in completed for dep in task.depends_on):
                return ExecutiveResult(objective.objective_id or uuid4().hex, plan, tuple(task_results), False, f"dependencies for task {task.task_id} are not complete")
            payload = dict(task.action.payload)
            payload.pop("_scope_id", None)
            action = type(task.action)(task.action.action, task.action.risk, task.action.reason, payload)
            operation = BoundedOperation(task.name, task.capability, action, resource_request=task.resource)
            result = self.runtime.run_bounded_operation(
                operation,
                owner_approved=owner_approved,
                capability_approved=capability_approved,
                canary_health=health.get(task.capability.capability_id),
            )
            task_results.append((task.task_id, result))
            if not result.success:
                return ExecutiveResult(objective.objective_id or uuid4().hex, plan, tuple(task_results), False, f"task {task.task_id} failed: {result.message}")
            completed.add(task.task_id)
        return ExecutiveResult(objective.objective_id or uuid4().hex, plan, tuple(task_results), True, "objective tasks completed and verified")
