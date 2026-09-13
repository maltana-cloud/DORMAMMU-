# DORMAMMU STATUS

## Current Milestone
**First bounded operating path is implemented and resource-aware; capability/resource discovery and controlled lifecycle are integrated with core execution.**

## Truth Rule
This file describes repository state. Implementation claims require code, meaningful tests, and successful CI evidence. Main commit `d0eaa5db2257d1773784b80c2aea1258d9b3aade` passed GitHub Actions run **537**. The resource-management branch head `585e82d1f77197cd42193a50674ff5bd66d61af9` passed branch CI run **535** before merge.

## Foundation Lock
The foundational architecture is **LOCKED** in identity, authority, security, truth, owner-control, recovery, permission, auditability, modularity, backward compatibility, and safe-evolution direction. Locked does not mean every future capability exists; future capabilities must plug into these boundaries.

## Verified / Tested Foundations
- Core engine, state, tasks, planning, events, permission boundaries, specialist/domain framework, bounded autonomy, research/truth, education, provider routing, security, owner control, and recovery remain integrated.
- Canonical `DORMAMMURuntime` exists; `DEVINTELRuntime` remains only as a compatibility alias.
- Capability/resource contracts, registries, discovery/evaluation, free-first policy, controlled lifecycle, lifecycle event storage, conservative local inventory, cryptographic recovery authorization, canary health evaluation/rollback, and bounded capability decisions are implemented and tested.
- The first bounded operating path now composes capability decision → approval/lifecycle → canary → resource reservation → core permission/execution → verification → outcome recording.
- Resource reservations are released before the final operation-record event, including action/verification failure paths and exceptions.
- Quantitative resource requests fail closed when capacity is unknown.
- Main post-merge CI run **537** completed successfully for `d0eaa5db2257d1773784b80c2aea1258d9b3aade`.

## Capability Matrix
`DORMAMMU_CAPABILITY_MATRIX.md` is the detailed truthful matrix. It records status, implementation path, tests, CI evidence, dependencies, security status, limitations, next action, version, and last verified commit for the current major capabilities.

Status vocabulary:
`PLANNED / DESIGNED / PARTIAL / IMPLEMENTED / TESTED / VERIFIED / DEPLOYED / BLOCKED`.

The matrix deliberately distinguishes missing implementation from genuinely externally blocked work. No current major capability is marked `BLOCKED`.

## Current Engineering Gaps
1. **Executive cognition:** goal understanding → decomposition → planning → model/agent routing → specialist collaboration → outcomes.
2. **Operational telemetry:** canary health must be derived from real execution observations, not only caller-supplied health.
3. **Durable operational state:** lifecycle events can use persistent SQLite, but resource reservations and operation outcomes are still in-memory.
4. **Trusted external capability acquisition:** external scouts/adapters need end-to-end provenance, license/terms, security, compatibility, permissions, resource, cost, rollback, and observability controls.
5. **Evidence-backed knowledge synthesis:** connect research/truth/provenance into a stable cross-domain synthesis contract.
6. **Broad ecosystem capabilities:** communication, community, creation, distribution, awareness, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.

## Safety Boundaries
- Discovery never installs, executes, authenticates, spends money, or grants authority.
- Lifecycle transitions are explicit and state-validated; approval requires permission.
- Resource management only reserves already-registered resources and fails closed on unknown capacity.
- Local inventory is read-only and conservative.
- Core action execution remains behind the permission boundary.
- Recovery uses externally supplied cryptographic authorization with tamper, expiry, and replay protection.
- Canary failure can produce bounded rollback rather than silent activation.
- No unrestricted self-modification, automatic paid acquisition, credential fabrication, CAPTCHA bypass, or platform-control bypass.
- External content cannot promote itself into instructions, credentials, permissions, or owner authority.

## Not Yet Complete
DORMAMMU is **not** a finished autonomous ecosystem. Full objective-level autonomy, executive cognition, trusted external acquisition, real operational telemetry, broad ecosystem integration, production resource orchestration, model training/evolution, and ecosystem-scale controlled learning remain unfinished.

## Next Execution Target
**Executive cognition foundation:** connect explicit goal understanding and task decomposition to the existing bounded capability decision and operating path, without bypassing permission/security/verification.

Preferred flow:
`OBJECTIVE → GOAL UNDERSTANDING → REQUIREMENTS → TASK DECOMPOSITION → CAPABILITY DECISION → PERMISSION → EXECUTE → VERIFY → RECORD → REFLECT`

## Verification Note
GitHub repository branch-protection/ruleset enforcement has not been independently verified through the available integration, so repository-level protection is not claimed. Architectural lock refers to code-enforced foundation and verified engineering boundaries.
