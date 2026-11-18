<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# BearDog v0.9.0 — Wave 113: Wave 49 Ecosystem Tightening Handoff

**Date**: May 25, 2026
**Scope**: Wave 49 ecosystem tightening — all three cleanup vectors addressed.

---

## Deliverables

### Vector A: Cut stale deployment patterns — CLEAN
- No `target/release/beardog` or `which beardog` references in scripts or docs.
- Binary distribution uses `plasmidBin` depot exclusively.
- `notify-plasmidbin.yml` active in `.github/workflows/`.

### Vector B: Consolidate wateringHole — CLEAN
- No local `wateringHole/` tree — all handoffs centralized in `infra/wateringHole/`.

### Vector C: Fossilize showcase/ — DONE
- `showcase/` directory (153 files, 1.5 MB) replaced with a README pointer.
- Contents: security harness, ACME proto demos, HSM discovery, BTSP tunnel, key lineage, entropy mixing, audit logging, monitoring, dynamic config, performance profiling, ecosystem integration, advanced features.
- Fossil record preserved per Wave 49 mandate.

### Pipeline Debt Items (from audit)
- **`--security-socket` flag**: N/A for bearDog. bearDog exposes a single IPC socket via `--socket` / `BEARDOG_SOCKET` env var (5-tier discovery). No `SONGBIRD_SECURITY_SOCKET` env var — that is a songbird-specific concern.
- **sled DB corruption**: N/A for bearDog. No sled dependency in any `Cargo.toml` or `Cargo.lock`. In-memory bond persistence; filesystem-based ACME cert storage. SIGTERM handler handles transport/socket cleanup only.

## Verification Checklist

- [x] No `showcase/` directory (only README pointer)
- [x] No local `wateringHole/` tree
- [x] No `which beardog` or `target/release/beardog` in scripts
- [x] `notify-plasmidbin.yml` active in `.github/workflows/`
- [x] Commit message references `Wave 49 ecosystem tightening`

## Quality Gates

- `cargo fmt --check`: PASS
- `cargo clippy --workspace -- -D warnings`: PASS (0 warnings)
- `cargo test --workspace`: PASS (14,940+ tests)
