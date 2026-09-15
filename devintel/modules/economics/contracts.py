"""Bounded contracts for economic and business intelligence."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

MAX_TEXT=4096
MAX_EVIDENCE=32
MAX_AMOUNT=1_000_000_000.0

class OpportunityKind(str, Enum): BUSINESS="business"; JOB="job"; PRODUCT="product"; SERVICE="service"; INVESTMENT="investment"
class RiskKind(str, Enum): MARKET="market"; OPERATIONAL="operational"; FINANCIAL="financial"; COMPLIANCE="compliance"
class EconomicAction(str, Enum): ANALYZE="analyze"; PLAN="plan"; BUDGET="budget"; SPEND="spend"; INVEST="invest"
@dataclass(frozen=True)
class EconomicEvidence:
    source_id:str; statement:str; confidence:float=0.0
@dataclass(frozen=True)
class Opportunity:
    opportunity_id:str; kind:OpportunityKind; title:str; description:str; estimated_value:float=0.0; currency:str="USD"; evidence:tuple[EconomicEvidence,...]=()
@dataclass(frozen=True)
class BusinessPlan:
    plan_id:str; opportunity_id:str; objective:str; assumptions:tuple[str,...]; actions:tuple[str,...]; expected_value:float; expected_cost:float; currency:str="USD"
@dataclass(frozen=True)
class EconomicSignal:
    opportunity_id:str; signal:str; score:float; evidence:tuple[str,...]=()
@dataclass(frozen=True)
class EconomicDecision:
    allowed:bool; reason:str; requires_owner_approval:bool; risk:str

def validate_amount(value:float)->float:
    value=float(value)
    if value<0 or value>MAX_AMOUNT: raise ValueError("amount out of bounds")
    return value

def digest_plan(plan:BusinessPlan)->str:
    raw="|".join((plan.plan_id,plan.opportunity_id,plan.objective,";".join(plan.assumptions),";".join(plan.actions),str(plan.expected_value),str(plan.expected_cost),plan.currency))
    return sha256(raw.encode()).hexdigest()
