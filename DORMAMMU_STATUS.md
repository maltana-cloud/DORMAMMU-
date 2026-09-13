# DORMAMMU STATUS

## Current Milestone
**Canonical identity + architecture continuity + extensibility foundation**

## Completed
- [x] DORMAMMU master architecture charter exists and defines the locked-but-extensible architecture.
- [x] DORMAMMU project charter added as the canonical concise builder reference.
- [x] README identifies DORMAMMU as the product/project identity.
- [x] Agent constitution migrated to DORMAMMU naming and canonical filenames.
- [x] Multi-AI working rules migrated to DORMAMMU naming.
- [x] Canonical `DORMAMMURuntime` runtime identity added.
- [x] Historical `DEVINTELRuntime` remains as a compatibility alias so existing consumers are not broken.
- [x] Package metadata/docstring now identifies DORMAMMU while preserving the historical `devintel/` import path temporarily.
- [x] Legacy `DEVINTEL_STATUS.md` converted into a compatibility redirect instead of competing status documentation.
- [x] Future capability addition is explicitly protected as a first-class architectural requirement.

## Extensibility Contract

DORMAMMU is **locked in principles, authority boundaries, security constitution, truth boundary, owner control, recovery protections, and architectural direction**. It is deliberately **not frozen in functionality**.

Future domains, agents, models, tools, providers, platforms, datasets, compute resources, media/music/film systems, games, education capabilities, languages, business models, and capabilities not yet known may be added later.

Every new capability should follow:

`DISCOVER GAP → DEFINE CONTRACT → ISOLATE → PERMISSION → SECURITY CHECK → BUILD/INTEGRATE → TEST → VERIFY → REGISTER/VERSION → CANARY → MONITOR → KEEP OR ROLLBACK`

Existing capabilities should remain operational while new capabilities are introduced whenever practical. New functionality must not silently rewrite protected foundations or acquire authority merely because it exists.

## Identity Migration Boundary

DORMAMMU is the only public product identity. The historical `devintel/` package namespace and `DEVINTELRuntime` symbol are temporary compatibility surfaces. They must not be used for new product-facing documentation or architecture.

A complete namespace migration should happen as a separate tested compatibility milestone rather than through an unsafe mass rename.

## Verification State

The current identity/documentation changes are committed to the active feature branch. Existing runtime compatibility is preserved by the explicit legacy alias.

The branch still requires full automated test/CI verification before merge. No unobserved test result is claimed.

## Next Engineering Work

1. Run and verify the full test suite for this migration.
2. Complete the remaining safe public-facing `DEVINTEL` documentation cleanup.
3. Introduce the first implementation of Capability & Resource Discovery: contracts, registry, evaluation policy, scoped lifecycle, and tests.
4. Connect controlled provider routing to real research/model adapters.
5. Integrate Education/Conversation/Research/Truth/Distribution into the first real autonomous operating path.

## Non-Negotiable Rule

**Every AI that works on DORMAMMU must leave a truthful, test-backed checkpoint before stopping.**
