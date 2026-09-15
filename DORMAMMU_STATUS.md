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

## Category 19 Completion Evidence
- `ResearchDiscoveryEngine` adds a dedicated provider-isolated discovery boundary without replacing the established research pipeline;
- discovery accepts the existing `ResearchCandidate` contract and reuses canonical HTTP(S) URL normalization;
- candidate retrieval is explicitly bounded by caller limit and engine maximums;
- provider failures are isolated so later providers can continue to contribute candidates;
- malformed or wrong-type provider output is rejected at the untrusted discovery boundary;
- canonical URL duplicates are removed across providers before final results are returned;
- results are deterministic, sorted by canonical URL and title, and remain bounded;
- discovery output is explicitly untrusted and cannot grant authority, permissions, credentials, or execution capability;
- regression coverage verifies fallback after deduplication, canonicalization, bounds, malformed output rejection, and provider-failure isolation;
- CI run #1095 passed for the final Category 19 implementation commit;
- implementation remains additive and preserves locked verification, knowledge, security, owner-control, runtime, provider, persistence, audit, and truth boundaries.

## Security Boundary
`IDENTITY ≠ AUTHENTICATION ≠ SESSION ≠ CAPABILITY ≠ AUTHORITY`

Discovery produces candidates, not trusted knowledge. External source content cannot become verified truth merely because it was discovered. Discovery cannot execute discovered content, alter policy, bypass provider controls, or grant permissions.

## Production Boundary
Category 19 is complete at the repository architecture level, not a claim that DORMAMMU has production-scale web discovery. Production still requires workload-specific source/provider selection, network timeout/retry policy, rate-limit handling, source reputation and freshness policy, content extraction hardening, substantive fact-checking, monitoring/alerting, distributed coordination where needed, and deployment-specific operational evidence.

## Post-Roadmap Engineering
Categories 1–19 are now complete/locked at their defined repository boundaries. **Category 20 — Problem & Opportunity Discovery** is the next planned capability boundary.

New capabilities must preserve the locked foundation and use established discovery, permission, security, testing, verification, versioning, canary, monitoring, fallback, and rollback rules.

## Handoff Rule
Every AI working on DORMAMMU must verify the repository itself, preserve this truthful checkpoint, and build forward from the repository rather than treating prior chat history as authoritative.
