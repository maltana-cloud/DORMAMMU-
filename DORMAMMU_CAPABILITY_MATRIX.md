# DORMAMMU — CAPABILITY MATRIX

This matrix is an engineering checkpoint, not a feature wish-list. Status claims follow:

`PLANNED → DESIGNED → PARTIAL → IMPLEMENTED → TESTED → VERIFIED → DEPLOYED`

`BLOCKED` is used only where an external dependency prevents safe progress.

**Current checkpoint:** Categories 1–7 are complete and locked at the repository architecture level. Category 7 was implemented in PR #68, merged as `be49628ed4ac7039f20823731b71e9f59bf7cb1a`, tested by feature-head CI #848, and followed by successful main-branch documentation checkpoint runs #850 and #851. Production readiness remains unclaimed.

| Capability | Status | Implementation / evidence | Security boundary | Known limitation |
|---|---|---|---|---|
| Foundation & Governance | VERIFIED | charter, working rules, project state, engineering map, governance controls | explicit authority and fail-closed governance | operational governance still needs real deployment evidence |
| Core Intelligence | VERIFIED | cognition, evidence synthesis, routing, learning, semantic safety evaluation, bounded self-model | cognition never grants authority | provider-specific operational evidence remains future work |
| Capability & Resource Intelligence | VERIFIED | discovery, provenance, capability/resource lifecycle, inventory, leases, scheduling | explicit permissions; no silent installation/provisioning/spending | distributed/provider-backed scheduling remains future work |
| Ecosystem Awareness | VERIFIED | bounded aggregation plus approved HTTPS awareness adapter | trusted-source/host/size/time/content gates; observations are untrusted | live multi-source polling/distribution loop remains future work |
| Engineering Intelligence | VERIFIED | bounded static repository/code intelligence and safety tests | static analysis; no implicit import/execute | broader repository graph, dependency vulnerability intelligence, repair loop remain future work |
| Language & Communication | VERIFIED | bounded language intelligence, normalization, tokenization, intent/risk hints, response constraints | advisory only; high-impact intents require confirmation | heuristic language detection and production speech/provider adapters remain future work |
| Research & Domain Expansion | COMPLETE / LOCKED | `devintel/modules/research/` bounded domain evidence/proposal/assessment/expansion/registry contracts; PR #68; CI #848; main docs CI #850/#851 | verified evidence required; confidence/risk/capability coverage are fail-closed; registry admission grants no execution authority | no unrestricted crawler, installation, authentication, spending, publishing, or domain execution |
| Creative Intelligence | NEXT | architecture target | must reuse existing permission, resource, verification and recovery boundaries | major implementation work remains |
| Simulation & Interactive Worlds | PLANNED | architecture direction | scoped actions only | no subsystem yet |
| Social & Community Intelligence | PARTIAL | community/publishing-facing modules and policy foundations | no fake engagement; identity and authority separated | no complete autonomous community loop |
| Economic & Business Intelligence | PARTIAL | opportunity/business foundations | spending and financial authority protected | no autonomous commercial execution |
| Owner & Platform Security | PARTIAL | owner-control, recovery, security foundations | zero-trust boundaries, recovery protections | deeper platform security work remains |
| Autonomous Operations | PARTIAL | bounded autonomy cycle, telemetry, recovery, learning | finite, permission-preflighted, proposal-oriented | continuous distributed operations not built |
| Evolution & Self-Improvement | EARLY | controlled reflection/learning foundations | no unrestricted self-modification | training/evaluation/model factory not built |

## Category 7 completion boundary

Category 7 is complete when DORMAMMU can represent a proposed new domain using explicit evidence and boundaries, assess that proposal against verification state, evidence confidence, declared risk, and required capability coverage, and admit only eligible proposals into a deterministic versioned registry. Registration is separate from execution authority.

The implemented boundary deliberately does **not** make domain expansion equivalent to unrestricted autonomous acquisition. It does not install code, execute providers, authenticate accounts, spend money, publish externally, bypass platform controls, or grant permissions.

## Category 7 verification evidence

- PR #68: `feat: complete category 7 research and domain expansion`
- Merge commit: `be49628ed4ac7039f20823731b71e9f59bf7cb1a`
- Feature-head CI: workflow #848 — successful, including tests
- Main checkpoint CI: workflow #850 — successful
- Subsequent main documentation CI: workflow #851 — successful

## Highest-priority gaps after Category 7

1. Category 8 — Creative Intelligence.
2. Real external research providers and live multi-source research adapters.
3. Full repository graph/dependency intelligence and broader coding-agent orchestration.
4. Distributed resource/provider scheduling and broader operational telemetry.
5. Production speech/audio and communication-channel adapters.
6. Model Training & Evolution / Model Factory.
7. Production operational evidence for real providers and models.

## Verification rule

`TESTED` means meaningful repository tests exist and passed. `VERIFIED` requires stronger integration/operational evidence appropriate to the capability. `DEPLOYED` requires an authorized real deployment. Documentation, imports, or a green unit test alone never constitute production proof.
