# DORMAMMU STATUS

## Current Milestone
**Bounded autonomous execution, deterministic specialist routing, controlled outcome learning, bounded natural-language goal intake, and explicit production capability-source configuration are implemented on `main`.**

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. Production readiness requires capability-appropriate operational evidence. Production capability-source configuration was merged from PR #57 at `5a1dde0182417342af3b0f972d075eddc8eb64d9`. Its initial CI run exposed one learning-test failure; that failure was corrected before merge. The available integration does not currently expose a post-fix CI run for the merged commit, so this milestone is not claimed as CI-verified until a successful run is observed.

## Repository Checkpoint
- Canonical runtime: `DORMAMMURuntime`; `DEVINTELRuntime` remains a compatibility alias.
- Evidence-backed knowledge synthesis and executive integration exist on `main`.
- Durable resource leases are implemented with expiry, atomic capacity acquisition, persistence, and runtime integration.
- Capability discovery/admission has provenance-aware evidence, strict trust-source gates, deterministic acquisition ranking/fallback, explicit approval, lifecycle/canary controls, bounded JSON/HTTPS catalog scouts, and durable explicit source configuration.
- Autonomous execution is finite and fail-closed; every planned action is scope-bound and permission-preflighted before acting.
- Model/agent/specialist routing selects only healthy, approved, requirement-compatible registered specialists and supplies deterministic collaboration fallbacks.
- Reflection/learning accepts only verified same-scope outcomes, requires sufficient evidence, persists evidence/proposals, and emits reversible bounded proposals.
- Natural-language intake has an explicit untrusted-input boundary: scope matching, confidence/ambiguity gates, and fail-closed handling for high-impact language.

## Current Engineering Gaps
1. **General semantic goal understanding:** the NL boundary is implemented, but a production semantic interpreter still requires explicit provider/model integration and evaluation; the deterministic parser intentionally handles only simple bounded normalization.
2. **Broad ecosystem capabilities:** communication, community, creation, distribution, awareness, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.
3. **Distributed resource/provider scheduling:** current routing is deterministic/local rather than a distributed scheduler.
4. **Outcome-aware routing integration:** learning currently produces durable reversible proposals; it does not autonomously alter routing policy or specialist weights.

## Safety Boundaries
- Capability sources are disabled unless explicitly enabled and included in the active trusted-evidence policy.
- External source retrieval is HTTPS-only and bounded by explicit host, timeout, and response-size controls.
- Source configuration never implies installation, execution, credentials, spending, or authority.
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
Proceed to the next highest-value unfinished dependency: **general semantic goal understanding and outcome-aware routing integration**, while preserving the existing explicit safety boundary and proposal-only learning model.

Preferred operating path:
`OBJECTIVE → OBSERVE → UNDERSTAND → PLAN → CAPABILITY SELECTION → PERMISSION → SECURITY CHECK → ACT → VERIFY → RECORD → REFLECT → LEARN`

## Verification Note
Repository branch-protection/ruleset enforcement has not been independently verified through the available integration, so repository-level protection is not claimed. Architectural safety boundaries remain code-enforced.
