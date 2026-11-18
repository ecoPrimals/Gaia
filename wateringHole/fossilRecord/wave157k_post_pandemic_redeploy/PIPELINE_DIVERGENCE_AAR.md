# Pipeline Divergence AAR — Wave 157k (Aug 14, 2026)

**Reporter**: sporeGate (foreman)
**Duration**: 08:14–09:00 EDT
**Severity**: P1 — build pipeline blind to source changes, depot stale for 2+ days

---

## Incident

westGate reported: "The auto-announce persistence code and the convergence.check riboCipher routing fix are in Forgejo but haven't been picked up by the golgi builder yet."

The sporeGate cascade was running, pulling repos, and reporting `"[harvest] OK — 0 built, 13 current"` — but the x86_64 binaries in the depot were from Aug 12, built from older commits.

## Root Cause

**Three stacked bugs** caused the divergence:

### 1. Serde Flatten Collision (Critical)

`ProvenanceFile` uses `#[serde(flatten)]` on `entries: BTreeMap<String, ProvenanceEntry>`. Both `ProvenanceFile` and `ProvenanceEntry` have fields named `target` and `builder`. Serde's flatten implementation silently consumed the per-entry `target`/`builder` fields for the outer struct, causing `entry.target` to always deserialize as `None`.

```
ProvenanceFile.target = "x86_64-unknown-linux-musl"  (top-level)
ProvenanceEntry.target = None                         (LOST — serde ate it)
```

### 2. No Target-Awareness in Drift Detection

`drift::has_upstream_changes` compared `provenance.commit` vs `ls-remote HEAD`. The aarch64 cross-build had written provenance entries with the correct commits (matching current HEAD), so the x86_64 harvest said "commit unchanged" — unable to see that those commits were built for the wrong architecture.

### 3. Stale Binary in `~/.local/bin`

An 11-day-old `membrane` binary at `~/.local/bin/membrane` (Aug 3) was shadowing the current `/usr/local/bin/membrane` in `$PATH`. Multiple deploy/fix cycles went unnoticed because the wrong binary was being executed.

### 4. Write-Back Data Loss

`update_provenance` re-read existing entries via `toml::from_str::<ProvenanceFile>` (hitting the flatten collision), then wrote them back with lost `target`/`builder`/`blake3` fields. Each harvest cycle stripped more data from the provenance file.

## Fixes Applied

### Two-Pass TOML Parse (depot.rs)
`load_provenance` now parses raw `toml::Value` first, then deserializes each `[primal]` section individually via `try_into::<ProvenanceEntry>()`, bypassing the serde flatten collision. `update_provenance` also uses `load_provenance` to read existing entries.

### Target-Aware Drift Detection (drift.rs)
`has_upstream_changes` now checks `entry.target` against `detect_target_triple()`. If they differ, the primal is marked stale regardless of commit match. Both strict and lenient variants updated.

### Provenance Trio Wiring (drift.rs + harvest.rs)
Drift detection queries `rootpulse_harvest` via neuralAPI first (per-target authority), falling back to flat provenance.toml. After each harvest, per-entry build records are written to `rootpulse_harvest`.

### Graph Definitions (wateringHole/graphs/)
Created `rootpulse_commit`, `rootpulse_harvest`, `rootpulse_diff` graph definitions. All three are now discoverable by neuralAPI. Full activation awaits primal step handler implementations.

### Binary PATH Fix
`~/.local/bin/membrane` updated to match `/usr/local/bin/membrane`.

### Provenance Restoration + Full Rebuild
Provenance.toml restored from backup (data-loss from write-back bug). All 13 primals rebuilt for `x86_64-unknown-linux-musl`. 28 binaries pushed to golgiBody depot.

## Verification

- `membrane plasmid.harvest --local` → `13 current, 0 failed`
- `membrane temporal.cascade --check` → `15 synced`
- Provenance entries all show `target = "x86_64-unknown-linux-musl"` (14/14)
- neuralAPI `graph.list` shows 6 graphs (3 rootpulse + 3 existing)

## Commits

- `3f9fa14` cellMembrane: fix: resolve pipeline divergence — provenance target-awareness + trio wiring
- `c0c7f89` wateringHole: feat: rootpulse graph definitions

## Architecture Note

The flat `provenance.toml` is now a **cache** — the rootpulse_harvest trio is designed as the canonical multi-target authority. Until primals implement graph step handlers (dag.append, index.upsert, etc.), the flat file with two-pass parsing provides correct target-aware drift detection. The trio query degrades gracefully to the flat file fallback.
