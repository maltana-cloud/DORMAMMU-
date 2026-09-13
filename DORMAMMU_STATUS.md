# DORMAMMU STATUS

## Current Milestone
**Evidence-backed knowledge synthesis is implemented and merged into `main`.** DORMAMMU can now accept only verified claims, normalize them, preserve canonical provenance, expose uncertainty, detect contradictory verified claims, and prevent contradictory/low-confidence evidence from becoming executive requirements.

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. Main merge commit `19d4d3ae0682cf4a34f80db0a0da7d6fd6379aae` contains the synthesis milestone; PR #44 head `c78dfeae0f5de5f027d8fd1f44333d902948e694` passed GitHub Actions run **603** with the full repository test suite. Main-branch post-merge CI for the merge commit is not yet independently observed, so the synthesis milestone is **TESTED/merged**, not claimed `VERIFIED` on main until that post-merge check is observed.

## Verified / Tested Foundations
- Core engine, state, tasks, planning, events, permission boundaries, specialist/domain framework, bounded autonomy, research/truth, education, provider routing, security, owner control, and recovery remain integrated.
- Canonical `DORMAMMURuntime` exists; `DEVINTELRuntime` remains only as a compatibility alias.
- Capability/resource discovery, evaluation, lifecycle, local inventory, cryptographic recovery, canary evaluation/rollback, and bounded capability decisions remain implemented/tested.
- Resource management reserves only registered resources, enforces declared capacity/cost/permission, and releases reservations before operation recording.
- Executive contracts separate `Objective`, `GoalUnderstanding`, `TaskSpec`, and `ExecutivePlan` from execution authority.
- Executive execution delegates tasks to the bounded operating path.
- Operational telemetry persists observations and requires a minimum sample count before deriving health.
- Bounded execution records operation duration, success, verification, stage, and resource reservation metadata.
- Knowledge synthesis now excludes unsupported inputs, preserves provenance, detects normalized contradictions, and blocks contradictory/low-confidence signals from executive requirements.
- Main runtime compatibility was repaired during synthesis integration: provider registration uses the actual `ProviderRouter.register(...)` contract and the runtime snapshot compatibility API remains present.

## Capability Matrix
`DORMAMMU_CAPABILITY_MATRIX.md` is the detailed truthful matrix. It records status, implementation path, tests, CI evidence, dependencies, security status, limitations, next action, version, and last verified commit.

## Current Engineering Gaps
1. **Post-merge verification:** main merge commit needs an independently observed successful CI run before the synthesis milestone is marked `VERIFIED`.
2. **Evidence-backed executive intelligence:** synthesis is available, but its signals are not yet safely consumed as requirements/success criteria by the executive engine.
3. **Durable resource leases:** operation telemetry is durable, but active resource reservations remain in-memory.
4. **Trusted external capability acquisition:** scouts/adapters need end-to-end provenance, license/terms, security, compatibility, permissions, resource, cost, rollback, and observability controls.
5. **Evidence-backed arbitrary natural-language goal understanding:** current default interpreter normalizes explicit fields rather than inferring arbitrary goals.
6. **Model/agent routing and specialist collaboration:** automated selection and coordination are not complete.
7. **Broad ecosystem capabilities:** communication, community, creation, distribution, awareness, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.

## Safety Boundaries
- Synthesis is evidence processing, not authority; external content cannot grant permissions or instructions.
- Only `VerificationResult.verified=True` claims enter the verified-claim contract.
- Contradictory verified claims are explicitly uncertain and cannot become executive requirements.
- Discovery never installs, executes, authenticates, spends money, or grants authority.
- Lifecycle transitions are explicit and state-validated; capability approval requires permission.
- Resource management only reserves already-registered resources and fails closed on unknown capacity.
- Core action execution remains behind the permission boundary.
- Recovery uses externally supplied cryptographic authorization with tamper, expiry, and replay protection.
- Canary failure can produce bounded rollback rather than silent activation.
- No unrestricted self-modification, automatic paid acquisition, credential fabrication, CAPTCHA bypass, or platform-control bypass.

## Not Yet Complete
DORMAMMU is **not** a finished autonomous ecosystem. It has a tested bounded objective/execution/measurement foundation and a tested evidence-synthesis layer, but not full arbitrary-objective autonomy, dynamic model/agent routing, complete cross-domain executive reasoning, durable resource leasing, autonomous external capability acquisition, or ecosystem-scale learning.

## Next Execution Target
**Evidence-backed executive intelligence:** connect `SynthesisResult.executive_requirements()` to explicit executive requirements/success criteria through a conservative adapter that preserves provenance and uncertainty, rejects contradictions/low confidence, and never grants authority to evidence.

Preferred loop:
`RESEARCH → VERIFY EVIDENCE → NORMALIZE CLAIMS → SYNTHESIZE → CHECK CONTRADICTIONS → EXPOSE PROVENANCE/UNCERTAINTY → EXECUTIVE REQUIREMENTS → PLAN → BOUNDED EXECUTION`

## Verification Note
Repository branch-protection/ruleset enforcement has not been independently verified through the available integration, so repository-level protection is not claimed. Architectural lock refers to code-enforced foundation and verified engineering boundaries.
