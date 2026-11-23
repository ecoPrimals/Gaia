# Wave 55b: Deep Debt Sweep + Script Archival

**Date**: May 27, 2026
**Author**: primalSpring / eastGate
**Scope**: Security fixes, IPC performance, idiomatic Rust, script fossilization

---

## Security / Correctness (P0)

1. **MethodGate enforced auth**: `NoopVerifier` no longer used in Enforced mode.
   BearDog-unreachable now downgrades to Permissive with `tracing::warn`.
2. **Real timestamps**: `iso_now()`/`system_time_to_iso()` replaced fake hardcoded
   dates with Euclidean civil date computation (pure Rust, no chrono).
3. **Seed entropy**: Weak `"fallback-seed-entropy-unavailable"` string replaced
   with PID+clock derivation when `getrandom` fails.
4. **Hardcoded paths**: exp112 absolute `/home/eastgate` path → env/traversal.

## Performance (P1)

5. **NeuralBridge**: 15 connect-per-call sockets → single lazy `RefCell` with
   reconnect-on-failure. Hot-path syscalls reduced from 15 to 1 per bridge.
6. **DispatchError**: Now captures `IpcError::kind()` discriminant for structured
   error context. New `const fn kind()` on `IpcError`.

## Architecture (P1)

7. **Self-knowledge**: `s_nest_atomic` foreign source-path checks into biomeOS/
   lithoSpore repos replaced with runtime `ctx.client_for()` capability discovery.
8. **Clone reduction**: Routing table build, barracuda precision, TCP result clones.
9. **Named constants**: `MAX_BTSP_FRAME_BYTES` replaces magic `16*1024*1024`.

## Script Archival (12 items → `fossilRecord/scripts_wave55b_may2026/`)

| Script | Rust Replacement |
|--------|-----------------|
| `check_method_gate.sh` | `primalspring registry --check all` |
| `check_method_coverage.sh` | `primalspring registry --check coverage` |
| `check_graph_methods.sh` | `primalspring registry --check graphs` |
| `check_method_strings.sh` | `primalspring registry --check source` |
| `regenerate_checksums.sh` | `primalspring checksums` |
| `gen_seed_fingerprints.sh` | `certification/entropy.rs` |
| `nucleus_launcher.sh` | Rust `nucleus_launcher` binary |
| `ttt_nucleus.sh` | `nucleus_launcher --family-id ttt` |
| `composition_nucleus.sh` | `nucleus_launcher` |
| `live_nucleus.sh` | `nucleus_launcher start` |
| `validate_compositions.py` | `primalspring validate --track composition` |
| `gen_checksums.rs` (example) | `primalspring checksums` |

## Remaining Primordial Patterns (for next wave cycle)

These patterns are documented as deprecated but still active in library paths.
Full NUCLEUS deployment standardization requires completing their migration:

1. **`discover_primal` / `probe_primal`** — still in IPC discover/probes layer.
   Experiments cleaned (Wave 18), but library surface retains for backward compat.
   Target: wrap behind `CompositionContext::discover()` exclusively.

2. **`harness` module** — deprecated process spawner, still public in `lib.rs`.
   Used by some experiments. Target: experiment migration to `nucleus_launcher`.

3. **`launcher/spawn.rs` + `launcher/biomeos.rs`** — `std::process::Command`
   for primal launch. Target: all launch through `nucleus_launcher` or plasmidBin.

4. **Environment variable scatter** — `TOWER_HOST`, `SONGBIRD_PEERS`,
   `BIOMEOS_GRAPHS_DIR` etc. not centralized in `env_keys.rs`.

5. **`desktop_nucleus.sh`** — still referenced in README/graphs. Target: replace
   with standardized `nucleus_launcher` / plasmidBin cell deployment.

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 813 (797 pass, 16 live-tier) |
| Clippy warnings | 0 |
| Scenarios | 56 |
| Methods | 460 |
| Signals | 15 |
| Experiments | 93 |
| Deploy graphs | 96 |
| Archived scripts | 12 |
