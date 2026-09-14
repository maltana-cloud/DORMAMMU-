# DORMAMMU STATUS

## Current Milestone
**Bounded autonomous execution, deterministic specialist routing, controlled outcome learning, bounded natural-language goal intake, provider-backed semantic interpretation, explicit production capability-source configuration, runtime outcome-aware cognition integration, deterministic semantic safety evaluation, and ecosystem-awareness aggregation are implemented on `main`.**

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. Production readiness requires capability-appropriate operational evidence. Runtime cognition integration merged from PR #60 at `d8691b813efdc71d79cc1e4e3c666cec00e8ba58`; available integration did not expose workflow/status evidence for that merged commit. Semantic evaluation PR #62 merged at `a190e11a40843dc375777d381042825eee2eaafa`; its head CI job passed before merge, while no post-merge workflow was exposed for the squash commit. Awareness aggregation was added directly to `main`; no workflow evidence is currently exposed for its latest direct commits.

## Repository Checkpoint
- Canonical runtime: `DORMAMMURuntime`; `DEVINTELRuntime` remains a compatibility alias.
- Evidence-backed knowledge synthesis and executive integration exist on `main`.
- Durable resource leases are implemented with expiry, atomic capacity acquisition, persistence, and runtime integration.
- Capability discovery/admission has provenance-aware evidence, strict trust-source gates, deterministic acquisition ranking/fallback, explicit approval, lifecycle/canary controls, bounded JSON/HTTPS catalog scouts, and durable explicit source configuration.
- Autonomous execution is finite and fail-closed; every planned action is scope-bound and permission-preflighted before acting.
- Model/agent/specialist routing selects only healthy, approved, requirement-compatible registered specialists and supplies deterministic collaboration fallbacks.
- Reflection/learning accepts only verified same-scope outcomes, attributes outcomes to optional specialist subjects, persists evidence/proposals, and emits reversible bounded proposals.
- Outcome-aware routing consumes durable proposals as bounded scoring preferences; hard health, approval, skill, metadata, cost, provider, and version gates remain dominant.
- Natural-language intake is an explicit untrusted-input boundary with scope matching, confidence/ambiguity gates, and fail-closed high-impact handling.
- Provider-backed semantic interpretation is available behind that boundary; malformed, unavailable, out-of-range, ambiguous, or scope-invalid provider output fails closed or requires confirmation.
- Runtime composition owns the durable learning store, outcome-aware routing service, semantic goal boundary, runtime goal-understanding entry point, and learned specialist-routing entry point.
- Semantic evaluation has deterministic representative, ambiguous, and high-impact rejection cases plus injectable unsafe-boundary regression coverage; it records structured safety outcomes only and never executes actions or grants authority.
- Ecosystem awareness aggregation provides bounded, scope-filtered, freshness/importance/confidence-ranked, deterministic observations and does not publish, authenticate, contact, or grant distribution authority.

## Governance / Identity Checkpoint
- `AGENTS.md` is the DORMAMMU engineering constitution on `main`.
- `AI_WORKING_RULES.md` is the DORMAMMU multi-AI collaboration contract.
- `DORMAMMU_CHARTER.md` is the master architecture and operating charter.
- `DORMAMMU_PROJECT_CHARTER.md` is now the canonical project-level charter.
- `DEVINTEL_STATUS.md` is retained only as a compatibility alias and is not an independent status source.
- The duplicate `DEVINTEL_PROJECT_CHARTER.md` was removed so there is one canonical project charter.
- PR #36 remains explicitly closed/unmerged and is not treated as merged history; useful migration intent has been superseded by the canonical files now on `main`.

## Current Engineering Gaps
1. **Broad ecosystem capabilities:** communication, community, creation, distribution, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.
2. **Distributed resource/provider scheduling:** current routing remains deterministic/local rather than a distributed scheduler.
3. **Operational/provider evidence:** real-provider/model-specific semantic evaluation and repository-wide CI evidence for earlier merged cognition work remain operational follow-ups; production readiness is not claimed without that evidence.

## Safety Boundaries
- Capability sources are disabled unless explicitly enabled and included in the active trusted-evidence policy.
- External source retrieval is HTTPS-only and bounded by explicit host, timeout, and response-size controls.
- Source configuration never implies installation, execution, credentials, spending, or authority.
- Routing is selection, not authority.
- Only registered, approved, healthy, requirement-compatible specialists can be selected.
- Learned routing preference is bounded and advisory; it cannot make an ineligible specialist eligible or bypass hard gates.
- Learning cannot mutate authority, permissions, credentials, security controls, privileged code, or handlers.
- Natural-language input and semantic-model output never grant authority or directly create executable actions.
- Ambiguous, low-confidence, scope-mismatched, malformed, unavailable, or high-impact natural-language intent fails closed or requires explicit confirmation.
- Selected capabilities still pass through existing permission, security, lifecycle, canary, resource, execution, and verification boundaries.
- No automatic credentials, spending, irreversible actions, authority escalation, CAPTCHA bypass, or platform-control bypass.

## Capability Matrix
`DORMAMMU_CAPABILITY_MATRIX.md` is the engineering checkpoint for implementation status and evidence.

## Next Execution Target
Proceed to **broad ecosystem capabilities**, selecting the highest-value capability that can be implemented end-to-end while preserving the existing control plane. Distributed resource/provider scheduling follows after the ecosystem capability foundation is materially implemented.

Preferred operating path:
`OBJECTIVE → OBSERVE → UNDERSTAND → PLAN → CAPABILITY SELECTION → PERMISSION → SECURITY CHECK → ACT → VERIFY → RECORD → REFLECT → LEARN → BOUNDED POLICY PREFERENCE`

## Verification Note
Repository branch protection/ruleset enforcement is not independently verified through the available integration, so repository-level protection is not claimed. Architectural safety boundaries remain code-enforced.

## Handoff Rule
Every AI working on DORMAMMU must verify the repository itself, leave a truthful test-backed checkpoint, and continue from `main` rather than treating prior chat history as authoritative.
