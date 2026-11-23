# cellMembrane Wave 157d — G69 Phase 2 Lineage Metadata

**Date:** 2026-08-09
**Author:** eastGate primalSpring overwatch
**Wave:** 157d
**Commit:** `a5d79a2` — `evolve: G69 Phase 2 lineage metadata + deprecated cleanup + socket consolidation`

---

## Summary

G69 Phase 2 delivery: per-entry provenance enrichment, deprecated code removal,
and socket suffix consolidation. 24 files changed, 389 insertions, 172 deletions.

---

## Changes

### 1. G69 Phase 2 — Per-Entry Provenance Enrichment

`ProvenanceEntry` enriched with 4 new fields (all `#[serde(default)]` for
backward compatibility with legacy `provenance.toml` files):

| Field | Type | Source |
|-------|------|--------|
| `blake3` | `Option<String>` | Binary hash from `stage_to_depot_async()` |
| `built_at` | `Option<String>` | UTC ISO 8601 timestamp at provenance write |
| `target` | `Option<String>` | Target triple this binary was built for |
| `builder` | `Option<String>` | Gate identity that produced the binary |

`HarvestResult` gains structured `commit`/`blake3`/`target` fields with
`skip_serializing_if = "Option::is_none"` — eliminates fragile string parsing
(`detail.split("commit=")`) in `update_provenance()`. New `HarvestResult::new()`
helper consolidates 14 construction sites across `harvest.rs` and `build.rs`.

`validate_lineage()` hardened:
- Per-entry `builder` check (falls back to file-level for legacy files)
- Per-entry `blake3` cross-check against binary on disk
- New reason: "provenance blake3 does not match binary"

guideStone P2 comment updated to reflect reality.

### 2. Deprecated Code Removal

| Item | Action |
|------|--------|
| `TargetArch` re-export in `lib.rs` | Removed (0 production callers, enum stays in `arch.rs` for deserialization) |
| `DEFAULT_SERVICE_FILTER` in `constants.rs` | Deleted (0 callers, superseded by `MembraneService::build_service_filter()`) |

### 3. Socket Suffix Consolidation

New constants and helper in `cellmembrane-types/src/service/constants.rs`:
- `SOCKET_SUFFIX = ".sock"`
- `socket_filename(binary: &str) -> String` — returns `"{binary}.sock"`

15 production call sites migrated from bare `".sock"` string literals:
- `transport.rs` (both crates)
- `gate/sockets.rs` (6 sites)
- `plasmid/mod.rs`, `plasmid/canary.rs`, `plasmid/signing_crypto.rs`
- `dispatch/sign_dispatch.rs`, `dispatch/infra.rs`
- `impulse/primal.rs` (2 sites)
- `gate/mesh.rs`, `provision/bootstrap.rs`
- `service/capability.rs` (`TARPC_SOCKET_SUFFIX` standardized)

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Tests | 1344 | 1349 |
| Clippy warnings | 0 | 0 |
| Files changed | — | 24 |
| Net lines | — | +217 |
| Deprecated symbols removed | — | 2 (`TargetArch` re-export, `DEFAULT_SERVICE_FILTER`) |
| Bare `.sock` literals (production) | ~15 | 0 |
| Provenance fields per entry | 3 | 7 |

---

## Upstream Notes

- **Backward compatibility**: Legacy `provenance.toml` files without G69 Phase 2
  fields parse cleanly via `#[serde(default)]`. `validate_lineage()` falls back
  to file-level builder when per-entry builder is absent.
- **HarvestResult JSON**: New fields use `skip_serializing_if = "Option::is_none"`,
  so JSON output remains unchanged for non-built results. Existing consumers
  (e.g., `plasmid.status`, `plasmid.harvest` output) are unaffected.
- **`TargetArch`**: Enum definition retained in `arch.rs` with `#[deprecated]`
  annotation. Only the public re-export from `lib.rs` was removed. External crates
  that import `cellmembrane_types::TargetArch` should switch to `Platform`.
