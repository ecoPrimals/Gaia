# cellMembrane Wave 143b Deep Debt

**Date**: Jul 16, 2026 | **Wave**: 143b | **From**: eastGate cellMembrane team
**Commits**: `e1b056e`, `592685e` | **Tests**: 1,073 | **Clippy**: 0 warnings

---

## Delivered

### CSPRNG → `getrandom` (Security Evolution)

The non-Unix CSPRNG fallback (BLAKE3-derived from pid+timestamp, with cyclic
byte repetition for >32 byte buffers) was a known weak point with an explicit
TODO comment. Replaced with `getrandom` crate — single code path, OS-native
RNG on all platforms. Eliminates the `#[cfg(unix)]`/`#[cfg(not(unix))]` split
in `gate/nucleus.rs`.

### Service Filter → Registry-Derived

`DEFAULT_SERVICE_FILTER` (hand-maintained grep regex) replaced by
`MembraneService::build_service_filter()` which generates the filter
from the service registry + `INFRA_SERVICE_FILTER_EXTRAS` (forgejo,
fail2ban). New primals added to the registry automatically appear in
the filter. Tests verify every registry entry is covered.

### GLACIAL_SHIFT_TRACKER Trimmed (554→77 lines)

Full wave-by-wave history (Waves 50–142b) archived to
`infra/fossilRecord/cellMembrane/GLACIAL_SHIFT_TRACKER_FULL_HISTORY_wave142b.md`.
Active tracker now contains only: current status, last 2 wave entries,
stadial criteria, sovereignty table, and Dark Forest compliance.

---

## CAC Status Update (L3 + L6)

The blurb marks L3 (Heads TreeParity) and L6 (Cascade tree-parity policy)
as "FRAGO issued" but both are **SOLVED** by Wave 142b:

- **L3**: `freshness.rs::publish_gate_heads()` uses `git_rev_parse_tree()`
  (tree hashes, not commit SHAs) since Wave 142b.
- **L6**: `sync_engine.rs::try_local_tree_parity()` checks tree parity
  before impulse/policy dispatch. `try_pull_converge()` checks tree parity
  after rebase conflict.

Blurb CAC table should update L3 and L6 to SOLVED.

---

## Round 2 (`592685e`) — Typed Probes + Dead Code Cleanup

### `ProbeResult` Type (Structural)

Replaced 9 functions returning `(bool, String)` tuples with a typed
`ProbeResult { ok, detail }` struct providing `pass()` / `fail()`
constructors. Affects `gate/health.rs`, `gate/verify.rs`, `gate/nucleus.rs`,
`gate/mesh.rs`, and `gate/bootstrap.rs` consumption sites.

### `Priority::Priority` → `Priority::Urgent`

Eliminated `#[allow(clippy::enum_variant_names)]` by renaming the
self-referential variant. Wire compatibility preserved via
`#[serde(alias = "priority")]` and `FromStr` accepting both strings.

### `format_bytes` Integer Math

Removed `#[allow(clippy::cast_precision_loss)]` by replacing `as f64` casts
with integer-only arithmetic using half-up rounding. Output unchanged.

### `build_err` Consolidation

Eliminated 3 identical `const fn build_err(msg: String)` helpers across
`sandbox.rs`, `canary.rs`, `toolchain.rs` — now direct `ShadowError::Build(...)`.

### Dead Code + `#[allow]` Cleanup

- `DepotUpdatedNotification`: `pub`→`pub(crate)`, `from_json` returns `Self`
  (removed `#[allow(dead_code)]` x2 + `#[allow(clippy::unnecessary_wraps)]`)
- Webhook serde fields: `#[allow(dead_code)]` replaced with per-field
  `reason` attributes documenting future consumption
- Manifest API methods: `#[allow(dead_code)]` annotated with `reason`

### Production Audit (No Action Needed)

- Only 3 production `.expect()` calls — all in `ribocipher.rs` for infallible
  HMAC-SHA256 construction. Justified.
- `#![forbid(unsafe_code)]` on both crates — zero unsafe.
- All external dependencies are pure Rust. No evolution needed.
- All files <800L (largest: 762).

---

## Remaining cellMembrane Deep Debt (P3)

| Item | Priority | Notes |
|------|----------|-------|
| Cytoplasm static IP table → manifest-only | P3 | Requires topology migration |
| Named Pipe transport implementation | P3 | Windows parity — stub exists |
| ribocipher nuclear tier | P3 | Deferred until per-peer lineage keys |
| `(bool, String)` remaining in provision/ | P3 | Non-gate modules still use tuple pattern |
