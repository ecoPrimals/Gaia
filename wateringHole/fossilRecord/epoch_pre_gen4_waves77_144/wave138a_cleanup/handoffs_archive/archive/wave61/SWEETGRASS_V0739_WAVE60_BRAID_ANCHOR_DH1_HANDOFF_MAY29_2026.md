# sweetGrass v0.7.39 — Wave 60 Upstream + DH-1

**Date**: May 29, 2026
**From**: sweetGrass team
**Re**: Wave 60 — Upstream Primal Evolution Targets

---

## Vectors Completed

### A. `braid.anchor` Method (Wave 60 upstream target)

New method for `rootpulse.branch` signal graphs. Anchors a braid to a
DAG branch point so provenance is established at branch creation time.

- **Wire**: `braid.anchor` — accepts `{braid_id, branch_id}`
- **Behavior**: Loads braid, computes branch-scoped anchor preimage
  (`sha256(braid_id + branch_id + data_hash)`), signs via Tower/BearDog
  `crypto.sign`. Returns `anchored_at_branch: true`, `content_hash`,
  and optional Ed25519 `witness`.
- **Registration**: dispatch table, `niche.rs` CAPABILITIES (38 total),
  `operation_dependencies` (cost: medium, depends: `braid.create`),
  semantic mapping ("anchor to branch"), `capability_registry.toml`.
- **Signal graph consumer**: `rootpulse.branch` (primalSpring Wave 60 spec)

### B. DH-1: `/tmp` Hardcoding Cleanup

Zero hardcoded `/tmp` writes in production code. Enables
`ProtectSystem=strict` on cellMembrane VPS.

- **Removed** `DEFAULT_SOCKET_DIR` constant (`"/tmp/biomeos"`)
- **Replaced** with `default_socket_dir()` → `std::env::temp_dir().join("biomeos")`
- **UDS fallback** changed from bare `{temp_dir}/sweetgrass.sock` to
  `{temp_dir}/biomeos/sweetgrass.sock` (always namespaced)
- **Updated** NestGate discovery, composition health probes, neural
  announce — all use `default_socket_dir()` or `temp_dir()`
- **Tests** use `std::env::temp_dir()` assertions (platform-portable)
- **Remaining `/tmp` refs**: test-only fixture paths (DH-1 compliant)

---

## Metrics

| Metric | Value |
|--------|-------|
| Version | v0.7.39 |
| Tests | 1,560 local + 56 Docker CI |
| Methods | 38 (12 domains + 10 wire aliases) |
| Source | 194 `.rs` files, 55,621 LOC, max 763 lines |
| Clippy | 0 warnings (pedantic + nursery) |
| Production debt | 0 findings |
| DH-1 | Compliant — zero `/tmp` hardcodes in production |

---

## Posture for Downstream Waves

| Wave | Item | Status |
|------|------|--------|
| 60 | `braid.anchor` upstream target | **COMPLETE** |
| 60 | DH-1 `/tmp` cleanup | **COMPLETE** |
| 64 | Signal graph integration testing | Ready — method discoverable via `capability.call("braid", "braid.anchor", ...)` |
| 65 | Cross-gate graph executor | No sweetGrass prep needed |
| 55 | v0.8.0 (live signing, convergence) | Next natural evolution |
