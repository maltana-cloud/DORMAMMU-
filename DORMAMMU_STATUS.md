# DORMAMMU STATUS

## Current Milestone
**Category 19 — Research & Discovery Engine is COMPLETE / LOCKED at the repository architecture level.** DORMAMMU now has a bounded, provider-isolated source discovery boundary that produces canonicalized, deduplicated, deterministic, untrusted research candidates for the established ingestion and verification pipeline.

## Truth Rule
Implementation claims require code, meaningful tests, integration evidence, and successful CI. Production readiness requires capability-appropriate operational evidence.

## Category Status
1. Foundation & Governance — COMPLETE / LOCKED
2. Core Intelligence — COMPLETE / LOCKED
3. Capability & Resource Intelligence — COMPLETE / LOCKED
4. Ecosystem Awareness — COMPLETE / LOCKED
5. Engineering Intelligence — COMPLETE / LOCKED
6. Language & Communication — COMPLETE / LOCKED
7. Research & Domain Expansion — COMPLETE / LOCKED
8. Creative Intelligence — COMPLETE / LOCKED
9. Simulation & Interactive Worlds — COMPLETE / LOCKED
10. Social & Community Intelligence — COMPLETE / LOCKED
11. Economic & Business Intelligence — COMPLETE / LOCKED
12. Owner & Platform Security — COMPLETE / LOCKED
13. Autonomous Operations — COMPLETE / LOCKED
14. Evolution & Self-Improvement — COMPLETE / LOCKED
15. Production Runtime & Orchestration — COMPLETE / LOCKED
16. Persistent Intelligence Infrastructure — COMPLETE / LOCKED
17. Real Capability & Provider Infrastructure — COMPLETE / LOCKED
18. Intelligence & Knowledge System — COMPLETE / LOCKED
19. Research & Discovery Engine — COMPLETE / LOCKED
20. Problem & Opportunity Discovery — IMPLEMENTED / PENDING FINAL CI + MERGE

## Category 20 Scope
Category 20 converts verified research synthesis into bounded, advisory problem and opportunity candidates. It does not independently treat discovered material as truth; upstream verification and synthesis remain authoritative gates.

## Category 20 Completion Evidence
- `ProblemOpportunityEngine` consumes only the established `SynthesisResult` contract;
- candidates are explicitly classified as `problem` or `opportunity` and remain advisory;
- evidence URLs are preserved on every candidate;
- candidate confidence and ranking are bounded to `[0, 1]`;
- contradictory synthesis remains explicitly uncertain and confidence is capped conservatively;
- candidate counts are bounded by caller and engine limits;
- deterministic ranking is used for reproducibility;
- detection terms are normalized and validated;
- no money-based value assumption is introduced by the discovery layer;
- unrelated verified statements are excluded rather than converted into invented opportunities;
- regression tests cover problem detection, opportunity detection, contradiction handling, irrelevant evidence, bounds, and validation;
- an existing upstream `VerificationResult` test-fixture type mismatch exposed by Category 20 integration tests was corrected without weakening production validation;
- final CI and merge are required before this category becomes COMPLETE / LOCKED.

## Security Boundary
`IDENTITY ≠ AUTHENTICATION ≠ SESSION ≠ CAPABILITY ≠ AUTHORITY`

Problem/opportunity discovery produces advisory intelligence only. It cannot execute discovered opportunities, grant permissions, create credentials, alter policy, or bypass owner/security controls.

## Production Boundary
Category 20 does not claim autonomous real-world opportunity detection at production scale. Production requires domain-specific signal definitions, source diversity, substantive verification/fact-checking, freshness and reputation policies, longitudinal evidence, calibrated scoring, monitoring/alerting, workload/resource controls, and deployment-specific operational evidence.

## Post-Roadmap Engineering
Categories 1–19 are complete/locked at their defined repository boundaries. **Category 20 — Problem & Opportunity Discovery** is the active capability boundary; **Category 21 — Domain Intelligence** follows only after Category 20 passes final verification and is merged.

New capabilities must preserve the locked foundation and use established discovery, permission, security, testing, verification, versioning, canary, monitoring, fallback, and rollback rules.

## Handoff Rule
Every AI working on DORMAMMU must verify the repository itself, preserve this truthful checkpoint, and build forward from the repository rather than treating prior chat history as authoritative.
