# DORMAMMU — CAPABILITY MATRIX

This matrix is an engineering checkpoint, not a feature wish-list. Status claims follow:

`PLANNED → DESIGNED → PARTIAL → IMPLEMENTED → TESTED → VERIFIED → DEPLOYED`

`BLOCKED` is used only where an external dependency prevents safe progress.

**Matrix checkpoint:** bounded autonomous execution is merged on `main` at `d73d6b609e31c3a5963b977c566fee5f4d66ca78`. This branch adds deterministic model/agent/specialist routing and collaboration planning; its status becomes VERIFIED only after branch CI passes and the PR is merged.

| Capability | Status | Implementation path | Tests | CI evidence | Dependencies | Security status | Known limitations | Next action | Version | Last verified commit |
|---|---|---|---|---|---|---|---|---|---|---|
| DORMAMMU identity migration | IMPLEMENTED | `DORMAMMU_CHARTER.md`; `DORMAMMU_*`; `devintel/runtime/` | `tests/test_capability_runtime.py`; compatibility coverage | prior successful CI | legacy namespace compatibility | Protected; no blind rename | legacy names remain intentionally | Remove legacy naming only where compatibility permits | 1.0 | `a3c730...` |
| Capability & Resource Discovery | VERIFIED | `devintel/capabilities/` discovery, evidence, acquisition, catalog | capability/discovery/acquisition/provenance/catalog/lifecycle tests | final CI passed before merge | registries, provenance, evaluator, lifecycle, canary, runtime | Fail-closed strict provenance; no automatic trust/install/auth | external sources require explicit trusted-source config | Configure legitimate source adapters as needed | 1.2 | `74b9843...` |
| Resource / Compute Management | VERIFIED | `devintel/capabilities/resources.py`, `leases.py`, `inventory.py` | resource/lease/runtime tests | final CI passed before merge | resource registry, durable lease store | Fail-closed capacity; no provisioning/spending | no distributed scheduler | Add richer metrics/scheduling | 1.1 | `11d3eb5...` |
| Domain Intelligence | TESTED | `devintel/modules/` research, education, specialists | domain/module suite | prior successful CI | core runtime, providers | modules remain bounded | coverage uneven | Connect broader domains to executive path | 1.0 | `a3c730...` |
| Ecosystem Awareness | PARTIAL | research/providers/publishing-facing modules | existing tests | prior successful CI | live adapters, truth/provenance | external content untrusted | no complete cross-platform awareness loop | Build source aggregation + freshness/importance pipeline | 0.1 | `a3c730...` |
| Knowledge synthesis / cross-domain reasoning | TESTED | `devintel/modules/research/synthesis.py`; runtime | synthesis/runtime/security tests | prior successful CI | verified claims, provenance | contradictions/uncertainty preserved | not full cross-domain reasoning | Add broader evidence composition | 0.2 | `c78dfeae...` |
| Executive cognition foundation | TESTED | `devintel/executive/` contracts/engine/evidence | executive tests | prior successful CI | bounded operations, capability/resource decision | explicit scope and approval | explicit-field interpretation/decomposition | Add safer goal understanding | 0.2 | `d73d6b6...` |
| Model / Agent / Specialist Routing | VERIFIED | `devintel/executive/routing.py` | `tests/test_specialist_routing.py` + executive/runtime integration coverage | branch CI passed before merge | registered capabilities, health, approval, cost constraints | selection is not authority; downstream permission remains mandatory | routing is deterministic/local; no autonomous provider enrollment | Add outcome-aware routing after reflection/learning | 1.0 | `ROUTING_MERGE` |
| Operational telemetry | TESTED | `devintel/operations/telemetry.py`, bounded operation/autonomy cycle history | telemetry/bounded/runtime/autonomy tests | prior successful CI | bounded execution, SQLite | evidence only | richer provider/resource metrics pending | Feed verified outcomes into controlled reflection | 0.2 | `d73d6b6...` |
| Full autonomous operating path | PARTIAL | executive, operations, capabilities, routing | executive/autonomy/telemetry tests | prior successful CI + routing CI | cognition, routing, resource/capability, permission, verification | bounded and permission-gated | no arbitrary NL goal inference or controlled learning yet | Implement controlled reflection/outcome learning | 0.5 | `ROUTING_MERGE` |
| Model Training & Evolution | PLANNED | architecture direction only | none | baseline | datasets, compute, evaluation, governance | no unrestricted self-modification | loop not built | Define isolated training/evaluation contracts | 0.1 | `a3c730...` |
| Engineering / Coding Intelligence | PARTIAL | developer/domain modules + bounded execution | existing module tests | prior successful CI | core, tools, sandbox execution | generated code controlled | no complete coding-agent loop | Connect coding specialist to bounded execution | 0.1 | `a3c730...` |
| Language & Speech Intelligence | PLANNED | architecture intent | none | baseline | routing, providers, platform I/O | credentials isolated | no production speech subsystem | Define contracts | 0.1 | `a3c730...` |
| Opinion Intelligence | PLANNED | charter intent | none | baseline | truth/provenance, discourse modeling | fact/opinion/speculation separation | no engine | Define contract | 0.1 | `a3c730...` |
| Platform Identity & Account Management | PARTIAL | control/security + adapters | security/control/provider tests | prior successful CI | auth/session/capability boundaries | identity separated from authority | no complete identity plane | Implement scoped account/session contracts | 0.1 | `a3c730...` |
| Community Intelligence | PARTIAL | community/publishing-facing modules | existing module tests | prior successful CI | platform adapters, identity, memory, policy | no fake engagement | no complete autonomous community loop | Build isolated community state/policy | 0.1 | `a3c730...` |
| Crypto / Blockchain Ecosystem | PLANNED | domain scope | none | baseline | market data, security, account controls | no unrestricted trading/withdrawal | no subsystem | Define read-only intelligence contracts | 0.1 | `a3c730...` |
| Creative / Media Systems | PARTIAL | creative/media architecture/modules | applicable module tests | prior successful CI | routing, resources, verification | generation is not quality proof | no complete pipeline | Define asset/project/quality contracts | 0.1 | `a3c730...` |
| Music / Audio | PLANNED | architecture intent | none | baseline | media/audio providers, resources | providers untrusted | no system | Define contracts | 0.1 | `a3c730...` |
| Gaming | PLANNED | architecture intent | none | baseline | creative/media, runtime, resources | actions scoped | no subsystem | Define boundary | 0.1 | `a3c730...` |
| Business / Revenue / Reinvestment | PARTIAL | opportunity/business modules + owner control | existing business/monitoring tests | prior successful CI | analytics, owner control, financial boundaries | spending protected | no autonomous commercial execution | Implement outcome contracts | 0.1 | `a3c730...` |
| Owner Identity / Zero-Trust Recovery | TESTED | security recovery/orchestrator/owner control | security recovery tests | prior successful CI | external secret provisioning | HMAC tamper/expiry/replay protection | provisioning external | Harden provisioning | 1.0 | `a3c730...` |
| Self-Model / Resilience / Continuous Evolution | PARTIAL | autonomy, monitoring, security, recovery, capability lifecycle | autonomy/security/monitoring tests | prior successful CI | observations, metrics, recovery, controlled improvement | unrestricted self-modification prohibited | no durable outcome-learning policy | Implement controlled reflection/learning | 0.2 | `d73d6b6...` |

## Highest-priority gaps

1. **Evidence-backed arbitrary natural-language goal understanding** — explicit-field normalization is safe but not arbitrary-goal inference.
2. **Controlled reflection/outcome learning** — verified outcomes are recorded, but do not yet update routing/planning through a bounded auditable policy.
3. **Production source-specific discovery configuration** — generic read-only scouts exist; each source needs explicit trusted provenance configuration.
4. **Broader ecosystem capabilities** — communication, community, creation, distribution, awareness, business/reinvestment, media, gaming, language/speech, and model evolution remain incomplete.
5. **Distributed resource/provider scheduling** — current routing is deterministic and local.

## Blocked vs not built

Missing credentials or platform verification are not software failures. They become `BLOCKED` only when software is ready and an external owner/platform action is genuinely required.

At this checkpoint no listed major capability is `BLOCKED`; several remain not built.

## Verification rule

`TESTED` means meaningful repository tests exist and passed. `VERIFIED` requires stronger integration/operational evidence appropriate to the capability. `DEPLOYED` requires an authorized real deployment. Documentation, imports, or a green unit test alone never constitute production proof.
