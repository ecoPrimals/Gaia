# Wave 68: biomeOS v3.90 — Clippy Zero + Env SSOT Expansion

**Date:** 2026-06-02
**Gate:** southGate
**Repo:** primals/biomeOS
**Wave:** 68

---

## Summary

Continuation of deep debt cleanup. Zero clippy warnings (from 18), expanded env
var SSOT to 50+ centralized constants, split `primal_spawner.rs`, and refactored
pseudospore file loading. This follows the v3.89 `capability.call` P0 proxy fix.

## Completed Items

### 1. Zero clippy warnings (18 → 0)

All 18 warnings across 6 crates resolved:
- `biomeos-core`: unnecessary borrow removed
- `biomeos-federation`: `match Option` → idiomatic `let...else`
- `biomeos-atomic-deploy`: `map(..).flatten()` → `filter_map()`
- `biomeos-api`: `unwrap_or(Default::default())` → lazy evaluation
- `biomeos-unibin`: `unwrap_or(json!())` → lazy evaluation
- `biomeos-pseudospore`: function-too-long + repeated match patterns → helpers

### 2. Env var SSOT expansion (+20 constants, 25 call sites)

Added 20 new constants to `env_config::vars`:
- Realtime: `WS_ENDPOINT`, `SSE_ENDPOINT`, `API_WS`, `API_SSE`
- STUN: `STUN_SERVER`, `NO_PUBLIC_STUN`, `STUN_SERVERS`, `STUN_FALLBACK_ADDRESS`
- Compute: `COMPUTE_ENDPOINT`, `TOADSTOOL_ENDPOINT`
- Registry: `REGISTRY_DIR`, `GITHUB_API_URL`, `GITHUB_TOKEN`
- Boot: `KERNEL`
- UI: `USER`
- CLI: `PLASMID_DIR`, `CHIMERA_DEFINITIONS_DIR`, `BIN_CHIMERAS_DIR`,
  `BIN_PRIMALS_DIR`, `NICHE_TEMPLATES_DIR`, `SPORE_PATHS`, `CLI_LOG_ROOT`

25 raw `env::var("BIOMEOS_*")` call sites wired to constants across
`biomeos-ui`, `biomeos-core`, `biomeos-boot`, `biomeos-cli`.

### 3. primal_spawner.rs split (765 → 607L)

Extracted `executor/launch_profiles.rs` (172L) containing:
- `LaunchProfile` / `LaunchProfilesConfig` types
- `load_launch_profiles()` — TOML config parser
- `configure_primal_sockets()` — data-driven socket setup

### 4. pseudospore refactor

- `load_pseudospore()` reduced from 128 → 82 lines via generic `read_and_parse_toml`
  and `read_and_parse_json` helpers
- `verify_checksums()` match → `if let` for idiomatic Rust

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 7,983 passing |
| Clippy | 0 warnings (was 18) |
| Env vars centralized | 50+ total (20 new) |
| Files changed | ~20 |
| New modules | `executor/launch_profiles.rs` |

## Upstream Notes

- FRAGO acked (partial): biomeOS capability.call resolved, Songbird + bearDog
  remain for separate sessions in those repos
- Ready as mesh partner for `discovery.peers` test once Songbird socket fix lands
- No remaining TODO/FIXME in production code
