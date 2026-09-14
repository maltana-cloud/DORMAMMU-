# DORMAMMU — CAPABILITY MATRIX

This matrix is an engineering checkpoint, not a feature wish-list. Status claims follow:

`PLANNED → DESIGNED → PARTIAL → IMPLEMENTED → TESTED → VERIFIED → DEPLOYED`

`BLOCKED` is used only where an external dependency prevents safe progress.

**Current checkpoint:** Categories 1–7 are complete and locked at the repository architecture level. Category 8 is actively being completed on its feature branch and is intentionally not marked complete. Production readiness remains unclaimed.

| Capability | Status | Implementation / evidence | Security boundary | Known limitation |
|---|---|---|---|---|
| Foundation & Governance | VERIFIED | charter, working rules, project state, engineering map, governance controls | explicit authority and fail-closed governance | operational governance still needs real deployment evidence |
| Core Intelligence | VERIFIED | cognition, evidence synthesis, routing, learning, semantic safety evaluation, bounded self-model | cognition never grants authority | provider-specific operational evidence remains future work |
| Capability & Resource Intelligence | VERIFIED | discovery, provenance, capability/resource lifecycle, inventory, leases, scheduling | explicit permissions; no silent installation/provisioning/spending | distributed/provider-backed scheduling remains future work |
| Ecosystem Awareness | VERIFIED | bounded aggregation plus approved HTTPS awareness adapter | trusted-source/host/size/time/content gates; observations are untrusted | live multi-source polling/distribution loop remains future work |
| Engineering Intelligence | VERIFIED | bounded static repository/code intelligence and safety tests | static analysis; no implicit import/execute | broader repository graph, dependency vulnerability intelligence, repair loop remain future work |
| Language & Communication | VERIFIED | bounded language intelligence, normalization, tokenization, intent/risk hints, response constraints | advisory only; high-impact intents require confirmation | heuristic language detection and production speech/provider adapters remain future work |
| Research & Domain Expansion | COMPLETE / LOCKED | bounded domain evidence/proposal/assessment/expansion/registry contracts; PR #68; CI #848; main docs CI #850/#851 | verified evidence required; confidence/risk/capability coverage are fail-closed; registry admission grants no execution authority | no unrestricted crawler, installation, authentication, spending, publishing, or domain execution |
| Creative Intelligence | PARTIAL | `devintel/modules/creative/`: ideation, variations, planning, critique/repair, consistency contracts, provider/resource compatibility, lineage, runtime integration and tests | advisory-only creative layer; no publish/spend/auth/authority; provider catalogue does not contact providers | deeper cognition/research/language/security/telemetry integration, durable persistence, richer quality verification, and authorized creation adapters remain |
| Simulation & Interactive Worlds | PLANNED | architecture direction | scoped actions only | no subsystem yet |
| Social & Community Intelligence | PARTIAL | community/publishing-facing modules and policy foundations | no fake engagement; identity and authority separated | no complete autonomous community loop |
| Economic & Business Intelligence | PARTIAL | opportunity/business foundations | spending and financial authority protected | no autonomous commercial execution |
| Owner & Platform Security | PARTIAL | owner-control, recovery, security foundations | zero-trust boundaries, recovery protections | deeper platform security work remains |
| Autonomous Operations | PARTIAL | bounded autonomy cycle, telemetry, recovery, learning | finite, permission-preflighted, proposal-oriented | continuous distributed operations not built |
| Evolution & Self-Improvement | EARLY | controlled reflection/learning foundations | no unrestricted self-modification | training/evaluation/model factory not built |

## Category 8 completion boundary

Category 8 is complete only when creative understanding, ideation, planning, creation integration, critique, repair, verification, consistency, provenance/lineage, resource/provider awareness, cognition/research/language integration, permission/security boundaries, observability, persistence requirements, tests, CI, and truthful project-state documentation are all implemented and verified. External creation/publishing remains authorized and bounded; intelligence itself never grants authority.

## Current Category 8 evidence

- Feature branch: `codex/category-8-creative-intelligence`
- Runtime integration: `DORMAMMURuntime.creative` and `creative_plan(...)`
- Current test coverage includes deterministic planning, ideation/variation bounds, critique/revision, consistency, provider fallback/compatibility, lineage, runtime integration, and authority-surface checks.
- Latest observed repository test workflow before the most recent documentation commit passed; the latest documentation commit's workflow must still be observed.

## Highest-priority gaps after Category 7

1. Finish Category 8 — Creative Intelligence before moving to Category 9.
2. Real external research providers and live multi-source research adapters.
3. Full repository graph/dependency intelligence and broader coding-agent orchestration.
4. Distributed resource/provider scheduling and broader operational telemetry.
5. Production speech/audio and communication-channel adapters.
6. Model Training & Evolution / Model Factory.
7. Production operational evidence for real providers and models.

## Verification rule

`TESTED` means meaningful repository tests exist and passed. `VERIFIED` requires stronger integration/operational evidence appropriate to the capability. `DEPLOYED` requires an authorized real deployment. Documentation, imports, or a green unit test alone never constitute production proof.
