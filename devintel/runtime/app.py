"""Composition root connecting DORMAMMU's bounded subsystems."""
from __future__ import annotations
from dataclasses import dataclass
import os
from typing import Any, Sequence
from ..autonomy.engine import AutonomousEngine, Observer, Planner, Verifier, Recorder
from ..autonomy.store import AutonomousCycleStore
from ..autonomy.contracts import Observation
from ..capabilities import (AcquisitionPlan, CapabilityAcquisition, CapabilityDescriptor, CapabilityDiscovery, CapabilityGap, CapabilityLifecycle, CapabilityRegistry, CapabilityRequirement, DiscoveryResult, ResourceDescriptor, ResourceRegistry, LifecycleStore, CapabilityDecision, CapabilityDecisionEngine, CanaryDecision, CanaryHealth, CanaryMonitor, CanaryPolicy, ResourceDecision, ResourceManager, ResourceRequest, ResourceLeaseStore)
from ..capabilities.contracts import CapabilityStatus
from ..capabilities.inventory import local_capabilities, local_resources
from ..control.service import OwnerControlCenter
from ..core.audit import AuditLog
from ..core.orchestrator import Orchestrator
from ..core.runtime import RuntimeContext
from ..executive import ExecutiveEngine, ExecutivePlan, ExecutiveResult, Objective, TaskSpec, EvidenceBackedUnderstanding
from ..modules.creative import CreativeBrief, CreativePipeline, CreativeProvider, CreativeProviderRegistry, CreativeResult
from ..modules.education.contracts import Assessment, EducationMode
from ..modules.education.engine import EducationEngine
from ..modules.education.integrations import EducationIntegrationResult, EducationSubsystemIntegration
from ..modules.education.outcomes import EducationFeedbackBridge, OutcomeEngine, OutcomeSummary
from ..modules.education.teaching import TeachingEngine, TeachingProfile, TeachingResponse
from ..modules.monitoring.engine import MonitoringEngine
from ..modules.plugins.service import PluginService
from ..modules.research import KnowledgeSynthesisEngine, SynthesisResult, VerifiedClaim
from ..modules.security.orchestrator import SecurityOrchestrator
from ..modules.security.recovery import CryptographicRecovery, RecoveryRequest
from ..modules.specialists.education import EducationSpecialist
from ..operations.telemetry import OperationObservation, OperationalTelemetryStore
from ..providers.contracts import ProviderCapability
from ..providers.live import GenerationRequest, ProviderRouter, ResearchRequest
from ..providers.live_adapters import configured_live_providers
from ..providers.registry import ProviderRegistry

@dataclass(frozen=True)
class RuntimeSnapshot:
    scope_id: str
    runtime_state: str
    metrics: dict[str, int]
    plugin_status: tuple[tuple[str, str, int], ...]
    monitoring_state: str
    audit_events: int

