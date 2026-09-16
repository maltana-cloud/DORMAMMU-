"""Knowledge and research primitives for DORMAMMU."""

from .contracts import ResearchCandidate, ResearchDocument, ResearchObservation, canonicalize_url, content_digest
from .knowledge import Claim, Entity, Relationship
from .limits import ResearchLimits
from .normalization import normalize_content, normalize_text, normalize_title
from .opportunities import OpportunityCandidate
from .persistent_store import SQLiteResearchStore
from .pipeline import ResearchBatch, ResearchPipeline, ResearchRoute, SourceProvider
from .providers import RSSProvider, StaticProvider
from .store import InMemoryResearchStore, ResearchStore
from .synthesis import Contradiction, KnowledgeSynthesisEngine, SynthesisResult, SynthesisSignal, VerifiedClaim
from .verification import ProvenanceVerifier, ResearchVerifier, VerificationResult
from .domain_expansion import DomainAssessment, DomainEvidence, DomainExpander, DomainProposal
from .domain_registry import DomainRecord, DomainRegistry
from .discovery import DiscoveryProvider, DiscoveryResult, ResearchDiscoveryEngine
from .acquisition import EvidenceAcquisition, EvidenceAcquisitionGateway

__all__ = [
    "ResearchCandidate", "ResearchDocument", "ResearchObservation", "canonicalize_url", "content_digest",
    "Claim", "Entity", "Relationship", "ResearchLimits",
    "normalize_content", "normalize_text", "normalize_title", "OpportunityCandidate",
    "ResearchBatch", "ResearchPipeline", "ResearchRoute", "SourceProvider", "RSSProvider", "StaticProvider",
    "ResearchStore", "InMemoryResearchStore", "SQLiteResearchStore",
    "ResearchVerifier", "ProvenanceVerifier", "VerificationResult",
    "VerifiedClaim", "Contradiction", "SynthesisSignal", "SynthesisResult", "KnowledgeSynthesisEngine",
    "DomainAssessment", "DomainEvidence", "DomainExpander", "DomainProposal", "DomainRecord", "DomainRegistry",
    "DiscoveryProvider", "DiscoveryResult", "ResearchDiscoveryEngine",
    "EvidenceAcquisition", "EvidenceAcquisitionGateway",
]
