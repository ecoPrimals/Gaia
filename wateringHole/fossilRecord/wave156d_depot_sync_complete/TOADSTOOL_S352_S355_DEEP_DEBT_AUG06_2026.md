# ToadStool S352–S355 Deep Debt Handoff

**Date**: August 6, 2026
**Sessions**: S352, S353, S354, S355
**Gate**: eastGate
**Author**: overwatch (automated)

---

## Summary

Four sessions of deep debt evolution focused on socket permissions, workspace
build fixes, C2 dual-socket naming alignment, and hardcoded primal name
elimination.

---

## S352 — Systemd Socket Permissions (B1/B2)

- `ensure_biomeos_directory` permissions changed `0o700` → `0o750` (group-traversable)
- Default socket mode changed `0o600` → `0o660` (group-writable) in both
  JSON-RPC (`pure_jsonrpc/connection/unix.rs`) and tarpc (`tarpc_server/mod.rs`)
- `PRODUCTION_DEPLOYMENT_GUIDE.md` updated: `Group=biomeos`, `0o660` now default
- Other primals in a composition can now access toadStool sockets

## S353 — C5 Workspace Build Blocker + Orphan Cleanup

- 6 neuromorphic crates excluded from default workspace (C5: `rustChip/akida-chip`
  is biomeGate-local). Build on biomeGate: `cargo build -p akida-driver`
- `AkidaNpuDispatch` adapter moved to `akida-driver` crate. `toadstool-core`
  no longer depends on `akida-driver`
- 8 orphan `.rs` files deleted (1,382 lines dead code)
- `unimplemented!()` replaced with `&HardwareCapabilities::UNKNOWN`
- Scripts `run-coverage.sh` / `run-hardware-tests.sh` updated

## S354 — C2 Dual-Socket Naming Alignment (G64 Cephalization)

- tarpc socket renamed `compute-tarpc.sock` → `compute.tarpc.sock` (Wave 156j C2)
- Server now honors `TOADSTOOL_TARPC_SOCKET` env var
- Backward-compat symlink: `compute-tarpc.sock` → `compute.tarpc.sock`
- `identity.get` JSON response includes `tarpc_socket_name`
- `primal-capabilities.toml` and `capability_registry.toml` updated

## S355 — Hardcoded Primal Names, Fake Data, Dead Code, C2 Announce Parity

- 3 hardcoded primal name violations replaced:
  - `songBird IPC integration` → `coordination service with webhook.export capability`
  - `petalTongue domain` → `hardware transport capability`
  - `biomeOS tower integration` → `remote compute service via coordination`
- `tarpc_socket_name` added to `primal.announce` (C2 parity with `identity.get`)
- `InMemoryBackend` module gated behind `cfg(test)`
- `get_device_usage()` evolved from fake zeros to `not_supported`
- `DeviceUsage::default()` documented as unmeasured sentinel
- Dead `validate_and_optimize` deleted from `NaturalLanguageConfig`

---

## Quality Gates (S355)

| Gate | Result |
|------|--------|
| `cargo clippy --workspace --all-targets -- -D warnings` | 0 warnings |
| `cargo fmt --all -- --check` | 0 diffs |
| `cargo test --workspace --lib` | **9,008 passed**, 0 failed, 20 ignored |
| Production `unwrap()`/`expect()` | 0 |
| Production `todo!()`/`unimplemented!()` | 0 |
| Hardcoded primal name violations | 0 |
| Files > 750L (production) | 0 |

---

## Remaining Debt (toadStool-local)

| Item | Priority | Notes |
|------|----------|-------|
| Test coverage → 90% (D-COV) | P2 | 9,008+ lib tests; ~85%+ line; gap in VFIO/DRM/V4L2/akida |
| GPU runtime facade gap | P2 | `execute_kernel()` and `compile_kernel()` are stubs; wired to `ComputeDispatch` guidance |
| EcosystemService deprecated migration | P2 | 4 files still reference deprecated enum; migration path via `adapters/` + `ServiceType` |
| ~25 honest stubs (`not_supported`) | P3 | Platform transport, sandbox, mesh relay — typed error returns, not fake data |
| Wire-contract consumer constants | P3 | `CONSUMER_BARRACUDA_MLP` etc. — published schema, coordinate before rename |

---

## Cross-Primal Impact

- **All primals using `compute-tarpc.sock`**: Must update to `compute.tarpc.sock`.
  Backward-compat symlink active during transition period.
- **Composition peers**: Socket permissions now `0o660` — primals in `biomeos`
  group can access without `TOADSTOOL_SOCKET_MODE` env var override.
- **biomeGate builds**: Neuromorphic crates excluded from default workspace.
  Build separately with `cargo build -p akida-driver`.
