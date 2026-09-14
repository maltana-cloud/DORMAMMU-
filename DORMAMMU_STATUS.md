# DORMAMMU STATUS

## Current Milestone
**Category 3 — Capability & Resource Intelligence is COMPLETE and LOCKED at the repository architecture level.** DORMAMMU now connects capability discovery and hard eligibility evaluation to deterministic resource selection and durable resource reservation, with bounded fallback and fail-closed behavior.

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. Production readiness requires capability-appropriate operational evidence. Category 3 PR #64 merged at `58b1a54ad9c225cf80565d4859291d6449383446`; its final branch test workflow run #814 completed successfully.

## Repository Checkpoint
- Canonical runtime: `DORMAMMURuntime`; `DEVINTELRuntime` remains a compatibility alias.
- Evidence-backed knowledge synthesis and executive integration exist on `main`.
- Durable resource leases are implemented with expiry, atomic capacity acquisition, persistence, and runtime integration.
- Capability discovery/admission has provenance-aware evidence, strict trust-source gates, deterministic acquisition ranking/fallback, explicit approval, lifecycle/canary controls, bounded JSON/HTTPS catalog scouts, and durable explicit source configuration.
- The unified discovery engine connects local inventory, trusted external sources, capability evaluation, and resource decisions.
- Capability/resource scheduling now pairs only hard-eligible discovered capabilities with registered resources, reserves through durable leases, orders candidates deterministically, and fails closed when capacity is unavailable.
- Autonomous execution is finite and fail-closed; every planned action is scope-bound and permission-preflighted before acting.
- Model/agent/specialist routing selects only healthy, approved, requirement-compatible registered specialists and supplies deterministic collaboration fallbacks.
- Reflection/learning accepts only verified same-scope outcomes, attributes outcomes to optional specialist subjects, persists evidence/proposals, and emits reversible bounded proposals.
- Outcome-aware routing consumes durable proposals as bounded scoring preferences; hard health, approval, skill, metadata, cost, provider, and version gates remain dominant.
- Natural-language intake is an explicit untrusted-input boundary with scope matching, confidence/ambiguity gates, and fail-closed high-impact handling.
- Provider-backed semantic interpretation is available behind that boundary; malformed, unavailable, out-of-range, ambiguous, or scope-invalid provider output fails closed or requires confirmation.
- Runtime composition owns the durable learning store, outcome-aware routing service, semantic goal boundary, runtime goal-understanding entry point, and learned specialist-routing entry point.
- Semantic evaluation has deterministic representative, ambiguous, and high-impact rejection cases plus injectable unsafe-boundary regression coverage; it records structured safety outcomes only and never executes actions or grants authority.
- Core cognition maintains bounded facts, hypotheses, unresolved questions, deterministic state identity, scope-safe comparison, and a descriptive self-model of known capabilities/resources/limits without authority.
- Ecosystem awareness aggregation provides bounded, scope-filtered, freshness/importance/confidence-ranked, deterministic observations and does not publish, authenticate, contact, or grant distribution authority.

## Governance / Identity Checkpoint
- `AGENTS.md` is the DORMAMMU engineering constitution on `main`.
- `AI_WORKING_RULES.md` is the DORMAMMU multi-AI collaboration contract.
- `DORMAMMU_CHARTER.md` is the master architecture and operating charter.
- `DORMAMMU_PROJECT_CHARTER.md` is the canonical project-level charter.
- `DEVINTEL_STATUS.md` is retained only as a compatibility alias and is not an independent status source.
- The duplicate `DEVINTEL_PROJECT_CHARTER.md` was removed so there is one canonical project charter.
- PR #36 remains explicitly closed/unmerged and is not treated as merged history.

## Category Status
1. Foundation & Governance — COMPLETE / LOCKED
2. Core Intelligence — COMPLETE / LOCKED
3. Capability & Resource Intelligence — COMPLETE / LOCKED
4. Ecosystem Awareness — NEXT
5. Engineering Intelligence — MAJOR WORK REMAINS
6. Language & Communication — PARTIAL / LATER
7. Research & Domain Expansion — MAJOR WORK REMAINS
8. Creative Intelligence — MAJOR WORK REMAINS
9. Simulation & Interactive Worlds — MAJOR WORK REMAINS
10. Social & Community Intelligence — MAJOR WORK REMAINS
11. Economic & Business Intelligence — MAJOR WORK REMAINS
12. Owner & Platform Security — DEEPER WORK REMAINS
13. Autonomous Operations — PARTIAL
14. Evolution & Self-Improvement — EARLY

## Current Engineering Gaps
1. **Category 4 ecosystem awareness:** approved live source adapters and continuous observation remain incomplete.
2. **Distributed provider/resource scheduling:** scheduling is currently deterministic/local; distributed orchestration remains later work.
3. **Real provider adapters:** legitimate model/tool/API/dataset adapters still require explicit integration and operational evidence.
4. **Operational/provider evidence:** real-provider/model-specific semantic evaluation and broader historical CI evidence remain operational follow-ups; production readiness is not claimed.

## Safety Boundaries
- Capability sources are disabled unless explicitly enabled and included in the active trusted-evidence policy.
- External source retrieval is HTTPS-only and bounded by explicit host, timeout, and response-size controls.
- Source configuration never implies installation, execution, credentials, spending, or authority.
- Capability selection never bypasses hard trust, security, compatibility, performance, license, cost, or permission gates.
- Resource selection uses only registered resources with known sufficient capacity and declared permission; reservations are durable, scoped leases.
- Scheduler fallback is bounded and deterministic; exhausted capacity fails closed rather than provisioning or spending.
- Routing is selection, not authority.
- Learned routing preference is bounded and advisory; it cannot make an ineligible specialist eligible or bypass hard gates.
- Learning cannot mutate authority, permissions, credentials, security controls, privileged code, or handlers.
- Natural-language input and semantic-model output never grant authority or directly create executable actions.
- Ambiguous, low-confidence, scope-mismatched, malformed, unavailable, or high-impact natural-language intent fails closed or requires explicit confirmation.
- Cognitive state/self-model is descriptive and bounded; it cannot grant permissions, authority, credentials, or unrestricted self-modification.
- Selected capabilities still pass through existing permission, security, lifecycle, canary, resource, execution, and verification boundaries.
- No automatic credentials, spending, irreversible actions, authority escalation, CAPTCHA bypass, or platform-control bypass.

## Capability Matrix
`DORMAMMU_CAPABILITY_MATRIX.md` is the engineering checkpoint for implementation status and evidence.

## Next Execution Target
Proceed to **Category 4 — Ecosystem Awareness**. Do not restart Categories 1–3. Build live approved source adapters and continuous bounded observation on the existing trust, provenance, scope, ranking, telemetry, and security control plane.

Preferred operating path:
`OBJECTIVE → OBSERVE → UNDERSTAND → PLAN → CAPABILITY DISCOVERY → EVALUATE → SELECT → PERMISSION → SECURITY CHECK → RESOURCE RESERVATION → ACT → VERIFY → RECORD → REFLECT → LEARN → BOUNDED POLICY PREFERENCE`

## Verification Note
Category 3 branch CI passed before merge. Post-merge documentation checkpoint is being committed separately; repository branch protection/ruleset enforcement is not independently verified through the available integration, so repository-level protection is not claimed.

## Handoff Rule
Every AI working on DORMAMMU must verify the repository itself, leave a truthful test-backed checkpoint, and continue from `main` rather than treating prior chat history as authoritative.
