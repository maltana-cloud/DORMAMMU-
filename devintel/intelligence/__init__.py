"""Integrated intelligence capabilities."""

from .collaboration import CollaborationRequest, CollaborationResponse, CollaborationStatus, HumanCollaborationEngine
from .domain import DomainIntelligenceEngine, DomainProfile, DomainSignal
from .ecosystem import AgentDescriptor, AgentRegistry, CoordinationResult, CoordinationTask, EcosystemCoordinator
from .global_discovery import DiscoveryRound, GlobalDiscoveryEngine, GlobalDiscoveryPolicy
from .knowledge import KnowledgeConflict, KnowledgeIntelligence, KnowledgeItem, KnowledgeQuery
from .problem_opportunity import ProblemOpportunityCandidate, ProblemOpportunityEngine, ProblemOpportunityResult
from .gap_missions import GapMissionEngine, MissionProposal

__all__ = [
    "CollaborationRequest", "CollaborationResponse", "CollaborationStatus", "HumanCollaborationEngine",
    "DomainIntelligenceEngine", "DomainProfile", "DomainSignal",
    "AgentDescriptor", "AgentRegistry", "CoordinationResult", "CoordinationTask", "EcosystemCoordinator",
    "DiscoveryRound", "GlobalDiscoveryEngine", "GlobalDiscoveryPolicy",
    "KnowledgeConflict", "KnowledgeIntelligence", "KnowledgeItem", "KnowledgeQuery",
    "ProblemOpportunityCandidate", "ProblemOpportunityEngine", "ProblemOpportunityResult",
    "GapMissionEngine", "MissionProposal",
]
