# DORMAMMU STATUS

## Current Milestone
**Trusted capability discovery and admission is implemented and verified on `main`.** DORMAMMU now has explicit provenance evidence, strict trust-source gating, security/compatibility/performance/license/cost/permission evaluation, deterministic acquisition ranking and fallback planning, explicit owner approval, lifecycle/canary controls, and durable SQLite-backed admitted-capability state.

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. The trusted capability admission milestone was merged to `main` at `d6b8431f98a13a825875a9a6e8aaaffa773a39ec` after the final branch CI passed.

## Repository Checkpoint
- Canonical runtime: `DORMAMMURuntime`; `DEVINTELRuntime` remains a compatibility alias.
- Evidence-backed knowledge synthesis and executive integration exist on `main`.
- Durable resource leases are implemented with expiry, atomic capacity acquisition, persistence, and runtime integration.
- Capability discovery now has provenance-aware evidence and strict admission gates; newly discovered external candidates are not trusted automatically.
- Capability acquisition coordinates discovery → evaluation → explicit approval → lifecycle registration → canary → fallback without installing software, acquiring credentials, spending money, executing external candidates, or bypassing owner/platform controls.

## Current Engineering Gaps
1. **Production capability discovery adapters:** legitimate source adapters still need to be built and explicitly trusted per source; external candidates remain untrusted until provenance and all gates pass.
2. **Evidence-backed arbitrary natural-language goal understanding:** current interpreter normalizes explicit fields rather than safely inferring arbitrary goals.
3. **Model/agent/specialist routing and collaboration:** automated selection and coordination remain incomplete.
4. **Reflection/learning:** telemetry exists, but no controlled outcome-learning loop yet turns evidence into bounded improvement.
5. **Broad ecosystem capabilities:** communication, community, creation, distribution, awareness, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.

## Safety Boundaries
- Capability provenance is evidence, not authority.
- External candidates fail closed when provenance/trusted-source evidence is absent in strict mode.
- Capability admission still requires explicit owner approval and the existing lifecycle/canary gates.
- Resource leases only reserve already-registered resources; they never provision machines, acquire credentials, spend money, or grant authority.
- Core action execution remains behind the permission boundary.
- Recovery uses externally supplied cryptographic authorization with tamper, expiry, and replay protection.
- No unrestricted self-modification, automatic paid acquisition, credential fabrication, CAPTCHA bypass, or platform-control bypass.

## Capability Matrix
`DORMAMMU_CAPABILITY_MATRIX.md` is reconciled to the verified capability-admission and durable-resource milestones.

## Next Execution Target
Proceed to the next highest-value dependency: **production capability discovery adapters and source-specific trust configuration**, then verify and move to the next category.

Preferred capability path:
`REQUIREMENT → CAPABILITY REGISTRY → GAP → SCOUT → PROVENANCE → TRUST → SECURITY → COMPATIBILITY → PERFORMANCE → COST → LICENSE → PERMISSION → COMPARE → SELECT → EXPLICIT APPROVAL → REGISTER → CANARY → ACTIVATE → MONITOR → FALLBACK`

## Verification Note
Repository branch-protection/ruleset enforcement has not been independently verified through the available integration, so repository-level protection is not claimed. Architectural safety boundaries remain code-enforced.
