"""Capability and resource discovery subsystem."""
from .contracts import (
    CapabilityDescriptor, CapabilityGap, CapabilityRequirement, CapabilityStatus,
    DiscoveryResult, Evaluation, ResourceDescriptor, ResourceKind,
)
from .discovery import CapabilityDiscovery, DefaultEvaluator, DiscoveryPolicy
from .lifecycle import CapabilityLifecycle, LifecycleEvent
from .registry import CapabilityRegistry, GapRegistry, ResourceRegistry

__all__ = [
    "CapabilityDescriptor", "CapabilityGap", "CapabilityRequirement", "CapabilityStatus",
    "DiscoveryResult", "Evaluation", "ResourceDescriptor", "ResourceKind",
    "CapabilityDiscovery", "DefaultEvaluator", "DiscoveryPolicy",
    "CapabilityLifecycle", "LifecycleEvent",
    "CapabilityRegistry", "GapRegistry", "ResourceRegistry",
]
