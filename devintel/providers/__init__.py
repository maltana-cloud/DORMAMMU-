"""Provider adapter boundaries for replaceable external integrations."""
from .contracts import ProviderCapability, ProviderHealth, ProviderResult
from .execution import CapabilityExecution, CapabilityExecutor
from .live import (
    GenerationProvider,
    GenerationRequest,
    GenerationResponse,
    ProviderRouter,
    ResearchProvider,
    ResearchRequest,
    ResearchResult,
)
from .live_adapters import GeminiGenerationProvider, WikipediaResearchProvider, configured_live_providers
from .registry import ProviderRegistry
from .resource_execution import ResourceAwareProviderExecutor, ResourceExecutionResult

__all__ = [
    "ProviderCapability", "ProviderHealth", "ProviderResult", "CapabilityExecution", "CapabilityExecutor", "ProviderRegistry",
    "GenerationProvider", "GenerationRequest", "GenerationResponse", "ResearchProvider", "ResearchRequest", "ResearchResult",
    "ProviderRouter", "GeminiGenerationProvider", "WikipediaResearchProvider", "configured_live_providers",
    "ResourceAwareProviderExecutor", "ResourceExecutionResult",
]
