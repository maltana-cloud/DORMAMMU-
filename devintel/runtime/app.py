"""Composition root connecting DORMAMMU's bounded subsystems."""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any
from ..autonomy.engine import AutonomousEngine, Observer, Planner, Verifier, Recorder
from ..autonomy.contracts import Observation
from ..capabilities import (CapabilityDescriptor, CapabilityDiscovery, CapabilityGap, CapabilityLifecycle, CapabilityRegistry, CapabilityRequirement, DiscoveryResult, ResourceDescriptor, ResourceRegistry, LifecycleStore, CapabilityDecision, CapabilityDecisionEngine, CanaryHealth, CanaryMonitor, CanaryPolicy, ResourceDecision, ResourceManager, ResourceRequest)
from ..capabilities.inventory import local_capabilities, local_resources
from ..control.service import OwnerControlCenter
from ..core.audit import AuditLog
from ..core.orchestrator import Orchestrator
from ..core.runtime import RuntimeContext
from ..modules.education.contracts import Assessment, EducationMode
from ..modules.education.engine import EducationEngine
from ..modules.education.integrations import EducationIntegrationResult, EducationSubsystemIntegration
from ..modules.education.outcomes import EducationFeedbackBridge, OutcomeEngine, OutcomeSummary
from ..modules.education.teaching import TeachingEngine, TeachingProfile, TeachingResponse
from ..modules.monitoring.engine import MonitoringEngine
from ..modules.plugins.service import PluginService
from ..modules.security.orchestrator import SecurityOrchestrator
from ..modules.security.recovery import CryptographicRecovery, RecoveryRequest
from ..modules.specialists.education import EducationSpecialist
from ..providers.live import GenerationRequest, ProviderRouter, ResearchRequest
from ..providers.live_adapters import configured_live_providers
from ..providers.registry import ProviderRegistry

@dataclass(frozen=True)
class RuntimeSnapshot:
    scope_id: str; runtime_state: str; metrics: dict[str, int]; plugin_status: tuple[tuple[str, str, int], ...]; monitoring_state: str; audit_events: int

