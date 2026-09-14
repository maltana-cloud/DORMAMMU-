# DORMAMMU — CAPABILITY MATRIX

This matrix is an engineering checkpoint, not a feature wish-list. Status claims follow:

`PLANNED → DESIGNED → PARTIAL → IMPLEMENTED → TESTED → VERIFIED → DEPLOYED`

`BLOCKED` is used only where an external dependency prevents safe progress.

**Current checkpoint:** Categories 1–8 are complete and locked at the repository architecture level. Production readiness remains unclaimed.

| Capability | Status | Implementation / evidence | Security boundary | Known limitation |
|---|---|---|---|---|
| Foundation & Governance | VERIFIED | charter, working rules, project state, engineering map, governance controls | explicit authority and fail-closed governance | operational governance still needs real deployment evidence |
| Core Intelligence | VERIFIED | cognition, evidence synthesis, routing, learning, semantic safety evaluation, bounded self-model | cognition never grants authority | provider-specific operational evidence remains future work |
| Capability & Resource Intelligence | VERIFIED | discovery, provenance, capability/resource lifecycle, inventory, leases, scheduling | explicit permissions; no silent installation/provisioning/spending | distributed/provider-backed scheduling remains future work |
| Ecosystem Awareness | VERIFIED | bounded aggregation plus approved HTTPS awareness adapter | trusted-source/host/size/time/content gates; observations are untrusted | live multi-source polling/distribution loop remains future work |
| Engineering Intelligence | VERIFIED | bounded static repository/code intelligence and safety tests | static analysis; no implicit import/execute | broader repository graph, dependency vulnerability intelligence, repair loop remain future work |
| Language & Communication | VERIFIED | bounded language intelligence, normalization, tokenization, intent/risk hints, response constraints | advisory only; high-impact intents require confirmation | heuristic language detection and production speech/provider adapters remain future work |
| Research & Domain Expansion | COMPLETE / LOCKED | bounded domain evidence/proposal/assessment/expansion/registry contracts; PR #68; CI #848; main docs CI #850/#851 | verified evidence required; confidence/risk/capability coverage are fail-closed; registry admission grants no execution authority | no unrestricted crawler, installation, authentication, spending, publishing, or domain execution |
| Creative Intelligence | COMPLETE / LOCKED | deterministic ideation/variation/planning/critique/repair; consistency; provider compatibility/fallback; verification/safety; lineage persistence; creation-request handoff; language/research/cognition context; runtime telemetry integration; PR #69; CI #946 (320 passed) | advisory creative layer; no publish/spend/auth/authority; creation adapter only constructs a host-routed request and does not execute providers | subjective artistic quality and factual truth require downstream verification; real provider credentials/quotas remain environment-dependent |
| Simulation & Interactive Worlds | PLANNED | architecture direction | scoped actions only | no subsystem yet |
| Social & Community Intelligence | PARTIAL | community/publishing-facing modules and policy foundations | no fake engagement; identity and authority separated | no complete autonomous community loop |
| Economic & Business Intelligence | PARTIAL | opportunity/business foundations | spending and financial authority protected | no autonomous commercial execution |
| Owner & Platform Security | PARTIAL | owner-control, recovery, security foundations | zero-trust boundaries, recovery protections | deeper platform security work remains |
| Autonomous Operations | PARTIAL | bounded autonomy cycle, telemetry, recovery, learning | finite, permission-preflighted, proposal-oriented | continuous distributed operations not built |
| Evolution & Self-Improvement | EARLY | controlled reflection/learning foundations | no unrestricted self-modification | training/evaluation/model factory not built |

## Category 8 completion boundary

Category 8 is complete at the repository architecture level: creative understanding, ideation, planning, creation handoff, critique, repair, verification, consistency, provenance/lineage, resource/provider awareness, cognition/research/language integration, permission/security boundaries, observability, persistence, tests, CI, and truthful project-state documentation are implemented and verified. External creation/publishing remains authorized and bounded; intelligence itself never grants authority.

## Category 8 verification evidence

- Feature branch: `codex/category-8-creative-intelligence`
- Pull request: #69
- Feature-head CI: workflow #946 — **success; 320 tests passed**.
- Runtime integration: `DORMAMMURuntime.creative`, `creative_plan(...)`, `creative_context_for(...)`, and `creative_creation_request(...)`.
- Durable lineage is opt-in through `creative_lineage_store_path`; default runtime storage remains in-memory.
- Creation handoff uses the existing host-controlled generation request contract; the creative layer does not contact providers or grant execution authority.

## Highest-priority gaps after Category 8

1. Category 9 — Simulation & Interactive Worlds.
2. Real external research providers and live multi-source research adapters.
3. Full repository graph/dependency intelligence and broader coding-agent orchestration.
4. Distributed resource/provider scheduling and broader operational telemetry.
5. Production speech/audio and communication-channel adapters.
6. Model Training & Evolution / Model Factory.
7. Production operational evidence for real providers and models.

## Verification rule

`TESTED` means meaningful repository tests exist and passed. `VERIFIED` requires stronger integration/operational evidence appropriate to the capability. `DEPLOYED` requires an authorized real deployment. Documentation, imports, or a green unit test alone never constitute production proof.
