from __future__ import annotations

from devintel.capabilities.contracts import ResourceDescriptor, ResourceKind
from devintel.providers.contracts import ProviderHealth
from devintel.providers.live import GenerationRequest, GenerationResponse, ResearchRequest, ResearchResult
from devintel.runtime import DORMAMMURuntime


class ResearchProvider:
    provider_id = "test-research"

    def health(self):
        return ProviderHealth(self.provider_id, True, "ready")

    def search(self, request: ResearchRequest):
        return (
            ResearchResult(
                "https://example.com/evidence",
                title="Evidence",
                content="A bounded research document.",
                source="Example Publisher",
            ),
        )


class GenerationProvider:
    provider_id = "test-generation"

    def health(self):
        return ProviderHealth(self.provider_id, True, "ready")

    def generate(self, request: GenerationRequest):
        return GenerationResponse("generated", self.provider_id)


def test_runtime_acquisition_preserves_provenance_and_verified_claims():
    runtime = DORMAMMURuntime()
    try:
        runtime.register_research_provider("test-research", ResearchProvider(), priority=1)
        acquired = runtime.acquire_evidence("bounded evidence", max_results=2)
        assert acquired.accepted == 1
        assert acquired.documents[0].metadata["evidence_provider_id"] == "test-research"
        assert acquired.documents[0].metadata["evidence_unverified"] == "true"

        claim = runtime.verified_claim(
            "https://example.com/evidence",
            subject="system",
            predicate="has evidence",
            object_value="document",
            confidence=0.9,
            evidence=("https://example.com/evidence",),
        )
        assert claim.verification.verified
        assert claim.evidence_urls == ("https://example.com/evidence",)
    finally:
        runtime.close()


def test_runtime_verified_claim_fails_closed_without_provenance():
    runtime = DORMAMMURuntime()
    try:
        runtime.register_research_provider("test-research", ResearchProvider(), priority=1)
        runtime.acquire_evidence("bounded evidence", max_results=1)
        try:
            runtime.verified_claim(
                "https://example.com/evidence",
                subject="system",
                predicate="has evidence",
                object_value="document",
                confidence=0.9,
            )
        except ValueError as exc:
            assert "verification" in str(exc)
        else:
            raise AssertionError("unverified claim must fail closed")
    finally:
        runtime.close()


def test_runtime_resource_execution_releases_lease():
    runtime = DORMAMMURuntime()
    try:
        runtime.register_generation_provider("test-generation", GenerationProvider(), priority=1)
        runtime.register_resource(
            ResourceDescriptor(
                "test-api",
                ResourceKind.API,
                "Test API",
                capacity="1",
                availability="ready",
                permissions=("approved",),
            )
        )
        result = runtime.execute_generation_with_resource(
            GenerationRequest("test", max_tokens=16),
            resource_kind=ResourceKind.API,
        )
        assert result.result.success
        assert result.resource_id == "test-api"
        assert result.reservation_id
        assert runtime.resource_reservations() == ()
    finally:
        runtime.close()


def test_runtime_resource_execution_fails_closed_without_capacity():
    runtime = DORMAMMURuntime()
    try:
        runtime.register_generation_provider("test-generation", GenerationProvider(), priority=1)
        result = runtime.execute_generation_with_resource(GenerationRequest("test", max_tokens=16))
        assert not result.result.success
        assert "resource" in result.result.error
        assert result.reservation_id is None
    finally:
        runtime.close()