class DORMAMMURuntime:
    """Single composition root for DORMAMMU bounded subsystems."""
    def __init__(self, *, lifecycle_store_path: str = ":memory:", recovery_secret: bytes | None = None, canary_policy: CanaryPolicy | None = None) -> None:
        self.context = RuntimeContext(); self.audit = AuditLog(); self.orchestrator = Orchestrator(runtime=self.context, audit=self.audit)
        secret = recovery_secret
        if secret is None and os.environ.get("DORMAMMU_RECOVERY_SECRET"):
            secret = bytes.fromhex(os.environ["DORMAMMU_RECOVERY_SECRET"])
        self.recovery = CryptographicRecovery(secret) if secret is not None else None
        self.security = SecurityOrchestrator(events=self.context.events, audit=self.audit, runtime_state=self.context.state, recovery=self.recovery); self.monitoring = MonitoringEngine(); self.plugins = PluginService()
        self.providers = ProviderRegistry(); self.live_providers = ProviderRouter(); self._configure_live_providers()
        self.capability_registry = CapabilityRegistry(); self.resource_registry = ResourceRegistry(); self.resource_manager = ResourceManager(self.resource_registry); self.capability_discovery = CapabilityDiscovery(registry=self.capability_registry)
        self.lifecycle_store = LifecycleStore(lifecycle_store_path); self.capability_lifecycle = CapabilityLifecycle(self.capability_registry, recorder=self.lifecycle_store.record); self.canary_monitor = CanaryMonitor(self.capability_lifecycle, canary_policy); self.capability_decisions = CapabilityDecisionEngine(self.capability_registry, self.capability_discovery); self.refresh_local_inventory()
        self.education = EducationEngine(); self.education_specialist = EducationSpecialist(self.plugins, self.education); self.teaching = TeachingEngine(); self.outcomes = OutcomeEngine(); self.education_feedback = EducationFeedbackBridge(self.outcomes)
        self.control = OwnerControlCenter(self); self.orchestrator.register("education.record_assessment", self._record_assessment_action)

    def _configure_live_providers(self) -> None:
        gemini, wikipedia = configured_live_providers(); self.register_research_provider(wikipedia.provider_id, wikipedia, priority=1000)
        if gemini is not None: self.register_generation_provider(gemini.provider_id, gemini, priority=1000)
    def refresh_local_inventory(self) -> tuple[ResourceDescriptor, ...]:
        resources = local_resources(); [self.resource_registry.register(r) for r in resources]; [self.capability_registry.register(c) for c in local_capabilities()]; return resources
    def register_capability(self, capability: CapabilityDescriptor) -> None: self.capability_registry.register(capability)
    def register_resource(self, resource: ResourceDescriptor) -> None: self.resource_registry.register(resource)
    def decide_resource(self, request: ResourceRequest) -> ResourceDecision: return self.resource_manager.decide(request)
    def reserve_resource(self, request: ResourceRequest) -> ResourceDecision: return self.resource_manager.reserve(request)
    def release_resource(self, reservation_id: str) -> None: self.resource_manager.release(reservation_id)
    def resource_reservations(self) -> tuple[tuple[str, str, float], ...]: return self.resource_manager.active_reservations()
    def create_capability_gap(self, requirement: CapabilityRequirement, gap_id: str | None = None) -> CapabilityGap: return self.capability_discovery.discover(requirement, gap_id=gap_id).gap
    def resolve_capability_gap(self, requirement: CapabilityRequirement, *, gap_id: str | None = None) -> DiscoveryResult: return self.capability_discovery.discover(requirement, gap_id=gap_id)
    def discover_capabilities(self, requirement: CapabilityRequirement, *, gap_id: str | None = None) -> DiscoveryResult: return self.resolve_capability_gap(requirement, gap_id=gap_id)
    def decide_capability(self, requirement: CapabilityRequirement) -> CapabilityDecision: return self.capability_decisions.decide(requirement)
    def evaluate_canary(self, capability_id: str, health: CanaryHealth): return self.canary_monitor.evaluate(capability_id, health)
    def capability_observations(self, scope_id: str) -> tuple[Observation, ...]:
        if not isinstance(scope_id, str) or not scope_id.strip(): raise ValueError("scope_id is required")
        return (Observation(scope_id, "capability_inventory", tuple(self.capability_registry.get(cid) for cid in self.capability_registry.ids())), Observation(scope_id, "resource_inventory", self.resource_registry.all()), Observation(scope_id, "capability_gaps", tuple(self.capability_discovery.gaps.all())), Observation(scope_id, "resource_reservations", self.resource_manager.active_reservations()))
    def lifecycle_history(self, capability_id: str | None = None): return self.lifecycle_store.history(capability_id)
    def begin_recovery(self, scope: str, authorization: RecoveryRequest): return self.security.begin_recovery(scope, authorization)
    def restore(self, scope: str, checks: tuple[str, ...]): return self.security.restore(scope, checks)
    def close(self) -> None: self.lifecycle_store.close()
    def _record_assessment_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        assessment = payload.get("assessment")
        if not isinstance(assessment, Assessment): raise TypeError("assessment payload is required")
        progress = self.education.record_assessment(assessment); self.outcomes.record(assessment)
        return {"scope_id": progress.scope_id, "learner_id": progress.learner_id, "domain": progress.domain, "mastered_skills": progress.mastered_skills}
    def record_education_assessment(self, assessment: Assessment, *, owner_approved: bool = False):
        from ..core.contracts import ActionRequest, ActionRisk
        return self.execute(ActionRequest("education.record_assessment", ActionRisk.LOW, "record learner assessment", {"scope_id": assessment.scope_id, "assessment": assessment}), owner_approved=owner_approved)
    def education_outcome_summary(self, scope_id: str, learner_id: str, domain: str) -> OutcomeSummary: return self.outcomes.summary(scope_id, learner_id, domain)
    def education_feedback_observer(self, scope_id: str): return self.education_feedback.observe(scope_id)
    def register_action(self, action: str, handler: Any) -> None: self.orchestrator.register(action, handler)
    def execute(self, request: Any, *, owner_approved: bool = False, value: float = 0.0): return self.orchestrator.execute(request, owner_approved=owner_approved, value=value)
    def bounded_operation_engine(self):
        from ..operations.bounded import BoundedOperationEngine
        return BoundedOperationEngine(self)
    def run_bounded_operation(self, operation: Any, **kwargs: Any):
        return self.bounded_operation_engine().run(operation, **kwargs)
    def autonomous_engine(self, observer: Observer, planner: Planner, verifier: Verifier, recorder: Recorder | None = None) -> AutonomousEngine: return AutonomousEngine(self.orchestrator, observer, planner, verifier, recorder)
    def autonomous_education_feedback(self, planner: Planner, verifier: Verifier, recorder: Recorder | None = None) -> AutonomousEngine: return AutonomousEngine(self.orchestrator, self.education_feedback_observer, planner, verifier, recorder)
    def autonomous_capability_inventory(self, planner: Planner, verifier: Verifier, recorder: Recorder | None = None) -> AutonomousEngine: return AutonomousEngine(self.orchestrator, self.capability_observations, planner, verifier, recorder)
    def education_integration(self, **adapters: object) -> EducationSubsystemIntegration: return EducationSubsystemIntegration(**adapters)
    def education_signals(self, scope_id: str, domain: str, *, learner_id: str = "", **adapters: object) -> EducationIntegrationResult: return self.education_integration(**adapters).collect(scope_id, domain, learner_id=learner_id)
    def register_teaching_profile(self, profile: TeachingProfile) -> TeachingProfile: return self.teaching.register_profile(profile)
    def teaching_profile(self, channel_id: str) -> TeachingProfile | None: return self.teaching.profile(channel_id)
    def teach(self, scope_id: str, learner_id: str, profile: TeachingProfile, lesson: Any, *, mode: EducationMode = EducationMode.COURSE, progress: Any = None) -> TeachingResponse: return self.teaching.teach(scope_id, learner_id, profile, lesson, mode=mode, progress=progress)
    def mentor_prompt(self, profile: TeachingProfile, goal: str, progress: Any = None) -> str: return self.teaching.mentor_prompt(profile, goal, progress)
    def generate(self, request: GenerationRequest): return self.live_providers.generate(request)
    def research(self, request: ResearchRequest): return self.live_providers.research(request)
    def register_generation_provider(self, provider_id: str, provider: Any, *, priority: int = 100) -> None:
        from ..providers.contracts import ProviderCapability
        self.live_providers.register(provider_id, provider, ProviderCapability.GENERATION, priority=priority)
    def register_research_provider(self, provider_id: str, provider: Any, *, priority: int = 100) -> None:
        from ..providers.contracts import ProviderCapability
        self.live_providers.register(provider_id, provider, ProviderCapability.RESEARCH, priority=priority)
    def snapshot(self, scope_id: str) -> RuntimeSnapshot:
        if not isinstance(scope_id, str) or not scope_id.strip(): raise ValueError("scope_id is required")
        plugins = tuple((plugin_id, state.value, generation) for plugin_id, state, generation in self.plugins.status())
        return RuntimeSnapshot(scope_id, self.context.state.state.value, self.context.snapshot_metrics(), plugins, self.monitoring.overall_state(scope_id).value, len(self.audit.history()))

# Backward compatibility: legacy internal imports remain valid while DORMAMMU
# is the canonical public identity.
DEVINTELRuntime = DORMAMMURuntime
