# Wave 54b: Deep Debt Sweep + Script-to-Rust Evolution

**Date:** 2026-05-27
**Spring:** primalSpring
**Scope:** Owned code deep debt, dependency evolution, script absorption

## Summary

Comprehensive audit and refactoring of primalSpring's owned code to modern
idiomatic Rust, eliminating external jelly-string dependencies, hardcoding,
shell-outs, and absorbing bash/Python CI tools into Rust subcommands.

## Dependency Evolution

- **`hostname` crate eliminated** (17→16 runtime deps) — replaced with
  `std::env::var("HOSTNAME")` / `"HOST"` fallback chain.
- **`clap` default-features trimmed** — dropped terminal color/styling stack
  (`anstream`, `anstyle`). CLI tools are non-interactive/CI-focused.
- **Crypto bootstrap boundary mapped**: `hmac`, `sha2`, `hkdf`,
  `chacha20poly1305`, `getrandom`, `base64`, `zeroize`, `blake3` are the
  irreducible local crypto surface for BTSP Phase 1+3 handshake. Cannot
  delegate to BearDog without circular dependency (need crypto to talk to
  the crypto primal). Post-handshake, codebase already delegates to primals
  via JSON-RPC (`crypto.hash`, `genetic.*`, `crypto.sign/verify`).
- **`toml`** justified: structural config/manifest parsing, not crypto.

## Hardcoding Centralized

- `tolerances::runtime_dir()` — reads real UID from `/proc/self/status`,
  replaces hardcoded `/run/user/1000` in 4 files.
- `tolerances::biomeos_socket_dir()` — centralized socket path resolution.
- `tolerances::default_port_for()` / `port_env_key_for()` — centralized
  primal→port/env maps, eliminating 26-line duplicated match blocks in
  orchestrator.
- `tolerances::LAN_BIND_ADDRESS` / `RUNTIME_DIR_FALLBACK` — named constants
  replacing inline `"0.0.0.0"` and `"/tmp"`.
- biomeOS graph paths: depth-1..4 relative discovery with `RELATIVE_GRAPHS_PATH`.

## Shell-Out Eliminated

- **`pkill` replaced with PID-file tracking**: `nucleus_launcher` writes
  `$XDG_RUNTIME_DIR/biomeos/.pids/{primal}.pid` at spawn. Stop reads PID
  files and sends SIGTERM via `kill` binary. Falls back to `/proc` scan.
- Logs moved from `/tmp/{primal}.log` to `$XDG_RUNTIME_DIR/biomeos/logs/`.

## Rust CLI Evolution

### `nucleus_launcher` — full lifecycle
- `nucleus_launcher start --family-id <ID> [--composition nucleus] [--federation-port 7700]`
- `nucleus_launcher stop [--composition nucleus]`
- `nucleus_launcher status [--composition nucleus]`

### `primalspring` UniBin — new subcommands
- `primalspring checksums [--output path]` — BLAKE3 manifest generation
  (replaces `regenerate_checksums.sh` + `b3sum`)
- `primalspring registry --check {source|graphs|coverage|all}` — method-string
  drift detection (replaces 4 `check_method_*.sh` bash/grep scripts)

## Script Triage (35 files, ~10K lines)

| Category | Count | Action |
|----------|------:|--------|
| DEPRECATED (NUCLEUS launchers) | 4 | Headers updated, callers rewired to Rust |
| CI_TOOL (absorbed to Rust) | 7 | 6 deprecated, 1 deleted |
| ORCHESTRATION | 9 | Callers rewired; composition_lib.sh P4 |
| CONSUMER | 3 | Documented as plasmidBin responsibility |
| DEMO | 5 | Retained for downstream springs |
| LAB | 4 | Retained (external benchScale/Docker/ADB) |
| BRIDGE | 3 | Retained (Godot, WebSocket, sporePrint) |

## Audit Results

| Dimension | Result |
|-----------|--------|
| Files >800 lines | 0 (max 776) |
| Unsafe blocks | 0 (`#![forbid(unsafe_code)]`) |
| Production mocks | 0 (harness genetics is correct test infra) |
| Runtime deps | 16, all justified |
| Clippy warnings | 0 |
| Test count | 813 (797 pass + 16 live-tier) |

## Impact on Downstream

- Springs using `nucleus_launcher.sh` should switch to Rust binary
- Springs using `check_method_*.sh` should switch to `primalspring registry`
- `fetch_primals.sh` deprecation pending `plasmidbin fetch` implementation
- `validate_compositions.py` deprecated; use `primalspring validate --tier live`
