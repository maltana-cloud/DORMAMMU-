from devintel.modules.creative import AssetKind, CreativeBrief, CreativeLineageStore, CreativePipeline, CreativeProvider, CreativeProviderRegistry
from devintel.modules.creative.verification import CreativeSafetyGate, CreativeVerifier

def brief(purpose="Explain a complex idea"):
    return CreativeBrief(purpose, "learners", AssetKind.VIDEO, constraints=("respect copyright",), success_criteria=("clear",), evidence_refs=("claim:1",))

def test_verification_passes_structurally_valid_plan():
    b = brief(); plan = __import__("devintel.modules.creative", fromlist=["CreativeIntelligence"]).CreativeIntelligence().plan(b)
    result = CreativeVerifier().verify(b, plan)
    assert result.passed and result.score >= .85 and not result.defects

def test_safety_gate_requires_review_for_external_authority_terms():
    allowed, reasons = CreativeSafetyGate().assess(brief("publish the generated video"))
    assert not allowed and reasons

def test_pipeline_marks_restricted_creative_request_unverified():
    providers = CreativeProviderRegistry((CreativeProvider("local", "Local", (AssetKind.VIDEO,), approved=True),))
    result = CreativePipeline(providers=providers).run(brief("publish the generated video"))
    assert not result.verification.passed and result.verification.requires_review

def test_lineage_survives_reopen(tmp_path):
    path = str(tmp_path / "creative.sqlite")
    store = CreativeLineageStore(path=path)
    b = brief(); plan = __import__("devintel.modules.creative", fromlist=["CreativeIntelligence"]).CreativeIntelligence().plan(b)
    import hashlib
    pd = __import__("devintel.modules.creative", fromlist=["plan_digest"]).plan_digest(plan); bd = __import__("devintel.modules.creative", fromlist=["brief_digest"]).brief_digest(b)
    ad = hashlib.sha256(pd.encode()).hexdigest(); from devintel.modules.creative import CreativeLineageRecord
    store.record(CreativeLineageRecord(ad, pd, bd, b.evidence_refs, 0, store.now())); store.close()
    reopened = CreativeLineageStore(path=path)
    assert reopened.get(ad).evidence_refs == ("claim:1",)
    reopened.close()
