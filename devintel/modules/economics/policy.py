"""Economic authority policy: intelligence never grants spending or investment authority."""
from .contracts import *

class EconomicPolicy:
    def decide(self, action:EconomicAction, *, owner_approved:bool=False, evidence_score:float=0.0, amount:float=0.0)->EconomicDecision:
        if action in (EconomicAction.SPEND,EconomicAction.INVEST):
            return EconomicDecision(False,"financial actions require an explicit owner-authorized execution path",True,"high")
        if not 0.0<=evidence_score<=1.0: return EconomicDecision(False,"invalid evidence score",False,"high")
        if amount<0 or amount>MAX_AMOUNT: return EconomicDecision(False,"amount out of bounds",False,"high")
        if evidence_score<0.5: return EconomicDecision(False,"insufficient evidence",False,"medium")
        return EconomicDecision(True,"bounded economic analysis is permitted",False,"low")
