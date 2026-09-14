# DORMAMMU STATUS

## Current Milestone
**Durable resource leases are implemented on the active engineering branch.** Resource reservations now use a SQLite-backed lease store with expiry, release, persistence across runtime reopen, and transaction-protected capacity acquisition. This milestone is not yet merged or marked VERIFIED; CI and integration verification remain required.

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. `main` remains unchanged at `8ee3881a2a4c269f9ebeb0cd32b9f0ebf75f1219` while durable-lease work proceeds on `codex/durable-resource-leases`.

## Repository Checkpoint
- Canonical runtime: `DORMAMMURuntime`; `DEVINTELRuntime` remains a compatibility alias.
- Evidence-backed knowledge synthesis and executive integration exist on `main`.
- Capability/resource discovery, lifecycle, local inventory, canary evaluation, bounded decisions, operational telemetry, owner control, security and recovery remain integrated.
- Active branch adds `ResourceLeaseStore`, durable resource reservations, lease expiry, atomic capacity acquisition, runtime-configurable lease persistence, and runtime reopen coverage.

## Current Engineering Gaps
1. **Durable resource lease verification:** active branch implementation needs full CI and final integration/security review before merge.
2. **Trusted external capability acquisition:** scouts/adapters still need end-to-end provenance, license/terms, security, compatibility, permissions, resource, cost, rollback, and observability controls.
3. **Evidence-backed arbitrary natural-language goal understanding:** current interpreter normalizes explicit fields rather than safely inferring arbitrary goals.
4. **Model/agent/specialist routing and collaboration:** automated selection and coordination remain incomplete.
5. **Reflection/learning:** telemetry exists, but no controlled outcome-learning loop yet turns evidence into bounded improvement.
6. **Broad ecosystem capabilities:** communication, community, creation, distribution, awareness, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.

## Safety Boundaries
- Resource leases only reserve already-registered resources; they never provision machines, acquire credentials, spend money, or grant authority.
- Lease capacity acquisition is transaction-protected and fails closed when capacity is unknown or insufficient.
- Lease expiry releases capacity automatically; release is explicit and unknown lease IDs are rejected.
- Discovery never installs, executes, authenticates, spends money, or grants authority.
- Core action execution remains behind the permission boundary.
- Recovery uses externally supplied cryptographic authorization with tamper, expiry, and replay protection.
- No unrestricted self-modification, automatic paid acquisition, credential fabrication, CAPTCHA bypass, or platform-control bypass.

## Capability Matrix
`DORMAMMU_CAPABILITY_MATRIX.md` remains the detailed capability record. It must be updated after CI/integration verification of this branch; until then durable resource management remains `TESTED` rather than `VERIFIED`.

## Next Execution Target
Finish durable resource lease verification, merge only after successful CI and integration/security checks, then update the truthful matrix/state and proceed to the next highest-value dependency: **trusted external capability acquisition** unless repository inspection shows a more foundational blocker.

Preferred resource path:
`REGISTERED RESOURCE → ELIGIBILITY → DURABLE LEASE → EXPIRY/RELEASE → BOUNDED OPERATION → TELEMETRY → HEALTH/CANARY`

## Verification Note
Repository branch-protection/ruleset enforcement has not been independently verified through the available integration, so repository-level protection is not claimed. Architectural safety boundaries remain code-enforced.
