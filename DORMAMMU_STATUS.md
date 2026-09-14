# DORMAMMU STATUS

## Current Milestone
**Bounded autonomous execution, deterministic specialist routing, controlled outcome learning, and a bounded natural-language goal intake boundary are implemented on `main`.**

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. The routing milestone was merged at `d91d89b7f5bf4c9de6f6e37c85416f77e4003334`; controlled outcome learning was merged at `49289b1bc72de6d97035073ca7901bd7c04cb312`; bounded natural-language goal understanding was merged at `7adad2d2f2259afc40a8bc46070c15c199dfb888`.

## Repository Checkpoint
- Canonical runtime: `DORMAMMURuntime`; `DEVINTELRuntime` remains a compatibility alias.
- Evidence-backed knowledge synthesis and executive integration exist on `main`.
- Durable resource leases are implemented with expiry, atomic capacity acquisition, persistence, and runtime integration.
- Capability discovery/admission has provenance-aware evidence, strict trust-source gates, deterministic acquisition ranking/fallback, explicit approval, lifecycle/canary controls, and bounded JSON/HTTPS catalog scouts.
- Autonomous execution is finite and fail-closed; every planned action is scope-bound and permission-preflighted before acting.
- Model/agent/specialist routing selects only healthy, approved, requirement-compatible registered specialists and supplies deterministic collaboration fallbacks.
- Reflection/learning accepts only verified same-scope outcomes, requires sufficient evidence, persists evidence/proposals, and emits reversible bounded proposals.
- Natural-language intake now has an explicit untrusted-input boundary: scope matching, confidence/ambiguity gates, and fail-closed handling for high-impact language.

## Current Engineering Gaps
1. **General semantic goal understanding:** the NL boundary is implemented, but a production semantic interpreter still requires explicit provider/model integration and evaluation; the deterministic parser intentionally handles only simple bounded normalization.
2. **Production capability source configuration:** generic read-only scouts exist; each real external source still needs explicit trusted provenance configuration and validation.
3. **Broad ecosystem capabilities:** communication, community, creation, distribution, awareness, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.
4. **Distributed resource/provider scheduling:** current routing is deterministic/local rather than a distributed scheduler.

## Safety Boundaries
- Routing is selection, not authority.
- Only registered, approved, healthy, requirement-compatible specialists can be selected.
- Learning cannot override hard routing gates or mutate authority, permissions, credentials, security controls, privileged code, or handlers.
- Natural-language input never grants authority or directly creates executable actions.
- Ambiguous, low-confidence, scope-mismatched, or high-impact natural-language intent fails closed or requires explicit confirmation.
- Selected capabilities still pass through existing permission, security, lifecycle, canary, resource, execution, and verification boundaries.
- No automatic credentials, spending, irreversible actions, authority escalation, CAPTCHA bypass, or platform-control bypass.

## Capability Matrix
`DORMAMMU_CAPABILITY_MATRIX.md` is the engineering checkpoint for implementation status and evidence.

## Next Execution Target
Proceed to the next highest-value unfinished dependency: **production capability source configuration**, turning the generic provenance-aware JSON/HTTPS scout into explicitly configured, source-specific trusted discovery without automatic trust or installation.

Preferred operating path:
`OBJECTIVE → OBSERVE → UNDERSTAND → PLAN → CAPABILITY SELECTION → PERMISSION → SECURITY CHECK → ACT → VERIFY → RECORD → REFLECT → LEARN`

## Verification Note
Repository branch-protection/ruleset enforcement has not been independently verified through the available integration, so repository-level protection is not claimed. Architectural safety boundaries remain code-enforced.
