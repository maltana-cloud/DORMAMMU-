"""Runtime integration for bounded economic intelligence."""
from __future__ import annotations
from .contracts import Opportunity
from .engine import EconomicEngine
from .persistence import EconomicPlanStore
class EconomicSubsystemIntegration:
    def __init__(self,runtime,store_path=":memory:"):
        self.runtime=runtime; self.engine=EconomicEngine(); self.store=EconomicPlanStore(store_path)
    def plan(self,opportunity:Opportunity,**kwargs):
        plan=self.engine.plan(opportunity,**kwargs); digest=self.store.save(plan)
        self.runtime.record_operation_observation_from_result("economic:"+plan.plan_id,"economic.business.intelligence","plan",True,True,0.0,"business plan verified",None,None)
        return plan,digest
    def analyze(self,opportunity:Opportunity):return self.engine.analyze(opportunity)
    def close(self):self.store.close()
