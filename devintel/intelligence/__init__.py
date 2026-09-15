"""Integrated intelligence capabilities."""

from .domain import DomainIntelligenceEngine, DomainProfile, DomainSignal
from .knowledge import KnowledgeConflict, KnowledgeIntelligence, KnowledgeItem, KnowledgeQuery
from .problem_opportunity import ProblemOpportunityCandidate, ProblemOpportunityEngine, ProblemOpportunityResult

__all__ = [
    "DomainIntelligenceEngine", "DomainProfile", "DomainSignal",
    "KnowledgeConflict", "KnowledgeIntelligence", "KnowledgeItem", "KnowledgeQuery",
    "ProblemOpportunityCandidate", "ProblemOpportunityEngine", "ProblemOpportunityResult",
]
