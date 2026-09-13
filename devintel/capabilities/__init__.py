"""Capability and resource discovery subsystem."""
from .contracts import (
    CapabilityDescriptor, CapabilityGap, CapabilityRequirement, CapabilityStatus,
    DiscoveryResult, Evaluation, ResourceDescriptor, ResourceKind,
)
from .discovery import CapabilityDiscovery, DefaultEvaluator, DiscoveryPolicy
from .inventory import local_capabilities, local_resources
from .lifecycle import CapabilityLifecycle, LifecycleEvent
from .registry import CapabilityRegistry, GapRegistry, ResourceRegistry
from .store import LifecycleStore

__all__ = [
    "CapabilityDescriptor", "CapabilityGap", "CapabilityRequirement", "CapabilityStatus",
    "DiscoveryResult", "Evaluation", "ResourceDescriptor", "ResourceKind",
    "CapabilityDiscovery", "DefaultEvaluator", "DiscoveryPolicy",
    "CapabilityLifecycle", "LifecycleEvent", "LifecycleStore", "local_capabilities", "local_resources",
    "CapabilityRegistry", "GapRegistry", "ResourceRegistry",
]
