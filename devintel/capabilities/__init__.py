"""Capability and resource discovery subsystem."""
from .contracts import (
    CapabilityDescriptor, CapabilityGap, CapabilityRequirement, CapabilityStatus,
    DiscoveryResult, Evaluation, ResourceDescriptor, ResourceKind,
)
from .discovery import CapabilityDiscovery, DefaultEvaluator, DiscoveryPolicy
from .registry import CapabilityRegistry, GapRegistry, ResourceRegistry

__all__ = [
    "CapabilityDescriptor", "CapabilityGap", "CapabilityRequirement", "CapabilityStatus",
    "DiscoveryResult", "Evaluation", "ResourceDescriptor", "ResourceKind",
    "CapabilityDiscovery", "DefaultEvaluator", "DiscoveryPolicy",
    "CapabilityRegistry", "GapRegistry", "ResourceRegistry",
]
