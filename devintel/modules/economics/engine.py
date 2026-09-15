"""Deterministic economic analysis and business planning."""
from __future__ import annotations
from .contracts import *

class EconomicEngine:
    def analyze(self, opportunity:Opportunity)->tuple[EconomicSignal,...]:
        evidence=tuple(e.source_id for e in opportunity.evidence if 0.0<=e.confidence<=1.0)
        quality=min(1.0, len(evidence)/3.0)
        value=min(1.0, opportunity.estimated_value/MAX_AMOUNT) if opportunity.estimated_value>=0 else 0.0
        return (EconomicSignal(opportunity.opportunity_id,"evidence_quality",quality,evidence), EconomicSignal(opportunity.opportunity_id,"value_scale",value,evidence))
    def plan(self, opportunity:Opportunity, *, objective:str, assumptions:tuple[str,...]=(), actions:tuple[str,...]=(), expected_cost:float=0.0)->BusinessPlan:
        cost=validate_amount(expected_cost); value=validate_amount(opportunity.estimated_value)
        if not objective.strip(): raise ValueError("objective is required")
        if len(assumptions)>32 or len(actions)>32: raise ValueError("plan bounds exceeded")
        return BusinessPlan("plan-"+opportunity.opportunity_id,opportunity.opportunity_id,objective,tuple(assumptions),tuple(actions),value,cost,opportunity.currency)
    def compare(self, plans:tuple[BusinessPlan,...])->BusinessPlan|None:
        if not plans:return None
        return max(plans,key=lambda p:(p.expected_value-p.expected_cost,-p.expected_cost,p.plan_id))
