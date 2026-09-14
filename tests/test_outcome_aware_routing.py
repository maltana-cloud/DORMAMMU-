from datetime import datetime, timezone

from devintel.autonomy.learning import OutcomeEvidence, OutcomeLearner
from devintel.autonomy.learning_store import LearningStore
from devintel.executive.outcome_routing import OutcomeAwareRoutingService
from devintel.executive.routing import SpecialistDescriptor, SpecialistKind, SpecialistRouter, RoutingRequirement


def _evidence(subject: str, cycle: str, metric: float) -> OutcomeEvidence:
    return OutcomeEvidence("scope-a", cycle, metric > 0, True, metric, subject_id=subject, recorded_at=datetime.now(timezone.utc))


def test_verified_outcomes_can_create_bounded_routing_preference():
    store = LearningStore()
    router = SpecialistRouter()
    router.register(SpecialistDescriptor("model-a", SpecialistKind.MODEL, "p", "1", ("research",), cost=1))
    router.register(SpecialistDescriptor("model-b", SpecialistKind.MODEL, "p", "1", ("research",), cost=1))
    service = OutcomeAwareRoutingService(router, store, OutcomeLearner(min_samples=3))
    for i in range(3): service.record_and_reflect(_evidence("model-b", f"c{i}", 1.0))
    assert service.select("scope-a", RoutingRequirement("research", ("research",))).specialist.specialist_id == "model-b"


def test_learning_cannot_override_hard_routing_gates():
    store = LearningStore(); router = SpecialistRouter()
    router.register(SpecialistDescriptor("approved", SpecialistKind.MODEL, "p", "1", ("research",), cost=1, approved=True))
    router.register(SpecialistDescriptor("unapproved", SpecialistKind.MODEL, "p", "1", ("research",), cost=0, approved=False))
    service = OutcomeAwareRoutingService(router, store, OutcomeLearner(min_samples=1))
    service.record_and_reflect(_evidence("unapproved", "c1", 1.0))
    assert service.select("scope-a", RoutingRequirement("research", ("research",))).specialist.specialist_id == "approved"


def test_learning_is_durable_across_reopen(tmp_path):
    path = str(tmp_path / "learning.db")
    store = LearningStore(path)
    service = OutcomeAwareRoutingService(SpecialistRouter(), store, OutcomeLearner(min_samples=1))
    service.record_and_reflect(_evidence("model-a", "c1", 0.5))
    store.close()
    reopened = LearningStore(path)
    assert reopened.proposals("scope-a")[0].subject_id == "model-a"
    reopened.close()