class DORMAMMURuntime:
    """Single composition root for DORMAMMU bounded subsystems."""
    def __init__(self, *, lifecycle_store_path: str = ":memory:", operation_store_path: str = ":memory:", resource_lease_store_path: str = ":memory:", autonomy_store_path: str = ":memory:", recovery_secret: bytes | None = None, canary_policy: CanaryPolicy | None = None) -> None:
        self.context = RuntimeContext(); self.audit = AuditLog(); self.orchestrator = Orchestrator(runtime=self.context, audit=self.audit)
        secret = recovery_secret
        if secret is None and os.environ.get("DORMAMMU_RECOVERY_SECRET"): secret = bytes.fromhex(os.environ["DORMAMMU_RECOVERY_SECRET"])
        self.recovery = CryptographicRecovery(secret) if secret is not None else None
        self.security = SecurityOrchestrator(events=self.context.events, audit=self.audit, runtime_state=self.context.state, recovery=self.recovery); self.monitoring = MonitoringEngine(); self.plugins = PluginService()
        self.providers = ProviderRegistry(); self.live_providers = ProviderRouter(); self._configure_live_providers()
        self.capability_registry = CapabilityRegistry(); self.resource_registry = ResourceRegistry(); self.resource_lease_store = ResourceLeaseStore(resource_lease_store_path); self.resource_manager = ResourceManager(self.resource_registry, self.resource_lease_store); self.capability_discovery = CapabilityDiscovery(registry=self.capability_registry)
        self.lifecycle_store = LifecycleStore(lifecycle_store_path); self.operation_store = OperationalTelemetryStore(operation_store_path); self.autonomy_store = AutonomousCycleStore(autonomy_store_path); self.capability_lifecycle = CapabilityLifecycle(self.capability_registry, recorder=self.lifecycle_store.record); self.canary_monitor = CanaryMonitor(self.capability_lifecycle, canary_policy); self.capability_decisions = CapabilityDecisionEngine(self.capability_registry, self.capability_discovery); self.capability_acquisition = CapabilityAcquisition(self.capability_discovery, self.capability_lifecycle); self.refresh_local_inventory()
        self.executive = ExecutiveEngine(self); self.knowledge_synthesis = KnowledgeSynthesisEngine()
        self.creative_providers = CreativeProviderRegistry(); self.creative = CreativePipeline(providers=self.creative_providers)
        self.education = EducationEngine(); self.education_specialist = EducationSpecialist(self.plugins, self.education); self.teaching = TeachingEngine(); self.outcomes = OutcomeEngine(); self.education_feedback = EducationFeedbackBridge(self.outcomes)
        self.control = OwnerControlCenter(self); self.orchestrator.register("education.record_assessment", self._record_assessment_action)

    def _configure_live_providers(self) -> None:
        gemini, wikipedia = configured_live_providers(); self.register_research_provider(wikipedia.provider_id, wikipedia, priority=1000)
        if gemini is not None: self.register_generation_provider(gemini.provider_id, gemini, priority=1000)
    def refresh_local_inventory(self) -> tuple[ResourceDescriptor, ...]:
        resources = local_resources(); [self.resource_registry.register(r) for r in resources]; [self.capability_registry.register(c) for c in local_capabilities()]; return resources
    def register_capability(self, capability: CapabilityDescriptor) -> None: self.capability_registry.register(capability)
    def register_resource(self, resource: ResourceDescriptor) -> None: self.resource_registry.register(resource)
    def register_research_provider(self, provider_id: str, provider: Any, *, priority: int = 100) -> None: self.live_providers.register(provider_id, provider, ProviderCapability.RESEARCH, priority=priority)
    def register_generation_provider(self, provider_id: str, provider: Any, *, priority: int = 100) -> None: self.live_providers.register(provider_id, provider, ProviderCapability.GENERATION, priority=priority)
    def register_creative_provider(self, provider: CreativeProvider) -> None: self.creative_providers.register(provider)
    def creative_plan(self, brief: CreativeBrief) -> CreativeResult: return self.creative.run(brief)
    def snapshot(self, scope_id: str) -> RuntimeSnapshot:
        if not isinstance(scope_id, str) or not scope_id.strip(): raise ValueError("scope_id is required")
        plugins = tuple((plugin_id, state.value, generation) for plugin_id, state, generation in self.plugins.status())
        return RuntimeSnapshot(scope_id, self.context.state.state.value, self.context.snapshot_metrics(), plugins, self.monitoring.overall_state(scope_id).value, len(self.audit.history()))
    def decide_resource(self, request: ResourceRequest) -> ResourceDecision: return self.resource_manager.decide(request)
    def reserve_resource(self, request: ResourceRequest) -> ResourceDecision: return self.resource_manager.reserve(request)
    def release_resource(self, reservation_id: str) -> None: self.resource_manager.release(reservation_id)
    def resource_reservations(self) -> tuple[tuple[str, str, float], ...]: return self.resource_manager.active_reservations()
    def record_operation_observation(self, observation: OperationObservation) -> None: self.operation_store.record(observation)
    def record_operation_observation_from_result(self, operation_id: str, capability_id: str, stage: str, success: bool, verified: bool, duration_ms: float, message: str, resource_id: str | None = None, resource_quantity: float | None = None) -> None: self.record_operation_observation(OperationObservation(operation_id, capability_id, stage, success, verified, duration_ms, message, resource_id, resource_quantity))
    def operation_history(self, capability_id: str | None = None, *, limit: int = 100) -> tuple[OperationObservation, ...]: return self.operation_store.history(capability_id, limit)
    def operational_health(self, capability_id: str, *, window: int = 20, min_samples: int = 5) -> CanaryHealth | None: return self.operation_store.health(capability_id, window=window, min_samples=min_samples)
    def evaluate_operational_health(self, capability_id: str, *, window: int = 20, min_samples: int = 5) -> CanaryDecision:
        health = self.operational_health(capability_id, window=window, min_samples=min_samples)
        if health is None: raise RuntimeError("insufficient operational observations for health evaluation")
        capability = self.capability_registry.get(capability_id)
        if capability is None: raise KeyError(capability_id)
        if capability.status is CapabilityStatus.ACTIVE and health.healthy: return CanaryDecision(capability_id, CapabilityStatus.ACTIVE, False, False, "operational health verified from recorded observations")
        return self.evaluate_canary(capability_id, health)
    def create_capability_gap(self, requirement: CapabilityRequirement, gap_id: str | None = None) -> CapabilityGap: return self.capability_discovery.discover(requirement, gap_id=gap_id).gap
    def resolve_capability_gap(self, requirement: CapabilityRequirement, *, gap_id: str | None = None) -> DiscoveryResult: return self.capability_discovery.discover(requirement, gap_id=gap_id)
    def discover_capabilities(self, requirement: CapabilityRequirement, *, gap_id: str | None = None) -> DiscoveryResult: return self.resolve_capability_gap(requirement, gap_id=gap_id)
    def plan_capability_acquisition(self, requirement: CapabilityRequirement, *, gap_id: str | None = None) -> AcquisitionPlan: return self.capability_acquisition.plan(requirement, gap_id=gap_id)
    def approve_capability_acquisition(self, plan: AcquisitionPlan, *, owner_approved: bool = False) -> CapabilityDescriptor: return self.capability_acquisition.approve_and_register(plan, owner_approved=owner_approved)
    def capability_fallback(self, plan: AcquisitionPlan, failed_capability_id: str): return self.capability_acquisition.fallback_plan(plan, failed_capability_id)
    def decide_capability(self, requirement: CapabilityRequirement) -> CapabilityDecision: return self.capability_decisions.decide(requirement)
    def evaluate_canary(self, capability_id: str, health: CanaryHealth): return self.canary_monitor.evaluate(capability_id, health)
    def capability_observations(self, scope_id: str) -> tuple[Observation, ...]:
        if not isinstance(scope_id, str) or not scope_id.strip(): raise ValueError("scope_id is required")
        return (Observation(scope_id, "capability_inventory", tuple(self.capability_registry.get(cid) for cid in self.capability_registry.ids())), Observation(scope_id, "resource_inventory", self.resource_registry.all()), Observation(scope_id, "capability_gaps", tuple(self.capability_discovery.gaps.all())), Observation(scope_id, "resource_reservations", self.resource_manager.active_reservations()))
    def lifecycle_history(self, capability_id: str | None = None): return self.lifecycle_store.history(capability_id)
    def synthesize_knowledge(self, topic: str, claims: Sequence[VerifiedClaim], *, excluded_claims: int = 0) -> SynthesisResult: return self.knowledge_synthesis.synthesize(topic, claims, excluded_claims=excluded_claims)
    def evidence_backed_understanding(self, objective: Objective, synthesis: SynthesisResult) -> EvidenceBackedUnderstanding: return self.executive.evidence_adapter.understand(objective, synthesis)
    def plan_from_synthesis(self, objective: Objective, synthesis: SynthesisResult, tasks: tuple[TaskSpec, ...]) -> ExecutivePlan: return self.executive.plan_from_synthesis(objective, synthesis, tasks)
    def run_objective_from_synthesis(self, objective: Objective, synthesis: SynthesisResult, tasks: tuple[TaskSpec, ...], **kwargs: Any) -> ExecutiveResult: return self.executive.execute_from_synthesis(objective, synthesis, tasks, **kwargs)
    def begin_recovery(self, scope: str, authorization: RecoveryRequest): return self.security.begin_recovery(scope, authorization)
    def restore(self, scope: str, checks: tuple[str, ...]): return self.security.restore(scope, checks)
    def autonomous_cycle_history(self, scope_id: str | None = None, *, limit: int = 100): return self.autonomy_store.history(scope_id, limit=limit)
    def close(self) -> None: self.operation_store.close(); self.lifecycle_store.close(); self.resource_lease_store.close(); self.autonomy_store.close()
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
    def run_bounded_operation(self, operation: Any, **kwargs: Any): return self.bounded_operation_engine().run(operation, **kwargs)
    def plan_objective(self, objective: Objective, tasks: tuple[TaskSpec, ...]) -> ExecutivePlan: return self.executive.plan(objective, tasks)
    def run_objective(self, objective: Objective, tasks: tuple[TaskSpec, ...], **kwargs: Any) -> ExecutiveResult: return self.executive.execute(objective, tasks, **kwargs)
    def autonomous_engine(self, observer: Observer, planner: Planner, verifier: Verifier, recorder: Recorder | None = None, *, improver=None, max_actions: int = 32) -> AutonomousEngine: return AutonomousEngine(self.orchestrator, observer, planner, verifier, recorder or self.autonomy_store.record, improver, max_actions=max_actions)
    def autonomous_education_feedback(self, planner: Planner, verifier: Verifier, recorder: Recorder | None = None, *, improver=None, max_actions: int = 32) -> AutonomousEngine: return self.autonomous_engine(self.education_feedback_observer, planner, verifier, recorder, improver=improver, max_actions=max_actions)
    def autonomous_capability_inventory(self, planner: Planner, verifier: Verifier, recorder: Recorder | None = None, *, improver=None, max_actions: int = 32) -> AutonomousEngine: return self.autonomous_engine(self.capability_observations, planner, verifier, recorder, improver=improver, max_actions=max_actions)
    def education_integration(self, **adapters: object) -> EducationSubsystemIntegration: return EducationSubsystemIntegration(**adapters)
    def education_signals(self, scope_id: str, domain: str, *, learner_id: str = "", **adapters: object) -> EducationIntegrationResult: return self.education_integration(**adapters).collect(scope_id, domain, learner_id=learner_id)
    def register_teaching_profile(self, profile: TeachingProfile) -> TeachingProfile: return self.teaching.register_profile(profile)
    def teaching_profile(self, channel_id: str) -> TeachingProfile | None: return self.teaching.profile(channel_id)
    def teach(self, scope_id: str, learner_id: str, profile: TeachingProfile, lesson: Any, *, mode: EducationMode = EducationMode.COURSE, progress: Any = None) -> TeachingResponse: return self.teaching.teach(scope_id, learner_id, profile, lesson, mode=mode, progress=progress)
    def mentor_prompt(self, profile: TeachingProfile, goal: str, progress: Any = None) -> str: return self.teaching.mentor_prompt(profile, goal, progress)
    def generate(self, request: GenerationRequest): return self.live_providers.generate(request)
    def research(self, request: ResearchRequest): return self.live_providers.research(request)

DEVINTELRuntime = DORMAMMURuntime
