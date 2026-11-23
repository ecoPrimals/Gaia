# lithoSpore Wave 58 — NC-5 Preparation

**Date:** May 28, 2026
**From:** lithoSpore (data primal)
**To:** primalSpring coordination, biomeOS, hotSpring, groundSpring

---

## Status

NC-5 is **UNBLOCKED**. All code deliverables confirmed DELIVERED by primalSpring
Wave 58 audit. lithoSpore is preparing for first live postPrimordial emission
while waiting on v3.81 VPS deployment and hotSpring column U.

## What Shipped (Wave 58)

| Item | Detail |
|------|--------|
| **Env var centralization** | `litho-core/src/env_vars.rs` — 18 constants, ecosystem pattern (matches sweetGrass/rhizoCrypt). All `std::env::var` calls across lithoSpore now reference centralized constants. |
| **`emit-pseudospore --from-dir`** | New CLI flag reads name/version/origin from existing `scope.toml`. Delegation path for nest-validate and other springs. CLI overrides take precedence. |
| **Golden round-trip test** | `PseudoSporeEnvelope` end-to-end: create pseudoSpore dir → load → validate → verify checksums. |
| **`--from-dir` integration test** | `resolve_emit_from_dir` tested with scope.toml parsing and CLI override precedence. |
| **7/7 Tier-0 structural** | alleles/citrate now use `tier0_structural()` (completed from Wave 56). |
| **`litho parity` in CI** | Cross-tier parity check added to GitHub Actions workflow. |
| **groundSpring `domain_profile.toml`** | Authored for LTEE evolutionary biology domain — 7 entity groups, 3 derivation pipelines, 6 audit checks. Ready for `litho emit-pseudospore --spring groundSpring`. |
| **GLACIAL_SHIFT_READINESS.md** | Resolved 3 merge conflict blocks (HEAD/Wave 51+ kept). |

## Metrics

```
191 tests, 0 failures
0 clippy warnings
0 unsafe code
All files ≤ 800 LOC
7/7 Tier 0, 7/7 Tier 1, 7/7 Tier 2 PASS
75/75 science checks
litho-core: 11 modules (retired pseudospore.rs + graph_checks.rs dead code)
pseudospore-core: 10 modules
cargo deny: advisories ok, bans ok, licenses ok, sources ok
```

## Critical Path (lithoSpore perspective)

```
v3.81 on VPS ← biomeOS (P0)
  └→ hotSpring column U ← first live NUCLEUS ingest of v1.6.1
       └→ groundSpring column U ← domain_profile.toml now ready
            └→ NC-5.live ← first postPrimordial emission
                 └→ stadial gates
```

## For biomeOS

- `pseudospore-core` is ready as a workspace dependency.
- Consumer API: `PseudoSporeEnvelope::load(root)` → `.validate()`.
- Replace inline `validate_scope` + `verify_blake3` in `nucleus_ingest.rs`.
- `lib.rs` exports: `ScopeDoc`, `Blake3Manifest`, `LiveSporeDoc`, `PseudoSporeEnvelope`,
  `EnvelopeValidation`, `SporeError`, `ChecksumEntry`, `EnvironmentReceipt`,
  `FermentTranscript`, `DomainProfile`.

## For hotSpring

- nest-validate currently calls `litho emit-pseudospore <dir> --from-validation-results`
  which does not exist. Replace with `--from-dir <dir>` (reads scope.toml).
- When v3.81 is deployed: `biomeos nucleus ingest` path becomes primary;
  `litho ingest-pseudospore` is the offline fallback.

## For groundSpring

- `domain_profile.toml` placed at `springs/groundSpring/validation/domain_profile.toml`.
- Ready for `litho emit-pseudospore --spring groundSpring --domain-profile <path>`.
- Second column U target after hotSpring.

## No Further Code Needed

lithoSpore's code surface is complete for NC-5.live. The remaining path is
operational: deploy v3.81, run live ingest, validate column U. We are ready.
