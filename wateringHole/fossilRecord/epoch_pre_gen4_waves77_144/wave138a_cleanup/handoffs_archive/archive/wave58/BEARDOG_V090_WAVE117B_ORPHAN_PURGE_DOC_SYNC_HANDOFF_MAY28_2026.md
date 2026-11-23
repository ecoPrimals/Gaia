# BearDog v0.9.0 — Wave 117b: Orphan Purge, Root Doc Sync, Config Annotations

**Date**: May 28, 2026
**Commit**: `2a7be2f40`
**Quality Gates**: `cargo fmt` ✓ | `cargo clippy -D warnings` ✓ | `cargo test --workspace` ✓ (14,987 tests, 0 failures)

---

## Summary

Wave 117b is a companion cleanup pass focused on dead code removal, documentation alignment, and config template annotation.

## 1. Orphan File Purge (21 files, ~3,500 LOC)

All files confirmed as orphans — not wired into any module tree via `mod` declarations.

### beardog-genetics (9 files)
| File | LOC | Issue |
|------|-----|-------|
| `genetics/api.rs` | 78 | Duplicate stub `InMemoryGeneticsStore` |
| `genetics/types.rs` | 218 | Real store impl, but never `mod`-declared |
| `genetics/handlers.rs` | 184 | Corrupted syntax (~line 24) |
| `genetics/entropy_simple.rs` | 252 | Malformed struct definitions |
| `genetics/biome_genetics.rs` | 321 | `BiomeGenetics` trait, unwired |
| `genetics/peer_to_peer_genetics.rs` | 138 | P2P genetics types, unwired |
| `genetics/zero_copy.rs` | 336 | `GeneticsPool`, unwired |
| `genetics/simd_optimization.rs` | 310 | Malformed struct definitions |
| `genetics/tests.rs` | 85 | References non-existent `GeneticsEngine` |

### beardog-core (6 files)
| File | LOC | Issue |
|------|-----|-------|
| `core/operations.rs` | 243 | Imports non-existent `beardog_genetics::api` |
| `core/new_mod.rs` | 38 | "Legacy layout" duplicate of `core/mod.rs` |
| `core/beardog_core.rs` | 327 | Alternate `BearDogCore`; active is `core/system.rs` |
| `core/ecosystem_coordination.rs` | 126 | `impl BearDogCore` extension, never wired |
| `core/primal_provider.rs` | 198 | Imports non-existent `crate::ecosystem_simple` |
| `ai/ecosystem_coordination.rs` | 160 | Not declared in `ai/mod.rs` |

### beardog-types (6 files)
| File | LOC | Issue |
|------|-----|-------|
| `canonical/providers.rs` | 432 | Superseded by `providers_unified/` |
| `canonical/relationships.rs` | 301 | Never `mod`-declared |
| `canonical/workflow.rs` | 433 | Superseded by `config/workflow` |
| `canonical/security.rs` | 512 | Superseded by `security_unified/` |
| `canonical/metrics.rs` | 470 | Superseded by `monitoring/metrics` |
| `canonical/genetics.rs` | 511 | Superseded by `config/genetics` |

## 2. Root Documentation Sync

All 9 root markdown files aligned to Wave 117:

| File | Changes |
|------|---------|
| README.md | Date → May 28; tests → 14,987+; Rust files → 2,115 |
| STATUS.md | Date → May 28 (Wave 117); tests → 14,987+; Waves 116-117 entries added |
| ARCHITECTURE.md | Date → May 28; tests → 14,987+ |
| ROADMAP.md | Date → May 28; tests → 14,987+ |
| CONTEXT.md | Date → May 28; tests → 14,987+ |
| START_HERE.md | Date → May 28; tests → 14,987+ |
| SECURITY.md | Date → May 28 |
| docs/README.md | Date → May 28 |
| docs/PRIMAL_CONTRACTS.md | Date → May 28 |

## 3. HTTP-Era Config Annotations

Added pre-UniBin disclaimers to 5 config template files:

| File | Annotation |
|------|------------|
| `configs/production.toml` | HTTP/REST `[api]` sections marked as pre-UniBin era |
| `configs/network-defaults.toml` | HTTP endpoint references marked as pre-UniBin |
| `configs/beardog-config-template.toml` | `[network.http/https/cors]` sections marked |
| `configs/beardog-config.toml` | HTTP bind addresses marked as pre-UniBin |
| `configs/env-template.example` | HTTP/REST vars marked as pre-UniBin |

## Remaining Low-Priority Items

| Item | Notes |
|------|-------|
| `PRIMAL_CONTRACTS.md` method catalog | Category breakdowns stale (103→106 CryptoHandler, 8→12 IonicBond, missing auth.issue_session etc.) |
| `docs/references/QUICK_START_SOFTWARE_HSM.md` | Still references deleted `api/server.rs` path |
| Coverage wave naming in tests | Tests named `wave2`, `wave3`, `wave10` etc. — cosmetic only |
| `configs/README.md` | Documents `[server]` as "HTTP server configuration" |

---

*Prepared for downstream primalSpring audit.*
