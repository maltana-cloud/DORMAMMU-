"""Integrated intelligence capabilities."""

from .collaboration import CollaborationRequest, CollaborationResponse, CollaborationStatus, HumanCollaborationEngine
from .domain import DomainIntelligenceEngine, DomainProfile, DomainSignal
from .ecosystem import AgentDescriptor, AgentRegistry, CoordinationResult, CoordinationTask, EcosystemCoordinator
from .knowledge import KnowledgeConflict, KnowledgeIntelligence, KnowledgeItem, KnowledgeQuery
from .problem_opportunity import ProblemOpportunityCandidate, ProblemOpportunityEngine, ProblemOpportunityResult

__all__ = [
    "CollaborationRequest", "CollaborationResponse", "CollaborationStatus", "HumanCollaborationEngine",
    "DomainIntelligenceEngine", "DomainProfile", "DomainSignal",
    "AgentDescriptor", "AgentRegistry", "CoordinationResult", "CoordinationTask", "EcosystemCoordinator",
    "KnowledgeConflict", "KnowledgeIntelligence", "KnowledgeItem", "KnowledgeQuery",
    "ProblemOpportunityCandidate", "ProblemOpportunityEngine", "ProblemOpportunityResult",
]
