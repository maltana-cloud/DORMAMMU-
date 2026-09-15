# DORMAMMU — CAPABILITY MATRIX

This matrix is an engineering checkpoint, not a feature wish-list. Status claims follow:

`PLANNED → DESIGNED → PARTIAL → IMPLEMENTED → TESTED → VERIFIED → DEPLOYED`

`BLOCKED` is used only where an external dependency prevents safe progress.

**Current checkpoint:** Categories 1–13 are complete and locked at the repository architecture level. Production readiness remains unclaimed.

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
| Economic & Business Intelligence | COMPLETE / LOCKED | bounded opportunity/evidence analysis; deterministic business planning/comparison; durable advisory-plan persistence; runtime telemetry; fail-closed financial action policy | intelligence never grants spending/investment/payment/credential authority | real financial feeds, commerce adapters and production financial controls remain future work |
| Owner & Platform Security | COMPLETE / LOCKED | cryptographically authenticated owner approvals; fail-closed migration boundary; bounded single-use approvals; tamper-evident audit chain; scoped containment/recovery; recovery authorization; security regression coverage; PR #73; CI #1029 (352 passed) | owner proof is scoped/time-bound; intelligence, external content, models, capabilities, and runtime state do not grant authority; recovery remains independently protected | production identity/session integration, secret rotation, secure deployment, and operational security evidence remain external/deployment work |
| Autonomous Operations | COMPLETE / LOCKED | bounded autonomous cycle; scoped observe/plan/permission/act/verify/record/improve loop; durable cycle history; operation telemetry; capability/resource integration; bounded multi-cycle supervisor with cycle/duration limits and fail-closed stop behavior | autonomy remains finite and permission-gated; improvement is proposal-only; no unrestricted background execution | production scheduler/workers, distributed coordination, durable production infrastructure, live health/alerting and deployment evidence remain future work |
| Evolution & Self-Improvement | EARLY | controlled reflection/learning foundations | no unrestricted self-modification | training/evaluation/model factory not built |

## Category 13 completion boundary

Category 13 is complete at the repository architecture level: autonomous execution is bounded, scoped, permission-preflighted, verified, durably recorded, observable, and repeatable under explicit finite supervisory limits. Failure stops are fail-closed. Learning/improvement produces proposals only and cannot modify code, authority, secrets, or security policy. Production schedulers, distributed workers, deployment infrastructure, and environment-specific operational evidence remain explicit external/deployment dependencies.

## Verification rule

`TESTED` means meaningful repository tests exist and passed. `VERIFIED` requires stronger integration/operational evidence appropriate to the capability. `DEPLOYED` requires an authorized real deployment. Documentation, imports, or a green unit test alone never constitute production proof.
