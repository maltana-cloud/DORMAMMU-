import pytest
from devintel.modules.economics import *

def opp(value=1000): return Opportunity("o1",OpportunityKind.BUSINESS,"Test","bounded opportunity",value,"USD",(EconomicEvidence("src","claim",.9),))
def test_analysis_is_deterministic():
    e=EconomicEngine(); assert e.analyze(opp())==e.analyze(opp())
def test_plan_and_digest():
    p=EconomicEngine().plan(opp(),objective="validate demand",assumptions=("price stable",),actions=("research",),expected_cost=100)
    assert digest_plan(p)==digest_plan(p)
def test_compare_prefers_net_value():
    e=EconomicEngine(); a=e.plan(opp(1000),objective="a",expected_cost=100); b=e.plan(Opportunity("o2",OpportunityKind.SERVICE,"B","b",950),objective="b",expected_cost=10)
    assert e.compare((a,b)) is b
def test_policy_fail_closed_for_money():
    p=EconomicPolicy(); assert not p.decide(EconomicAction.SPEND,evidence_score=1).allowed
    assert p.decide(EconomicAction.PLAN,evidence_score=.8).allowed
    assert not p.decide(EconomicAction.PLAN,evidence_score=.1).allowed
def test_bounds():
    with pytest.raises(ValueError): validate_amount(1_000_000_001)
def test_persistence(tmp_path):
    s=EconomicPlanStore(str(tmp_path/'plans.db')); p=EconomicEngine().plan(opp(),objective='x'); d=s.save(p); assert s.get_digest(p.plan_id)==d; assert s.count()==1; s.close()
def test_runtime_integration(tmp_path):
    from devintel.runtime.app import DORMAMMURuntime
    r=DORMAMMURuntime(operation_store_path=str(tmp_path/'ops.db')); x=EconomicSubsystemIntegration(r,str(tmp_path/'eco.db')); p,d=x.plan(opp(),objective='x'); assert d==digest_plan(p); assert r.operation_history('economic.business.intelligence'); x.close(); r.close()
