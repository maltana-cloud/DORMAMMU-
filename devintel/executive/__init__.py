"""DORMAMMU executive cognition contracts and bounded engine."""
from .contracts import ExecutivePlan, GoalUnderstanding, Objective, TaskSpec
from .engine import DefaultGoalInterpreter, ExecutiveEngine, ExecutiveResult, ExplicitTaskDecomposer
from .evidence import EvidenceBackedExecutiveAdapter, EvidenceBackedUnderstanding, EvidenceRequirementError

__all__ = [
    "DefaultGoalInterpreter",
    "ExecutiveEngine",
    "ExecutivePlan",
    "ExecutiveResult",
    "EvidenceBackedExecutiveAdapter",
    "EvidenceBackedUnderstanding",
    "EvidenceRequirementError",
    "ExplicitTaskDecomposer",
    "GoalUnderstanding",
    "Objective",
    "TaskSpec",
]
