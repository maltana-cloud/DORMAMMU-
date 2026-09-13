"""Composition root connecting DORMAMMU's bounded subsystems."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..autonomy.engine import AutonomousEngine, Observer, Planner, Verifier, Recorder
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
from ..modules.specialists.education import EducationSpecialist
from ..providers.live import GenerationRequest, ProviderRouter, ResearchRequest
from ..providers.live_adapters import configured_live_providers
from ..providers.registry import ProviderRegistry

@dataclass(frozen=True)
class RuntimeSnapshot:
    """Owner-facing operational snapshot; observations never grant authority."""
    scope_id: str
    runtime_state: str
    metrics: dict[str, int]
    plugin_status: tuple[tuple[str, str, int], ...]
    monitoring_state: str
    audit_events: int

class DEVINTELRuntime:
    """Single composition root for DORMAMMU bounded subsystems.

    ``DEVINTELRuntime`` remains the public Python class name for backward
    compatibility. DORMAMMU is the canonical product identity.
    """
    def __init__(self) -> None:
        self.context = RuntimeContext()
        self.audit = AuditLog()
        self.orchestrator = Orchestrator(runtime=self.context, audit=self.audit)
        self.security = SecurityOrchestrator(events=self.context.events, audit=self.audit, runtime_state=self.context.state)
        self.monitoring = MonitoringEngine()
        self.plugins = PluginService()
        self.providers = ProviderRegistry()
        self.live_providers = ProviderRouter()
        self._configure_live_providers()
        self.education = EducationEngine()
        self.education_specialist = EducationSpecialist(self.plugins, self.education)
        self.teaching = TeachingEngine()
        self.outcomes = OutcomeEngine()
        self.education_feedback = EducationFeedbackBridge(self.outcomes)
        self.control = OwnerControlCenter(self)
        self.orchestrator.register("education.record_assessment", self._record_assessment_action)

    def _configure_live_providers(self) -> None:
        """Register defaults at low precedence; explicit host registrations win."""
        gemini, wikipedia = configured_live_providers()
        self.register_research_provider(wikipedia.provider_id, wikipedia, priority=1000)
        if gemini is not None:
            self.register_generation_provider(gemini.provider_id, gemini, priority=1000)

    def _record_assessment_action(self, payload: dict[str, Any]) -> dict[str, Any]:
        assessment = payload.get("assessment")
        if not isinstance(assessment, Assessment): raise TypeError("assessment payload is required")
        progress = self.education.record_assessment(assessment)
        self.outcomes.record(assessment)
        return {"scope_id": progress.scope_id, "learner_id": progress.learner_id, "domain": progress.domain, "mastered_skills": progress.mastered_skills}

    def record_education_assessment(self, assessment: Assessment, *, owner_approved: bool = False):
        """Record verified learning feedback through the core permission path."""
        from ..core.contracts import ActionRequest, ActionRisk
        request = ActionRequest("education.record_assessment", ActionRisk.LOW, "record learner assessment", {"scope_id": assessment.scope_id, "assessment": assessment})
        return self.execute(request, owner_approved=owner_approved)

    def education_outcome_summary(self, scope_id: str, learner_id: str, domain: str) -> OutcomeSummary:
        return self.outcomes.summary(scope_id, learner_id, domain)

    def education_feedback_observer(self, scope_id: str):
        return self.education_feedback.observe(scope_id)

    def register_action(self, action: str, handler: Any) -> None:
        self.orchestrator.register(action, handler)

    def execute(self, request: Any, *, owner_approved: bool = False, value: float = 0.0):
        return self.orchestrator.execute(request, owner_approved=owner_approved, value=value)

    def autonomous_engine(self, observer: Observer, planner: Planner, verifier: Verifier, recorder: Recorder | None = None) -> AutonomousEngine:
        return AutonomousEngine(self.orchestrator, observer, planner, verifier, recorder)

    def autonomous_education_feedback(self, planner: Planner, verifier: Verifier, recorder: Recorder | None = None) -> AutonomousEngine:
        return AutonomousEngine(self.orchestrator, self.education_feedback_observer, planner, verifier, recorder)

    def education_integration(self, **adapters: object) -> EducationSubsystemIntegration:
        return EducationSubsystemIntegration(**adapters)

    def education_signals(self, scope_id: str, domain: str, *, learner_id: str = "", **adapters: object) -> EducationIntegrationResult:
        return self.education_integration(**adapters).collect(scope_id, domain, learner_id=learner_id)

    def register_teaching_profile(self, profile: TeachingProfile) -> TeachingProfile:
        return self.teaching.register_profile(profile)

    def teaching_profile(self, channel_id: str) -> TeachingProfile | None:
        return self.teaching.profile(channel_id)

    def teach(self, scope_id: str, learner_id: str, profile: TeachingProfile, lesson: Any, *, mode: EducationMode = EducationMode.COURSE, progress: Any = None) -> TeachingResponse:
        return self.teaching.teach(scope_id, learner_id, profile, lesson, mode=mode, progress=progress)

    def mentor_prompt(self, profile: TeachingProfile, goal: str, progress: Any = None) -> str:
        return self.teaching.mentor_prompt(profile, goal, progress)

    def generate(self, request: GenerationRequest):
        """Generate through the provider router; output is not truth-verified here."""
        return self.live_providers.generate(request)

    def research(self, request: ResearchRequest):
        """Retrieve research through replaceable providers; verification stays separate."""
        return self.live_providers.research(request)

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
