"""DORMAMMU executive cognition contracts and bounded engine."""
from .contracts import ExecutivePlan, GoalUnderstanding, Objective, TaskSpec
from .engine import DefaultGoalInterpreter, ExecutiveEngine, ExecutiveResult, ExplicitTaskDecomposer
from .evidence import EvidenceBackedExecutiveAdapter, EvidenceBackedUnderstanding, EvidenceRequirementError
from .routing import CollaborationPlan, CollaborationStep, RouteCandidate, RoutingRequirement, SpecialistDescriptor, SpecialistKind, SpecialistRouter
from .nl_goal import BoundedNaturalLanguageGoalBoundary, DeterministicNaturalLanguageInterpreter, GoalInterpretation, NaturalLanguageGoalInterpreter, ProviderSemanticNaturalLanguageInterpreter
from .outcome_routing import OutcomeAwareRoutingService
from .cognition import CognitiveFact, CognitiveHypothesis, CognitiveSelfModel, CognitiveState, CoreCognition

__all__ = [
    "DefaultGoalInterpreter", "ExecutiveEngine", "ExecutivePlan", "ExecutiveResult",
    "EvidenceBackedExecutiveAdapter", "EvidenceBackedUnderstanding", "EvidenceRequirementError",
    "ExplicitTaskDecomposer", "GoalUnderstanding", "Objective", "TaskSpec",
    "CollaborationPlan", "CollaborationStep", "RouteCandidate", "RoutingRequirement",
    "SpecialistDescriptor", "SpecialistKind", "SpecialistRouter",
    "BoundedNaturalLanguageGoalBoundary", "DeterministicNaturalLanguageInterpreter", "GoalInterpretation", "NaturalLanguageGoalInterpreter", "ProviderSemanticNaturalLanguageInterpreter",
    "OutcomeAwareRoutingService", "CognitiveFact", "CognitiveHypothesis", "CognitiveSelfModel", "CognitiveState", "CoreCognition",
]
