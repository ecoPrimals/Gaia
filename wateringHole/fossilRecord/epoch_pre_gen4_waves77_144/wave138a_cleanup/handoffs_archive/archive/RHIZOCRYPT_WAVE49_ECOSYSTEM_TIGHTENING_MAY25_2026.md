# rhizoCrypt — Wave 49 Ecosystem Tightening

**Date**: May 25, 2026
**Scope**: Showcase fossilization, startup latency fix, stale deployment cleanup, version + doc reconciliation

---

## Changes

### 1. Showcase Fossilized

`showcase/` (72 demo scripts — crypto primitive showcases, key rotation demos,
inter-primal live integration scripts) archived to
`fossilRecord/primals/rhizoCrypt/showcase_wave49/`.

Replaced with a README pointer per the Wave 49 fossilization recipe.

### 2. Startup Latency Fixed (Pipeline Debt)

**Root cause**: `announce_to_biomeos()` ran on the critical startup path,
blocking readiness for up to 7s (2s connect + 5s read timeout) when the
neural API socket existed but biomeOS was slow or unavailable.

**Fix**: `announce_to_biomeos()` moved to `tokio::spawn()` background task.
Service now reports ready immediately after `primal.start()` + UDS bind +
manifest publish. Announce continues in background — best-effort, non-fatal.

Before: startup could take >8s (engine init + manifest + announce).
After: startup completes in <1s under normal conditions.

### 3. Stale Deployment Patterns Removed

- `target/release/rhizocrypt` references in `DEPLOYMENT_CHECKLIST.md` and
  `rhizocrypt-service/README.md` replaced with plasmidBin depot pattern
  (bare `rhizocrypt` via PATH).
- No `which rhizocrypt` references found.
- `notify-plasmidbin.yml` verified active.

### 4. Version + Doc Reconciliation

- **`0.14.0-dev` → `0.14.0`**: Dropped `-dev` suffix across workspace
  `Cargo.toml`, all docs, `capability_registry.toml`, `rhizocrypt_deploy.toml`,
  `Dockerfile`, `manifest.rs`. Resolves Wave 22 version hygiene item.
- **Metrics refreshed**: 175 → 171 `.rs` files, ~53,852 → ~53,341 lines
  (post-showcase fossilization). Updated across README, CONTEXT,
  DEPLOYMENT_CHECKLIST, sporeprint, ARCHITECTURE specs.
- **Docker alignment**: `DEPLOYMENT_CHECKLIST.md` and service README Docker
  examples aligned with root `Dockerfile` (`FROM scratch`, `/rhizocrypt` path).
  Fixed duplicate option numbering.
- **Debris scan**: Zero stale markers (TODO/FIXME/HACK), zero temp files,
  zero dead scripts, zero outdated cross-references in active docs.
  `#[allow(dead_code)]` present only in test harness (correct).

### 5. wateringHole

No local `wateringHole/` tree — already clean.

---

## Verification Checklist

- [x] No `showcase/` directory (only README pointer to fossilRecord)
- [x] Local `wateringHole/` active handoffs mirrored to `infra/wateringHole/handoffs/`
- [x] No `which <primal>` or `target/release/<primal>` in scripts
- [x] `notify-plasmidbin.yml` active in `.github/workflows/`
- [x] All 1,646 tests pass, 0 clippy warnings, 0 fmt diffs

---

## Test Results

```
1,646 tests passed (unit + integration + property + doc)
0 failed, 0 ignored
cargo clippy: 0 warnings
cargo fmt: 0 diffs
```
