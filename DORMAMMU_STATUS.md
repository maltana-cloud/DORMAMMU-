# DORMAMMU STATUS

## Current Milestone
**Bounded autonomous execution, deterministic specialist routing, controlled outcome learning, bounded natural-language goal intake, explicit production capability-source configuration, and bounded outcome-aware routing integration are implemented on `main`.**

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. Production readiness requires capability-appropriate operational evidence. The latest outcome-aware routing integration was merged from PR #58 at `ec62eaef6d544a192e99666deb5d9e6639b2aefb`. The available integration currently exposes no workflow run or status checks for that merged commit, so CI verification is not claimed.

## Repository Checkpoint
- Canonical runtime: `DORMAMMURuntime`; `DEVINTELRuntime` remains a compatibility alias.
- Evidence-backed knowledge synthesis and executive integration exist on `main`.
- Durable resource leases are implemented with expiry, atomic capacity acquisition, persistence, and runtime integration.
- Capability discovery/admission has provenance-aware evidence, strict trust-source gates, deterministic acquisition ranking/fallback, explicit approval, lifecycle/canary controls, bounded JSON/HTTPS catalog scouts, and durable explicit source configuration.
- Autonomous execution is finite and fail-closed; every planned action is scope-bound and permission-preflighted before acting.
- Model/agent/specialist routing selects only healthy, approved, requirement-compatible registered specialists and supplies deterministic collaboration fallbacks.
- Reflection/learning accepts only verified same-scope outcomes, attributes outcomes to optional specialist subjects, persists evidence/proposals, and emits reversible bounded proposals.
- Outcome-aware routing can consume those durable proposals as a bounded scoring preference; hard health, approval, skill, metadata, cost, provider, and version gates remain dominant.
- Natural-language intake has an explicit untrusted-input boundary: scope matching, confidence/ambiguity gates, and fail-closed handling for high-impact language.

## Current Engineering Gaps
1. **General semantic goal understanding:** the NL boundary is implemented, but a production semantic interpreter still requires explicit provider/model integration and evaluation; the deterministic parser intentionally handles only simple bounded normalization.
2. **Broad ecosystem capabilities:** communication, community, creation, distribution, awareness, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.
3. **Distributed resource/provider scheduling:** current routing remains deterministic/local rather than a distributed scheduler.
4. **Operational CI evidence:** the available integration has not exposed workflow/status checks for the latest merged learning/routing integration, so repository-wide verification remains pending.

## Safety Boundaries
- Capability sources are disabled unless explicitly enabled and included in the active trusted-evidence policy.
- External source retrieval is HTTPS-only and bounded by explicit host, timeout, and response-size controls.
- Source configuration never implies installation, execution, credentials, spending, or authority.
- Routing is selection, not authority.
- Only registered, approved, healthy, requirement-compatible specialists can be selected.
- Learned routing preference is bounded and advisory; it cannot make an ineligible specialist eligible or bypass hard gates.
- Learning cannot mutate authority, permissions, credentials, security controls, privileged code, or handlers.
- Natural-language input never grants authority or directly creates executable actions.
- Ambiguous, low-confidence, scope-mismatched, or high-impact natural-language intent fails closed or requires explicit confirmation.
- Selected capabilities still pass through existing permission, security, lifecycle, canary, resource, execution, and verification boundaries.
- No automatic credentials, spending, irreversible actions, authority escalation, CAPTCHA bypass, or platform-control bypass.

## Capability Matrix
`DORMAMMU_CAPABILITY_MATRIX.md` is the engineering checkpoint for implementation status and evidence.

## Next Execution Target
Proceed to the next highest-value unfinished dependency: **general semantic goal understanding**, then broaden the ecosystem and distributed provider/resource scheduling without weakening the existing safety boundary.

Preferred operating path:
`OBJECTIVE → OBSERVE → UNDERSTAND → PLAN → CAPABILITY SELECTION → PERMISSION → SECURITY CHECK → ACT → VERIFY → RECORD → REFLECT → LEARN → BOUNDED POLICY PREFERENCE`

## Verification Note
Repository branch-protection/ruleset enforcement has not been independently verified through the available integration, so repository-level protection is not claimed. Architectural safety boundaries remain code-enforced.
