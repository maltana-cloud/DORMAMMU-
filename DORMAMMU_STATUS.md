# DORMAMMU STATUS

## Current Milestone
**Capability & Resource Discovery — foundational implementation**

## Truth Rule
This file describes repository state; implementation claims are based on code/tests/CI evidence, not documentation alone.

## Verified Foundations
- Systems #1–#10, plugin/specialist framework, core orchestration, permissions, security/truth, autonomy, education, and provider routing are present in the repository and covered by the existing test suite.
- Live provider adapters exist for keyless Wikipedia retrieval and optional Gemini generation.
- Runtime now exposes canonical `DORMAMMURuntime`; `DEVINTELRuntime` remains only as a compatibility alias.
- CI run 453 passed before the capability-discovery commits in this checkpoint; it does **not** verify the newer capability-discovery files.

## Capability Discovery Implemented
- Typed capability requirements, gaps, descriptors, resource descriptors, evaluation results, and lifecycle states.
- Thread-safe capability, gap, and resource registries.
- Pluggable capability scout contract.
- Deterministic evaluator covering trust, security, compatibility, performance, license, cost, and permission gates.
- Free-first default policy; paid candidates require explicit policy enablement.
- Registration requires all evaluation gates to pass.
- Discovery is advisory: it does not install, execute, download, authenticate, or grant authority to discovered candidates.

Implementation: `devintel/capabilities/`
Tests: `tests/test_capability_discovery.py`

## Identity Boundary
DORMAMMU is the only public product identity. `devintel/` and `DEVINTELRuntime` are compatibility surfaces only. No mass rename is being performed because existing imports must remain stable.

## Known Gaps
- No external capability marketplace/scout is enabled yet.
- Resource inventory is not yet connected to live CPU/GPU/RAM/storage telemetry.
- Discovery results are not yet fed into the AutonomousEngine as capability/resource observations.
- Capability lifecycle persistence, canary monitoring, and rollback orchestration are not yet implemented.
- Wikipedia remains retrieval/snippet evidence, not a general web research engine.
- Gemini remains optional and requires an owner-supplied credential.

## Next Action
1. Verify the capability-discovery tests in CI.
2. Add a safe built-in local resource/capability inventory.
3. Feed capability gaps and resource observations into bounded autonomy.
4. Add lifecycle/version/rollback records before enabling any real external scout.
5. Connect verified research retrieval to Research/Truth and generation to Conversation/Education.

## Completion Standard
Capability discovery is not complete until discovery, evaluation, permissions, security, compatibility, cost, resource requirements, lifecycle, observability, fallback, rollback, and integration are implemented and verified.

**Every AI working on DORMAMMU must leave a truthful, test-backed checkpoint.**
