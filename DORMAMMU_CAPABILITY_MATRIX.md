# DORMAMMU — CAPABILITY MATRIX

This matrix is an engineering checkpoint, not a feature wish-list. Status claims follow:

`PLANNED → DESIGNED → PARTIAL → IMPLEMENTED → TESTED → VERIFIED → DEPLOYED`

`BLOCKED` is used only where an external dependency prevents safe progress.

**Current checkpoint:** Categories 1–10 are complete and locked at the repository architecture level. Production readiness remains unclaimed.

| Capability | Status | Implementation / evidence | Security boundary | Known limitation |
|---|---|---|---|---|
| Foundation & Governance | VERIFIED | charter, working rules, project state, engineering map, governance controls | explicit authority and fail-closed governance | operational governance still needs real deployment evidence |
| Core Intelligence | VERIFIED | cognition, evidence synthesis, routing, learning, semantic safety evaluation, bounded self-model | cognition never grants authority | provider-specific operational evidence remains future work |
| Capability & Resource Intelligence | VERIFIED | discovery, provenance, capability/resource lifecycle, inventory, leases, scheduling | explicit permissions; no silent installation/provisioning/spending | distributed/provider-backed scheduling remains future work |
| Ecosystem Awareness | VERIFIED | bounded aggregation plus approved HTTPS awareness adapter | trusted-source/host/size/time/content gates; observations are untrusted | live multi-source polling/distribution loop remains future work |
| Engineering Intelligence | VERIFIED | bounded static repository/code intelligence and safety tests | static analysis; no implicit import/execute | broader repository graph, dependency vulnerability intelligence, repair loop remain future work |
| Language & Communication | VERIFIED | bounded language intelligence, normalization, tokenization, intent/risk hints, response constraints | advisory only; high-impact intents require confirmation | heuristic language detection and production speech/provider adapters remain future work |
| Research & Domain Expansion | COMPLETE / LOCKED | bounded domain evidence/proposal/assessment/expansion/registry contracts; PR #68; CI #848; main docs CI #850/#851 | verified evidence required; registry admission grants no execution authority | no unrestricted crawler, installation, authentication, spending, publishing, or domain execution |
| Creative Intelligence | COMPLETE / LOCKED | deterministic ideation/variation/planning/critique/repair; consistency; provider compatibility/fallback; verification/safety; lineage persistence; creation handoff; cognition/research/language context; telemetry; PR #69 | advisory creative layer; no publish/spend/auth/authority | real provider credentials/quotas remain environment-dependent |
| Simulation & Interactive Worlds | COMPLETE / LOCKED | deterministic worlds/entities/actions/ticks; planning; replay integrity; persistence/recovery; resource/telemetry runtime integration; PR #70; CI #969; main CI #970 | explicit world action allowlist; no external execution authority | no production physics/rendering/multiplayer authority |
| Social & Community Intelligence | COMPLETE / LOCKED | bounded community observation; demand/question/opportunity/risk signals; deterministic response planning; provenance; fail-closed publication policy; durable plan persistence; runtime telemetry; PR #71; CI #988 | no fake engagement/identity; external publication requires platform authorization and owner approval | real platform adapters, production moderation, live polling and long-running distribution remain future work |
| Economic & Business Intelligence | PARTIAL | opportunity/business foundations | spending and financial authority protected | no autonomous commercial execution |
| Owner & Platform Security | PARTIAL | owner-control, recovery, security foundations | zero-trust boundaries, recovery protections | deeper platform security work remains |
| Autonomous Operations | PARTIAL | bounded autonomy cycle, telemetry, recovery, learning | finite, permission-preflighted, proposal-oriented | continuous distributed operations not built |
| Evolution & Self-Improvement | EARLY | controlled reflection/learning foundations | no unrestricted self-modification | training/evaluation/model factory not built |

## Category 10 completion boundary

Category 10 is complete at the repository architecture level: community observations, member/content normalization, deterministic signal detection, demand/opportunity/question/risk classification, bounded response drafting, provenance retention, fail-closed publication policy, durable plan persistence, runtime telemetry integration, authority-surface tests, and truthful state documentation are implemented and verified. External publication remains separately authorized; intelligence never grants platform authority.

## Category 10 verification evidence

- Feature branch: `codex/category-10-social-community-intelligence`
- Pull request: #71
- Feature-head CI: workflow #988 — **success; 338 tests passed**.
- Runtime integration: `CommunitySubsystemIntegration` connects analysis to the existing operational telemetry path.
- Durable plans use bounded SQLite persistence with content-addressed identifiers.
- Publication decisions require platform authorization and owner approval; the community intelligence layer contains no publish transport.

## Highest-priority gaps after Category 10

1. Category 11 — Economic & Business Intelligence.
2. Deeper Owner & Platform Security.
3. Real external research providers and live multi-source adapters.
4. Full repository graph/dependency intelligence and broader coding-agent orchestration.
5. Distributed resource/provider scheduling and broader operational telemetry.
6. Production speech/audio and communication-channel adapters.
7. Model Training & Evolution / Model Factory.
8. Production operational evidence for real providers and models.

## Verification rule

`TESTED` means meaningful repository tests exist and passed. `VERIFIED` requires stronger integration/operational evidence appropriate to the capability. `DEPLOYED` requires an authorized real deployment. Documentation, imports, or a green unit test alone never constitute production proof.
