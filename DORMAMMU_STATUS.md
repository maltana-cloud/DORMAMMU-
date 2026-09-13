# DORMAMMU STATUS

## Current Milestone
**Executive cognition foundation is implemented and connected to the bounded operating path: explicit objective → goal understanding → task decomposition → capability decision → permission → execution → verification → recording.**

## Truth Rule
This file describes repository state. Implementation claims require code, meaningful tests, integration evidence, and successful CI. Main commit `58a3afe21a18c7a826da3f635c73da6ec244a625` passed GitHub Actions run **555**. The preceding executive branch CI run **554** also passed.

## Foundation Lock
The foundational architecture is **LOCKED** in identity, authority, security, truth, owner-control, recovery, permission, auditability, modularity, backward compatibility, and safe-evolution direction. Locked does not mean every future capability exists; future capabilities must plug into these boundaries.

## Verified / Tested Foundations
- Core engine, state, tasks, planning, events, permission boundaries, specialist/domain framework, bounded autonomy, research/truth, education, provider routing, security, owner control, and recovery remain integrated.
- Canonical `DORMAMMURuntime` exists; `DEVINTELRuntime` remains only as a compatibility alias.
- Capability/resource contracts, registries, discovery/evaluation, free-first policy, controlled lifecycle, lifecycle event storage, conservative local inventory, cryptographic recovery authorization, canary health evaluation/rollback, and bounded capability decisions are implemented and tested.
- Resource management reserves only registered resources, enforces declared capacity/cost/permission, and releases reservations before operation recording.
- Executive contracts now separate `Objective`, `GoalUnderstanding`, `TaskSpec`, and `ExecutivePlan` from execution authority.
- The default goal interpreter only normalizes explicit objective fields; it does not claim hidden semantic reasoning.
- Task decomposition validates unique IDs, dependencies, acyclicity, and explicit objective scope.
- Executive execution delegates every task to the existing bounded operating path, preserving capability approval, resource reservation, core permission, canary gating, verification, and recording.
- Main CI run **555** completed successfully for `58a3afe21a18c7a826da3f635c73da6ec244a625`.

## Capability Matrix
`DORMAMMU_CAPABILITY_MATRIX.md` is the detailed truthful matrix. It records status, implementation path, tests, CI evidence, dependencies, security status, limitations, next action, version, and last verified commit for the current major capabilities.

Status vocabulary:
`PLANNED / DESIGNED / PARTIAL / IMPLEMENTED / TESTED / VERIFIED / DEPLOYED / BLOCKED`.

No current major capability is marked `BLOCKED`; missing software is recorded as not built rather than falsely attributed to external blockers.

## Current Engineering Gaps
1. **Operational telemetry:** canary health is still supplied as a bounded input; it must be derived from real execution observations/metrics.
2. **Durable operational state:** lifecycle events support persistent SQLite, but operation outcomes and resource reservations are not yet durable.
3. **Trusted external capability acquisition:** scouts/adapters need end-to-end provenance, license/terms, security, compatibility, permissions, resource, cost, rollback, and observability controls.
4. **Evidence-backed knowledge synthesis:** connect research/truth/provenance into a stable cross-domain synthesis contract.
5. **Model/agent routing and specialist collaboration:** executive tasks currently receive explicit decompositions; automated capability/model selection and specialist collaboration are not yet complete.
6. **Broad ecosystem capabilities:** communication, community, creation, distribution, awareness, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.

## Safety Boundaries
- Discovery never installs, executes, authenticates, spends money, or grants authority.
- Lifecycle transitions are explicit and state-validated; capability approval requires permission.
- Executive tasks must explicitly declare their objective scope.
- Capability approval can be supplied globally or as an explicit set of approved capability IDs; no implicit owner approval is created.
- Resource management only reserves already-registered resources and fails closed on unknown capacity.
- Core action execution remains behind the permission boundary.
- Recovery uses externally supplied cryptographic authorization with tamper, expiry, and replay protection.
- Canary failure can produce bounded rollback rather than silent activation.
- No unrestricted self-modification, automatic paid acquisition, credential fabrication, CAPTCHA bypass, or platform-control bypass.
- External content cannot promote itself into instructions, credentials, permissions, or owner authority.

## Not Yet Complete
DORMAMMU is **not** a finished autonomous ecosystem. Executive cognition is now a tested foundation, not a complete autonomous executive: it does not yet generate task decompositions from arbitrary natural-language objectives, select models/agents/specialists dynamically, synthesize cross-domain evidence, or learn from durable outcomes.

## Next Execution Target
**Operational telemetry and outcome recording:** make canary decisions evidence-driven by capturing execution health, latency, error, verification, resource, and outcome metrics through stable contracts, then feed those observations back into lifecycle/canary decisions.

Preferred loop:
`OBJECTIVE → UNDERSTAND → DECOMPOSE → CAPABILITY/RESOURCE DECISION → PERMISSION → ACT → MEASURE → VERIFY → RECORD → REFLECT`

## Verification Note
GitHub repository branch-protection/ruleset enforcement has not been independently verified through the available integration, so repository-level protection is not claimed. Architectural lock refers to code-enforced foundation and verified engineering boundaries.
