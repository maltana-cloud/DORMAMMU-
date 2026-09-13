# DORMAMMU STATUS

## Current Milestone
**Evidence-driven operational telemetry is implemented and connected to bounded execution: operations now record duration, success, verification, stage, and resource reservations into a durable SQLite store; health can be derived from recorded observations and routed through the existing canary/lifecycle boundary.**

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. Main commit `6d061efae23d98d689058c01ce65cb63c56ba647` passed GitHub Actions run **575**. Telemetry branch CI run **573** also passed.

## Verified / Tested Foundations
- Core engine, state, tasks, planning, events, permission boundaries, specialist/domain framework, bounded autonomy, research/truth, education, provider routing, security, owner control, and recovery remain integrated.
- Canonical `DORMAMMURuntime` exists; `DEVINTELRuntime` remains only as a compatibility alias.
- Capability/resource discovery, evaluation, lifecycle, local inventory, cryptographic recovery, canary evaluation/rollback, and bounded capability decisions remain implemented/tested.
- Resource management reserves only registered resources, enforces declared capacity/cost/permission, and releases reservations before operation recording.
- Executive contracts separate `Objective`, `GoalUnderstanding`, `TaskSpec`, and `ExecutivePlan` from execution authority.
- Executive execution delegates tasks to the bounded operating path.
- Operational telemetry persists observations and requires a minimum sample count before deriving health.
- Bounded execution automatically records operation duration, success, verification, stage, and resource reservation metadata.
- Active capability health that is healthy is reported as verified without reactivation; unhealthy active health still enters the existing degradation/rollback boundary.
- Main CI run **575** completed successfully for `6d061efae23d98d689058c01ce65cb63c56ba647`.

## Capability Matrix
`DORMAMMU_CAPABILITY_MATRIX.md` is the detailed truthful matrix. It records status, implementation path, tests, CI evidence, dependencies, security status, limitations, next action, version, and last verified commit.

## Current Engineering Gaps
1. **Evidence-backed knowledge synthesis:** connect research/truth/provenance into a stable cross-domain synthesis contract.
2. **Durable resource leases:** operation telemetry is durable, but resource reservations themselves are still in-memory.
3. **Trusted external capability acquisition:** scouts/adapters need end-to-end provenance, license/terms, security, compatibility, permissions, resource, cost, rollback, and observability controls.
4. **Evidence-backed goal understanding:** current default interpreter normalizes explicit fields rather than inferring arbitrary natural-language goals.
5. **Model/agent routing and specialist collaboration:** automated selection and coordination are not complete.
6. **Broad ecosystem capabilities:** communication, community, creation, distribution, awareness, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.

## Safety Boundaries
- Telemetry is evidence, not authority; recording data cannot grant permissions or activate capabilities.
- Health evaluation fails closed until enough observations exist.
- Discovery never installs, executes, authenticates, spends money, or grants authority.
- Lifecycle transitions are explicit and state-validated; capability approval requires permission.
- Executive tasks must explicitly declare objective scope.
- Resource management only reserves already-registered resources and fails closed on unknown capacity.
- Core action execution remains behind the permission boundary.
- Recovery uses externally supplied cryptographic authorization with tamper, expiry, and replay protection.
- Canary failure can produce bounded rollback rather than silent activation.
- No unrestricted self-modification, automatic paid acquisition, credential fabrication, CAPTCHA bypass, or platform-control bypass.

## Not Yet Complete
DORMAMMU is **not** a finished autonomous ecosystem. It now has a tested bounded objective/execution/measurement foundation, but not full arbitrary-objective autonomy, dynamic model/agent routing, cross-domain synthesis, durable resource leasing, autonomous external capability acquisition, or ecosystem-scale learning.

## Next Execution Target
**Evidence-backed knowledge synthesis:** build a stable research/truth/provenance synthesis contract that can combine verified evidence across domains, expose provenance and uncertainty, and feed trustworthy requirements/success criteria into executive planning without turning model output into authority.

Preferred loop:
`RESEARCH → VERIFY EVIDENCE → NORMALIZE CLAIMS → SYNTHESIZE → CHECK CONTRADICTIONS → EXPOSE PROVENANCE/UNCERTAINTY → FEED EXECUTIVE REQUIREMENTS`

## Verification Note
GitHub repository branch-protection/ruleset enforcement has not been independently verified through the available integration, so repository-level protection is not claimed. Architectural lock refers to code-enforced foundation and verified engineering boundaries.
