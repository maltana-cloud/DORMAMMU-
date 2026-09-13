# DORMAMMU STATUS

## Current Milestone
**Foundation locked in direction and safety boundaries; canonical builder control plane established; next target is the first end-to-end bounded operating path.**

## Truth Rule
This file describes repository state. Implementation claims require code, meaningful tests, and successful CI evidence. The latest verified code checkpoint is commit `a3c7308256eeec36c31d7840e899a6aea199fc47`, validated by GitHub Actions run **507**.

## Foundation Lock
The foundational architecture is now **LOCKED** in its identity, authority, security, truth, owner-control, recovery, permission, auditability, modularity, backward-compatibility, and safe-evolution direction.

Locked does **not** mean every future capability exists. It means future capabilities must plug into these boundaries rather than silently weakening or replacing them.

## Verified Foundations
- Core systems, specialist/domain framework, orchestration, permissions, security/truth, autonomy, education, and provider routing remain in the repository.
- Live provider adapters exist for keyless Wikipedia retrieval and optional Gemini generation.
- Canonical `DORMAMMURuntime` exists; `DEVINTELRuntime` remains only as a compatibility alias.
- Capability/resource discovery, deterministic evaluation gates, free-first policy, controlled lifecycle, lifecycle event storage, safe local inventory, cryptographic recovery authorization, canary health monitoring/rollback, and bounded capability decisions are implemented and tested.
- The runtime foundation integration suite now verifies actual lifecycle-event persistence across close/reopen.
- GitHub Actions run 507 passed on the resulting code checkpoint.

## Canonical Builder Control Plane
`DORMAMMU_ENGINEERING_MAP.md` is the canonical builder entry point.

A new builder should be able to enter the repository cold and determine:

`WHAT IS DORMAMMU? → WHAT MUST NEVER CHANGE? → WHAT EXISTS? → WHAT IS VERIFIED? → WHAT IS PARTIAL? → WHAT IS NOT BUILT? → WHAT COMES NEXT? → WHAT DEPENDS ON WHAT? → HOW IS IT TESTED? → WHAT IS DONE? → HOW DOES IT REACH THE NORTH STAR?`

Builders must still verify code, tests, CI, and recent history rather than trusting documentation blindly.

## Verified Safety Boundaries
- Discovery does not install, execute, authenticate, or grant authority.
- Lifecycle transitions are explicit and state-validated; approval requires permission.
- Local resource inventory is read-only and conservative.
- Autonomy capability observations are data-only and do not grant authority.
- Recovery uses an externally supplied cryptographic secret, with tamper, expiry, and replay protection.
- Canary failure can produce bounded degradation/rollback rather than silent activation.
- No unrestricted self-modification or automatic paid acquisition.
- External content cannot promote itself into instructions, credentials, permissions, or owner authority.

## Remaining Engineering Work
- Build the first real end-to-end bounded operating path:
  `GOAL → REQUIREMENTS → CAPABILITY DECISION → PERMISSION CHECK → APPROVAL WHEN REQUIRED → LIFECYCLE → CANARY → ACT → VERIFY → RECORD`.
- Connect real operational health metrics to canary monitoring before claiming production autonomous rollout.
- Configure durable lifecycle storage explicitly in deployed runtimes.
- Add trusted external capability scouts and integration adapters only after their complete security/permission/licensing/rollback path is verified.
- Connect executive cognition: goal understanding, decomposition, planning, model/agent routing, specialist collaboration, execution, verification, reflection, and outcomes.
- Progressively integrate ecosystem capabilities, creation, distribution, awareness, monetization, resource orchestration, model training/evaluation, and controlled self-improvement.

## Not Yet Complete
DORMAMMU is **not** being represented as a finished autonomous ecosystem. Full production autonomy, broad external capability acquisition, complete executive cognition, full ecosystem loops, and ecosystem-scale controlled learning remain future engineering work.

## Engineering Rule
`PLANNED ≠ DESIGNED ≠ PARTIAL ≠ IMPLEMENTED ≠ TESTED ≠ VERIFIED ≠ DEPLOYED`

Every builder must leave a truthful, test-backed checkpoint. Never claim a capability because a document describes it.

## Next Execution Target
**First end-to-end bounded operating path.**

Do not start an unrelated feature before this dependency is connected and verified.

## Verification Note
GitHub repository branch-protection/ruleset enforcement could not be independently verified through the available integration, so repository-level protection is not claimed here. The architectural lock refers to the code-enforced foundation and its verified engineering boundaries, not an unverified GitHub administration setting.
