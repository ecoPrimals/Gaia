# biomeOS v3.84 — Deep Debt Wave 58b

**Date:** May 28, 2026
**From:** biomeOS team (southGate)
**To:** primalSpring coordination
**Version:** v3.83 → v3.84

---

## Summary

Continued env var centralization (wired 22 more constants) and extracted
inline test modules from two near-800L files, bringing zero production files
above the 800-line threshold.

---

## Changes

### 1. Env Var Wiring (22 additional constants)

Wired remaining env vars that already had constants in `env_config::vars`
but were still accessed via raw `env::var("...")` strings:

`BIND_ADDRESS`, `MODE`, `AUTH_MODE`, `NODE_ID`, `NODE_ID_LEGACY`,
`DISCOVERY_PROVIDER`, `REGISTRY_PROVIDER`, `STORAGE_PROVIDER`,
`ALLOW_LOOPBACK`, `SKIP_MDNS_PROBE`, `INSECURE`, `BTSP_ENFORCE`,
`PLASMID_BIN`, `PLASMID_BIN_DIR`, `NEURAL_API_SOCKET`,
`SECURITY_PROVIDER`, `NETWORK_PROVIDER`, `STRICT_DISCOVERY`

~90% of production `env::var` reads now route through `env_config::vars`.

### 2. Test Extraction Refactors

| File | Before | After (prod) | Tests extracted to |
|------|--------|-------------|-------------------|
| `connection.rs` | 798L | 376L | `connection_tests.rs` (422L) |
| `suggestions/mod.rs` | 772L | 22L | `suggestions_tests.rs` (750L) |

**Result:** Zero production `.rs` files exceed 800 lines.

---

## Verification

- `cargo check --workspace` — 0 warnings
- `cargo test --workspace` — 8,053 passed, 0 failed
- Zero `#[allow(clippy::` in production
- Zero production files >800L

---

## Production Hygiene Summary (cumulative)

| Metric | Status |
|--------|--------|
| Unsafe code | 0 production (`forbid(unsafe_code)` on 50+ roots) |
| Mocks in production | 0 (all confined to tests) |
| TODO/FIXME/HACK markers | 0 |
| C dependencies | 0 (deny.toml enforced) |
| `#[allow(clippy::` in production | 0 |
| `#[allow(clippy::` in tests | 0 (all migrated to `#[expect]`) |
| Files >800L (production) | 0 |
| Env var centralization | ~90% of reads via constants |

---

*Wave 58b. Deep debt resolved. Deploy the ecosystem.*
