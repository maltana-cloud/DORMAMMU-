# DORMAMMU — CAPABILITY MATRIX

This matrix is an engineering checkpoint, not a feature wish-list. Status claims follow:

`PLANNED → DESIGNED → PARTIAL → IMPLEMENTED → TESTED → VERIFIED → DEPLOYED`

`BLOCKED` is used only where an external dependency prevents safe progress.

**Matrix checkpoint:** bounded autonomous operating, durable resource leases, trusted capability admission, bounded catalog scouting, and model/agent/specialist routing are merged on `main`. Routing PR #54 passed CI before merge at `d91d89b7b5bf4c9de6f6e37c85416f77e4003334`.

| Capability | Status | Implementation path | Tests | CI evidence | Dependencies | Security status | Known limitations | Next action | Version | Last verified commit |
|---|---|---|---|---|---|---|---|---|---|---|
| DORMAMMU identity migration | IMPLEMENTED | `DORMAMMU_CHARTER.md`; `DORMAMMU_*`; `devintel/runtime/` | compatibility coverage | successful CI | legacy namespace compatibility | Protected; no blind rename | legacy names remain intentionally | Remove legacy naming where compatibility permits | 1.0 | `a3c730...` |
| Capability & Resource Discovery | VERIFIED | `devintel/capabilities/` discovery, evidence, acquisition, catalog | discovery/acquisition/provenance/catalog/lifecycle/runtime tests | PR #51 CI passed | registries, provenance, evaluator, lifecycle, canary | Fail-closed strict provenance; no automatic trust/install/auth | external sources require explicit trusted-source configuration | Add legitimate source-specific configuration as needed | 1.2 | `74b9843...` |
| Resource / Compute Management | VERIFIED | `devintel/capabilities/resources.py`, `leases.py`, `inventory.py` | resource/lease/runtime tests | successful CI | resource registry, durable lease store, local inventory | fail-closed capacity; no provisioning/spending | no distributed scheduler | Add richer metrics/scheduling | 1.1 | `11d3eb5...` |
| Domain Intelligence | TESTED | `devintel/modules/` research, education, specialists | domain/module suite | successful CI | core runtime, providers | bounded modules | coverage uneven | Connect more domain services | 1.0 | `d73d6b6...` |
| Ecosystem Awareness | PARTIAL | research/providers/publishing-facing modules | existing tests | successful CI | live adapters, truth/provenance | external content untrusted | no complete cross-platform loop | Build source aggregation + freshness/importance | 0.1 | `d73d6b6...` |
| Knowledge synthesis / cross-domain reasoning | TESTED | `devintel/modules/research/synthesis.py`; runtime | synthesis/runtime/security tests | successful CI | verified claims, provenance | contradictions/uncertainty preserved | not full reasoning | Add broader evidence composition | 0.2 | `d73d6b6...` |
| Executive cognition foundation | TESTED | `devintel/executive/` contracts/engine/evidence | executive tests | successful CI | bounded operations, capability/resource decision | explicit scope/approval | no arbitrary high-impact goal inference | Add evidence-backed goal understanding | 0.1 | `d73d6b6...` |
| Model / Agent / Specialist Routing | VERIFIED | `devintel/executive/routing.py` | `tests/test_specialist_routing.py` | PR #54 CI passed | registered specialists, health, approval, explicit requirements | selection is not authority; downstream permission mandatory | deterministic/local; no autonomous enrollment or outcome-aware adaptation | Feed verified outcomes into controlled routing policy later | 1.0 | `d91d89b...` |
| Operational telemetry | TESTED | `devintel/operations/telemetry.py`; bounded/autonomy stores | telemetry/bounded/runtime/autonomy tests | successful CI | bounded execution, SQLite | evidence only | richer provider/resource metrics pending | Feed verified outcomes into reflection | 0.2 | `d73d6b6...` |
| Full autonomous operating path | VERIFIED | `devintel/autonomy/`, executive, operations, capabilities, routing | autonomy/safety/cycle/runtime/routing tests | PR #52 + PR #54 CI passed | cognition, routing, resource/capability, permission, verification | bounded, permission-preflighted, finite, proposal-only improvement | no arbitrary NL inference or automatic learning | Implement controlled reflection/outcome learning | 0.6 | `d91d89b...` |
| Model Training & Evolution | PLANNED | architecture direction | none | baseline | datasets, compute, evaluation, governance | no unrestricted self-modification | loop not built | Define isolated training/evaluation contracts | 0.1 | `d73d6b6...` |
| Engineering / Coding Intelligence | PARTIAL | developer/domain modules + bounded execution | existing tests | successful CI | core, tools, sandbox | generated code controlled | no complete coding-agent loop | Connect coding specialist to bounded execution | 0.1 | `d73d6b6...` |
| Language & Speech Intelligence | PLANNED | architecture intent | none | baseline | routing, providers, platform I/O | credentials isolated | no production speech subsystem | Define contracts | 0.1 | `d73d6b6...` |
| Opinion Intelligence | PLANNED | charter intent | none | baseline | truth/provenance, discourse | fact/opinion/speculation separated | no engine | Define contract | 0.1 | `d73d6b6...` |
| Platform Identity & Account Management | PARTIAL | control/security + adapters | security/control/provider tests | successful CI | auth/session/capability boundaries | identity separated from authority | no complete identity plane | Implement scoped account/session contracts | 0.1 | `d73d6b6...` |
| Community Intelligence | PARTIAL | community/publishing-facing modules | existing tests | successful CI | platform adapters, identity, memory, policy | no fake engagement | no autonomous community loop | Build isolated community state/policy | 0.1 | `d73d6b6...` |
| Crypto / Blockchain Ecosystem | PLANNED | domain scope | none | baseline | market data, security, account controls | no unrestricted trading/withdrawal | no subsystem | Define read-only intelligence contracts | 0.1 | `d73d6b6...` |
| Creative / Media Systems | PARTIAL | creative/media architecture/modules | applicable tests | successful CI | routing, resources, verification | generation not quality proof | no complete pipeline | Define asset/project/quality contracts | 0.1 | `d73d6b6...` |
| Music / Audio | PLANNED | architecture intent | none | baseline | media/audio providers, resources | providers untrusted | no system | Define contracts | 0.1 | `d73d6b6...` |
| Gaming | PLANNED | architecture intent | none | baseline | creative/media, runtime, resources | actions scoped | no subsystem | Define boundary | 0.1 | `d73d6b6...` |
| Business / Revenue / Reinvestment | PARTIAL | opportunity/business modules + owner control | existing tests | successful CI | analytics, owner control, financial boundaries | spending protected | no autonomous commercial execution | Implement outcome contracts | 0.1 | `d73d6b6...` |
| Owner Identity / Zero-Trust Recovery | TESTED | security recovery/orchestrator/owner control | recovery tests | successful CI | external secret provisioning | HMAC tamper/expiry/replay protection | provisioning external | Harden provisioning | 1.0 | `d73d6b6...` |
| Self-Model / Resilience / Continuous Evolution | PARTIAL | autonomy, monitoring, security, recovery, capability lifecycle | autonomy/security/monitoring tests | successful CI | observations, metrics, recovery, controlled improvement | proposal-only improvement | no automatic outcome learning | Implement controlled reflection/learning | 0.2 | `d73d6b6...` |

## Highest-priority gaps

1. **Controlled reflection/outcome learning** — verified outcomes are recorded but do not yet update routing/planning through a bounded auditable policy.
2. **Evidence-backed arbitrary natural-language goal understanding** — explicit structured goals remain the safe boundary.
3. **Production capability source configuration** — generic scouts exist; each real source needs explicit trusted provenance configuration and validation.
4. **Broad ecosystem capabilities** — communication, community, creation, distribution, awareness, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.
5. **Distributed resource/provider scheduling** — current routing is deterministic/local.

## Blocked vs not built

Missing credentials or platform verification are not software failures. They become `BLOCKED` only when software is ready and an external owner/platform action is genuinely required.

At this checkpoint no listed major capability is `BLOCKED`; several remain not built.

## Verification rule

`TESTED` means meaningful repository tests exist and passed. `VERIFIED` requires stronger integration/operational evidence appropriate to the capability. `DEPLOYED` requires an authorized real deployment. Documentation, imports, or a green unit test alone never constitute production proof.
