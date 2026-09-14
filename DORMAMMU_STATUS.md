# DORMAMMU STATUS

## Current Milestone
**Bounded autonomous operating path is implemented and verified on `main`.** DORMAMMU now has an explicit OBSERVE → UNDERSTAND → PLAN → PERMISSION → SECURITY CHECK → ACT → VERIFY → RECORD → IMPROVE cycle, durable autonomous-cycle history, bounded plan size, permission preflight, and proposal-only improvement.

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. The autonomous operating-path milestone was merged to `main` at `d73d6b609e31c3a5963b977c566fee5f4d66ca78` after PR #52 CI passed with 243+ tests.

## Repository Checkpoint
- Canonical runtime: `DORMAMMURuntime`; `DEVINTELRuntime` remains a compatibility alias.
- Evidence-backed knowledge synthesis and executive integration exist on `main`.
- Durable resource leases are implemented with expiry, atomic capacity acquisition, persistence, and runtime integration.
- Capability discovery/admission has provenance-aware evidence, strict trust-source gates, security/compatibility/performance/license/cost/permission evaluation, deterministic acquisition ranking/fallback, explicit approval, lifecycle/canary controls, and bounded JSON/HTTPS catalog scouts.
- Autonomous execution is finite and fail-closed; every planned action is scope-bound and permission-preflighted before acting.
- Autonomous cycle history is durable in SQLite and integrated into the runtime.

## Current Engineering Gaps
1. **Production capability source configuration:** generic read-only JSON/HTTPS catalog scouts exist, but each real external source still needs explicit trusted-source configuration and source-specific validation.
2. **Evidence-backed arbitrary natural-language goal understanding:** current planning contracts safely operate on explicit structured goals/actions rather than inferring arbitrary high-impact intent.
3. **Model/agent/specialist routing and collaboration:** automated selection and coordination remain incomplete.
4. **Reflection/learning:** the autonomous loop can generate bounded improvement proposals, but it does not yet automatically learn policy/strategy from outcomes.
5. **Broad ecosystem capabilities:** communication, community, creation, distribution, awareness, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.

## Safety Boundaries
- Capability provenance is evidence, not authority.
- External candidates fail closed when provenance/trusted-source evidence is absent in strict mode.
- Capability admission requires explicit owner approval and lifecycle/canary gates when a new candidate is selected.
- Resource leases only reserve already-registered resources; they never provision machines, acquire credentials, spend money, or grant authority.
- Autonomous execution preflights permissions for the complete plan before any action is allowed to run.
- Improvement is proposal-only; it cannot mutate code, handlers, permissions, credentials, or authority.
- Core action execution remains behind the permission boundary.
- Recovery uses externally supplied cryptographic authorization with tamper, expiry, and replay protection.
- No unrestricted self-modification, automatic paid acquisition, credential fabrication, CAPTCHA bypass, or platform-control bypass.

## Capability Matrix
`DORMAMMU_CAPABILITY_MATRIX.md` is reconciled to the current verified autonomous-operating, capability-admission, and durable-resource milestones.

## Next Execution Target
Proceed to the next highest-value unfinished dependency: **model/agent/specialist routing and collaboration**, while keeping arbitrary natural-language goal understanding and production source configuration as separate bounded gaps.

Preferred operating path:
`OBSERVE → UNDERSTAND → PLAN → PERMISSION CHECK → SECURITY CHECK → ACT → VERIFY → RECORD → IMPROVE`

Preferred capability path:
`REQUIREMENT → CAPABILITY REGISTRY → GAP → SCOUT → PROVENANCE → TRUST → SECURITY → COMPATIBILITY → PERFORMANCE → COST → LICENSE → PERMISSION → COMPARE → SELECT → EXPLICIT APPROVAL → REGISTER → CANARY → ACTIVATE → MONITOR → FALLBACK`

## Verification Note
Repository branch-protection/ruleset enforcement has not been independently verified through the available integration, so repository-level protection is not claimed. Architectural safety boundaries remain code-enforced.
